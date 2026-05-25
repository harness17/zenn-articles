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

Zenn / Qiita の投稿対象になる Markdown と、公開前レビューに必要な構成メモはコミットします。

コミット対象:

- `articles/*.md` — Zenn 投稿対象。`published: false` の下書きも、公開前レビュー対象なら含める
- `books/` — Zenn 本の投稿対象
- `qiita/public/*.md` — Qiita 投稿対象。`ignorePublish: true` の下書きも、レビュー対象なら含める
- `drafts/*.md` — 公開してもよい構成メモ、候補表、公開ログ
- `note/drafts/`, `note/promo/`, `note/import/` — note 投稿用の原稿とインポート成果物
- `.agents/skills/`, `.claude/skills/` — 記事運用に使うスキル

コミットしないもの:

- `qiita/public/.remote/` — Qiita CLI の同期キャッシュ
- `qiita/public/newArticle*.md` — Qiita CLI が作る空テンプレ記事
- `drafts/private/`, `drafts/*-local.md` — 個人事情、応募戦略、未整理の候補メモ
- `.env*`, `CLAUDE.local.md`, ローカル設定

記事候補リストや下書きは、外に出してよい編集計画ならコミット対象にします。就職戦略、守秘判断前の案件情報、個人事情を含む候補は My-Skill-Graph か `drafts/private/` に置き、公開リポジトリには含めません。

## 主な技術領域

- 個人開発で遭遇した課題と解決（YouTube Data API クォータ設計、Electron 配布、Manifest V3 移行 等）
- ASP.NET Core 10 での設計判断（DevNext / Phycock を題材に）
- AI 協調開発（Claude Code 活用ワークフロー）

## 関連リポジトリ

- [DevNext](https://github.com/harness17/DevNext) — ASP.NET Core 10 製テンプレート
- [youtube-schedule](https://github.com/harness17/youtube-schedule) — Electron アプリ
- [google-chrome-extensions](https://github.com/harness17/google-chrome-extensions) — Manifest V3

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
