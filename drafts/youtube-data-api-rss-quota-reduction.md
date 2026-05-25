# 構成メモ: YouTube Data API のクォータを RSS で 99% 削減した話

> ⚠️ 旧構成（自動/手動分離フォーカス）は実装と乖離していたため、案A（RSS プライマリ + キャッシュ階段化）に書き換え済み（2026-05-10）。

## メタ情報

- **slug 案**: `youtube-data-api-rss-quota-reduction` または `youtube-data-api-quota-99-percent-cut`
- **type**: tech
- **emoji**: 🪶（軽量化のニュアンス）または 📉
- **topics**: `youtube` / `googleapi` / `electron` / `nodejs` / `rss`（5個）
- **想定文字数**: 3000〜3500字
- **想定執筆時間**: 4〜5時間
- **ステータス**: 構成中

## タイトル案

| 案 | タイトル | 字数 | 強み |
|----|---------|------|------|
| **A**（推奨） | YouTube Data API のクォータが枯渇したので search.list を捨てて RSS にした話 | 41 | ストーリー型・転換が明確 |
| B | 個人開発で YouTube Data API のクォータを 99% 削減した話 | 30 | 数字インパクト |
| C | search.list を RSS に切り替えて YouTube Data API のクォータを 99% 減らした | 39 | 変更主語 + 数字 |

→ **A 推奨**。「枯渇 → 転換 → 結果」の3段が読まれやすい。検索ヒット狙いなら C。

---

## 想定読者

個人開発で YouTube Data API（または同類のクォータ制限がある外部 API）を使っていて、「ポーリング設計でクォータ枯渇に困っている」「RSS や代替経路を知りたい」エンジニア。

---

## 記事の核

**「2026年4月12日、search.list を捨てて RSS フィードに切り替えた瞬間、クォータ消費が 99% 削減された」** という具体的な転換点を中心に据える。

実装レイヤーを4段階で説明：
1. **失敗体験**：300チャンネルを search.list で叩いて数時間で枯渇
2. **第1層**：RSS プライマリ化（0クォータ）
3. **第2層**：subscriptions.list の 24h キャッシュ + RSS 失敗時の playlistItems フォールバック
4. **第3層**：自動ポーリングと手動更新の `forceFullRecheck` 切り分け（軽く触れる）

---

## 構成

### はじめに（200〜300字）

- YouTom の概要：購読チャンネルの配信予定を一覧表示する Electron デスクトップアプリ
- 最初の実装：300チャンネルの subscriptions に対して **search.list（100ユニット/呼び出し）** で動画ID取得 → 30分ごとにポーリング
- 起きたこと：**数時間で 10,000 ユニットを使い切った**（10,000 ÷ 100 = 100呼び出しで枯渇）
- この記事で学べること：search.list を RSS に切り替えるだけで 99% 削減できる、その後の階段化設計

---

### セクション1: クォータが枯渇するまで何が起きていたか（500〜600字）

- 伝えること: YouTube Data API クォータの仕様 + 自分の初期実装の失敗
- 具体例：
  - YouTube Data API v3 の上限：10,000 ユニット/日
  - 主要呼び出しコスト：
    - **search.list = 100 ユニット**（公式 docs から引用）
    - playlistItems.list = 1 ユニット
    - subscriptions.list = 1 ユニット
    - videos.list = 1 ユニット
  - 初期実装の構成：300チャンネル × search.list × 30分間隔 → 30分で 30,000ユニット消費試算（実測は数時間で枯渇）
  - 枯渇すると 403 quotaExceeded
  - リセットは Pacific Time 0:00（JST 17:00頃）
- 出典: [YouTube Data API v3 — Quota and Usage](https://developers.google.com/youtube/v3/getting-started#quota)

---

### セクション2: 第1層：search.list を RSS に切り替えた（700〜900字）★メイン1

- 伝えること: YouTube はチャンネルごとに RSS フィードを公開している。これを使えば動画ID取得が 0 ユニットで済む
- 転換点：**2026年4月12日のコミット**「`perf: replace search.list with RSS feed to reduce quota usage 99%`」
- 具体例：
  - RSS の URL：`https://www.youtube.com/feeds/videos.xml?channel_id={channelId}`
  - **0 クォータ**で動画ID + タイトル + 公開時刻が取れる
  - 認証不要（API キー / OAuth トークン不要）
  - タイムアウト 3秒、`AbortController` で打ち切り
- コード抜粋：`src/main/fetchers/rssFetcher.js`（10〜30行抜粋）
- 注意点：
  - RSS は最新 15件しか返さない → 古い動画は取れない
  - メンバー限定動画は出てこない
  - パース失敗・404・タイムアウト時のハンドリングが必須

---

### セクション3: 第2層：キャッシュとフォールバックで穴を埋める（700〜900字）★メイン2

- 伝えること: RSS が万能ではない。失敗時のフォールバックと、購読チャンネル取得のキャッシュを階段化する
- 具体例：
  - **subscriptions.list の 24h キャッシュ**（`SUBS_CACHE_TTL_MS = 24 * 60 * 60 * 1000`）
    - 購読チャンネルは頻繁に変わらないので 1日1回でいい
    - 300チャンネル → 6呼び出し（pageToken で 50件ずつ × 6ページ）= 6 ユニット
    - キャッシュなしなら毎ポーリング 6 ユニット → キャッシュで 1日 6 ユニットに
  - **RSS 失敗時のフォールバック階段**：
    1. RSS 取得失敗（HTTP 4xx / タイムアウト / パース失敗）
    2. → `playlistItems.list`（1 ユニット/ch）にフォールバック
    3. これで RSS が落ちている間も最低限の同期を維持
  - コード抜粋：`schedulerService.js:118-150`（RSS → fallback の制御フロー）
- 数字で締める：1日あたり実測クォータ消費（仮想例）
  - 旧：search.list × 300ch × 48回（30分間隔）= 1,440,000 ユニット相当
  - 新：subscriptions（6/日）+ RSS（0）+ videos.list（fetched_ids 件数程度）= 数百ユニット/日
  - **99%以上の削減を実現**

---

### セクション4: 第3層：自動と手動の役割分担（300〜400字）

- 伝えること: 自動ポーリングと手動更新で「同じ取得経路の挙動を変えるフラグ」を1つだけ用意した
- 具体例：
  - 自動：30分ごと（`REFRESH_INTERVAL_MS = 30 * 60 * 1000`）、`forceFullRecheck: false`
  - 手動：ユーザーがボタンクリック、`scheduler.refresh({ forceFullRecheck: true })`
  - 違い：`forceFullRecheck` のとき、既知動画も含めて videos.list で再取得（新規動画 + 更新確認）
  - コード抜粋：`videoHandlers.js:59-64` + `schedulerService.js:177-186`
- 「自動と手動で取得内容を完全に分ける」必要はなく、「強度フラグ1つ」で切り分けられる、というシンプルさを推す

---

### セクション5: クォータ切れ時のユーザー案内（200〜300字）※今後の課題として正直に書く

- 伝えること: 現状の実装は「簡易トーストのみ」。今後の改善余地を明示する
- 現状：
  - `error === 'QUOTA_EXCEEDED'` のとき「本日の API 上限に達しました」をトースト表示（`App.jsx:198-203`）
- 今後やりたいこと：
  - 「消えないバナー」表示
  - リセット時刻を JST で計算して表示（PT 0:00 → JST 17:00頃）
  - 「明日の 17時 まで使えない」とユーザーに分かるように
- これは記事の **「読者へのアクション提案」** にもなる：自分のアプリでも忘れずに

---

### まとめ（200〜250字）

- 要点3つ：
  1. **search.list は捨てて RSS にする**：チャンネルごとの RSS フィードで 0 クォータ
  2. **キャッシュとフォールバックで階段化**：subscriptions は 24h、RSS 失敗時は playlistItems
  3. **自動と手動はフラグ1つで切り分け**：完全分離は不要、`forceFullRecheck` で十分
- 他の API（Twitch、Spotify、Mastodon 等）にも応用できる原則：**「公開フィードがあるなら API より先にそっちを試す」**

---

## コード例の準備状況

| セクション | 出典ファイル | 行範囲 | 準備状況 |
|----------|------------|-------|---------|
| §1 失敗体験 | （数字のみ） | — | ✅ 公式 docs + 体感記憶 |
| §2 RSS フェッチャー | `src/main/fetchers/rssFetcher.js` | 1〜96（全96行 → 10〜30行に抜粋） | ✅ 場所特定済み |
| §3 24h キャッシュ | `src/main/services/schedulerService.js` | 3, 96〜107 | ✅ 場所特定済み |
| §3 フォールバック | `src/main/services/schedulerService.js` | 118〜150 | ✅ 場所特定済み |
| §3 PlaylistItems | `src/main/fetchers/playlistItemsFetcher.js` | 1〜21（全21行） | ✅ 場所特定済み |
| §3 Subscriptions | `src/main/fetchers/subscriptionsFetcher.js` | 1〜31（全31行） | ✅ 場所特定済み |
| §4 自動・手動 | `src/main/index.js` + `src/main/ipc/videoHandlers.js` + `src/main/services/schedulerService.js` | `index.js:61`, `videoHandlers.js:59-64`, `schedulerService.js:177-186` | ✅ 場所特定済み |
| §5 クォータエラー UI | `src/renderer/src/App.jsx` | 198〜203 | ✅ 場所特定済み |

---

## 参考リンク候補

### 公式
- [YouTube Data API v3 — Quota and Usage](https://developers.google.com/youtube/v3/getting-started#quota)
- [YouTube Data API v3 — Methods](https://developers.google.com/youtube/v3/docs)
- [YouTube RSS フィードの仕様（非公式・コミュニティドキュメント）](https://stackoverflow.com/questions/30630071/find-youtube-channel-rss-feed)

### 自分のリポジトリ
- [YouTom](https://github.com/harness17/youtube-schedule) — 本記事の実装元
- 該当コミット: [`f815c16`](https://github.com/harness17/youtube-schedule/commit/f815c16) — 「`perf: replace search.list with RSS feed to reduce quota usage 99%`」（2026-04-12）

### 関連記事候補（後続）
- 候補I「未署名 Electron アプリの SmartScreen 問題」（同じ YouTom から派生）
- 候補J「Phycock で Schedule を削除した設計判断」（別アプリ）

---

## 残タスク（執筆前に確認すること）

- [x] タイトル候補出し → A/B/C 提示済み（要確定）
- [x] §1 の失敗体験の具体的な数字 → **300チャンネル × search.list（100u）× 30分間隔 = 30分で 30,000u 試算**
- [x] §2/§3 の実コード場所 → **全部特定済み**
- [x] §4 の自動・手動の差分 → **`forceFullRecheck` フラグ1つと判明**
- [x] §5 の現状 → **簡易トーストのみ。記事では正直に「今後の課題」として書く**
- [ ] **タイトル A/B/C 確定**
- [ ] §3 でクォータ消費の旧/新比較を表で出すか文章で出すか決める
- [ ] §2 の RSS URL を貼るか、コードだけで済ませるか決める
- [ ] 全体を通読して文体ルール（「素晴らしい」等の NG 語）に触れていないか確認 → 執筆段階の `/article-review` で実施

---

## 執筆順序（推奨）

1. はじめに（短い）→ §1 失敗体験 → §2 RSS 転換 ← ここまでで記事の核
2. §3 階段化（細かい技術）→ §4 自動/手動（軽く）
3. §5 今後の課題 → まとめ
4. タイトル確定
5. `/article-review` でチェック → `published: false` のままコミット → ローカルプレビュー → 推敲
