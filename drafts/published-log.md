# Zenn 公開ログ

公開した記事の記録。Lapras スコア確認予定日と関連リポジトリの紐付け管理用。

## 運用メモ

- Zenn は 1 日に公開できる記事数が 2 本までのように見えるため、まとめて公開する場合も 2 本ずつ日を分ける。
- Lapras 確認は、実際に Zenn 上で公開確認できた日から 3〜7 日後を目安にする。
- ローカルの `published: true` と Zenn 実サイトの公開状態は分けて扱う。公開後は `https://zenn.dev/harness/articles/<slug>` に直接アクセスし、HTTP 200 とタイトル一致を確認する。
- 403 / 404 / タイトル不一致の場合は、レートリミットやデプロイ遅延の可能性があるため `実公開未確認` として再確認対象に残す。

## 2026-05-20 公開状態の再確認

2026-05-17 時点で 403 だった公開指定記事のうち、次の 2 本は Zenn 実サイトで 200 / タイトル一致を確認した。

- `codex-claude-skill-graph-worklog`: 200 / 公開確認（2026-05-20 再確認、Zenn 表示上は 2026-05-17 公開）
- `cross-agent-harness-introduction`: 200 / 公開確認（2026-05-20 再確認、Zenn 表示上は 2026-05-17 公開）

現在の未公開・公開保留:

- `phycock-schedule-entry-consolidation`: `published: false`。リタリコ確認が取れるまで公開保留。
- `zenn-article-repo-workflow`: `published: false`。公開前レビューと相互レビュー後に公開判断。

候補表のメンテナンス:

- `drafts/article-candidates.md` の最終突き合わせを 2026-05-20 に更新。
- 公開済み候補は「選定対象外」と明記し、次に選ぶ候補ショートリストを追加。

## 2026-05-24 Zenn 公開指定

### 1. AI同士のhandoffを多層契約チェックリストにした

- URL: https://zenn.dev/harness/articles/ai-handoff-multi-layer-contract-checklist
- 管理ファイル: `articles/ai-handoff-multi-layer-contract-checklist.md`
- テーマ系統: AI協調開発 / handoff / 作業契約
- 関連リポジトリ: [zenn-articles](https://github.com/harness17/zenn-articles) / [cross-agent-harness](https://github.com/harness17/cross-agent-harness)
- レビュー: Codex 初稿、ClaudeCode review-only 公開前レビュー済み、軽微指摘反映済み
- 公開状態: Zenn 公開確認済み（2026-05-24、ユーザー確認）
- Lapras確認予定日: 2026-05-29 〜 2026-05-31

## 2026-05-24 Qiita 公開（Chrome拡張系 独立記事3本）

### 1. Chrome拡張でYouTubeのSPA遷移後にcontent scriptが効かない問題を直した

- URL: https://qiita.com/harnesswinner/items/3bac40961a0b5ff20dee
- 管理ファイル: `qiita/public/youtube-spa-content-script-matches.md`
- テーマ系統: Chrome拡張 / Manifest V3 / SPA / YouTube
- 関連リポジトリ: ローカル `H:/ClaudeCode/GoogleChrome/youtube-playlist-date-sorter`（公開リポジトリ未push）
- レビュー: ClaudeCode 初稿、Codex 相互レビュー済み（codex MCP 経由、重大指摘なし）
- 公開状態: Qiita 公開確認済み（2026-05-24、Qiita CLI `Posted` 応答）
- Lapras確認予定日: 2026-05-29 〜 2026-05-31

### 2. Chrome拡張でDOMを並び替えた後にMutationObserverが再発火する問題への対処

- URL: https://qiita.com/harnesswinner/items/5429f56b3a8e23675703
- 管理ファイル: `qiita/public/chrome-extension-mutationobserver-rerender-loop.md`
- テーマ系統: Chrome拡張 / MutationObserver / DOM
- 関連リポジトリ: ローカル `H:/ClaudeCode/GoogleChrome/youtube-playlist-date-sorter`（公開リポジトリ未push）
- レビュー: ClaudeCode 初稿、Codex 相互レビュー済み（codex MCP 経由、重大指摘なし）
- 公開状態: Qiita 公開確認済み（2026-05-24、Qiita CLI `Posted` 応答）
- Lapras確認予定日: 2026-05-29 〜 2026-05-31

### 3. YouTubeプレイリストのDOM順を一度保存して通常順に戻す実装

- URL: https://qiita.com/harnesswinner/items/fa3a124e5fa50229a887
- 管理ファイル: `qiita/public/youtube-playlist-restore-dom-order.md`
- テーマ系統: Chrome拡張 / DOM / YouTube
- 関連リポジトリ: ローカル `H:/ClaudeCode/GoogleChrome/youtube-playlist-date-sorter`（公開リポジトリ未push）
- レビュー: ClaudeCode 初稿、Codex 相互レビュー済み（codex MCP 経由、軽微指摘1点を反映）
- 公開状態: Qiita 公開確認済み（2026-05-24、Qiita CLI `Posted` 応答）
- Lapras確認予定日: 2026-05-29 〜 2026-05-31
- 連動更新候補: `youtube-playlist-date-sorter` を `harness17/google-chrome-extensions` に push する際、READMEに3記事リンク追加

## 2026-05-20 Qiita 公開

### 1. YouTube Data API のクォータ枯渇を RSS で避ける設計にした話

- URL: https://qiita.com/harnesswinner/items/e2d5dba192540222d8d5
- 元記事: https://zenn.dev/harness17/articles/youtube-data-api-rss-quota-reduction
- 管理ファイル: `qiita/public/youtube-data-api-rss-quota-reduction.md`
- テーマ系統: YouTube Data API / API クォータ / RSS
- 関連リポジトリ: [YouTom](https://github.com/harness17/youtube-schedule)
- レビュー: Codex 初稿、ClaudeCode review-only `REVIEWED_OK`
- 公開状態: Qiita 公開確認済み（2026-05-20、Qiita CLI `published=true` / URL確認）

### 2. YouTubeの配信予定を追うWindowsアプリ YouTom を作った

- URL: https://qiita.com/harnesswinner/items/52c94119fed2aba20f7e
- 元記事: https://zenn.dev/harness17/articles/youtom-introduction
- 管理ファイル: `qiita/public/youtom-introduction.md`
- テーマ系統: Electron / React / YouTube / 個人開発
- 関連リポジトリ: [YouTom](https://github.com/harness17/youtube-schedule)
- レビュー: Codex 初稿、ClaudeCode review-only `REVIEWED_OK`
- 公開状態: Qiita 公開確認済み（2026-05-20、Qiita CLI `published=true` / URL確認）
- 連動更新: YouTom repo `docs/signpath-readiness.md` に Qiita 外部言及 2件として追記済み

## 2026-05-19 公開

### CodexとClaude Codeを相互呼び出しするハーネスを組んだ

- URL: https://zenn.dev/harness/articles/cross-agent-harness-automation
- テーマ系統: AI 協調開発 / Codex・Claude Code 運用 / 自動化
- 文字数: 約4,000字
- 関連リポジトリ: [cross-agent-harness](https://github.com/harness17/cross-agent-harness) / [zenn-articles](https://github.com/harness17/zenn-articles)
- 想定読者: Codex と Claude Code を併用する個人開発者
- Zenn実サイト: 200 / 公開確認（2026-05-19、タイトル一致確認済み）
- レビュー: ClaudeCode 公開前レビュー + Codex 相互レビュー（codex MCP 経由）、重大指摘なし
- Lapras確認予定日: 2026-05-24（公開から5日後）

## 2026-05-17 Zenn 実公開状態の突き合わせ

### Zenn 実サイトで 200 確認

- `devnext-mvc-helper-extensions`
- `fullcalendar-event-color-rendering`
- `youtube-data-api-rss-quota-reduction`
- `claude-code-workflow-evolution`
- `electron-smartscreen-oss-distribution`
- `youtom-introduction`
- `aspnet-core-identity-to-commonlibrary`
- `ai-cross-review-handoff-workflow`

### ローカルは published: true だが Zenn 実サイトは 403（当時）

- `phycock-schedule-entry-consolidation`
- `codex-claude-skill-graph-worklog`
- `cross-agent-harness-introduction`

次アクション（当時）: Zenn ダッシュボードのデプロイ履歴または翌日の直接アクセスで再確認する。実公開確認できるまで Lapras 確認予定日の起算点にしない。

2026-05-17 追記: 未push の chore コミット 2 件を `origin/main` へ push し Zenn の GitHub 同期を再トリガー。Zenn ダッシュボードのデプロイ結果で原因が確定 —「投稿数の上限に達したためデプロイされませんでした」（対象: codex-claude-skill-graph-worklog / cross-agent-harness-introduction / phycock-schedule-entry-consolidation。https://zenn.dev/faq#rate-limit ）。再 push しても上限ウィンドウが空くまで拒否されるため push は止め、上限解除後に再確認する。

2026-05-17 追記2: `phycock-schedule-entry-consolidation` はリタリコ確認が取れるまで公開保留のため `published: false` に戻した（commit 48ba35e）。rate limit 解除後も自動公開されない。残る公開待ちは `codex-claude-skill-graph-worklog` / `cross-agent-harness-introduction` の 2 本。

2026-05-20 追記: `codex-claude-skill-graph-worklog` / `cross-agent-harness-introduction` は Zenn 実サイトで 200 / タイトル一致を確認済み。未公開で残すのは `phycock-schedule-entry-consolidation` のみ。

## 2026-05-17 公開確認

### 1. CodexとClaude Codeの共同作業をcross-agent-harnessに切り出した

- URL: https://zenn.dev/harness/articles/cross-agent-harness-introduction
- テーマ系統: AI 協調開発 / Codex・Claude Code 運用 / OSS
- 文字数: 約5,000字（本文）
- 関連リポジトリ: [cross-agent-harness](https://github.com/harness17/cross-agent-harness) / [zenn-articles](https://github.com/harness17/zenn-articles)
- 想定読者: Codex と Claude Code を同じリポジトリで併用し、担当境界や handoff 運用に迷っている人
- Lapras確認予定日: 2026-05-22

## 2026-05-16 公開確認

### 1. ASP.NET Core MVCでScheduleEntryに寄せた設計判断

- URL: https://zenn.dev/harness/articles/phycock-schedule-entry-consolidation
- テーマ系統: ASP.NET Core 10 / MVC / データモデル設計
- 文字数: 約9,900字
- 関連リポジトリ: [DevNext](https://github.com/harness17/DevNext)
- 想定読者: ASP.NET Core MVC で入力モデルとテーブル設計の粒度に迷っている人
- 現在の扱い: 2026-05-17 に `published: false` へ戻し、リタリコ確認が取れるまで公開保留
- Lapras確認予定日: 公開確認後に再設定

### 2. AIとの設計判断をMy-Skill-Graphに残して再利用する

- URL: https://zenn.dev/harness/articles/codex-claude-skill-graph-worklog
- テーマ系統: AI 協調開発 / ナレッジ管理 / Obsidian
- 文字数: 約4,000字
- 関連リポジトリ: [zenn-articles](https://github.com/harness17/zenn-articles)
- 想定読者: AI コーディングエージェントで設計判断が会話ログに散らばることに困っている個人開発者
- Lapras確認予定日: 2026-05-21

## 2026-05-13 公開確認

### 1. 未署名Electronアプリを配布するとSmartScreenで止まる問題に向き合った話

- URL: https://zenn.dev/harness/articles/electron-smartscreen-oss-distribution
- テーマ系統: 個人開発 / Electron / Windows 配布
- 文字数: 約7,700字
- 関連リポジトリ: [YouTom](https://github.com/harness17/youtube-schedule)
- 想定読者: 個人開発 Electron アプリを Windows 向けに配布したい人
- Lapras確認予定日: 2026-05-18

### 2. 推しの配信予定を見逃さないために YouTom を作った

- URL: https://zenn.dev/harness/articles/youtom-introduction
- テーマ系統: 個人開発 / Electron / React / YouTube
- 文字数: 約4,700字
- 関連リポジトリ: [YouTom](https://github.com/harness17/youtube-schedule)
- 想定読者: YouTube の配信予定管理や個人開発デスクトップアプリに興味がある人
- Lapras確認予定日: 2026-05-18

## 2026-05-11 公開確認

### 1. YouTube Data API のクォータ枯渇を RSS で99%削減した話

- URL: https://zenn.dev/harness/articles/youtube-data-api-rss-quota-reduction
- テーマ系統: 個人開発 / API クォータ設計
- 文字数: 約4,500字
- 関連リポジトリ: [YouTom](https://github.com/harness17/youtube-schedule)
- 想定読者: 個人開発で外部 API を使うエンジニア、YouTube Data API を扱う人
- Lapras確認予定日: 2026-05-16

### 2. Claude Code運用を数ヶ月で見直してrulesとskillsに分けた話

- URL: https://zenn.dev/harness/articles/claude-code-workflow-evolution
- テーマ系統: AI 協調開発 / Claude Code / Codex 運用
- 文字数: 約4,500字
- 関連リポジトリ: [zenn-articles](https://github.com/harness17/zenn-articles)
- 想定読者: Claude Code や Codex の運用ルールを育てたい人
- Lapras確認予定日: 2026-05-16

## 2026-05-10 公開確認

### 1. ASP.NET MVCの自作HelperをASP.NET Coreに移植した話

- URL: https://zenn.dev/harness/articles/devnext-mvc-helper-extensions
- テーマ系統: ASP.NET Core 10 / Razor Helper
- 文字数: 約4,500字
- 関連リポジトリ: [DevNext](https://github.com/harness17/DevNext)
- 想定読者: ASP.NET Core MVC で自作 Helper を整理したいエンジニア
- Lapras確認予定日: 2026-05-16

### 2. FullCalendarでDTOの色が反映されない時に見たこと

- URL: https://zenn.dev/harness/articles/fullcalendar-event-color-rendering
- テーマ系統: ASP.NET Core 10 / フロントエンド連携 / FullCalendar
- 文字数: 約3,900字
- 関連リポジトリ: [DevNext](https://github.com/harness17/DevNext)
- 想定読者: FullCalendar で色表示や eventContent カスタマイズに詰まった人
- Lapras確認予定日: 2026-05-16

## 2026-05-24 公開（Qiita）

### 1. Claude CodeのCLAUDE.mdを@importで分割してトピック別ルールに整理した

- 媒体: Qiita
- URL: https://qiita.com/harnesswinner/items/6678320489deec25113a
- slug: `claude-md-import-split-rules`
- 管理ファイル: `qiita/public/claude-md-import-split-rules.md`
- テーマ系統: AIエージェント運用 / Claude Code 設定
- 文字数: 約8,700字
- 関連リポジトリ: [DevNext](https://github.com/harness17/DevNext)（`.claude/rules/` 構成実例として参照）
- 元 Zenn 記事: なし（独立記事）
- レビュー: Codex 3ラウンド相互レビュー（thread 019e57ad / 019e589e / 019e58a2）で重大指摘0達成
- 公開状態: Qiita 公開確認済み（2026-05-25、HTTP 200 + タイトル一致）
- Lapras確認予定日: 2026-05-29 〜 2026-05-31

## 2026-05-25 公開（Qiita）

### 1. AIに「修正して」と頼むと無関係コードまで触られる問題をSurgical Changesルールで抑えた

- 媒体: Qiita
- URL: https://qiita.com/harnesswinner/items/e8ac450dbfd60757f487
- slug: `ai-edit-surgical-changes-rule`
- 管理ファイル: `qiita/public/ai-edit-surgical-changes-rule.md`
- テーマ系統: AI駆動開発 / プロンプト設計 / コードレビュー
- 文字数: 約6,900字
- 関連リポジトリ: [forrestchang/andrej-karpathy-skills](https://github.com/forrestchang/andrej-karpathy-skills)（Karpathy 原則の出典 OSS）
- 元 Zenn 記事: なし（独立記事）
- レビュー: Codex 3ラウンド相互レビュー（thread 019e57ad / 019e589e / 019e58a2）で重大指摘0達成
- 公開状態: Qiita 公開確認済み（2026-05-25、HTTP 200 + タイトル一致）
- レート制限メモ: 2026-05-24 に記事1 と同時 publish 試行 → レート制限で記事2 が失敗、翌日 18:06 JST に再 publish 成功
- Lapras確認予定日: 2026-05-30 〜 2026-06-01

### 2. AI同士のhandoffで作業範囲が曖昧になる問題を契約チェックリストで抑えた

- 媒体: Qiita
- URL: https://qiita.com/harnesswinner/items/5bb47dec500eb36a8369
- slug: `ai-handoff-contract-checklist`
- 管理ファイル: `qiita/public/ai-handoff-contract-checklist.md`
- テーマ系統: AI協調開発 / handoff / 作業契約
- 文字数: 約7,200字
- レビュー: Codex 初稿、ClaudeCode review-only 重大指摘なし、軽微指摘反映済み
- 公開状態: Qiita 公開確認済み（2026-05-25 18:18 JST、Qiita CLI `Posted` 応答）
- Lapras確認予定日: 2026-05-30 〜 2026-06-01

### 3. git add .で余計なファイルを混ぜないために個別ファイル指定へ寄せた

- 媒体: Qiita
- URL: https://qiita.com/harnesswinner/items/871470b50d10ccbbeac9
- slug: `git-add-explicit-file-rule`
- 管理ファイル: `qiita/public/git-add-explicit-file-rule.md`
- テーマ系統: Git運用 / 開発環境 / セキュリティ
- 文字数: 約6,600字
- レビュー: Codex 初稿、ClaudeCode review-only 重大指摘なし、軽微指摘反映済み
- 公開状態: Qiita 公開確認済み（2026-05-25 18:18 JST、Qiita CLI `Posted` 応答）
- Lapras確認予定日: 2026-05-30 〜 2026-06-01

### 4. AIに実装を任せる前に完成条件を宣言するSprint Contract運用

- 媒体: Qiita
- URL: https://qiita.com/harnesswinner/items/98669d5afa40d36299d5
- slug: `sprint-contract-before-implementation`
- 管理ファイル: `qiita/public/sprint-contract-before-implementation.md`
- テーマ系統: AI駆動開発 / テスト戦略 / 開発プロセス
- 文字数: 約6,800字
- レビュー: Codex 初稿、ClaudeCode review-only 重大指摘なし、軽微指摘反映済み
- 公開状態: Qiita 公開確認済み（2026-05-25 18:18 JST、Qiita CLI `Posted` 応答）
- Lapras確認予定日: 2026-05-30 〜 2026-06-01

### 2. AI同士のhandoffで作業範囲が曖昧になる問題を契約チェックリストで抑えた

- 媒体: Qiita
- URL: https://qiita.com/harnesswinner/items/5bb47dec500eb36a8369
- slug: `ai-handoff-contract-checklist`
- 管理ファイル: `qiita/public/ai-handoff-contract-checklist.md`
- テーマ系統: AI協調開発 / handoff / 作業契約
- 文字数: 約3,500字
- 関連リポジトリ: [zenn-articles](https://github.com/harness17/zenn-articles)
- 元 Zenn 記事: `articles/ai-handoff-multi-layer-contract-checklist.md` をQiita向けに「handoff契約チェックリスト」へ再構成
- レビュー: ClaudeCode review-only で重大指摘なし、軽微指摘（タグ修正）対応済み
- 公開状態: Qiita APIで公開確認済み（2026-05-25、タイトル一致）
- Lapras確認予定日: 2026-05-30 〜 2026-06-01

### 3. git add .で余計なファイルを混ぜないために個別ファイル指定へ寄せた

- 媒体: Qiita
- URL: https://qiita.com/harnesswinner/items/871470b50d10ccbbeac9
- slug: `git-add-explicit-file-rule`
- 管理ファイル: `qiita/public/git-add-explicit-file-rule.md`
- テーマ系統: Git / AIエージェント運用 / セキュリティ
- 文字数: 約3,600字
- 関連リポジトリ: [zenn-articles](https://github.com/harness17/zenn-articles)
- 元 Zenn 記事: なし（独立記事）
- レビュー: ClaudeCode review-only で重大指摘なし、軽微指摘（タグ修正・サンプルパス汎用化）対応済み
- 公開状態: Qiita APIで公開確認済み（2026-05-25、タイトル一致）
- Lapras確認予定日: 2026-05-30 〜 2026-06-01

### 4. AIに実装を任せる前に完成条件を宣言するSprint Contract運用

- 媒体: Qiita
- URL: https://qiita.com/harnesswinner/items/98669d5afa40d36299d5
- slug: `sprint-contract-before-implementation`
- 管理ファイル: `qiita/public/sprint-contract-before-implementation.md`
- テーマ系統: AI駆動開発 / テスト観点 / 開発プロセス
- 文字数: 約3,200字
- 関連リポジトリ: [zenn-articles](https://github.com/harness17/zenn-articles)
- 元 Zenn 記事: なし（独立記事）
- レビュー: ClaudeCode review-only で重大指摘なし、軽微指摘（独自用語注釈）対応済み
- 公開状態: Qiita APIで公開確認済み（2026-05-25、タイトル一致）
- Lapras確認予定日: 2026-05-30 〜 2026-06-01

## 2026-05-28 公開（Zenn）

### 1. Zenn記事をリポジトリ管理して公開前レビューまで回した実践メモ

- 媒体: Zenn
- URL: https://zenn.dev/harness/articles/zenn-article-repo-workflow
- slug: `zenn-article-repo-workflow`
- 管理ファイル: `articles/zenn-article-repo-workflow.md`
- テーマ系統: Zenn / 記事運用 / AI協調レビュー
- 文字数: 約5,000字
- 関連リポジトリ: [zenn-articles](https://github.com/harness17/zenn-articles)
- レビュー: Codex 初稿、ClaudeCode review-only で重大指摘なし、軽微指摘反映済み
- 公開状態: GitHub連携公開指定済み、Zenn実サイト確認待ち
- Lapras確認予定日: 2026-06-02 〜 2026-06-04

### 2. AIエージェントの長期記憶を軽く保つためにsession-briefを作った

- 媒体: Zenn
- URL: https://zenn.dev/harness/articles/ai-agent-session-brief-memory
- slug: `ai-agent-session-brief-memory`
- 管理ファイル: `articles/ai-agent-session-brief-memory.md`
- テーマ系統: AI協調開発 / ナレッジ管理 / コンテキスト圧縮
- 文字数: 約4,200字
- 関連リポジトリ: [zenn-articles](https://github.com/harness17/zenn-articles)
- レビュー: Codex 初稿、ClaudeCode review-only で重大指摘なし、軽微指摘反映済み
- 公開状態: GitHub連携公開指定済み、Zenn実サイト確認待ち
