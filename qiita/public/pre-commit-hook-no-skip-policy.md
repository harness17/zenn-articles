---
title: hookが落ちても--no-verifyで飛ばさず原因を直す運用にした
tags:
  - Git
  - pre-commit
  - 開発環境
  - AI
  - ClaudeCode
private: false
updated_at: '2026-06-02T22:00:28+09:00'
id: 3e7da11f59bba1bb8f17
organization_url_name: null
slide: false
ignorePublish: false
---

## 詰まったこと

記事リポジトリで Zenn / Qiita の下書きを増やしていると、公開前に直すべき問題がいくつか混ざります。

- 文体NG語が本文に残る
- `published: false` / `ignorePublish: true` の公開ゲートを崩す
- フォーマットやフロントマターが壊れる
- 守秘上出してはいけない情報が混ざる

こういう問題を hook や事前チェックで止める運用にすると、次に詰まるのは「hook が落ちたときに `--no-verify` で逃げたくなる」ことです。

`git commit --no-verify` は便利ですが、記事リポジトリでは危険でした。Zenn は `main` への push が公開トリガーになるため、壊れた記事や公開フラグの誤変更が混ざると、そのまま外へ出る可能性があります。

この記事では、1記事1トラブルとして「hook が落ちても skip せず原因を直す」運用に絞ります。

## 結論: hook失敗は3種類に分けて直す

自分の運用では、hook やコミット前チェックの失敗を次の3種類に分けます。

| 分類 | 例 | 対処 |
| --- | --- | --- |
| lint / 構文 | Markdown / JSON / YAML の構文崩れ | フォーマットか構文を直す |
| 文体チェック | NG語、AI的な締め文 | 別表現に直す |
| 公開ゲート | `published: true` や `ignorePublish: false` の誤変更 | フラグを戻し、公開指示があるか確認する |

ポイントは、落ちた hook を邪魔者として扱わないことです。hook は「公開前に見つけるための検知」なので、落ちたら分類して原因を消します。

## 実例: 保存時に文体NG語を警告する hook

このリポジトリでは、Claude Code 側の `.claude/settings.json` で `PostToolUse` hook を設定しています。

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/hooks/check-article-style.sh 2>/dev/null || true",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

hook 本体では、`articles/*.md` 以外を対象外にしてから、文体NG語を grep します。本文では検出語そのものを再掲せず、`writing-style.md` と同期している、という運用だけを書きます。

```bash
input=$(cat)

# file_path を抽出（tool_input から）
file=$(printf '%s' "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)

# articles/*.md でなければ何もしない
case "$file" in
  *articles/*.md|*articles\\*.md) ;;
  *) exit 0 ;;
esac
```

これは Git の `pre-commit` hook そのものではなく、保存時のチェックです。ただ、目的は同じです。コミット前に問題を見つけ、公開物へ混ざる前に直します。

Git 側の規約でも、`--no-verify` で pre-commit hook をスキップしない方針にしています。

```md
- `--no-verify` で pre-commit hook をスキップしない（hook が落ちたら原因を直す）
```

## 失敗例: 急いでいるとskipしたくなる

最初は、hook が落ちると「今は本文だけ見たいから後で直す」と考えがちでした。特に文体チェックは、ビルドエラーと違ってアプリが壊れるわけではありません。

しかし記事リポジトリでは、その考え方が危険でした。

たとえば、公開フラグを誤って変えたまま commit し、`main` に push すると Zenn 側の公開に進みます。文体NG語や守秘リスクも、公開後に気づくと修正コストが上がります。

「後で直す」は、公開トリガーを持つリポジトリでは弱い運用でした。落ちた時点で直す方が、結果として速く済みます。

## 対処パターン1: 文体チェックは語を消すのではなく文を直す

NG語にヒットしたとき、単に単語だけ削ると文章が不自然になります。次のように、事実ベースへ書き換えます。

```text
NG:
この仕組みはとても良い効果がありました。

OK:
この仕組みに変えたあと、起動時の通知連打がなくなりました。
```

文体チェックの目的は、文章を薄くすることではありません。過度な強調や曖昧な締めを避け、何が起きたかを具体的に書くことです。

## 対処パターン2: フロントマターは公開ゲートとして見る

記事の front matter は、単なるメタ情報ではなく公開ゲートです。

Zenn の下書きでは、次を維持します。

```yaml
published: false
```

Qiita の下書きでは、次を維持します。

```yaml
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: true
```

hook やレビューでここが落ちたら、文章の問題ではなく公開フローの問題として扱います。ユーザーが公開を明示していないなら、フラグを戻します。

## 対処パターン3: フォーマット失敗は機械的に直す

JSON や YAML の構文崩れは、本文の推敲とは別に扱います。原因がインデントやクォートなら、機械的に直してから再チェックします。

```powershell
# JSON の構文確認例
Get-Content -Raw .claude/settings.json | ConvertFrom-Json | Out-Null
Get-Content -Raw .codex/hooks.json | ConvertFrom-Json | Out-Null
```

フォーマットの問題を残したまま `--no-verify` で進めると、次のエージェントや次のセッションが原因調査から始まります。今見つけた人が直す方が、作業全体の待ち時間を減らせます。

## まとめ

- hook が落ちたときに `--no-verify` で飛ばすと、壊れた記事や公開フラグの誤変更が混ざる
- 失敗原因は lint / 文体チェック / 公開ゲートに分けると、直す順番が決めやすい
- 文体NG語は単語だけ削らず、体験や結果が分かる文に直す
- Zenn / Qiita の front matter は公開ゲートなので、ユーザーの明示があるまで下書き状態を維持する

hook は作業を止めるためではなく、公開前に直す場所を示すために置いています。落ちたら飛ばすのではなく、分類して原因を直す。この運用にしてから、公開前レビューで同じ種類の指摘を繰り返しにくくなりました。

## 参考リンク

- [harness17/zenn-articles](https://github.com/harness17/zenn-articles) - 本記事で扱った記事リポジトリ
- [Git Documentation - githooks](https://git-scm.com/docs/githooks)
- [Git Documentation - git commit](https://git-scm.com/docs/git-commit)
- [Codex用AGENTS.mdとClaude用CLAUDE.mdを分けて運用したメモ](https://qiita.com/harnesswinner/items/cb82e8caafa8daf52bcb)
