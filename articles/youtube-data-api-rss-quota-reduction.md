---
title: "YouTube Data API のクォータ枯渇を RSS で99%削減した話"
emoji: "📉"
type: "tech"
topics: ["youtube", "googleapi", "electron", "nodejs", "rss"]
published: true
---

## はじめに

個人開発の Electron デスクトップアプリ [youtube-schedule](https://github.com/harness17/youtube-schedule) で、YouTube Data API のクォータを数時間で使い切った話です。最終的には `search.list` を RSS フィードに切り替えてクォータ消費を 99% 削減しましたが、そこに至るまでの設計の階段を順に書きます。

同じように外部 API のクォータで詰まっている個人開発者向けに、「公開フィードがあるなら API より先にそっちを試す」という考え方を共有します。

## クォータが枯渇するまで

当時の構成はシンプルでした。

- Electron デスクトップアプリで、起動時と 30 分間隔でバックグラウンド更新
- 認証ユーザーの購読チャンネルは約 **300 件**
- 各チャンネルの新着動画 ID を `search.list` で取得

YouTube Data API v3 の上限は **10,000 ユニット/日**。主要な呼び出しのコストは公式ドキュメントに載っています。

| メソッド | コスト |
|---------|--------|
| `search.list` | **100 ユニット** |
| `subscriptions.list` | 1 ユニット |
| `playlistItems.list` | 1 ユニット |
| `videos.list` | 1 ユニット |

300 チャンネルに対して `search.list` を叩くと 100 × 300 = **30,000 ユニット**。1 回のフルリフレッシュで上限の 3 倍を消費する計算でした。

実際にアプリを起動するとクォータ枯渇まで一発で到達し、`403 quotaExceeded` が返り始めました。クォータのリセットは太平洋時間 0:00 です。日本時間では夏時間中（PDT, UTC-7）は 16:00、標準時間中（PST, UTC-8）は 17:00 頃なので、それまでは何もできません。

参考: [YouTube Data API v3 — Quota and Usage](https://developers.google.com/youtube/v3/getting-started#quota)

## 第1層：search.list を RSS に切り替えた

転換点は 2026 年 4 月 12 日のコミットでした。

> `perf: replace search.list with RSS feed to reduce quota usage 99%`

YouTube はチャンネルごとに RSS フィードを公開しています。

```text
https://www.youtube.com/feeds/videos.xml?channel_id={channelId}
```

このフィードから取れるのは次のような情報です。自分の検証では、取得できる動画は最新 15 件でした。

- 最新 **15 件** の動画 ID
- タイトル・公開時刻・説明文

API キーも OAuth トークンも不要、コストは **0 ユニット**。`fetch` で取って XML をパースするだけです。

```javascript
import nodeFetch from 'node-fetch'
import { XMLParser } from 'fast-xml-parser'

const UA = 'Mozilla/5.0 (compatible; YouTubeScheduleViewer)'

export function createRssFetcher({ timeoutMs = 3000 } = {}) {
  const parser = new XMLParser({ ignoreAttributes: false, attributeNamePrefix: '' })

  async function fetchOne(channelId) {
    const url = `https://www.youtube.com/feeds/videos.xml?channel_id=${encodeURIComponent(channelId)}`
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), timeoutMs)

    let res
    try {
      res = await nodeFetch(url, { headers: { 'User-Agent': UA }, signal: controller.signal })
    } catch (err) {
      clearTimeout(timer)
      if (err?.name === 'AbortError') return { success: false, reason: 'timeout' }
      return { success: false, reason: 'network' }
    }
    clearTimeout(timer)

    if (!res.ok) {
      return { success: false, reason: `http_${res.status}`, httpStatus: res.status }
    }

    const text = await res.text()
    const parsed = parser.parse(text)
    // entries から videoIds を取り出す（実装は省略）
    return { success: true, videoIds, entries }
  }

  return { fetch: fetchOne }
}
```

ただし RSS にも落とし穴があります。

- 自分の検証では最新 **15 件しか返らない** ので、それより古い動画は取れない
- メンバー限定動画はフィードに出てこない
- ネットワーク失敗・404・パース失敗があるため、失敗理由を構造化して返す設計が必要

特に「失敗理由を返す」ところは、後の **フォールバック階段化** で必須になります。次のセクションで説明します。

これで `search.list` を完全になくせました。残るは購読チャンネル取得（`subscriptions.list`）です。次の層で削ります。

## 第2層：キャッシュとフォールバックで階段化する

RSS は便利ですが万能ではありません。失敗時の補完と、購読チャンネル取得の節約を組み合わせます。

### subscriptions.list の 24 時間キャッシュ

購読チャンネルは頻繁に変わりません。1 日 1 回取れば十分です。

```javascript
const SUBS_CACHE_TTL_MS = 24 * 60 * 60 * 1000

async function resolveChannels(yt, now) {
  const lastSync = channelRepo.getLastSyncTime()
  if (lastSync && now - lastSync < SUBS_CACHE_TTL_MS) {
    return channelRepo.listAll() // キャッシュから返す
  }
  const fresh = await subsFetcher.fetch(yt)
  channelRepo.syncSubscriptions(fresh, now)
  return fresh
}
```

300 チャンネルだと `subscriptions.list` は `pageToken` で 50 件ずつ 6 ページ取得し、6 ユニット消費します。

- キャッシュなし（30 分間隔）：6 u × 48 回 = **288 u/日**
- キャッシュあり：**6 u/日**

数字としては小さいですが、後述のフォールバック分や `videos.list` の余地を確保するために削れるところは削っておきます。

### RSS が落ちたら playlistItems.list にフォールバック

RSS は YouTube 側の都合で `404` や `5xx` を返すことがあります。RSS が失敗したチャンネルだけ `playlistItems.list`（1 ユニット/ch）にフォールバックします。

```javascript
for (const batch of chunk(channels, RSS_PARALLEL)) {
  await Promise.all(
    batch.map(async (ch) => {
      const res = await rssFetcher.fetch(ch.id)
      if (res.success) {
        // RSS で取得成功（0 u）
        for (const id of res.videoIds) collected.add(id)
      } else {
        // RSS 失敗 → playlistItems にフォールバック（1 u/ch）
        const fallback = await playlistFetcher.fetch(yt, ch.uploadsPlaylistId)
        for (const id of fallback) collected.add(id)
      }
    })
  )
}
```

`playlistItems.list` はチャンネルごとの「アップロード済み動画プレイリスト」を取得する API で、実装では `uploadsPlaylistId` をチャンネル ID から組み立てています（`UCxxx` の頭 2 文字を `UU` に置き換える）。公式に取得するなら、`channels.list` の `contentDetails.relatedPlaylists.uploads` を使う方法があります。

これで RSS が一時的に落ちている間も、最低限の同期を維持できます。

### 数字で締める

旧（全件 `search.list`）：300 ch × 100 u × 48 回/日 = **1,440,000 u/日**（上限の 144 倍）
新（RSS + キャッシュ + フォールバック）：subs 6 u + RSS 0 u + `videos.list` の詳細取得が数十 u = **100 u/日 前後**

10,000 u/日の上限に対して **1% 以下** に収まる構成になりました。

## 第3層：自動と手動はフラグ 1 つで切り分ける

自動ポーリングと手動更新を「別経路」にする必要はありません。同じ取得関数にフラグ 1 つ渡すだけで十分です。

```javascript
// 自動: 30 分ごとにバックグラウンド更新
const REFRESH_INTERVAL_MS = 30 * 60 * 1000
setInterval(() => scheduler.refresh(), REFRESH_INTERVAL_MS)

// 手動: ユーザーが画面のボタンを押したとき
ipcMain.handle('schedule:refresh', async () => {
  await scheduler.refresh({ forceFullRecheck: true })
})
```

`forceFullRecheck: true` のとき、既知動画も含めて `videos.list` で再取得します。「見たいときに最新」をユーザーに提供しつつ、自動分の消費は最小に保てます。

「自動と手動で取得経路を完全に分ける」設計も検討しましたが、フラグ 1 つの方が読み手のコードもシンプルで、実装側のメンテナンスも楽でした。

## 第4層：クォータ切れ時のユーザー案内（今後の課題）

正直に書きます。現状の実装は簡易トーストだけです。

```javascript
useEffect(() => {
  if (error === 'QUOTA_EXCEEDED') {
    setToast('本日の API 上限に達しました')
  }
}, [error])
```

ここはまだ改善余地があります。

- 「消えないバナー」を画面上部に常時表示
- リセット時刻を JST で計算して表示（PT 0:00 → PDT 期間は JST 16:00、PST 期間は JST 17:00 頃）
- 「次のリセット時刻まで使えない」とユーザーが分かるように

トーストは数秒で消えるので、起動した瞬間に枯渇していると、ユーザーは「何も表示されない原因」を理解できません。書いている自分にも宿題として残っています。

## まとめ

クォータ枯渇の対策として効いた 3 つの判断です。

1. **`search.list` は捨てて RSS にする** — チャンネルごとの RSS フィードで 0 ユニット。99% 削減できた決定打
2. **キャッシュとフォールバックで階段化** — `subscriptions.list` は 24 時間キャッシュ、RSS 失敗時は `playlistItems.list` にフォールバック
3. **自動と手動はフラグ 1 つで切り分け** — 経路を分ける必要はなく、`forceFullRecheck` で十分

他の API（Twitch、Spotify、Mastodon など）にも応用できる原則は、

> **公開フィードがあるなら API より先にそっちを試す**

実装は [youtube-schedule](https://github.com/harness17/youtube-schedule) の `src/main/fetchers/` と `src/main/services/schedulerService.js` にあります。自分はこの一件以来、新しい外部 API を触るときは公式ドキュメントよりも先に「公開フィードはあるか」「キャッシュで節約できる呼び出しはどれか」を確認する手癖がつきました。

## 参考リンク

- [YouTube Data API v3 — Quota and Usage](https://developers.google.com/youtube/v3/getting-started#quota)
- [YouTube Data API v3 — Methods](https://developers.google.com/youtube/v3/docs)
- [youtube-schedule リポジトリ](https://github.com/harness17/youtube-schedule)
- 該当コミット: [`f815c16` perf: replace search.list with RSS feed to reduce quota usage 99%](https://github.com/harness17/youtube-schedule/commit/f815c16)
