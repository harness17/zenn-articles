---
title: Codex用AGENTS.mdとClaude用CLAUDE.mdを分けて運用したメモ
tags:
  - Markdown
  - 開発環境
  - AI
  - codex
  - ClaudeCode
private: false
updated_at: '2026-05-28T20:34:49+09:00'
id: cb82e8caafa8daf52bcb
organization_url_name: null
slide: false
ignorePublish: false
---

## はじめに

Codex と Claude Code を同じリポジトリで使うと、最初は `AGENTS.md` と `CLAUDE.md` に同じことを書きたくなります。

ただ、2つのエージェントは読むファイル名、得意な作業、ローカルで使う hook や skill の置き場所が少し違います。共通ルールを無理に1ファイルへ寄せると、片方にしか関係ない説明まで毎回読ませることになります。

この記事では、記事リポジトリで `AGENTS.md` と `CLAUDE.md` を分け、共通ルールは `.claude/rules/` に寄せた運用をまとめます。

## TL;DR / 結論コード

この構成にしました。

```text
.
├── AGENTS.md        # Codex向け。Codex側のhookとskillも書く
├── CLAUDE.md        # Claude Code向け。Claude側の設定を中心に書く
├── CLAUDE.local.md  # 個人設定。gitignore
├── .claude/rules/   # 共通ルール本体
├── .claude/skills/  # Claude側skill
├── .agents/skills/  # Codex側skill
└── .codex/hooks/    # Codex側hook
```

共通の執筆ルールは両方のルートファイルから同じファイルを参照します。

```markdown
## ルール

@.claude/rules/topic-policy.md
@.claude/rules/writing-style.md
@.claude/rules/zenn-workflow.md
@.claude/rules/article-requirements.md
@.claude/rules/privacy.md
@.claude/rules/writing-process.md
@.claude/rules/cross-agent-review.md
@.claude/rules/article-fact-check.md
```

## 何に詰まったか

Codex と Claude Code に同じ記事リポジトリを触らせると、次のようなズレが出ました。

- Codex は `.agents/skills/` を見るが、Claude Code は `.claude/skills/` を見る
- Codex 側の hook は `.codex/hooks.json`、Claude 側の hook は `.claude/settings.json`
- レビュー依頼の向きが「Codex 作成なら ClaudeCode」「ClaudeCode 作成なら Codex」で変わる
- 片方にしか必要ないローカル設定を書きすぎると、もう片方の起動コンテキストが重くなる

最初は `CLAUDE.md` を基準にして Codex にも読ませればよいと考えました。しかし Codex 側には `AGENTS.md` と `.agents/skills/` の文脈があります。Claude Code 側の詳細をそのまま読ませても、実行できないコマンドや不要なディレクトリ説明が混ざります。

## 分けた理由

分けた理由は、共通ルールとエージェント固有の実行環境を同じ粒度で扱わないためです。

このリポジトリでは、記事の方針や守秘義務、公開前レビューは共通ルールです。一方で hook や skill の実体はエージェントごとに違います。

`AGENTS.md` では Codex 側の実体を明示しています。

```markdown
## Hook

`articles/*.md` を保存すると、文体ルール違反語を警告する PostToolUse hook が走る。

- Codex 側: `.codex/hooks.json` → `.codex/hooks/check-article-style.sh`
- Claude 側: `.claude/settings.json` → `.claude/hooks/check-article-style.sh`
```

:::note warn
Codex 側の `hooks.json` では、Windows 環境で hook スクリプトを安定して呼ぶためにフルパス指定にする場合があります。記事では「どの設定ファイルがどのスクリプトを呼ぶか」を主題にしているため、ディレクトリ構成として相対パスで示しています。
:::

`CLAUDE.md` では Claude Code 側の設定を中心にし、最新の引き継ぎとして `CLAUDE_CODE_HANDOFF.md` を読むようにしています。

```markdown
## 最新の引き継ぎ

記事候補と Codex/ClaudeCode 連携の最新メモは `CLAUDE_CODE_HANDOFF.md` を参照する。
```

両方に完全に同じ文章を書くのではなく、同じ目的をそれぞれの実行環境に合わせて書き分ける形です。

## 注意点

この構成では、共通ルールの更新漏れに注意が必要です。

たとえば `writing-style.md` の文体NG語を更新したのに、hook 側の grep パターンを更新しないと、保存時の検出とレビュー時の検出がズレます。

:::note warn
`AGENTS.md` と `CLAUDE.md` を分けるだけでは、ルールの二重管理は減りません。共通ルールの本体を別ファイルに寄せ、ルートファイルは入口とエージェント固有差分に絞るのがポイントです。
:::

もう1つの注意点は、個人設定を混ぜないことです。`CLAUDE.local.md` のような個人用ファイルは gitignore に置き、公開リポジトリへ出すルートファイルにはローカル絶対パスや個人情報を書かないようにします。

## まとめ

Codex と Claude Code を同じリポジトリで使うときは、`AGENTS.md` と `CLAUDE.md` を無理に統合しない方が扱いやすくなりました。

- 共通ルールは `.claude/rules/` に寄せる
- エージェント固有の hook / skill / handoff 導線は入口ファイルに分けて書く
- 個人設定は公開されるルートファイルへ混ぜない

同じルールを守らせることと、同じファイルを読ませることは別問題でした。

## 参考リンク

- [harness17/zenn-articles](https://github.com/harness17/zenn-articles) - 本記事で扱った記事リポジトリ
- [AGENTS.md](https://github.com/harness17/zenn-articles/blob/main/AGENTS.md) - Codex 向け入口
- [CLAUDE.md](https://github.com/harness17/zenn-articles/blob/main/CLAUDE.md) - Claude Code 向け入口
- [Claude CodeのCLAUDE.mdを@importで分割してトピック別ルールに整理した](https://qiita.com/harnesswinner/items/6678320489deec25113a) - `CLAUDE.md` 分割自体の詳しい運用
