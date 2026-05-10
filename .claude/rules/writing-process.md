# 執筆プロセス

体調最優先。1記事に2週間かけて良い。最初の1本を出すまでが一番大変、それ以降は楽になる。

## Phase 1: 準備（30分）

1. テーマ決定（候補A〜Gから1つ）
2. ターゲット読者を1文で書く（例：「SQL Server を実務で使う中堅エンジニア」）
3. drafts/<slug>.md に構成メモを開始

→ Claude Code に依頼するなら `/article-plan` を起動する。

## Phase 2: 構成（60分）

1. 見出し3〜5個を確定
2. 各見出しで「何を伝えるか」「どんな例（コード or 図）を出すか」を箇条書き
3. コード例の実装または既存コード（DevNext など）からの引用準備

## Phase 3: 執筆（4〜6時間）

1. articles/<slug>.md に本文を書く（フロントマターは `published: false`）
2. はじめに → 本論 → まとめ の順
3. 図表が必要な箇所は Mermaid または images/ に画像を置く

## Phase 4: 推敲（60分）

1. 作成者と別エージェントへの相互レビュー依頼を `CLAUDE_CODE_HANDOFF.md` に残す
2. `/article-review` を実行（文体ルール違反、必須要素、守秘義務、相互レビュー記録チェック）
3. 指摘を反映
4. ローカルプレビュー（`npx zenn preview`）で見た目確認

## Phase 5: 公開・拡散（30分）

1. 相互レビューの重大指摘が残っていないことを確認
2. ユーザーが公開を明示したら、フロントマターを `published: true` に変更してコミット
3. main に push → Zenn 自動反映
4. `/article-publish` を実行（README更新、Lapras確認予約、職経書追記検討）

## 推奨ペース

- Month 1: 候補A or B（SQL Server系）— 1記事
- Month 2: 候補C（ASP.NET Core 10）— 1記事
- Month 3: 候補E or F（個人開発系）— 1記事

3ヶ月で3記事を目標。1ヶ月1記事ペースで OK。
