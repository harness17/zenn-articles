---
title: Claude CodeのCLAUDE.mdを@importで分割してトピック別ルールに整理した
tags:
  - Markdown
  - 開発環境
  - AI
  - ClaudeCode
private: false
updated_at: '2026-05-24T15:22:44+09:00'
id: 6678320489deec25113a
organization_url_name: null
slide: false
ignorePublish: false
---

## はじめに

Claude Code を使っているとプロジェクトごと・ユーザーごとに `CLAUDE.md` を書きます。最初は 1 ファイルで済みますが、ルールを追加していくと 200 行を超え、毎セッションでそのまま読み込まれてコンテキストが重くなります。

この記事では、`CLAUDE.md` を `@import` 構文でトピック別ファイルに分割した構成と、分割するときに決めた判断軸をまとめます。

対象は次のような人を想定しています。

- Claude Code を導入したが `CLAUDE.md` の分割粒度に迷っている
- ルールが増えてきて毎セッションの読み込みが重い
- グローバルルールとプロジェクト固有ルールの置き場所を整理したい

## 詰まったポイント

単一の `CLAUDE.md` にルールを書き続けると次の問題が出ました。

- 200 行を超えると編集中にどこに何があるか分からなくなる
- ルールを 1 つ修正したいだけで巨大ファイルを開くことになる
- 「ここに足すか、別の箇所に足すか」を毎回考えるコストが上がる
- セッションのたびに全文が読まれるため、使わないルールもトークンを消費する

最後の点が決定打でした。ルールが増えるほど 1 セッションあたりのコンテキストが圧迫されます。

## 採用した構成

`CLAUDE.md` は import の目次だけにして、本体は `.claude/rules/<topic>.md` に分けました。

```text
~/.claude/
├── CLAUDE.md              # 38行（@importのみ）
└── rules/
    ├── advisor-strategy.md          # 58行
    ├── api-quota-design.md          # 85行
    ├── git-ops.md                   # 38行
    ├── security-coding.md           # 74行
    ├── skill-graph-auto-register.md # 111行
    ├── handoff-capture.md           # 102行
    ├── test-strategy.md             # 62行
    ├── sprint-contract.md           # 40行
    └── ... 計17ファイル / 合計929行
```

`CLAUDE.md` の中身は次のように `@` 付きの相対パスで列挙します。

```markdown
# グローバルルール
ユーザに同調せず、目的達成を優先する。

@rules/claude-md-generation.md
@rules/git-ops.md
@rules/security-coding.md
@rules/api-quota-design.md
@rules/skill-graph-auto-register.md
```

Claude Code はセッション開始時に `CLAUDE.md` を読み、その中の `@<path>` を辿って各ファイルを取り込みます。プロジェクト側 `<repo>/CLAUDE.md` も同じ書式で取り込みできます。

## 分割の判断軸

実運用で次のラインに落ち着きました。

| 軸 | 採用したライン |
| --- | --- |
| 1 ファイルの粒度 | 1 トピック（例: git 操作、API クォータ、セキュリティコーディング） |
| ファイル分割の閾値 | 60〜100 行を超えたら別ファイルに抽出 |
| 冒頭の形式 | ルールが「いつ適用するか」を最初に宣言 |
| プロジェクト側の置き場所 | `<repo>/.claude/rules/<topic>.md` で同じ構造を踏襲 |

「いつ適用するか」を冒頭に書くのは、ルールが多くなった時に「このルールは今関係するか」を判断しやすくするためです。

例: `git-ops.md` の冒頭は次のように始まります。

```markdown
# Git 操作ルール

## git add は個別ファイル指定

`git add -A` や `git add .` は使用しない。
```

ルール名（見出し）が短く具体的なので、`CLAUDE.md` から飛んだ時に何のルールか即わかります。

## 落とし穴

分割するときに踏んだ落とし穴をまとめます。

### `@` パスの解決ルールを把握しておく

公式ドキュメント（[Memory and CLAUDE.md](https://docs.anthropic.com/en/docs/claude-code/memory)）の「Import additional files」セクションによると、`@path/to/import` 構文には次の仕様があります。

- 相対パスと絶対パスの両方が使える
- 相対パスは **import 文を含むファイル** からの相対（カレントワーキングディレクトリではない）
- import は再帰的に最大 5 hop まで辿られる
- ホームディレクトリエイリアスも使える（例: `@~/.claude/my-project-instructions.md`）

私は最初「絶対パスは使えない」と誤解して相対パスだけで書いていましたが、worktree 横断で個人設定を共有する場合は次のように `~/` 起点の絶対パス import が便利です。

```markdown
# Individual Preferences
- @~/.claude/my-project-instructions.md
```

### import を増やしすぎても context は減らない

これは設計上の落とし穴です。公式ドキュメントでも明示されていますが、import で分割しても **imported files load at launch**、つまりセッション開始時に全部展開されてコンテキストに乗ります。

> Splitting into `@path` imports helps organization but does not reduce context, since imported files load at launch.
> （ [Memory and CLAUDE.md - My CLAUDE.md is too large](https://docs.anthropic.com/en/docs/claude-code/memory) ）

つまり @import 分割は **編集しやすさと整理のため** であって、トークン消費そのものは減りません。本気でコンテキストを減らしたい場合は、公式ドキュメントが案内している `.claude/rules/` の `paths` frontmatter（path-scoped rules）を使い、対象ファイルを開いた時だけ読み込ませる方法を併用します。

私の運用では次のように分けています。

1. 全プロジェクトに常時必要なルール: `@rules/<topic>.md` で常時 import
2. 特定ディレクトリでのみ必要なルール: `.claude/rules/<topic>.md` に `paths:` frontmatter を付けて path-scoped 化

### 命名規則をメタルールで固定する

ルールが増えてくると、分割の粒度や import の書き方が揺れます。ぶれを防ぐために、`claude-md-generation.md` というメタルールを 1 つ作って次を強制しています。

```markdown
# CLAUDE.md 生成ルール

`CLAUDE.md` を生成・作成する際は、必ず `.claude/rules/` フォルダも並列して作成すること。

- ルール内容はトピックごとにファイルを分割する
- `CLAUDE.md` からは `@.claude/rules/xxx.md` 形式でインポートして参照する
```

これを `CLAUDE.md` の先頭近くで import しておくと、新規プロジェクトのセットアップを AI に任せた時にも同じ構造になります。

## まとめ

- `CLAUDE.md` は @import の目次だけにして、本体は `.claude/rules/<topic>.md` に分割する
- 分割の閾値は 60〜100 行、1 ファイル 1 トピック
- 各ルールの冒頭で「いつ適用するか」を宣言する
- 命名規則と分割方針をメタルール 1 枚に書いて先頭で import すると、新規プロジェクトでも構造が揃う
- **トークン消費そのものを減らしたい場合は `@import` 分割だけでは足りない。** `.claude/rules/` の `paths:` frontmatter による path-scoped rules を併用し、対象ファイルを開いた時だけ読み込ませる構成にする

ルールが増えてくると、置き場所を考えるコスト自体が小さくない作業時間になります。早めにトピック分割しておくと、後から増やすときに迷いません。

## 参考

- Claude Code 公式ドキュメント: [Memory and CLAUDE.md](https://docs.anthropic.com/en/docs/claude-code/memory)（`@path/to/import` 構文と `.claude/rules/` の仕様）
- 同上 [Import additional files](https://docs.anthropic.com/en/docs/claude-code/memory#import-additional-files) セクション（相対パス / 絶対パス / `~/` エイリアス / 5 hop の再帰展開）
- 同上 [Path-specific rules](https://docs.anthropic.com/en/docs/claude-code/memory#path-specific-rules) セクション（`paths:` frontmatter による条件付き読み込み）
- プロジェクト側 `.claude/rules/` 構成の実例: [harness17/DevNext - .claude/rules](https://github.com/harness17/DevNext/tree/master/.claude/rules)（ASP.NET Core 10 テンプレート、22 ファイルのトピック分割例）
