# 構成メモ: Codex と Claude の作業記録を My-Skill-Graph に残す運用を作った

## メタ情報

- **slug 案**: `codex-claude-skill-graph-worklog`
- **type**: tech
- **emoji**: 🧭
- **topics**: `ai` / `codex` / `claude` / `obsidian` / `workflow`
- **想定文字数**: 3000〜4000字
- **想定執筆時間**: 5〜6時間
- **ステータス**: 構成中

## タイトル案

| 案 | タイトル | 強み |
|----|---------|------|
| **A**（推奨） | Codex と Claude の作業記録を My-Skill-Graph に残す運用を作った | 共有記録としての主題が明確 |
| B | AIエージェント同士の引き継ぎを Obsidian に残すようにした話 | 引き継ぎ課題が前に出る |
| C | AIとの開発ログを「読める記録」に変えるために My-Skill-Graph を使った | Before / After が伝わる |

→ **A 推奨**。ツール紹介ではなく、「Codex と Claude が同じ作業文脈を共有するために、作業記録を残す運用を作った」という体験記事にできる。

---

## 想定読者

Codex や Claude Code を併用していて、会話ごとに文脈が切れること、別エージェントへの引き継ぎが曖昧になることに困っている個人開発者。

---

## 記事の核

AIエージェントとの作業は、1回の会話内ではかなり進みます。一方で、会話が変わると「なぜその判断をしたか」「Claude に何を見てほしいか」「次に何をやるか」が散らばりやすくなりました。

そこで、My-Skill-Graph を **AIとの会話ログ置き場** ではなく、**作業判断と引き継ぎを残す共有記録** として使うようにしました。記事では、次の3点に絞って書く。

1. 会話ログだけでは次の作業に使いにくかった
2. `decisions/`、`strategies/`、`ops/handoffs/`、`self/goals.md` に役割を分けた
3. Codex と Claude のどちらが続きから入っても、判断・変更・未解決点を追えるようになった

---

## 方針チェック

このテーマは、単なる「Obsidian でナレッジ管理する方法」ではなく、実際に AI エージェント併用で困ったことから生まれた運用改善として書く。

- **詰まったポイント**: Codex と Claude の会話・作業結果が分散し、次の作業者が「なぜそうしたか」を追いにくかった
- **解決の判断軸**: 全ログ保存ではなく、次の作業に必要な判断・戦略・引き継ぎだけを命題文で残す
- **実例**: `AGENTS.md` のルール、My-Skill-Graph のノート構造、handoff ファイル、記事候補の戦略メモ
- **書かないこと**: Obsidian 入門、Claude Code 入門、Codex 入門、知識管理ツール比較

---

## 構成

### はじめに（200〜300字）

- Codex と Claude Code を、個人開発と技術記事執筆で併用している。
- 最初は会話ごとに作業が進むだけで十分だと思っていた。
- しかし、複数日にまたがる作業や、片方のエージェントにレビューを渡す場面で、判断の理由が埋もれた。
- この記事では、My-Skill-Graph を「共有記録」として使い、AIエージェント間の引き継ぎを安定させた運用を書く。

### セクション1: 会話ログは残っていても、作業記録にはならなかった（500〜700字）

- 伝えること:
  - 会話ログは細かすぎて、次の作業者が読む前提の記録になりにくい。
  - 「何をしたか」より「なぜそれを選んだか」「次に何を見るか」が抜けると、作業再開のコストが高い。
- 具体例:
  - 記事候補を話したあと、なぜそのテーマを採用したかが会話の中に埋もれる。
  - Claude にレビューを頼むとき、対象ファイル・変更理由・未検証点を毎回説明し直す必要がある。
  - 設計判断と記事戦略が別々に残ると、Lapras や就職活動への接続が弱くなる。
- 書くポイント:
  - 「ログを全部保存する」ではなく、「次の判断に使える記録に圧縮する」必要があった、と置く。

### セクション2: My-Skill-Graph に4種類の置き場を作った（800〜1000字）★メイン1

- 伝えること:
  - 共有記録として使うために、記録の種類ごとに置き場を分けた。
  - それぞれのノートは、AIエージェントが次の作業で読む前提にした。
- 具体例:

| 置き場 | 役割 | 例 |
|--------|------|----|
| `decisions/` | 技術判断と理由 | 「XしたのはYのため」 |
| `strategies/` | 記事・OSS・就職活動への接続 | スキルグラフ導入記事の切り口 |
| `ops/handoffs/` | Codex / Claude 間の引き継ぎ | 対象、変更、検証、未解決点 |
| `self/goals.md` | 現在の作業スレッド | 次に進める記事候補 |

- コード例候補:

```markdown
---
description: "スキルグラフ導入方法の記事は、記事執筆プロセスの再現性を示す資産になる。"
opportunity_type: product
status: idea
next_action: "共有記録としての切り口で構成する"
created: 2026-05-10
---

# スキルグラフ導入記事は記事執筆プロセスの再現性を示すため
```

- 書くポイント:
  - `description` や `next_action` は、人間だけでなく次のエージェントにも効く。
  - タイトルを「命題文」にすると、検索結果だけで判断の中身を推測しやすい。

### セクション3: AGENTS.md に「いつ記録するか」を書いた（600〜800字）★メイン2

- 伝えること:
  - 運用は気合いで続けると崩れるため、エージェント用ルールに書いた。
  - すべてを記録するのではなく、記録する条件を限定した。
- 具体例:

```markdown
Persist when any of these happened:

- An architecture or design choice was made after comparing options.
- A new library, pattern, integration, security decision, deployment approach, or data model was adopted.
- An OSS, portfolio, job-search, freelance, or product strategy insight emerged from the technical work.
- self/goals.md should reflect a completed item, changed active thread, or clear next action.
```

- 書くポイント:
  -  routine なファイル読み取りや単純修正は残さない。
  - 記録の基準を作ったことで、ノートが増えすぎる問題を抑えた。
  - 「記録しない条件」もルールに入れた点を書く。

### セクション4: handoff はレビュー依頼の形に寄せた（600〜800字）★メイン3

- 伝えること:
  - Codex と Claude を併用するとき、一番効いたのは handoff の定型化だった。
  - 共有記録は、過去ログではなく「次の担当者が動けるメモ」として書く。
- 具体例:
  - `ops/handoffs/2026-05-10-zenn-article-candidates-codex.md`
  - 書く項目:
    - 背景
    - 対象ファイル
    - 変更内容
    - 検証結果
    - 未解決点
    - 次のアクション
- コード例候補:

```markdown
## Context

Codex drafted article candidates for Zenn based on the current topic policy.

## Changed

- Added a draft structure for the selected topic.
- Kept the focus on experience-based problem solving.

## Open Questions

- Whether Claude should review the framing before writing the article body.
```

- 書くポイント:
  - handoff は日記ではなく、レビュー依頼・継続作業の入口。
  - 共有先を意識して、長い会話を短く要約する。

### セクション5: 記録を記事戦略にもつなげる（400〜600字）

- 伝えること:
  - My-Skill-Graph は開発記録だけでなく、記事テーマや就職活動で説明する材料にもなる。
  - 「なぜこの技術を選んだか」を後から説明できること自体がポートフォリオ価値になる。
- 具体例:
  - 技術判断から Zenn 記事候補にする。
  - 記事候補から Lapras・職務経歴書で説明できる実績に接続する。
  - 今回の「共有記録としてのスキルグラフ」自体も記事テーマになった。
- 書くポイント:
  - AI活用記事に寄せすぎず、「判断の再利用」という実務寄りの価値に寄せる。

### まとめ（150〜250字）

- 要点3つ:
  1. 会話ログを全部残すだけでは、次の作業者が使いやすい記録にならない
  2. `decisions/`、`strategies/`、`ops/handoffs/`、`self/goals.md` に役割を分けると、判断・戦略・引き継ぎを分離できる
  3. AGENTS.md に記録条件を書くと、Codex と Claude のどちらが作業しても運用が揃いやすい
- 締め方:
  - AIエージェントとの作業は、その場で速く進めるだけでなく、次の会話に判断を渡せると強くなる。

---

## コード例の準備状況

| セクション | コード・引用元 | 出典 | 準備状況 |
|----------|----------------|------|----------|
| §2 strategy note | frontmatter + 命題文タイトル | `strategies/スキルグラフ導入記事は記事執筆プロセスの再現性を示すため.md` | ✅ 抜粋案あり |
| §3 persistence rule | `Persist when...` の条件 | `AGENTS.md` | ✅ 抜粋案あり |
| §4 handoff template | Context / Changed / Open Questions | `ops/handoffs/` | 未着手 |
| §5 goals update | active thread / completed item | `self/goals.md` | 未着手 |

---

## 参考リンク候補

- [Codex](https://openai.com/codex/)
- [Claude Code](https://docs.anthropic.com/claude-code)
- [Obsidian](https://obsidian.md/)
- [Zenn](https://zenn.dev/)
- [My-Skill-Graph 運用ノート]（公開可否を執筆前に判断）

---

## 残タスク（執筆前に確認すること）

- [ ] タイトル A/B/C を確定する
- [ ] `ops/handoffs/` から公開してよい例を1つ選ぶ
- [ ] `AGENTS.md` から引用する範囲を短くする
- [ ] My-Skill-Graph の具体パスを記事でどこまで出すか決める
- [ ] 個人情報・ローカルパス・就職活動の詳細が出すぎていないか確認する
- [ ] 公開前に `/article-review` で文体・守秘義務・必須要素を確認する

---

## 執筆順序（推奨）

1. §1 の困りごとを書く
2. §2 と §3 で運用ルールを書く
3. §4 の handoff 例を入れる
4. §5 で記事戦略への接続を書く
5. はじめに・まとめを最後に調整する
