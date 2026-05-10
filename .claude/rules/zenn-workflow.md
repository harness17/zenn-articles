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
2. 作成者と別エージェントへの相互レビュー依頼を handoff に記録
3. `/article-review` で公開前チェック
4. 重大指摘がなく、ユーザーが公開を明示したら `published: true` に変更してコミット
5. main に push → Zenn に自動反映
6. `/article-publish` で公開後アクションを実行

## Zenn 投稿制限メモ

- 2026-05-10 時点で、Zenn 側のレートリミットにより 1 日 2 本を超える公開反映が止まる可能性がある。
- 以後の公開は 1 日 2 本までを目安にし、公開反映されなかった記事は翌日以降に状況確認する。
- `published: false` の非公開記事は Zenn 上で下書き反映されるため、コミットしてよい。

## 相互レビューゲート

記事作成後は `cross-agent-review.md` に従い、Codex と ClaudeCode の相互レビューを通す。

- Codex が作成した記事: ClaudeCode へのレビュー依頼を `CLAUDE_CODE_HANDOFF.md` に追記する
- ClaudeCode が作成した記事: Codex へのレビュー依頼を `CLAUDE_CODE_HANDOFF.md` に追記する
- 継続作業に関わる場合は My-Skill-Graph の `ops/handoffs/` と `self/goals.md` も更新する
- `published: true` は、相互レビュー記録とユーザーの明示が揃うまで変更しない

## 親プロジェクト連携

- 公開後は `F:/Dropbox/Job-hunting/CLAUDE_CODE_HANDOFF.md` の「自己研鑽」セクションに記事リンクを追記
- Lapras 技術力スコアの変化を数日後に確認
