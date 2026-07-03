---
title: "AIエージェント別の詳細ルールの重複を共通正本へ戻した設計判断"
emoji: "🧭"
type: "tech"
topics: ["ai", "codex", "claudecode", "agents", "development"]
published: true
---

## はじめに

Chrome / Firefox 拡張を個人開発しているとき、Codex と Claude Code の両方に同じリポジトリを触らせていた。最初はそれぞれの入口である `AGENTS.md` と `CLAUDE.md` に、実装ルールや verify コマンドを書いていた。

ところが、拡張の構成が変わるたびに片方だけ更新され、もう片方のルールが古くなる問題が起きた。この記事では、エージェント別ファイルへ詳細ルールを重複させるのをやめ、`.agents/rules/` を共通正本にした判断を書く。

対象リポジトリは [harness17/kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker) です。

## 困ったこと: 入口ごとにルールがずれた

この拡張では、Amazon.co.jp の Kindle 蔵書情報をもとに、シリーズ候補や続刊・セール状態を確認している。実装境界はそれなりに細かい。

- content script は同一オリジン取得と保存を担当する
- background / offscreen はバックグラウンド照会を担当する
- popup / options は保存済み結果の表示を担当する
- Chrome は offscreen document、Firefox は background scripts で DOMParser を使う

このようなルールを、最初は Codex 用の `AGENTS.md` と Claude Code 用の `CLAUDE.md` の両方に書いていた。短期的には読みやすいが、更新時に破綻した。

たとえば verify コマンドが増えたとき、片方のファイルだけが新しい本数になり、もう片方は古いまま残る。片方のエージェントは「3本通せば十分」と判断し、もう片方は「5本必要」と判断する。実装の安全性を上げるためのルールが、逆に確認漏れの原因になっていた。

## 判断: エージェント別ファイルを正本にしない

この問題は「両方を忘れず更新する」では直らないと判断した。実装変更のたびに2ファイルを同期する運用は、時間が経つと必ず漏れる。

そこで、実装・データ・検証・公開の契約は `.agents/rules/` に集約し、`AGENTS.md` と `CLAUDE.md` は入口と索引だけにした。

現在の構成は次のようにしている。

```text
.agents/rules/
├── amazon-boundary.md
├── architecture-and-data.md
├── release-and-store.md
└── verification.md

AGENTS.md   # Codexの入口。共通ルールへの索引を持つ
CLAUDE.md   # Claude Codeの入口。共通正本を参照する
```

ポイントは、`AGENTS.md` と `CLAUDE.md` の違いを「読むエージェントの違い」に閉じることだった。実装契約そのものはエージェント固有にしない。

## 実装: AGENTS.md は索引にする

`AGENTS.md` には、作業開始時に読むべき共通ルールへのリンクを置いた。実装ルールの本文をここへ再コピーしない。

```markdown
## 共通ルール

- 常に読む: [.agents/rules/architecture-and-data.md](.agents/rules/architecture-and-data.md)
- 常に読む: [.agents/rules/verification.md](.agents/rules/verification.md)
- Amazon 取得、検索結果解析、fixture、権限を扱う場合: [.agents/rules/amazon-boundary.md](.agents/rules/amazon-boundary.md)
- manifest、store-assets、版上げ、パッケージ、公開を扱う場合: [.agents/rules/release-and-store.md](.agents/rules/release-and-store.md)

Claude Code 固有の共同作業ルールは `CLAUDE.md` と `.claude/rules/` を参照する。
プロジェクトの実装契約は `.agents/rules/` を正本とし、Claude/Codex 固有ファイルへ重複コピーしない。
```

ここで明示しているのは、どのルールを読むかと、どこを正本にするかだけである。たとえば「どの verify を通すか」は `AGENTS.md` に直接書かず、`.agents/rules/verification.md` に寄せる。

## 実装: CLAUDE.md も共通正本へ戻す

Claude Code 側の `CLAUDE.md` も、実装ルールを抱え込まない形にした。Claude Code 固有の共同作業ルールは残すが、実装契約は `AGENTS.md` と `.agents/rules/` へ戻す。

```markdown
# CLAUDE.md

Claude Code がこのリポジトリで作業するときの入口。

## 先に読む

実装・データ・検証・リリース契約は [AGENTS.md](AGENTS.md) と `.agents/rules/` を正本とする。
作業内容に対応する共通ルールを先に読む。

Claude/Codex共同作業が関係する場合は次も読む。

@.claude/rules/cross-agent-harness.md
@.claude/rules/project-collaboration-profile.md
@.claude/rules/handoff-protocol.md
@.claude/rules/store-reviewer-notes.md
```

この分け方にすると、Claude Code 専用の handoff や共同作業ルールは `CLAUDE.md` 側に残せる。一方で、データ境界や verify 本数のような実装契約は `.agents/rules/` だけを更新すればよい。

## 共通正本に入れたもの

`.agents/rules/architecture-and-data.md` には、モジュール境界とバックグラウンド照会契約を置いた。これは Codex でも Claude Code でも同じ判断で動いてほしい内容だからである。

```markdown
## バックグラウンド照会契約

- eligible series は completed / excluded を除き、有限の `highestVolume` を持つものとする。
- 1回の実行では対象全体を巡回し、内部的に `CHUNK_SIZE` ごとに処理する。chunk サイズを「alarm 1回の総上限」と誤解しない。
- Chrome は service worker に DOMParser が無いため offscreen document を使う。Firefox は background scripts に shared modules を読み込み inline 処理する。
- `status: unknown` で既存 cache がある場合は確定済みデータを上書きしない。3シリーズ連続で `unknown` になった場合はサイクルを失敗扱いにし、最終成功時刻を更新せず後続実行で再試行する。
- cache / queue / badge の更新は、途中停止後に再開可能な順序と粒度を保つ。
```

`.agents/rules/verification.md` には、確認コマンドをまとめた。

```powershell
node .\verify-kindle-library.mjs
node .\verify-catalog-probe.mjs
node .\verify-series-card.mjs
node .\verify-background-probe.mjs
node .\verify-auto-scan.mjs
```

この5本を入口ファイルへ重複コピーしない。将来 verify が増えたら、更新する場所は `verification.md` だけになる。

## 捨てた案

最初に考えたのは、`AGENTS.md` と `CLAUDE.md` の両方を毎回同じ内容に更新する運用だった。しかし、これは実装変更のたびに「もう片方も更新する」という記憶に依存する。

次に、片方をもう片方の完全コピーにする案も考えた。ただし、Claude Code には Claude Code 固有の共同作業ルールがあり、Codex には Codex 用の作業入口がある。完全コピーにすると、固有ルールまで混ざって逆に読みにくくなる。

採用したのは、次の分離だった。

| 種類 | 置き場所 |
| --- | --- |
| 実装・データ・検証・公開の契約 | `.agents/rules/` |
| Codex の作業入口 | `AGENTS.md` |
| Claude Code の作業入口と共同作業ルール | `CLAUDE.md` / `.claude/rules/` |

正本を1つにしつつ、入口ごとの違いは残す形である。

## 確認したこと

今回の構成では、次を確認した。

- `AGENTS.md` が `.agents/rules/architecture-and-data.md` と `.agents/rules/verification.md` を常時参照している
- `CLAUDE.md` が実装契約を `AGENTS.md` と `.agents/rules/` へ戻している
- `.agents/rules/` に `amazon-boundary.md`、`architecture-and-data.md`、`release-and-store.md`、`verification.md` がある
- verify コマンドの一覧が `verification.md` に集約されている
- Amazon 取得や公開物の境界が、実装入口ではなくトピック別ルールに分かれている

これで、実装変更時に「どちらのエージェント用ファイルを更新したか」を考える必要が減った。確認したい契約は `.agents/rules/` を見ればよい。

## まとめ

AIエージェントを複数使うと、入口ファイルも複数になる。しかし、入口が複数あることと、実装ルールの正本が複数あることは別問題だった。

今回の学びは次の3つ。

- `AGENTS.md` と `CLAUDE.md` に同じ詳細ルールを書かない
- 実装契約は `.agents/rules/` のような共通正本へ寄せる
- エージェント固有ファイルは、入口・索引・固有ルールに役割を絞る

ルールの drift は、注意力ではなく構造で減らすほうが安定した。

## 参考リンク

- [harness17/kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)
- [共通ルールディレクトリ](https://github.com/harness17/kindle-series-sale-tracker/tree/main/.agents/rules)
- [Chrome Extensions: Extension service worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle)
