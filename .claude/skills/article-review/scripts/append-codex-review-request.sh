#!/usr/bin/env bash
# Codex への相互レビュー依頼テンプレを CLAUDE_CODE_HANDOFF.md に自動追記する。
# article-review スキルのレビューコメント対応モードから呼ばれる。
# 使い方: bash append-codex-review-request.sh <記事ファイル名>
set -euo pipefail

ARTICLE="${1:?usage: append-codex-review-request.sh <article-filename>}"
HANDOFF="CLAUDE_CODE_HANDOFF.md"
DATE="$(date +%Y-%m-%d)"

if [ ! -f "$HANDOFF" ]; then
  echo "エラー: $HANDOFF が見つかりません。リポジトリルートで実行してください。" >&2
  exit 1
fi

if [ ! -f "articles/${ARTICLE}" ]; then
  echo "エラー: articles/${ARTICLE} が見つかりません。" >&2
  exit 1
fi

cat >> "$HANDOFF" <<EOF

## ${DATE} ClaudeCode 追記: ${ARTICLE} Codex レビュー依頼（レビューコメント対応後）

- 対象ファイル: \`articles/${ARTICLE}\`
- 主編集者: ClaudeCode（外部レビューコメント対応の本文修正）
- レビュー担当: Codex
- レビュー観点（外部レビューコメント対応後の再レビュー）:
  - 元コメント要点: <TODO: LAPRAS / Zenn AI / ユーザーコメントの要点>
  - 反映差分: <TODO: 本文に反映した修正の要約>
  - 未反映: <TODO: 反映しなかった指摘と理由>
  - 修正後の確認結果: <TODO: 文体NG語スキャン・git diff など実施済みチェックの結果>
  - Codex に確認してほしいこと: 追記がコメント対応の範囲に収まり本文の流れを崩していないか／文体NG語・守秘・事実整合に問題がないか
- 触ってよい範囲: 対象記事のみ
- \`published\` の変更・再 push はユーザー指示に従う
EOF

echo "Codex レビュー依頼テンプレを ${HANDOFF} に追記しました。<TODO> を Edit で埋めてください。"
