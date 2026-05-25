---
title: YouTube Data API のクォータ枯渇を RSS で避ける設計にした話
tags:
  - Node.js
  - SQLite
  - RSS
  - YouTubeAPI
  - Electron
private: false
updated_at: '2026-05-20T19:57:00+09:00'
id: e2d5dba192540222d8d5
organization_url_name: null
slide: false
ignorePublish: false
---

※この記事は Zenn で公開した記事を、Qiita 向けに一部加筆・再構成したものです。

原文: [YouTube Data API のクォータ枯渇を RSS で99%削減した話](https://zenn.dev/harness17/articles/youtube-data-api-rss-quota-reduction)

## 何に詰まったか

個人開発の Electron アプリ [youtube-schedule](https://github.com/harness17/youtube-schedule) で、YouTube の配信予定をまとめて見る仕組みを作っていました。

最初は YouTube Data API で購読チャンネルを取得し、各チャンネルの新着動画を API で確認する構成でした。ところが、起動してしばらくすると `403 quotaExceeded` が返り、当日は何も更新できなくなりました。

原因は `search.list` の使い方です。

YouTube Data API のデフォルトクォータは 1 日 10,000 ユニットです。公式の Quota Calculator では、`search.list` は 1 回 100 ユニット、`subscriptions.list` / `playlistItems.list` / `videos.list` はそれぞれ 1 回 1 ユニットとされています。

参考: [Quota Calculator | YouTube Data API](https://developers.google.com/youtube/v3/determine_quota_cost)

購読チャンネルが約 300 件ある状態で、各チャンネルに `search.list` を投げると、

```text
300 channels * 100 units = 30,000 units
```

1 回のフル更新だけで、デフォルト上限の 3 倍です。30 分ごとに自動更新する設計なら、計算するまでもなく破綻します。

## RSS を入口に変えた

最初にやめたのは、チャンネルごとの新着取得に `search.list` を使うことでした。

YouTube にはチャンネルごとの RSS フィードがあります。

```text
https://www.youtube.com/feeds/videos.xml?channel_id={channelId}
```

このフィードから、動画 ID、タイトル、URL、公開時刻などを取得できます。API キーも OAuth トークンも不要で、YouTube Data API のクォータも消費しません。

実装では、RSS 取得専用の fetcher を作りました。以下は記事用に空フィード処理やログ周辺を省いた抜粋です。実コードは [`src/main/fetchers/rssFetcher.js`](https://github.com/harness17/youtube-schedule/blob/master/src/main/fetchers/rssFetcher.js) にあります。

```javascript
import nodeFetch from 'node-fetch'
import { XMLParser } from 'fast-xml-parser'

const UA = 'Mozilla/5.0 (compatible; YouTubeScheduleViewer)'

function buildUrl(channelId) {
  return `https://www.youtube.com/feeds/videos.xml?channel_id=${encodeURIComponent(channelId)}`
}

export function createRssFetcher({ timeoutMs = 3000, fetchImpl = nodeFetch } = {}) {
  const parser = new XMLParser({ ignoreAttributes: false, attributeNamePrefix: '' })

  async function fetchOne(channelId) {
    const url = buildUrl(channelId)
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), timeoutMs)

    let res
    try {
      res = await fetchImpl(url, {
        headers: { 'User-Agent': UA },
        signal: controller.signal
      })
    } catch (err) {
      clearTimeout(timer)
      if (err?.name === 'AbortError') {
        return { success: false, reason: 'timeout' }
      }
      return { success: false, reason: 'network', errorMessage: err?.message ?? String(err) }
    }

    clearTimeout(timer)
    if (!res.ok) {
      return {
        success: false,
        reason: res.status === 404 ? 'http_404' : `http_${res.status}`,
        httpStatus: res.status
      }
    }

    const text = await res.text()
    const parsed = parser.parse(text)
    const rawEntries = parsed?.feed?.entry
      ? Array.isArray(parsed.feed.entry)
        ? parsed.feed.entry
        : [parsed.feed.entry]
      : []

    const entries = rawEntries
      .map((e) => {
        const id = e['yt:videoId'] ?? e.videoId ?? null
        if (typeof id !== 'string' || id.length === 0) return null
        const media = e['media:group'] ?? {}
        return {
          id,
          title: e.title ?? media['media:title'] ?? '',
          description: media['media:description'] ?? '',
          url: typeof e.link?.href === 'string'
            ? e.link.href
            : `https://www.youtube.com/watch?v=${id}`,
          published: e.published ?? null,
          updated: e.updated ?? null
        }
      })
      .filter(Boolean)

    return { success: true, videoIds: entries.map((e) => e.id), entries, httpStatus: res.status }
  }

  return { fetch: fetchOne }
}
```

ここで大事だったのは、失敗時に例外を投げるだけにしないことです。

RSS は外部の公開フィードなので、タイムアウト、404、5xx、XML パース失敗が起こります。後段でフォールバック判断をするため、`success: false` と `reason` を返す形にしました。

## API は補助に回す

RSS だけで済ませるとクォータは軽くなりますが、取得できる情報には限界があります。

たとえば、RSS ではライブ配信の予定時刻や現在のライブ状態を安定して取れません。そのため、動画 ID の候補を RSS で集めたうえで、必要な動画だけ `videos.list` の `liveStreamingDetails` で補う構成にしました。また、RSS が一時的に失敗したチャンネルを完全に捨てると、同期漏れが起きます。

そこで、取得経路を次のように分けました。

| 役割 | 使うもの | クォータ |
|---|---|---:|
| 購読チャンネル一覧 | `subscriptions.list` | 1 u / request |
| 新着動画 ID の入口 | RSS | 0 u |
| RSS 失敗時の補完 | `playlistItems.list` | 1 u / request |
| 動画詳細・ライブ状態 | `videos.list` | 1 u / request |

`subscriptions.list` で購読チャンネルを取る部分は、24 時間キャッシュしています。以下は `src/main/services/schedulerService.js` から、判断に必要な部分だけを抜粋しています。

```javascript
const SUBS_CACHE_TTL_MS = 24 * 60 * 60 * 1000

async function resolveChannels(yt, now) {
  const lastSync = channelRepo.getLastSyncTime()
  if (lastSync && now - lastSync < SUBS_CACHE_TTL_MS) {
    return channelRepo.listAll().filter(isRssCapableChannel)
  }

  const fresh = await subsFetcher.fetch(yt)
  channelRepo.syncSubscriptions(fresh, now)
  return channelRepo.listAll().filter(isRssCapableChannel)
}
```

購読チャンネルが 300 件なら、`maxResults: 50` で 6 ページ程度です。30 分ごとに毎回取ると 1 日 288 ユニットですが、24 時間キャッシュなら 1 日 6 ユニット程度で済みます。

## RSS 失敗時だけ playlistItems.list に落とす

RSS が失敗したチャンネルだけ、アップロード済み動画の playlist にフォールバックします。以下も実装の要点だけを抜粋したコードです。

```javascript
const RSS_PARALLEL = 10
const RSS_FALLBACK_COOLDOWN_MS = 6 * 60 * 60 * 1000
const RSS_FALLBACK_MAX_PER_REFRESH = 20

async function collectVideoIds(yt, channels, now) {
  const collected = new Set()
  let fallbackAttempts = 0

  for (const batch of chunk(channels, RSS_PARALLEL)) {
    await Promise.all(
      batch.map(async (ch) => {
        const res = await rssFetcher.fetch(ch.id)

        if (res.success) {
          for (const id of res.videoIds) collected.add(id)
          return
        }

        if (!authClient || !ch.uploadsPlaylistId) return
        if (fallbackAttempts >= RSS_FALLBACK_MAX_PER_REFRESH) return

        const lastFallbackAt = getLastRssFallbackAt(metaRepo, ch.id)
        if (now - lastFallbackAt < RSS_FALLBACK_COOLDOWN_MS) return

        fallbackAttempts++
        recordRssFallback(metaRepo, ch.id, now)

        const fallback = await playlistFetcher.fetch(yt, ch.uploadsPlaylistId)
        for (const id of fallback) collected.add(id)
      })
    )
  }

  return [...collected]
}
```

ここは Zenn 公開時点よりも実装を少し固くしました。

単純に「RSS が失敗したら `playlistItems.list`」だけだと、RSS 側が広範囲に落ちたときに API 側へ一気に寄ってしまいます。そこで、現在の実装では次の 2 つを入れています。

- 1 回の更新で fallback するチャンネル数を `RSS_FALLBACK_MAX_PER_REFRESH` で制限する
- 同じチャンネルへの fallback を `RSS_FALLBACK_COOLDOWN_MS` で抑制する

RSS を使っているのに、障害時だけ API クォータを大量に使う設計だと本末転倒です。フォールバックにも上限を持たせる必要がありました。

## 詳細取得は videos.list にまとめる

RSS で拾った動画 ID から、必要なものだけ `videos.list` で詳細取得します。

自動更新では、新規動画、ライブ中、配信予定、一定時間以上再チェックしていない動画だけを対象にします。手動更新では `forceFullRecheck` を渡し、既知動画も再取得できるようにしています。実コードでは、手動登録動画なども再チェック対象に加えていますが、ここでは自動/手動の分岐が分かる部分に絞ります。

```javascript
const known = videoRepo.getByIds(videoIds)
const knownIds = new Set(known.map((v) => v.id))

const recheckIds = forceFullRecheck
  ? Array.from(knownIds)
  : known
      .filter(
        (v) =>
          v.status === 'live' ||
          v.status === 'upcoming' ||
          (v.status !== 'ended' && now - v.lastCheckedAt > 24 * 60 * 60 * 1000)
      )
      .map((v) => v.id)

const newIds = videoIds.filter((id) => !knownIds.has(id))
const target = Array.from(new Set([...newIds, ...recheckIds]))
const details = await videoFetcher.fetch(yt, target)
```

「自動更新」と「手動更新」で完全に別の経路を作るのではなく、同じ refresh に `forceFullRecheck` を渡す形にしました。分岐を増やすより、再取得対象の選び方だけを変える方が保守しやすかったです。

## クォータ超過は例外ではなく状態として扱う

クォータ対策を入れても、外部 API を使っている以上、`quotaExceeded` は起こり得ます。

最初はエラーがコンソールに出るだけでしたが、現在は `quotaExceeded` を検知したらアプリ内状態として記録し、画面上部のバナーでリセット目安を出す設計にしています。以下は `refresh` の catch 部分を抜粋したものです。

```javascript
try {
  await doRefresh(opts)
  if (metaRepo.get(QUOTA_EXCEEDED_META_KEY)) {
    metaRepo.set(QUOTA_EXCEEDED_META_KEY, '', Date.now())
  }
} catch (err) {
  if (isQuotaError(err)) {
    metaRepo.set(QUOTA_EXCEEDED_META_KEY, String(Date.now()), Date.now())
    logger.warn('scheduler.refresh.quotaExceeded', {
      durationMs: Date.now() - startedAt
    })
    return
  }
  throw err
}
```

YouTube Data API の daily quota は Pacific Time の midnight にリセットされます。日本時間で見ると、PDT 期間は 16:00 頃、PST 期間は 17:00 頃です。

参考: [Quota Calculator | YouTube Data API](https://developers.google.com/youtube/v3/determine_quota_cost)

トースト通知だけだと数秒で消えてしまい、「なぜ更新されないのか」が分かりません。クォータ超過は一時的な障害ではなく、その日の運用状態として扱う方がユーザーに伝わります。

## どれくらい減ったか

ざっくりした計算です。

旧構成:

```text
300 channels * search.list 100 u * 48 refresh/day
= 1,440,000 u/day
```

新構成:

```text
subscriptions.list: about 6 u/day
RSS: 0 u
playlistItems.list: RSS failure channels only, capped
videos.list: new/recheck target only
```

全件 `search.list` に比べると、通常時は 1 日 100 ユニット前後に収まる構成になりました。10,000 ユニット/日のデフォルト上限に対して 1% 前後です。

この数字はチャンネル数、RSS 失敗率、配信頻度、手動更新回数で変わります。それでも、設計の主軸を「高コスト API で検索する」から「0 クォータの公開フィードで候補を集め、必要なときだけ API で補う」に変えた効果は大きかったです。

## SQLite に RSS の観測ログを残す

RSS は公式 API ではなく公開フィードなので、失敗率を見えるようにしています。

実装では `rss_fetch_log` に取得結果を残し、直近 24 時間の失敗率を UI に出せるようにしました。DDL は初期 migration の該当部分です。

```sql
CREATE TABLE IF NOT EXISTS rss_fetch_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  channel_id TEXT NOT NULL,
  fetched_at INTEGER NOT NULL,
  success INTEGER NOT NULL,
  http_status INTEGER,
  error_message TEXT
);

CREATE INDEX IF NOT EXISTS idx_rss_log_time ON rss_fetch_log(fetched_at);
```

RSS が安定している前提で作るのではなく、壊れたときにどの程度 API 側へ寄っているかを観測できるようにしておく。個人開発でも、外部依存がある処理ではこのログが後から効きます。

## まとめ

YouTube Data API のクォータ枯渇に対して、効いた判断は次の 4 つでした。

1. `search.list` を定期実行の入口にしない
2. チャンネル RSS で動画 ID の候補を集める
3. `subscriptions.list` は 24 時間キャッシュする
4. RSS 失敗時の API fallback にはクールダウンと上限を入れる

外部 API のクォータで詰まったとき、いきなり追加クォータ申請やリトライ制御に向かう前に、まず「API でなくても取れる入口がないか」を見る価値があります。

今回の実装では RSS がその入口でした。RSS で候補を集め、API は補助に回す。これだけで、クォータ設計はかなり扱いやすくなりました。

## リンク

- [youtube-schedule リポジトリ](https://github.com/harness17/youtube-schedule)
- [RSS fetcher 実装](https://github.com/harness17/youtube-schedule/blob/master/src/main/fetchers/rssFetcher.js)
- [schedulerService 実装](https://github.com/harness17/youtube-schedule/blob/master/src/main/services/schedulerService.js)
- [README: コード署名と配布状況](https://github.com/harness17/youtube-schedule#%E3%82%B3%E3%83%BC%E3%83%89%E7%BD%B2%E5%90%8D)
- [Releases](https://github.com/harness17/youtube-schedule/releases)
- [YouTube Data API Quota Calculator](https://developers.google.com/youtube/v3/determine_quota_cost)
- [YouTube Data API: Search list](https://developers.google.com/youtube/v3/docs/search/list)
- [YouTube Data API: PlaylistItems list](https://developers.google.com/youtube/v3/docs/playlistItems/list)
- [Zenn 原文](https://zenn.dev/harness17/articles/youtube-data-api-rss-quota-reduction)
