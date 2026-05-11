---
title: "CodexとClaudeの作業記録をMy-Skill-Graphに残す運用を作った"
emoji: "🧭"
type: "tech"
topics: ["ai", "codex", "claude", "obsidian", "workflow"]
published: false
---

## はじめに

OpenAI のコーディングエージェント環境である Codex と、Anthropic の Claude Code を、個人開発と技術記事執筆で併用しています。

最初は、会話ごとに作業が進めば十分だと思っていました。Codex に実装や記事の下書きを頼み、Claude Code にレビューや別視点の確認を頼む。1回の会話の中では、それでかなり進みます。

ただ、複数日にまたがる作業では別の問題が出てきました。前回なぜその判断をしたのか。次にどのファイルを見るべきなのか。Claude にレビューしてほしい論点は何なのか。こうした情報が、会話ログの中に埋もれていきました。

そこで、Obsidian で運用している個人用ナレッジベース `My-Skill-Graph` を、AI との会話ログ置き場ではなく、**作業判断と引き継ぎを残す共有記録**として使うようにしました。

この記事では、Zenn 記事管理リポジトリ [harness17/zenn-articles](https://github.com/harness17/zenn-articles) で実際に使っている、Codex と Claude Code の作業記録を `My-Skill-Graph` に残す運用を書きます。

## 会話ログは残っていても、作業記録にはならなかった

AI エージェントとの会話ログは、情報量が多いです。

途中で試した案、捨てた案、ツールの出力、修正前の文章、確認したルール。作業の過程は残ります。ただ、そのままでは次の作業者が読む前提の記録にはなりませんでした。

たとえば、Zenn の記事テーマを相談したとき、会話ログをたどれば「なぜそのテーマを採用したか」は分かります。しかし、後日見返したいのは会話全体ではありません。

見たいのは、だいたい次のような情報です。

- 何を選んだか
- 何を捨てたか
- なぜその選択にしたか
- 次に何をすればよいか

Claude Code にレビューを頼む場面でも同じでした。Codex が記事を書いたあと、Claude Code に見てほしいのは「全部読んで」ではなく、「この切り口で守秘義務や記事方針から外れていないか見てほしい」という具体的な依頼です。

会話ログは過程を残すには向いています。一方で、作業を再開する入口としては細かすぎました。

そこで、「ログを全部保存する」のではなく、「次の判断に使える形に圧縮する」方針にしました。

## My-Skill-Graph に4種類の置き場を作った

`My-Skill-Graph` では、記録の種類ごとに置き場を分けています。

| 置き場 | 役割 | 例 |
| --- | --- | --- |
| `decisions/` | 技術判断と理由 | `XしたのはYのため` |
| `strategies/` | 記事・OSS・就職活動への接続 | `記事テーマやポートフォリオ化の方針` |
| `ops/handoffs/` | Codex / Claude Code 間の引き継ぎ | `対象、変更、検証、未解決点` |
| `self/goals.md` | 現在の作業スレッド | `次に進める記事候補` |

ポイントは、会話単位ではなく、**記録の用途**で分けたことです。

たとえば、技術判断は `decisions/` に置きます。タイトルは「Redisについて」のような名詞ではなく、「RedisをキャッシュにしたのはDB負荷を下げるため」のような命題文にします。検索結果にタイトルだけが出ても、判断の中身を推測できるようにするためです。

記事や仕事探しにつながる気づきは `strategies/` に置きます。今回の記事も、最初は「スキルグラフ導入方法を書いたほうがよいか」という相談から始まりました。その場で、次のような戦略メモを残しました。

```markdown
---
description: "スキルグラフ導入方法の記事は、単なるツール紹介ではなく記事執筆プロセスの再現性と継続改善力を示すポートフォリオ資産になる。"
opportunity_type: product
status: active
next_action: "共有記録としての運用に絞って本文を書く"
created: 2026-05-10
---

# スキルグラフ導入記事は記事執筆プロセスの再現性を示すため
```

ここで残しているのは、記事本文ではありません。次に作業する自分や AI エージェントが、「このテーマはツール紹介ではなく、共有記録として書く」と分かるためのメモです。

この粒度にしたことで、会話をまたいでも作業の向きがぶれにくくなりました。

## AGENTS.md に「いつ記録するか」を書いた

記録は、気合いで続けようとすると崩れます。

毎回すべてを記録すると、ノートが増えすぎます。逆に、気が向いたときだけ書くと、重要な判断ほど忙しいタイミングで抜けます。

そこで、Codex 側の `AGENTS.md` に「記録する条件」を書きました。

```markdown
## Activity-end persistence

Persist when any of these happened:

- An architecture or design choice was made after comparing options.
- A new library, pattern, integration, security decision, deployment approach, or data model was adopted.
- An OSS, portfolio, job-search, freelance, or product strategy insight emerged from the technical work.
- self/goals.md should reflect a completed item, changed active thread, or clear next action.
```

実際の運用では、反対に「記録しないもの」も決めています。

- ルール確認やファイル読み取りだけの作業
- 単純なバグ修正
- フォーマットだけの変更
- git 操作だけで終わる作業

この線引きを入れたことで、`My-Skill-Graph` が作業ログの置き場になりすぎるのを避けられました。

記録したいのは、すべての行動ではありません。後から説明したい判断です。

たとえば、「記事のタイトルを少し直した」だけなら残しません。一方で、「記事の切り口をツール紹介から共有記録に変えた」なら残します。これは、後から本文を書くときにも、就職活動で技術発信の姿勢を説明するときにも使える判断だからです。

## handoff はレビュー依頼の形に寄せた

Codex と Claude Code を併用していて、一番効いたのは handoff の定型化でした。

片方のエージェントが作ったものを、もう片方に見てもらう。これは便利ですが、依頼が曖昧だとレビューも曖昧になります。

そこで、`My-Skill-Graph` の `ops/handoffs/` に、次のような観点で引き継ぎを書くようにしました。

```markdown
## Context

Codex drafted article candidates for Zenn based on the current topic policy.

## Changed

- Added a draft structure for the selected topic.
- Kept the focus on experience-based problem solving.

## Verification

- Checked the article requirements.
- Kept `published: false`.

## Open Questions

- Whether Claude Code should review the framing before writing the article body.
```

handoff は日記ではなく、次の担当者が動くための入口です。

そのため、細かい会話の流れは書きません。代わりに、背景、触ったファイル、変更内容、検証、未解決点を書きます。

この形にしてから、Claude Code にレビューを頼むときの説明が短くなりました。Codex 側も、Claude Code が残したメモを読めば、どこから作業を再開すればよいか分かります。

特に記事執筆では、公開前に別エージェントのレビューを通す運用にしています。作成者と別視点のレビューを入れることで、文体、守秘義務、記事方針の見落としを減らすためです。

## 記録を記事戦略にもつなげる

`My-Skill-Graph` を共有記録にしたことで、開発作業だけでなく、記事戦略にもつながるようになりました。

設計判断を `decisions/` に残しておくと、後から「この判断は記事にできるか」を見直せます。戦略メモを `strategies/` に残しておくと、「この記事は何のために書くのか」を会話の外に出せます。

今回の記事も、その流れで出てきました。

最初の問いは、「スキルグラフの導入方法も追加記事として書いたほうがよいか」でした。そこから、単なる導入手順ではなく、Codex と Claude Code の作業記録を共有記録にする運用として切り出しました。

この切り口なら、Obsidian の使い方そのものではなく、AI エージェントと作業するときに文脈をどう残すかを書けます。

技術記事としても、ポートフォリオとしても、「何を作ったか」だけでなく「なぜその運用にしたか」を説明できることは価値があります。AI を使って速く作業した、だけではなく、次の作業に判断を渡せる仕組みを作った、と言えるからです。

## まとめ

Codex と Claude Code を併用する中で、会話ログをそのまま残すだけでは、次の作業に使いにくいと感じました。

そこで、`My-Skill-Graph` に `decisions/`、`strategies/`、`ops/handoffs/`、`self/goals.md` という役割を持たせ、判断、戦略、引き継ぎ、現在地を分けて残すようにしました。

特に効いたのは、次の3点です。

- 会話ログではなく、次の判断に使う記録へ圧縮する
- AGENTS.md に記録する条件と記録しない条件を書く
- handoff をレビュー依頼の形にして、別エージェントが動き出せる入口にする

AI エージェントとの作業は、その場で速く進めるだけでも効果があります。さらに、判断を次の会話に渡せるようにすると、複数日にまたがる個人開発や記事執筆でも使いやすくなりました。

## 参考リンク

- [harness17/zenn-articles](https://github.com/harness17/zenn-articles)
- [Codex](https://openai.com/codex/)
- [Claude Code docs](https://docs.anthropic.com/claude-code)
- [Obsidian](https://obsidian.md/)
