# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## プロジェクト概要

GitHub: harness17の Zenn 技術記事執筆プロジェクト。コードリポジトリではなく、記事原稿と関連メモを管理する。

**最終目的**：Lapras 技術力スコア向上（記事スコア 0.00 → 1.5+）と就職選考での差別化。

## ディレクトリ構成

```
技術記事/
├── articles/          # 公開記事（zenn-cli 管理）
├── books/             # Zenn の本（必要時）
├── drafts/            # 公開前の下書き・構成メモ・コードサンプル
├── images/            # 記事用画像
├── .claude/
│   ├── rules/         # トピック別ルール
│   ├── skills/        # Claude 側スキル mirror
│   ├── hooks/         # 文体チェック hook
│   └── settings.json  # Claude 側 Hook 設定
├── .agents/
│   └── skills/        # Codex 側スキル（article-plan / article-review / article-publish）
├── .codex/
│   ├── hooks/         # Codex 側 hook 実体
│   └── hooks.json     # Codex 側 Hook 設定
├── AGENTS.md          # 本ファイル
├── CLAUDE.local.md    # 個人設定（gitignore）
└── README.md
```

## ルール

@.claude/rules/topic-policy.md
@.claude/rules/writing-style.md
@.claude/rules/zenn-workflow.md
@.claude/rules/article-requirements.md
@.claude/rules/privacy.md
@.claude/rules/writing-process.md
@.claude/rules/cross-agent-review.md

**最重要**：テーマ選定方針は `topic-policy.md`。**「課題解決力ベース・体験記事優先」** が軸。SQL Server チューニング等の知見深度が必要な解説記事は書かない。詰まった→解決した体験を優先する。

## 作業の流れ（要約）

| Phase | コマンド | 成果物 |
|-------|---------|--------|
| 構成 | `/article-plan` | drafts/<slug>.md に見出しとコード例計画 |
| 執筆 | （手動 or Codex支援） | articles/<slug>.md（`published: false`） |
| 相互レビュー依頼 | handoff 更新 | Codex 作成なら ClaudeCode、ClaudeCode 作成なら Codex に公開前レビューを依頼 |
| 推敲 | `/article-review` | 文体・必須要素・守秘義務チェック結果 |
| 公開 | フロントマターを `published: true` に変更してコミット & push | Zenn 自動反映 |
| 公開後 | `/article-publish` | README更新、Lapras確認、職経書追記検討 |

## Hook

`articles/*.md` を保存すると、文体ルール違反語（「素晴らしい」「驚くべき」など）を警告する PostToolUse hook が走る。

- Codex 側: `.codex/hooks.json` → `.codex/hooks/check-article-style.sh`
- Claude 側: `.claude/settings.json` → `.claude/hooks/check-article-style.sh`

## Git 規約

Claude 側 `.claude/rules/git-ops.md` と同等のルールを Codex 側にも適用する。

- `git add -A` / `git add .` は使用しない。個別ファイル指定に統一する
- 開発は `feature/xxx` ブランチで行う
- **`main` への直接コミット禁止**。マージは Pull Request または `git merge --no-ff`
- `--no-verify` で pre-commit hook をスキップしない（hook が落ちたら原因を直す）
- 既存コミットへの `--amend` より新規コミットを優先する

## 親プロジェクトとの関係

- 親：`F:/Dropbox/Job-hunting/`（職務経歴書、応募管理、Gmail分析）
- 連携点：公開した記事は親プロジェクトの `CLAUDE_CODE_HANDOFF.md` 自己研鑽セクションに追記する
- このプロジェクトは記事執筆に特化、親プロジェクトには触らない
