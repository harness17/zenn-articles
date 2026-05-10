# zenn-cli ワークフロー

## ディレクトリ構成

```
技術記事/
├── articles/          # 公開記事（zenn-cli が管理）
│   └── *.md
├── books/             # Zenn の本（必要になったら）
├── drafts/            # 公開前の下書き・構成メモ・コードサンプル
├── images/            # 記事に貼る画像（zenn-cli 慣例）
└── README.md
```

## 初回セットアップ（未実施なら必要）

```powershell
npm init --yes
npm install zenn-cli
npx zenn init
```

完了後、Zenn と GitHub リポジトリを連携する：
- Zenn の「GitHubリポジトリ連携」画面で `harness17/<repo-name>` を指定する
- main ブランチに push すると自動公開される

## 新規記事の作成

```powershell
npx zenn new:article --slug <slug> --type tech
```

`--slug` は英数小文字・ハイフンのみ。例：`youtube-data-api-quota-exhaustion`

## ローカルプレビュー

```powershell
npx zenn preview
# → http://localhost:8000 で確認
```

## フロントマターの必須項目

```yaml
---
title: "（30〜40字、検索される単語を含む）"
emoji: "🔧"
type: "tech"          # tech または idea
topics: ["sqlserver", "csharp", "aspnetcore"]  # 5個まで
published: false      # ★完成するまで false。公開時のみ true に変更
---
```

## 公開フロー

1. `published: false` のまま執筆・プレビュー確認
2. `/article-review` で公開前チェック
3. `published: true` に変更してコミット
4. main に push → Zenn に自動反映
5. `/article-publish` で公開後アクションを実行

## 親プロジェクト連携

- 公開後は `F:/Dropbox/Job-hunting/CLAUDE_CODE_HANDOFF.md` の「自己研鑽」セクションに記事リンクを追記
- Lapras 技術力スコアの変化を数日後に確認
