# Zenn記事をリポジトリ管理して公開前レビューまで回した話

## メタ情報
- type: tech
- topics: [zenn, github, codex, claudecode, writing]
- 想定文字数: 3000〜4000字
- 想定執筆時間: 4〜5時間
- ステータス: 構成中
- 元候補: 候補Q「Zenn 記事をリポジトリ管理して公開前レビューまで自動化した話」

## 方針チェック

- OKパターン: 「記事を思いつきで書くと品質がぶれた」→ 候補、draft、review、published-log に分けた → 公開前チェックと Lapras 確認まで回せるようにした体験記事。
- NGに寄せない: 「Zenn CLI 入門」「Markdown の書き方」「AIで記事を書く方法」の網羅解説にはしない。
- 既存記事との差分:
  - `ai-cross-review-handoff-workflow.md`: AI 2台レビューの盲点検出が主題。
  - `codex-claude-skill-graph-worklog.md`: 設計判断を My-Skill-Graph に残すことが主題。
  - 本記事: Zenn 記事リポジトリのディレクトリ、ルール、skills、hooks、公開ログをつないだ運用設計が主題。

## 事実確認メモ

ローカル一次情報として次を確認済み。

- `README.md`: `articles/`、`drafts/`、`images/`、関連リポジトリ、`npx zenn preview` の運用を記載。
- `.claude/rules/topic-policy.md`: 「課題解決力ベース・体験記事優先」を明文化。
- `.claude/rules/zenn-workflow.md`: 新規記事、公開フロー、相互レビューゲート、公開後アクションを記載。
- `.claude/rules/cross-agent-review.md`: 作成者と別エージェントによるレビュー担当を定義。
- `.agents/skills/article-plan/SKILL.md`: 候補から `drafts/<slug>.md` に構成メモを作る手順。
- `.agents/skills/article-review/SKILL.md`: フロントマター、文体、必須要素、守秘義務、相互レビューを確認する手順。
- `.agents/skills/article-publish/SKILL.md`: 公開ログ、README更新案、Lapras確認、親プロジェクト連携を扱う手順。
- `.codex/hooks.json` と `.codex/hooks/check-article-style.sh`: `articles/*.md` 保存時に文体NG語を警告する PostToolUse hook。
- `drafts/published-log.md`: 公開日、URL、テーマ系統、文字数、Lapras確認予定日を記録。
- `drafts/article-candidates.md`: 候補リストと既存記事、Zenn実公開状態の対応を記録。

## 想定読者

Zenn 投稿を続けたいが、ネタ管理、公開前レビュー、公開後の確認が散らばって品質が安定しない個人開発者。

## 構成

### はじめに（250〜350字）
- 何を伝えるか: Zenn 記事を単発の Markdown ではなく、候補管理から公開後確認まで含む小さな運用リポジトリとして扱った話。
- 具体例: `articles/` と `drafts/` の役割、公開ログ、レビューゲートに触れる。
- 想定文字数: 300字

### 本論セクション1: 思いつきで書くと品質がぶれた
- 伝えること: 記事数を増やすほど、テーマ選定、事実確認、文体、公開後確認が人間の記憶だけでは管理しづらくなった。
- 具体例: 候補H〜Rのように、体験ベースで書けるものと保留するものを分けた話。
- 想定文字数: 600〜800字

### 本論セクション2: 候補、下書き、公開記事をディレクトリで分けた
- 伝えること: `drafts/` は構成と準備、`articles/` は Zenn 連携対象、`drafts/article-candidates.md` は候補と既存記事の対応、`drafts/published-log.md` は公開後の追跡にした。
- 具体例: README の構成説明、候補対応表、公開ログの記録項目。
- 想定文字数: 700〜900字

### 本論セクション3: ルールを分けて、記事ごとの判断を軽くした
- 伝えること: ルートの指示に全部を書かず、topic-policy / writing-style / zenn-workflow / privacy / fact-check に分けたことで、記事作成時に見る観点を固定した。
- 具体例: 「課題解決力ベース・体験記事優先」と「公開前に `published: true` にしない」ルール。
- 想定文字数: 700〜900字

### 本論セクション4: skills と hook でレビュー観点を作業に埋め込んだ
- 伝えること: `article-plan`、`article-review`、`article-publish` の3段階に分け、保存時 hook で文体NG語だけを軽く検出する。
- 具体例: `.agents/skills/article-review/SKILL.md` のチェック項目、`.codex/hooks/check-article-style.sh` のNG語検出。
- 想定文字数: 800〜1000字

### 本論セクション5: 公開して終わりにしないためにログを残した
- 伝えること: 公開後に README 更新案、Lapras確認予定日、親プロジェクト連携を残すことで、記事をポートフォリオ資産として扱えるようにした。
- 具体例: `drafts/published-log.md` の公開確認日と Lapras確認予定日。
- 想定文字数: 600〜800字

### まとめ（150〜250字）
- 要点3つ:
  - 記事リポジトリは Markdown 置き場ではなく、候補、レビュー、公開後確認をつなぐ作業台にできる。
  - AIを使うほど、体験記事の軸と事実確認ルールを先に固定したほうが品質が安定する。
  - 公開ログまで残すと、Zenn記事を就職活動やポートフォリオ説明に再利用しやすくなる。

## コード例の準備状況

| セクション | コード言語 | 出典 | 準備状況 |
| --- | --- | --- | --- |
| ディレクトリ構成 | text | `README.md` / `AGENTS.md` | 確認済み |
| 新規記事作成コマンド | powershell | `.claude/rules/zenn-workflow.md` | 確認済み |
| article-review のチェック項目 | markdown | `.agents/skills/article-review/SKILL.md` | 抜粋範囲を選ぶ |
| 文体 hook | bash | `.codex/hooks/check-article-style.sh` | 抜粋範囲を選ぶ |
| 候補対応表 | markdown | `drafts/article-candidates.md` | 抜粋範囲を選ぶ |
| 公開ログの形式 | markdown | `drafts/published-log.md` | 抜粋範囲を選ぶ |

## 参考リンク候補

- [Zenn CLI](https://zenn.dev/zenn/articles/zenn-cli-guide)
- [GitHub - harness17/zenn-articles](https://github.com/harness17/zenn-articles)
- 先行記事: `AI 2 台クロスレビューで技術記事の盲点を拾う`
- 先行記事: `AIとの設計判断をMy-Skill-Graphに残して再利用する`
- 先行記事: `Claude Code運用を数ヶ月で見直してrulesとskillsに分けた話`

## 次のアクション

- 本文化する場合は、`articles/zenn-article-repo-workflow.md` を `published: false` で作成する。
- 既存AI協調記事と重複しないよう、本文では「レビュー担当の分離」そのものよりも、記事リポジトリ全体の運用設計に寄せる。
- 公開前には `/article-review` 相当で文体、守秘義務、GitHubリンク、5行以上の実コード、相互レビューゲートを確認する。
