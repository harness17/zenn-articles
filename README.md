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
