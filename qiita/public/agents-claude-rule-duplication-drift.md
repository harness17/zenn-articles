---
title: AGENTS.mdとCLAUDE.mdに同じルールを書いて内容がずれた
tags:
  - codex
  - AIエージェント
  - ClaudeCode
  - 開発運用
private: false
updated_at: '2026-07-03T20:32:44+09:00'
id: cbbe3478783ebc552208
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

Codex 用の `AGENTS.md` と Claude Code 用の `CLAUDE.md` に実装ルールを重複して書いていたら、片方だけ更新されてルールがずれた。正本を `.agents/rules/` に集約し、両方から参照する構成に変えたら drift が止まった。

## 起きたこと

Chrome 拡張の開発リポジトリで、Codex と Claude Code を共同で使っていた。最初はそれぞれの設定ファイルに実装ルールを直接書いていた。

```text
AGENTS.md   ← Codex が読む
CLAUDE.md   ← Claude Code が読む
```

どちらにも「verify コマンドの本数」「permissions の制約」「fixture の匿名化ルール」などを書いていた。

数週間後、`AGENTS.md` 側の verify 本数は更新されたが `CLAUDE.md` 側は古いまま残っていた。Claude Code がレビューで「verify は 3 本すべて pass」と報告するが、実際は 5 本に増えている——という状態が起きた。

## 原因

同じ情報を 2 箇所に書いていたこと自体が原因だった。

- `AGENTS.md` は Codex の作業で更新される
- `CLAUDE.md` は Claude Code の作業で更新される
- 片方のエージェントが実装を変えたとき、自分の設定ファイルだけ更新して、もう片方は触らない

「次回更新時に揃えよう」は機能しなかった。実装変更のたびに 2 ファイルを同期する運用は忘れられる。

## 修正

実装ルールの正本を `.agents/rules/` にトピック別ファイルとして置き、`AGENTS.md` と `CLAUDE.md` はそこへの参照だけにした。

```text
.agents/rules/
├── architecture-and-data.md   # データ構造・責務分離
├── verification.md            # verify コマンド・完了ゲート
├── amazon-boundary.md         # Amazon 取得・fixture・権限
└── release-and-store.md       # manifest・version・パッケージ
```

`AGENTS.md` は索引として各ルールへのリンクを持つ。

```markdown
# AGENTS.md

## 共通ルール

- 常に読む: [.agents/rules/architecture-and-data.md]
- 常に読む: [.agents/rules/verification.md]
- Amazon 取得を扱う場合: [.agents/rules/amazon-boundary.md]
- manifest・公開を扱う場合: [.agents/rules/release-and-store.md]
```

`CLAUDE.md` は Claude Code 固有の共同作業ルール（handoff プロトコル、担当境界）だけを持ち、実装契約は `AGENTS.md` と `.agents/rules/` を正本として参照する。

```markdown
# CLAUDE.md

実装・データ・検証・リリース契約は AGENTS.md と .agents/rules/ を正本とする。
```

## 変更前後の比較

| 観点 | 変更前 | 変更後 |
|------|--------|--------|
| ルールの置き場 | `AGENTS.md` と `CLAUDE.md` に直接記載 | `.agents/rules/` に集約 |
| 更新時の操作 | 2 ファイルを同期する | 1 ファイルを更新する |
| drift のリスク | 高い（片方の更新忘れ） | 低い（正本が 1 つ） |
| 各 md の役割 | ルール本体 + エージェント固有設定 | 索引・参照 + エージェント固有設定のみ |

## 再発防止として入れたこと

1. **読み順の固定**: `AGENTS.md` の作業開始で共通ルールを読むことを明記し、`CLAUDE.md` も実装契約を `AGENTS.md` と `.agents/rules/` に戻す
2. **handoff プロトコル**: 実装ルール変更時は `.agents/rules/` を更新し、handoff に「ルール変更あり」と明記する
3. **ハーネス見直し**: 実装が進んで契約が変わったら、handoff 履歴からルールの陳腐化を検出して更新する

## 教訓

- 2 箇所に同じ情報を書くと、必ず片方が古くなる。正本を 1 つにして参照する
- 「更新時に揃える運用」は AI エージェントでも人間でも忘れる。構造で防ぐ
- `AGENTS.md` と `CLAUDE.md` の違いは「どのエージェントが読むか」であって「何を書くか」ではない。実装契約は共通の場所に置く

## 参考

- [kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker) — この問題が起きた Chrome / Firefox 拡張リポジトリ
- [共通ルールディレクトリ](https://github.com/harness17/kindle-series-sale-tracker/tree/main/.agents/rules) — 正本として集約したルールファイル群
