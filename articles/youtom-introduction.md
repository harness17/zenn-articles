---
title: "推しの配信予定を見逃さないために Youtom を作った"
emoji: "📺"
type: "tech"
topics: ["electron", "react", "youtube", "nodejs", "indie"]
published: false
---

## はじめに

[Youtom](https://github.com/harness17/youtube-schedule) は、YouTube の登録チャンネルの配信予定・ライブ中の動画を一覧表示する Windows デスクトップアプリです。

YouTube の登録チャンネル画面は、配信予定を時系列で追う用途には向いていません。複数チャンネルを見ていると、「今日どの配信があるのか」「もう始まっている配信はどれか」「あとで見たい配信をどこに残すか」が分かりづらくなります。

その不便さを、自分用のデスクトップアプリとして切り出したのが Youtom です。この記事では、アプリの紹介をしつつ、配布しやすさと取得精度を両立するために簡易モードとフルモードを分けた判断を書きます。

## Youtom でできること

Youtom の中心は、配信予定とライブ中の動画を一覧で見る画面です。

- 配信予定・ライブ中の動画を日付ごとに表示する
- ライブ中の配信を上に出す
- 気になる配信に通知フラグを付ける
- 推しチャンネルをピン留めして一覧の上に寄せる
- 見逃し・アーカイブ・お気に入りを別タブで管理する
- 簡易モードでは OAuth なしでチャンネルを手動追加する

リポジトリは GitHub に公開しています。

https://github.com/harness17/youtube-schedule

最初は「登録チャンネルの配信予定を時刻順に見たい」という小さな要求でした。作っていくうちに、見逃し管理、通知、お気に入り、アーカイブ検索、ダークモード、自動アップデートまで増えました。

ただ、機能を増やすほど導入手順も重くなります。特に YouTube Data API を使う場合、Google Cloud Console で OAuth クライアントを作る必要があります。自分用なら許容できますが、他の人に使ってもらうには初手から重い手順です。

## 簡易モードとフルモードを分けた

そこで、Youtom では動作モードを 2 つに分けました。

| モード | 認証 | 主な用途 |
| --- | --- | --- |
| 簡易モード | 不要 | 手動追加したチャンネルの新着動画を見る |
| フルモード | 必要 | 登録チャンネル同期、配信予定時刻、ライブ検出、見逃し追跡を使う |

簡易モードは RSS だけで動きます。Google Cloud Console の設定も `credentials.json` も不要です。チャンネル URL や `@handle` を手動追加して、RSS フィードから新着動画を取得します。

フルモードは YouTube Data API を使います。登録チャンネルを自動同期し、`videos.list` で `liveStreamingDetails` を取得するため、配信予定時刻やライブ状態をより正確に扱えます。

この分け方にした理由は、導入の軽さと精度がトレードオフになるからです。

- 最初に触る人には、簡易モードで起動できるほうがよい
- 配信予定時刻や見逃し追跡が必要な人には、フルモードを案内したい
- 開発者の OAuth クライアントを同梱すると、全ユーザーでクォータを共有してしまう
- RSS-only に寄せ切ると、ライブ判定や予定時刻の精度が落ちる

この判断で、「すぐ使える入口」と「必要な人向けの高精度モード」を同じアプリ内に置けました。実際、簡易モードはアプリを起動してチャンネル URL や `@handle` を貼り付けるだけで動き出すのに対して、フルモードは Google Cloud Console で OAuth クライアントを作って `credentials.json` を配置する手順が入ります。同じアプリでもファーストタッチの所要時間は数十秒と十数分くらい違います。

## 実装では RSS を入口にした

簡易モードの入口は、チャンネルごとの RSS フィードです。

```text
https://www.youtube.com/feeds/videos.xml?channel_id={channelId}
```

実装では `fast-xml-parser` で Atom フィードを読み、動画 ID、タイトル、URL、公開時刻を取り出しています。

```javascript
export function createRssFetcher({ timeoutMs = 3000, fetchImpl = nodeFetch } = {}) {
  const parser = new XMLParser({ ignoreAttributes: false, attributeNamePrefix: '' })

  async function fetchOne(channelId) {
    const url = buildUrl(channelId)
    const controller = new AbortController()
    const timer = setTimeout(() => controller.abort(), timeoutMs)

    const res = await fetchImpl(url, {
      headers: { 'User-Agent': UA },
      signal: controller.signal
    })

    const text = await res.text()
    const parsed = parser.parse(text)
    const rawEntries = parsed?.feed?.entry
      ? Array.isArray(parsed.feed.entry)
        ? parsed.feed.entry
        : [parsed.feed.entry]
      : []

    return rawEntries.map((entry) => ({
      id: entry['yt:videoId'],
      title: entry.title,
      url: entry.link?.href,
      published: entry.published
    }))
  }

  return { fetch: fetchOne }
}
```

実際のコードでは、タイムアウト、HTTP エラー、空フィード、パース失敗をそれぞれ扱っています。RSS は無料で軽い一方、配信予定時刻やライブ状態までは安定して取れません。そのため、簡易モードでは「新着動画」として扱い、フルモードの「予定・ライブ」とはタブを分けています。

画面側でも、認証状態によって表示するタブを切り替えています。

```javascript
const tabs = [
  { key: 'feed', label: '新着動画', mode: 'simple' },
  { key: 'schedule', label: '予定・ライブ', mode: 'full' },
  { key: 'missed', label: '見逃し', mode: 'full' },
  { key: 'archive', label: 'アーカイブ', mode: 'full' },
  { key: 'favorites', label: 'お気に入り', mode: 'both' }
]

const visibleTabs = tabs.filter(
  (tab) => tab.mode === 'both' || (isAuthenticated ? tab.mode === 'full' : tab.mode === 'simple')
)
```

簡易モードで「予定・ライブ」タブを見せてしまうと、時刻が取れない動画と時刻付きの予定が混ざります。機能不足を UI 上で隠すより、取得できる情報に合わせて画面を分けるほうが誤解が少ないと判断しました。

## 自分用ツールから配布できる形へ

Youtom は最初から完成形を狙ったアプリではありません。自分が困ったところから順に足しています。

たとえば、気になる配信を後から見返すために「お知らせ」や「お気に入り」を追加しました。過去配信を探すためにアーカイブ検索を入れました。よく見るチャンネルを埋もれさせないためにピン留めを入れました。

その一方で、配布するときに邪魔になる部分も見えてきました。

- `credentials.json` の配置手順が分かりづらい
- Windows の未署名アプリ警告が出る
- YouTube Data API のクォータをどう分離するか考える必要がある
- RSS と API では取れる情報の粒度が違う

このあたりは、個人開発アプリを「自分だけが使える道具」から「他の人も試せる道具」に寄せるときに避けて通れませんでした。

## どんな人に向いているか

Youtom は、次のような人向けです。

- 複数の YouTube チャンネルの配信予定を追っている
- ライブ配信を見逃しやすい
- 気になる配信をお気に入りとして残したい
- YouTube の通常 UI では一覧性が足りない
- Electron 製の個人開発アプリの実装例を見たい

まずは簡易モードでチャンネルを手動追加し、必要になったらフルモードに切り替える使い方を想定しています。

## まとめ

Youtom は、YouTube の配信予定を時系列で追うために作った Electron アプリです。

技術的には、RSS で軽く始められる簡易モードと、YouTube Data API で精度を上げるフルモードを分けたことが大きな判断でした。プロダクトとしては、初回起動の軽さを確保しつつ、必要な人には登録チャンネル同期や見逃し追跡を提供できる構成になっています。

個人開発アプリは、機能追加よりも「どこまでを初手で要求するか」が体験に効くと感じました。Youtom では、その境界をモード分けで扱っています。

## 参考リンク

- [Youtom / youtube-schedule リポジトリ](https://github.com/harness17/youtube-schedule)
- [Releases](https://github.com/harness17/youtube-schedule/releases)
- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [Electron](https://www.electronjs.org/)
