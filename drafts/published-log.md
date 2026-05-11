# Zenn 公開ログ

公開した記事の記録。Lapras スコア確認予定日と関連リポジトリの紐付け管理用。

## 運用メモ

- Zenn は 1 日に公開できる記事数が 2 本までのように見えるため、まとめて公開する場合も 2 本ずつ日を分ける。
- Lapras 確認は、実際に Zenn 上で公開確認できた日から 3〜7 日後を目安にする。

## 2026-05-11 公開確認

### 1. YouTube Data API のクォータ枯渇を RSS で99%削減した話

- URL: https://zenn.dev/harness/articles/youtube-data-api-rss-quota-reduction
- テーマ系統: 個人開発 / API クォータ設計
- 文字数: 約4,500字
- 関連リポジトリ: [youtube-schedule](https://github.com/harness17/youtube-schedule)
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

## ストック中（published: false）

### Youtom 紹介記事

- ファイル: `articles/youtom-introduction.md`
- 関連リポジトリ: [youtube-schedule](https://github.com/harness17/youtube-schedule)
- 保留理由: 第1記事と同じリポジトリ題材で重複感あり。技術深度の高い記事で評価を作ってから公開する想定
- 改稿候補: 候補I（SmartScreen / OAuth配布）と統合する余地

### ScheduleEntry 集約記事（候補J）

- ファイル: `articles/phycock-schedule-entry-consolidation.md`
- 関連リポジトリ: [DevNext](https://github.com/harness17/DevNext)
- 保留理由: Codex 初稿作成済み。ClaudeCode による公開前レビュー待ち
- 位置づけ: ASP.NET Core MVC の予定入力モデル設計判断。Phycock 固有のセンシティブな文脈は一般化済み
