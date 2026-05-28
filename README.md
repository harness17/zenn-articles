# 技術記事

[@harness17](https://github.com/harness17)の技術記事リポジトリ。

## 構成

- `articles/` — 公開記事（zenn-cli が管理）
- `books/` — Zenn の本
- `drafts/` — 公開前の下書き・構成メモ
- `qiita/public/` — Qiita 投稿用の改稿記事（Qiita CLI 管理対象）
- `images/` — 記事用画像

## 方針

「実際に詰まって、自分で考えて、こう解決した」という体験ベースの技術記事を書きます。
網羅的な解説記事より、課題と解決の判断軸を言語化することを重視します。

## Git 管理方針

GitHub には公開済みの記事と、公開記事の再現に必要な設定だけをコミットします。

コミット対象:

- `articles/*.md` — Zenn 公開済み記事
- `books/` — Zenn 本の投稿対象
- `qiita/public/*.md` — Qiita 公開済み記事
- `note/promo/` — note 投稿用の公開済み告知原稿
- `.agents/skills/`, `.claude/skills/` — 記事運用に使うスキル

コミットしないもの:

- `drafts/` — 下書き、構成メモ、記事候補表、公開ログ
- `handoffs/`, `CLAUDE_CODE_HANDOFF.md` — エージェント間の作業引き継ぎ
- `note/drafts/`, `note/import/`, `note/published-log.md` — note 下書き、インポート成果物、公開ログ
- `qiita/public/.remote/` — Qiita CLI の同期キャッシュ
- `qiita/public/newArticle*.md` — Qiita CLI が作る空テンプレ記事
- `articles/*.md` の `published: false` 記事、`qiita/public/*.md` の `ignorePublish: true` 記事
- `.env*`, `CLAUDE.local.md`, `.mcp.json`, ローカル設定

記事候補リストや下書きは、公開リポジトリではなくローカル作業領域か My-Skill-Graph に置きます。新しい記事を公開したら、対象ファイルを `.gitignore` の allowlist に追加してからコミットします。

## 主な技術領域

- 個人開発で遭遇した課題と解決（YouTube Data API クォータ設計、Electron 配布、Manifest V3 移行 等）
- ASP.NET Core 10 での設計判断（DevNext / Phycock を題材に）
- AI 協調開発（Claude Code 活用ワークフロー）

## 関連リポジトリ

- [DevNext](https://github.com/harness17/DevNext) — ASP.NET Core 10 製テンプレート
- [YouTom](https://github.com/harness17/youtube-schedule) — Electron アプリ
- [google-chrome-extensions](https://github.com/harness17/google-chrome-extensions) — Manifest V3

## 最近の公開記事

### Qiita

- [AIにテストを書かせる前に観点リストを渡すようにした](https://qiita.com/harnesswinner/items/b4b6dde76d36bf25c2c1) (2026-05-28)
- [Codexにリファクタを任せる前に触る範囲を明示した](https://qiita.com/harnesswinner/items/8fa8058d2260273ac98b) (2026-05-28)
- [Claude CodeのPostToolUse hookで保存時に文体NG語を警告した](https://qiita.com/harnesswinner/items/55e03ef8ce0ae81170ec) (2026-05-28)
- [Codex用AGENTS.mdとClaude用CLAUDE.mdを分けて運用したメモ](https://qiita.com/harnesswinner/items/cb82e8caafa8daf52bcb) (2026-05-28)
- [AIに実装を任せる前に完成条件を宣言するSprint Contract運用](https://qiita.com/harnesswinner/items/98669d5afa40d36299d5) (2026-05-25)
- [git add .で余計なファイルを混ぜないために個別ファイル指定へ寄せた](https://qiita.com/harnesswinner/items/871470b50d10ccbbeac9) (2026-05-25)
- [AI同士のhandoffで作業範囲が曖昧になる問題を契約チェックリストで抑えた](https://qiita.com/harnesswinner/items/5bb47dec500eb36a8369) (2026-05-25)
- [AIに「修正して」と頼むと無関係コードまで触られる問題をSurgical Changesルールで抑えた](https://qiita.com/harnesswinner/items/e8ac450dbfd60757f487) (2026-05-25)
- [Claude CodeのCLAUDE.mdを@importで分割してトピック別ルールに整理した](https://qiita.com/harnesswinner/items/6678320489deec25113a) (2026-05-24)
- [Chrome拡張でDOMを並び替えた後にMutationObserverが再発火する問題への対処](https://qiita.com/harnesswinner/items/5429f56b3a8e23675703) (2026-05-24)
- [Chrome拡張でYouTubeのSPA遷移後にcontent scriptが効かない問題を直した](https://qiita.com/harnesswinner/items/3bac40961a0b5ff20dee) (2026-05-24)
- [YouTubeプレイリストのDOM順を一度保存して通常順に戻す実装](https://qiita.com/harnesswinner/items/fa3a124e5fa50229a887) (2026-05-24)
- [YouTubeの配信予定を追うWindowsアプリ YouTom を作った](https://qiita.com/harnesswinner/items/52c94119fed2aba20f7e) (2026-05-20)
- [YouTube Data API のクォータ枯渇を RSS で避ける設計にした話](https://qiita.com/harnesswinner/items/e2d5dba192540222d8d5) (2026-05-20)

Zenn 公開記事は [zenn.dev/harness](https://zenn.dev/harness) を参照。

## ローカル開発

```powershell
npm install
npx zenn preview
```

`http://localhost:8000` でプレビュー。

新規記事：

```powershell
npx zenn new:article --slug <slug> --type tech
```

Qiita 用の記事は `qiita/` に置きます。Zenn 原文を流用する場合は、冒頭に原文リンクと「一部加筆・再構成」の注記を入れ、単純コピーではなく Qiita 読者向けに構成を調整します。

Qiita CLI のプレビュー:

```powershell
npm run qiita:preview
```

Qiita への公開・更新:

```powershell
npm run qiita:publish -- <slug>
```
