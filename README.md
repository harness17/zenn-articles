# 技術記事（Zenn）

[@harness17](https://github.com/harness17)の Zenn 技術記事リポジトリ。

## 構成

- `articles/` — 公開記事（zenn-cli が管理）
- `books/` — Zenn の本
- `drafts/` — 公開前の下書き・構成メモ
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
