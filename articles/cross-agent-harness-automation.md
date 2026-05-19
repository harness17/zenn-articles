---
title: "CodexとClaude Codeを相互呼び出しするハーネスを組んだ"
emoji: "🔁"
type: "tech"
topics: ["ai", "codex", "claude", "workflow", "automation"]
published: true
---

## はじめに

この記事は、Codex と Claude Code の2つの AI コーディングエージェントを同じリポジトリで併用していて、どちらに何を渡すかを毎回手で書くのが重いと感じている個人開発者向けです。

Codex と Claude Code を同じリポジトリで使う運用は、以前 [cross-agent-harness](https://github.com/harness17/cross-agent-harness) に切り出しました。ここで言うハーネスは、依頼の渡し方やレビュー観点、公開ゲートを会話の外（リポジトリ内のファイルとスクリプト）に固定する仕組みのことです。

前回の記事では、共同作業のために `CLAUDE_CODE_HANDOFF.md`、project profile、skills、レビューゲートを用意した話を書きました。`CLAUDE_CODE_HANDOFF.md`（以下 handoff）は、AI 同士の作業依頼、レビュー結果、未確認事項を時系列で残す共有メモです。

ただ、実際に使ってみると次の課題が残りました。

- Codex で作業したあと、Claude Code にレビューしてほしい
- Claude Code で設計したあと、Codex に実装を渡したい
- そのたびに依頼文、対象範囲、verify 条件、戻し先を手で書くのが重い
- 片方の会話ログだけに結果が残ると、次の作業で追えない

そこで、`cross-agent-harness` に相互呼び出しの導線を足しました。

この記事では、Claude Code から Codex を呼び出す `/codex-dev` と、Codex から Claude Code をレビュー専用で呼び出す `invoke-claude-review.ps1` を、なぜ分けたかを書きます。

## 2つのAIを開くだけでは共同開発にならない

Codex と Claude Code は、どちらもターミナルから使えます。単純に考えると、2つのターミナルを開けば共同開発できそうに見えます。

しかし、自分の運用ではそれだけだと足りませんでした。

たとえば Codex で実装したあと、Claude Code にレビューを頼みたい場面があります。このとき、Claude Code に何を渡すべきでしょうか。

- 最新の handoff
- プロジェクト固有の profile
- `git diff HEAD`
- レビュー観点
- 触ってよい範囲
- publish / push してよいか

これを毎回手でプロンプトに書くと、漏れます。

逆方向も同じです。Claude Code で設計を詰めたあと、Codex に実装を渡したい場面があります。このときも、完成条件、対象ファイル、verify コマンド、禁止事項が曖昧だと、Codex が広く触りすぎます。

つまり、必要だったのは「別の AI を起動すること」ではありません。作業契約を持ったまま、もう片方へ渡すことでした。

## 呼び出しの単位を handoff にした

最初に決めたのは、相互呼び出しの中心を `CLAUDE_CODE_HANDOFF.md` に置くことです。

呼び出し時のプロンプトだけに依頼内容を書くと、その結果は呼び出した側のセッションに閉じます。次の作業者が読むには弱いです。

そこで、handoff には次を残すようにしました。

```md
## YYYY-MM-DD HH:mm 追記（<主題> — <agent> 作成）

- 対象: <branch / worktree / path>
- 作成者: <Codex | Claude Code | user>
- 主題: <一文>
- 触ってよい範囲: <files / directories>
- 触ってはいけない範囲: <unrelated files / user changes>
- 完成条件:
  - <normal behavior>
  - <preconditions / auth / usage>
  - <error handling>
  - <no-regression checks>
- セルフ verify: <command and result>
- レビュー観点:
  - <risk-focused checks>
```

この形式にしておくと、Codex から Claude Code を呼んでも、Claude Code から Codex を呼んでも、依頼と結果の戻し先が同じになります。

相互呼び出しを図にすると、こういう形です。

```mermaid
flowchart LR
    U["User"] --> H["CLAUDE_CODE_HANDOFF.md"]
    C["Codex"]
    CL["Claude Code"]

    CL -->|"限定実装を依頼"| H
    H -->|"完成条件と verify"| C
    C -->|"実装結果・未確認事項"| H

    C -->|"レビューを依頼"| H
    H -->|"handoff / profile / diff"| CL
    CL -->|"レビュー結果"| H

    H --> G{"merge / publish gate"}
    G -->|"user 明示あり"| U
    G -->|"条件未達"| H
```

ポイントは、Codex と Claude Code が直接好きにやり取りするのではなく、handoff を間に置くことです。

## Claude CodeからCodexを呼び出す

Claude Code から Codex を呼び出す導線は、`codex-dev` skill として置きました。

これは、Claude Code が設計と実装計画を作り、Codex を MCP サーバ経由で呼び出して、実装を委譲する流れです。

`cross-agent-harness` では、プロジェクトの `.mcp.json` に Codex MCP サーバを登録する前提にしています。

```json
{
  "mcpServers": {
    "codex": {
      "command": "codex",
      "args": ["mcp-server"]
    }
  }
}
```

`codex-dev` の中では、Codex に渡す指示を次のように固定しています。

```text
<RULE_FILE> のルールに従って、実装計画 <計画ファイルパス> をチェックボックス順に実装してください。
作業範囲は計画ファイルに書かれたファイル・責務に限定してください。
実装後に可能な範囲で verify を実行し、結果を報告してください。
git add / git commit / git push は実行しないでください。
ネットワーク、外部サービス、追加権限、danger-full-access が必要になった場合は作業を止め、必要な理由と未完了範囲を報告してください。
```

ここで重要なのは、Codex にいきなり「いい感じに実装して」と渡さないことです。

Claude Code 側で設計し、実装計画を作り、ユーザー承認を得てから Codex に渡します。Codex には、作業範囲を計画ファイルに限定させます。

また、Codex には commit / push をさせません。Codex は未コミット差分として実装を返し、Claude Code が差分と verify 結果を確認します。

この分担にすると、Claude Code は設計とレビュー、Codex は実装と検証という役割に寄せられます。

## CodexからClaude Codeをレビュー専用で呼び出す

逆方向、つまり Codex から Claude Code を呼び出す導線も作りました。

こちらは `scripts/invoke-claude-review.ps1` です。用途はレビュー専用に絞っています。

このスクリプトは、対象プロジェクトから次を集めます。

- `CLAUDE_CODE_HANDOFF.md`
- `.claude/rules/project-collaboration-profile.md`
- `git diff HEAD`

その上で、Claude Code CLI を `--print` で呼び出します。

```powershell
$arguments = @(
    "--print",
    "--output-format", "text",
    "--permission-mode", "dontAsk",
    "--tools", "",
    "--max-budget-usd", $MaxBudgetUsd.ToString([System.Globalization.CultureInfo]::InvariantCulture),
    $prompt
)

$review = & $ClaudeCommand @arguments
```

`--tools ""` を渡しているのは、Claude Code にファイル編集をさせないためです。Codex から呼ぶ Claude Code は、あくまで review-only の相手にしています。

プロンプト側でも、役割をレビューに限定しています。

```text
Task:
- Review the current handoff and diff only.
- Do not edit files.
- Prioritize correctness, security, regressions, missing tests, and merge blockers.
- Treat the project collaboration profile as binding.
- If there are no blocking findings, say that clearly and list residual risks or verification gaps.
- Reply in Japanese Markdown.
```

レビュー結果は、そのまま `CLAUDE_CODE_HANDOFF.md` に追記します。

```powershell
$appendLines = @(
    "",
    "---",
    "",
    "## $timestamp 追記（Claude Code 自動レビュー）",
    "",
    "- 対象: ``$targetRoot``",
    '- 呼び出し元: Codex / `scripts/invoke-claude-review.ps1`',
    '- 権限: review-only (`--tools ""`, `--permission-mode dontAsk`)',
    "- MaxBudgetUsd: $MaxBudgetUsd",
    "",
    ($review -join [Environment]::NewLine)
)
```

Codex が実装した差分を、Claude Code がレビューする。結果は handoff に戻る。次のセッションでは、どちらの AI から見ても同じ場所にレビュー結果があります。

これが欲しかった導線でした。

## 双方向にしたから、役割は分けた

相互呼び出しを作ると、何でも自動で回したくなります。

ただ、同じ worktree で2つの AI が実装し始めると、競合や上書き事故が起きます。そこで、呼び出し方向ごとに役割を分けました。

| 方向 | 主な用途 | 触る権限 |
| --- | --- | --- |
| Claude Code → Codex | 限定実装、テスト追加、機械的修正 | Codex が workspace を編集する |
| Codex → Claude Code | レビュー、リスク確認、merge / publish 判断材料 | Claude Code は編集しない |

Claude Code から Codex を呼ぶ場合は、実装を任せます。代わりに、計画ファイル、完成条件、verify、禁止事項を渡します。

Codex から Claude Code を呼ぶ場合は、レビューだけにします。`--tools ""` で編集権限を消し、handoff と diff を読んで判断だけ返してもらいます。

この非対称性が大事でした。

「相互呼び出し」と言っても、両方向で同じことをさせる必要はありません。むしろ、同じことをさせないためにハーネスが必要でした。

## mergeとpublishは自動化しない

相互呼び出しを入れても、merge / publish は自動化しません。

`cross-agent-harness` では、merge / publish 前に次の4条件を確認する形にしています。

```text
1. セルフ verify 済み
2. 反対側レビュー済み
3. 重大指摘なし
4. user が merge / publish を明示
```

AI 同士で実装とレビューを回せるようにしても、最後の判断は人間に残します。

特に Zenn 記事では `published: true` にすると公開へ進みます。アプリ開発なら、push、release、migration、破壊的変更も同じです。

呼び出しを自動化するほど、止める条件も明示しておく必要があります。

## まとめ

Codex と Claude Code を相互に呼び出すハーネスを組んだことで、2つの AI をただ併用する状態から、作業契約つきで渡し合う状態に近づきました。

やったことは大きく3つです。

- Claude Code → Codex は、`codex-dev` で設計済みタスクを MCP 経由で実装委譲する
- Codex → Claude Code は、`invoke-claude-review.ps1` で review-only の CLI 呼び出しにする
- 依頼、結果、未確認事項は `CLAUDE_CODE_HANDOFF.md` に戻す

重要だったのは、相互呼び出しを完全自動の開発フローにしなかったことです。

実装する側、レビューする側、判断する人を分ける。AI 同士をつなぐほど、その境界をファイルとスクリプトに落とす必要がありました。

## 参考リンク

- [harness17/cross-agent-harness](https://github.com/harness17/cross-agent-harness) — 本記事で扱った共同開発ハーネス
- [CodexとClaude Codeの共同作業をcross-agent-harnessに切り出した](https://zenn.dev/harness/articles/cross-agent-harness-introduction) — ハーネス全体の導入記事
- [AI 2 台クロスレビューで技術記事の盲点を拾う](https://zenn.dev/harness/articles/ai-cross-review-handoff-workflow) — Zenn 記事レビューでの先行運用
- [harness17/zenn-articles](https://github.com/harness17/zenn-articles) — 記事管理リポジトリ
