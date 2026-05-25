---
title: YouTubeの配信予定を追うWindowsアプリ Youtom を作った
tags:
  - RSS
  - YouTubeAPI
  - React
  - Electron
  - 個人開発
private: false
updated_at: '2026-05-20T19:57:30+09:00'
id: 52c94119fed2aba20f7e
organization_url_name: null
slide: false
ignorePublish: false
---

※この記事は Zenn で公開した記事を、Qiita 向けに一部加筆・再構成したものです。

原文: [推しの配信予定を見逃さないために Youtom を作った](https://zenn.dev/harness17/articles/youtom-introduction)

## 作ったもの

[Youtom](https://github.com/harness17/youtube-schedule) は、YouTube の配信予定・ライブ中の動画・見逃しをまとめて見るための Windows デスクトップアプリです。

複数のチャンネルを追っていると、YouTube の通常 UI だけでは次のような確認が面倒になります。

- 今日どの配信があるのか
- もう始まっている配信はどれか
- あとで見るつもりだった配信をどこに残すか
- よく見るチャンネルを一覧の上に固定できないか

最初は自分用に「配信予定を日付順に見たい」という小さな要求から作り始めました。今は、予定・ライブ、見逃し、アーカイブ、お気に入り、チャンネル推し設定、手動追加、ダークモード、自動アップデートまで入っています。

リポジトリと配布物は次にあります。

- [harness17/youtube-schedule](https://github.com/harness17/youtube-schedule)
- [Releases](https://github.com/harness17/youtube-schedule/releases)

## 最初からOAuth必須にしない

Youtom で一番悩んだのは、YouTube Data API をどこまで初回導入に要求するかでした。

登録チャンネルの自動同期や配信予定時刻を正確に扱うには、YouTube Data API が必要です。ただし API を使うには、ユーザー自身が Google Cloud Console で OAuth クライアントを作り、アプリに `credentials.json` を読み込ませる必要があります。

開発者なら理解できますが、「配信予定を見たいだけ」の人に最初からこの手順を要求すると、そこで離脱します。

そこで、Youtom は簡易モードとフルモードを分けています。

| モード | 認証 | できること | 向いている人 |
| --- | --- | --- | --- |
| 簡易モード | 不要 | 手動追加したチャンネルの新着動画を見る | まず触ってみたい人 |
| フルモード | 必要 | 登録チャンネル同期、配信予定時刻、ライブ検出、見逃し追跡 | 日常的に使いたい人 |

簡易モードは RSS だけで動きます。Google Cloud Console の設定も `credentials.json` も不要です。チャンネル URL や `@handle` を追加すると、そのチャンネルの RSS フィードから新着動画を取得します。

フルモードは YouTube Data API を使います。`subscriptions.list` で登録チャンネルを同期し、`videos.list` の `liveStreamingDetails` で配信予定時刻やライブ状態を補います。

## RSSとAPIで役割を分ける

RSS と YouTube Data API で取れる情報は違います。

| 取得方法 | 取れる情報 | 苦手なこと |
| --- | --- | --- |
| RSS | 新着動画、タイトル、URL、公開時刻 | 登録チャンネルの自動同期、予定時刻、ライブ状態 |
| YouTube Data API | 登録チャンネル、予定時刻、ライブ状態、動画詳細 | OAuth 設定、クォータ管理、認証エラー対応 |

この違いを隠さず、UI 側でもモードを分けています。

簡易モードでは「新着動画」タブを見せます。フルモードでは「予定・ライブ」「見逃し」「アーカイブ」「統計」など、API の詳細情報を前提にしたタブを見せます。

実コードでは、認証状態に応じて表示タブを切り替えています。以下は記事用に要点だけを抜粋した例です。実装全体は [`src/renderer/src/App.jsx`](https://github.com/harness17/youtube-schedule/blob/master/src/renderer/src/App.jsx) にあります。

```javascript
const tabs = [
  { key: 'feed', label: '新着動画', mode: 'simple' },
  { key: 'schedule', label: '予定・ライブ', mode: 'full' },
  { key: 'missed', label: '見逃し', mode: 'full' },
  { key: 'archive', label: 'アーカイブ', mode: 'full' },
  { key: 'favorites', label: 'お気に入り', mode: 'both' },
  { key: 'stats', label: '統計', mode: 'full' }
]

const visibleTabs = tabs.filter(
  (tab) => tab.mode === 'both' || (isAuthenticated ? tab.mode === 'full' : tab.mode === 'simple')
)
```

RSS で取得した動画に「予定・ライブ」らしい見た目を付けることもできます。しかし RSS にはスケジュール情報が含まれないため、未開始の配信予定と公開済み動画が混ざります。そこで、簡易モードは「新着動画」として扱い、フルモードの「予定・ライブ」とは分けました。

## RSS取得は軽い入口にする

簡易モードの入口は、チャンネルごとの RSS フィードです。

```text
https://www.youtube.com/feeds/videos.xml?channel_id={channelId}
```

実装では `fast-xml-parser` で Atom フィードを読み、動画 ID、タイトル、URL、公開時刻を取り出しています。以下は流れを説明するための抜粋で、このまま貼る用途の完全版ではありません。実コードではタイムアウト、HTTP エラー、空フィード、パース失敗も扱っています。

```javascript
import nodeFetch from 'node-fetch'
import { XMLParser } from 'fast-xml-parser'

function buildUrl(channelId) {
  return `https://www.youtube.com/feeds/videos.xml?channel_id=${encodeURIComponent(channelId)}`
}

export function createRssFetcher({ timeoutMs = 3000, fetchImpl = nodeFetch } = {}) {
  const parser = new XMLParser({ ignoreAttributes: false, attributeNamePrefix: '' })

  async function fetchOne(channelId) {
    const res = await fetchImpl(buildUrl(channelId), {
      headers: { 'User-Agent': 'Mozilla/5.0 (compatible; YouTubeScheduleViewer)' }
    })
    const parsed = parser.parse(await res.text())
    const rawEntries = parsed?.feed?.entry
      ? Array.isArray(parsed.feed.entry)
        ? parsed.feed.entry
        : [parsed.feed.entry]
      : []

    return rawEntries
      .map((entry) => ({
        id: entry['yt:videoId'],
        title: entry.title,
        url: entry.link?.href,
        published: entry.published
      }))
      .filter((entry) => entry.id)
  }

  return { fetch: fetchOne }
}
```

実コード: [`src/main/fetchers/rssFetcher.js`](https://github.com/harness17/youtube-schedule/blob/master/src/main/fetchers/rssFetcher.js)

RSS はクォータを消費しないので、最初の入口としては軽いです。一方で、配信予定時刻やライブ状態までは安定して取れません。そのため、Youtom では RSS を「まず触れる入口」として使い、精度が必要な機能は YouTube Data API に寄せています。

たとえば簡易モードでは、RSS で見える動画を「新着動画」として表示します。フルモードでは、同じ動画 ID に対して `videos.list` を使い、`liveStreamingDetails.scheduledStartTime` やライブ状態を補います。ここを混ぜると、「時刻が分かる配信予定」と「公開済み動画」が同じ一覧に並んでしまうため、タブを分けています。

## 認証ファイルが壊れても起動は止めない

配布アプリでは、認証ファイルまわりの失敗も初回体験に直結します。

たとえば `credentials.json` がない、形式が違う、読み込みに失敗する、といった状態は起こります。このときアプリ全体を起動不能にすると、簡易モードまで使えません。

そのため、現在の Youtom では `credentials.json` が壊れていても起動を継続し、簡易モードに退避します。README でも、簡易モードは OAuth なしで動くことを先に案内しています。

接続タブでは、`credentials.json` の状態と Google 連携状態をバッジで見せています。認証情報の読み込みと Google 連携を設定モーダル内に閉じ込めたことで、起動直後に認証画面で止まる構成を避けました。

関連実装:

- [`src/main/auth.js`](https://github.com/harness17/youtube-schedule/blob/master/src/main/auth.js)
- [`src/main/services/credentialsValidator.js`](https://github.com/harness17/youtube-schedule/blob/master/src/main/services/credentialsValidator.js)
- [`src/renderer/components/SettingsModal.jsx`](https://github.com/harness17/youtube-schedule/blob/master/src/renderer/components/SettingsModal.jsx)

## 配布時の壁はSmartScreenだった

Windows 向けに配布すると、未署名アプリでは SmartScreen の警告が出ます。

Youtom のリリースも、現時点では未署名です。README には回避手順を明記しています。

```text
1. 「詳細情報」をクリック
2. 「実行」ボタンをクリック
```

これはウイルスという意味ではなく、コード署名証明書がないアプリに出る一般的な警告です。ただ、ユーザーから見ると不安になります。

SignPath Foundation の OSS コード署名は一度申請しましたが、外部の利用実績・言及などの信頼シグナル不足で未承認でした。そこで今は、GitHub Release、Zenn / Qiita 記事、SNS告知などで、まずプロジェクトの外部信頼シグナルを積み上げる方針にしています。

この事情は、技術記事としては宣伝ではなく、個人開発アプリを配布するうえで実際に踏む問題でした。実装だけでなく、配布経路と信頼の作り方もプロダクト体験に含まれます。

## どんな人に向いているか

Youtom は、次のような人向けです。

- 複数の YouTube チャンネルの配信予定を追っている
- ライブ配信を見逃しやすい
- 気になる配信をお気に入りとして残したい
- YouTube の通常 UI では一覧性が足りない
- Electron 製の個人開発アプリの実装例を見たい

まずは簡易モードでチャンネルを手動追加し、必要になったらフルモードに切り替える使い方を想定しています。

## まとめ

Youtom では、導入の軽さと取得精度を分けて扱いました。

1. RSS だけで動く簡易モードを用意する
2. 正確な予定時刻や見逃し追跡は YouTube Data API を使うフルモードに寄せる
3. 認証ファイルが壊れていても簡易モードで起動できるようにする
4. 未署名配布の警告やコード署名の課題も README で説明する

個人開発アプリは、機能を増やすほど初回導入が重くなります。Youtom では、最初に触る人には RSS だけの軽い入口を渡し、必要な人だけ OAuth と API を設定する形にしました。

## リンク

- [Youtom / youtube-schedule リポジトリ](https://github.com/harness17/youtube-schedule)
- [Releases](https://github.com/harness17/youtube-schedule/releases)
- [README: インストールと簡易/フルモードの説明](https://github.com/harness17/youtube-schedule#readme)
- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [Electron](https://www.electronjs.org/)
- [Zenn 原文](https://zenn.dev/harness17/articles/youtom-introduction)
