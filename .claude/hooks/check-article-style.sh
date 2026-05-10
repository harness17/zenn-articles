#!/usr/bin/env bash
# articles/*.md 保存時に文体ルール違反語を検出する PostToolUse hook
# stdin: tool input/response JSON
# stdout: 検出時のみ {systemMessage: "..."} を返す

input=$(cat)

# file_path を抽出（tool_input から）
file=$(printf '%s' "$input" | sed -n 's/.*"file_path"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)

# articles/*.md でなければ何もしない
case "$file" in
  *articles/*.md|*articles\\*.md) ;;
  *) exit 0 ;;
esac

# 実ファイルが無ければ何もしない（Edit 直前でファイルが消えているケース対応）
[ -f "$file" ] || exit 0

# NG 語パターン（writing-style.md と同期）
pattern='素晴らしい|驚くべき|画期的|魔法のように|いかがでしたでしょうか|いかがだったでしょうか|ぜひ参考にしてみてください|ご参考になれば幸いです|皆さんも試してみてください'

hits=$(grep -nE "$pattern" "$file" 2>/dev/null)
[ -z "$hits" ] && exit 0

# JSON エスケープ用に特殊文字を処理してから systemMessage を組み立てる
escaped=$(printf '%s' "$hits" | sed 's/\\/\\\\/g; s/"/\\"/g' | awk '{printf "%s\\n", $0}')

printf '{"systemMessage":"[文体ルール違反語あり]\\n%s→ /article-review で全項目チェックするか、別表現に直してください。"}\n' "$escaped"
