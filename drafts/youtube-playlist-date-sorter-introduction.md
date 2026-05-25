# YouTubeプレイリストを投稿日順に見るChrome拡張を作った話

## メタ情報

- type: tech
- topics: [chrome拡張, manifestv3, javascript, youtube, 個人開発]
- 想定文字数: 2500〜3500字
- 想定執筆時間: 4〜5時間
- ステータス: 構成中
- 候補対応: K の派生。Manifest V3 移行の網羅ではなく、YouTube プレイリストを投稿日順に見るための実装判断に絞る

## 想定読者

YouTube の既存 UI では足りない並び順や操作を、Chrome 拡張で自分用に補いたい個人開発者。

## 読者前提と補足する用語

- 既知として扱うこと:
  - JavaScript の基本構文
  - Chrome 拡張が `manifest.json` を持つこと
  - YouTube のプレイリスト URL に `list` パラメータが含まれること
- 本文で補足する用語:
  - Manifest V3
  - content script
  - `chrome.storage.local`
  - YouTube の SPA 遷移
  - MutationObserver
- 初心者向け問題設定:
  - YouTube のプレイリストは、所有者が設定した順序では見られるが、「動画の投稿日が古い順に見たい」という用途ではそのまま扱いづらい。API でプレイリスト全体を取り直す方法もあるが、API キー、クォータ、認証設定が増える。今回はプレイリスト自体を変更せず、表示中の DOM と動画ページ HTML だけを使って、拡張側で投稿日順に並び替える判断をした。

## 構成

### はじめに（200〜300字）

- 何の記事か:
  - YouTube プレイリストを投稿日順に並び替え、その順序で次の動画へ移動する Chrome 拡張を作った話。
- 誰に読んでほしいか:
  - YouTube の UI を自分の用途に合わせたい人。
  - API キーを使わず、content script 中心で小さな拡張を作りたい人。
- 何が分かるか:
  - API を使わない判断。
  - DOM と動画 HTML から投稿日を集める流れ。
  - YouTube の再描画や SPA 遷移で詰まった点。
- 初出用語の短い補足:
  - content script は、対象ページ上で動く Chrome 拡張側の JavaScript。

### 本論セクション1: 何を作ったか

- 伝えること:
  - YouTube の `/playlist` と `/watch?...&list=...` で、表示中の動画を投稿日順に並び替える拡張である。
  - プレイリストの所有者データや YouTube 本体の内部キューは変更しない。
- 具体例:
  - README の機能説明。
  - UI 操作: 右下パネル、昇順 / 降順 / 通常順、次の動画へ、自動 ON、言語切替、最小化。
- 想定文字数:
  - 500〜700字
- 前後の接続:
  - 「何を作ったか」から「なぜ API を使わなかったか」へつなぐ。

### 本論セクション2: YouTube Data API ではなく DOM と HTML を使った

- 伝えること:
  - API キーなしで使えることを優先した。
  - content script の対象は YouTube 全体に広げつつ、パネル表示は `/playlist` と `/watch` の playlist 付き URL だけに絞っている。
  - 投稿日は各動画ページ HTML の `publishDate` / `datePublished` / 日本語日付表記から抽出する。
- 具体例:
  - `manifest.json` の `permissions: ["storage"]`、`host_permissions: ["https://www.youtube.com/*"]`、content script。
  - `shared/date-sorter.js` の `extractPublishDateFromHtml`。
- 想定文字数:
  - 700〜900字
- 前後の接続:
  - API を使わない設計は導入を軽くする一方、DOM 依存と HTML 解析の脆さを受け入れる必要がある、とつなぐ。

### 本論セクション3: 並び替えは表示 DOM と拡張側の次動画制御で実現した

- 伝えること:
  - プレイリストの保存順を変更するのではなく、画面上の行を並び替え、次に開く動画 URL を拡張側で決める。
  - 日付が取れない動画は最後に回し、同日や不明時は元の表示順を使う。
- 具体例:
  - `extractPlaylistItemsFromDocument` で videoId / title / originalIndex を取る。
  - `sortItemsByPublishDate` で `originalIndex` を tie-breaker に使う。
  - `findNextVideoId` と `buildWatchUrl`。
- 想定文字数:
  - 600〜800字
- 前後の接続:
  - 単純なソートだけでは YouTube の再描画で崩れるため、次のセクションで安定化の話へ移る。

### 本論セクション4: YouTube の SPA と再描画でパネルとバッジが消えた

- 伝えること:
  - `/playlist` から `/watch` へ遷移してもページ全体は再読み込みされないため、content script の初期化だけに頼るとパネルやバッジが不安定になった。
  - `yt-navigate-finish`、`popstate`、定期チェック、MutationObserver を組み合わせた。
  - バッジの remove / append を毎回行うと MutationObserver が再発火して点滅したため、差分更新に寄せた。
- 具体例:
  - `onNavigationMaybeChanged`
  - `ensurePanelObserver`
  - `tryAutoEnableSavedBadges`
  - `isOwnVisualMutation`
- 想定文字数:
  - 800〜1000字
- 前後の接続:
  - 実装の詰まりから、拡張を作るときの注意点としてまとめへつなぐ。

### まとめ（150〜250字）

- 要点3つ:
  - API キーなしで使える拡張にするため、YouTube Data API ではなく DOM と動画ページ HTML を使った。
  - プレイリスト自体は変更せず、表示順と次に開く URL を拡張側で制御した。
  - YouTube の SPA と再描画に合わせるには、初期化・復元・MutationObserver の扱いが実装の中心になった。

## コード例の準備状況

| セクション | コード言語 | 出典 | 準備状況 |
| --- | --- | --- | --- |
| API キーなしの権限設計 | json | `H:\ClaudeCode\GoogleChrome\youtube-playlist-date-sorter\manifest.json` | 場所確認済み |
| 投稿日抽出 | javascript | `H:\ClaudeCode\GoogleChrome\youtube-playlist-date-sorter\shared\date-sorter.js` | 場所確認済み |
| 並び替えと次動画決定 | javascript | `H:\ClaudeCode\GoogleChrome\youtube-playlist-date-sorter\shared\date-sorter.js` | 場所確認済み |
| プレイリスト行の取得 | javascript | `H:\ClaudeCode\GoogleChrome\youtube-playlist-date-sorter\content\content.js` | 場所確認済み |
| SPA 遷移と表示復元 | javascript | `H:\ClaudeCode\GoogleChrome\youtube-playlist-date-sorter\content\content.js` | 場所確認済み |
| 回帰確認 | javascript | `H:\ClaudeCode\GoogleChrome\youtube-playlist-date-sorter\verify-date-sorter.mjs` | 場所確認済み |

## 図表・比較表の予定

- 概念関係図:
  - Mermaid で「YouTube ページ DOM → videoId 抽出 → 各動画 HTML fetch → publishDate 抽出 → 並び替え → DOM 反映 / 次動画 URL 決定」を描く。
- トレードオフ表:
  - YouTube Data API を使う場合 / DOM + HTML を使う場合。
- 導入後の詰まりどころ:
  - YouTube の DOM 構造変更に弱い。
  - 表示中の最大 120 件だけを対象にしている。
  - SPA 遷移で content script の初期化タイミングがずれる。
  - MutationObserver で自分の DOM 変更を拾うと再描画ループになる。

## 参考リンク候補

- [google-chrome-extensions リポジトリ](https://github.com/harness17/google-chrome-extensions)
- [Chrome Extensions Manifest V3](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3)
- [chrome.storage API](https://developer.chrome.com/docs/extensions/reference/api/storage)
- [MutationObserver - MDN](https://developer.mozilla.org/docs/Web/API/MutationObserver)
- [YouTube Playlist Date Sorter README](https://github.com/harness17/google-chrome-extensions/tree/main/youtube-playlist-date-sorter)
