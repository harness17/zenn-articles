# Qiita 投稿用記事

Qiita 向けに改稿した記事を管理するフォルダです。

## 構成

- `public/` — Qiita CLI の記事管理対象
- `qiita.config.json` — Qiita CLI 設定

## 方針

- Zenn の `articles/` とは分けて管理する
- Zenn 原文を使う場合は、冒頭に原文リンクと「一部加筆・再構成」の注記を入れる
- Qiita のタグは 5 個以内に絞る
- 技術的価値が記事単体で伝わるように、宣伝導線は末尾に寄せる
- 公開前に秘密情報、未検証の数値、過剰な自己PRがないか確認する

## ローカル操作

初回ログイン:

```powershell
npx qiita --config qiita login
```

プレビュー:

```powershell
npm run qiita:preview
```

`qiita preview` は Qiita CLI の認証情報を読むため、未ログイン環境では `C:\Users\<user>\.config\qiita-cli\credentials.json` がなく失敗する。先に `npx qiita --config qiita login` を実行する。

新規記事:

```powershell
npm run qiita:new -- <slug>
```

公開・更新:

```powershell
npm run qiita:publish -- <slug>
```

すべて公開・更新:

```powershell
npm run qiita:publish:all
```

`QIITA_TOKEN` などの認証情報はリポジトリに置かず、Qiita CLI の認証ストアまたは GitHub Actions Secrets で管理します。
