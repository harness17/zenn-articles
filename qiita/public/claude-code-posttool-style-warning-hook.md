---
title: Claude CodeのPostToolUse hookで保存時に文体NG語を警告した
tags:
  - Bash
  - Markdown
  - 自動化
  - AI
  - ClaudeCode
private: false
updated_at: '2026-05-28T20:34:49+09:00'
id: 55e03ef8ce0ae81170ec
organization_url_name: null
slide: false
ignorePublish: false
---

## はじめに

技術記事を書いていると、公開前レビューで定型的な締め文や過度な強調表現を消す作業が発生します。

レビュー時にまとめて見つけても直せますが、保存時に気づける方が差し戻しが小さくなります。そこで Claude Code の `PostToolUse` hook で、記事ファイルを保存した直後に文体NG語を警告する仕組みにしました。

この記事では、`Write|Edit` の後に Bash スクリプトを実行し、対象が `articles/*.md` のときだけ grep する最小構成をまとめます。

## TL;DR / 結論コード

設定ファイルでは、`Write|Edit` の後にチェック用スクリプトを呼びます。

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

スクリプト側では、tool input から `file_path` を抜き、記事ファイルだけを対象にします。

```bash
input=$(cat)
file=$(printf '%s' "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)

case "$file" in
  *articles/*.md|*articles\\*.md) ;;
  *) exit 0 ;;
esac

[ -f "$file" ] || exit 0

pattern='NG_WORD_1|NG_WORD_2|NG_PHRASE_1|NG_PHRASE_2'
hits=$(grep -nE "$pattern" "$file" 2>/dev/null)
```

実コードでは、`NG_WORD_1` の部分にプロジェクトの文体ルールで禁止している語句を `|` 区切りで並べています。Qiita本文にはその語句自体を直接並べず、公開前チェックで誤検出されないようにしています。

## 何に詰まったか

最初は公開前レビューだけで十分だと思っていました。

しかし記事を何本も作ると、レビュー時に毎回同じ表現を探すことになります。文体NG語は内容の判断ではなく機械的に検出できます。人間や別エージェントのレビュー時間を、もっと技術説明や守秘リスクの確認に使いたい状態でした。

一方で、すべての Markdown に hook を走らせると邪魔になります。`README.md` や handoff には一時的なメモが入ることがあり、記事本文と同じ厳しさで警告するとノイズが増えます。

## 実装のポイント

### 対象ファイルを絞る

hook は `Write|Edit` 全体に対して発火します。そのため、スクリプトの先頭で `articles/*.md` だけに絞ります。

```bash
case "$file" in
  *articles/*.md|*articles\\*.md) ;;
  *) exit 0 ;;
esac
```

Windows と Unix 風パスの両方を想定し、スラッシュとバックスラッシュのどちらでも通すようにしました。

### 失敗しても編集を止めない

設定側では `2>/dev/null || true` を付けています。

```json
"command": "bash .claude/hooks/check-article-style.sh 2>/dev/null || true"
```

文体チェックは補助なので、grep や JSON 解析が失敗しただけで記事編集を止めるべきではありません。警告できるときだけ警告し、失敗時は黙って通す設計にしています。

### 警告は systemMessage にする

ヒットしたときだけ、Claude Code が読める JSON を返します。

```bash
escaped=$(printf '%s' "$hits" | sed 's/\\/\\\\/g; s/"/\\"/g' | awk '{printf "%s\\n", $0}')

printf '{"systemMessage":"[文体ルール違反語あり]\\n%s→ /article-review で全項目チェックするか、別表現に直してください。"}\n' "$escaped"
```

行番号を含めると、次の編集で直す場所が分かります。

## 注意点

この hook は公開前レビューの代わりにはなりません。

検出できるのは、あらかじめ列挙した文体NG語だけです。守秘義務、事実誤認、コードブロックの言語指定、Qiita / Zenn のフロントマターは別のレビューで確認する必要があります。

:::note warn
hook は「早めに気づく仕組み」であって、「公開可否を判断する仕組み」ではありません。公開前には別エージェントレビューと記事レビューのチェックリストを通します。
:::

また、NG語リストを `writing-style.md` とスクリプトの両方に持つとズレます。運用では、ルール変更時に hook の `pattern` も同時に確認することにしました。

## まとめ

保存時の文体警告は、小さい自動化ですが記事レビューのノイズを減らせました。

- `PostToolUse` で `Write|Edit` 後にスクリプトを実行する
- スクリプト側で `articles/*.md` に絞る
- 失敗しても編集を止めず、ヒット時だけ `systemMessage` を返す

人間や別エージェントのレビューは、機械で拾える表現ではなく、論理性と事実整合に使う方が効果的でした。

## 参考リンク

- [harness17/zenn-articles](https://github.com/harness17/zenn-articles) - 本記事で扱った記事リポジトリ
- [.claude/settings.json](https://github.com/harness17/zenn-articles/blob/main/.claude/settings.json) - Claude Code 側 hook 設定
- [.claude/hooks/check-article-style.sh](https://github.com/harness17/zenn-articles/blob/main/.claude/hooks/check-article-style.sh) - 文体チェックスクリプト
