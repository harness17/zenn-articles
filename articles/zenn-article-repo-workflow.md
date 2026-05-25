---
title: "Zenn記事をリポジトリ管理して公開前レビューまで回した話"
emoji: "📝"
type: "tech"
topics: ["zenn", "github", "codex", "claudecode", "writing"]
published: false
---

## はじめに

Zenn記事を書き始めたときは、Markdownを置いて公開できれば十分だと思っていました。ところが記事数を増やすと、テーマ候補、下書き、公開前レビュー、公開後の確認予定が別々の場所に散らばり、どの記事がどの状態なのかを思い出すところから始まるようになりました。

この記事では、Zenn記事を単なるMarkdown置き場ではなく、小さな運用リポジトリとして扱うようにした話を書きます。対象読者は、Zenn投稿を続けたいが、ネタ管理や公開前チェックが人間の記憶に寄りすぎている個人開発者です。

実例として使っているリポジトリは、Zenn記事を管理している [harness17/zenn-articles](https://github.com/harness17/zenn-articles) です。

## 思いつきで書くと品質がぶれた

最初に困ったのは、記事の品質より前に「何を書くべきか」がぶれることでした。

たとえば、個人開発で詰まった経験はいくつかあります。YouTube Data APIのクォータ枯渇、未署名ElectronアプリのSmartScreen警告、ASP.NET Core MVCの設計判断、AIコーディングエージェントの運用改善などです。どれも記事にはできますが、思いついた順に書くと、体験記事としての軸が弱いものまで混ざります。

そこで、候補を `drafts/article-candidates.md` に集め、状態を分けることにしました。単にタイトル案を並べるのではなく、候補ごとに「公開済み」「下書きあり」「未着手」「保留」を持たせています。

```markdown
| 候補 | 元テーマ | 状態 | 対応記事・下書き | 次の扱い |
| --- | --- | --- | --- | --- |
| H | YouTube Data API のクォータ枯渇と戦った話 | 公開済み | `articles/youtube-data-api-rss-quota-reduction.md` | 追加で書くなら別切り口にする |
| Q | Zenn 記事をリポジトリ管理して公開前レビューまで自動化した話 | 下書きあり | `drafts/zenn-article-repo-workflow.md` | 次に本文化する候補 |
| R | Electron 個人開発アプリを公開した後に必要だった運用メモ | 一部カバー | `articles/electron-smartscreen-oss-distribution.md` / `articles/youtom-introduction.md` | README / Releases / 署名方針の運用に絞れば別記事化可能 |
```

ここで重要だったのは、保留を明示したことです。書けそうな技術テーマでも、一次情報や失敗例が薄いものは、無理に記事化しないようにしました。記事数を増やすために網羅的な解説へ寄せると、自分の体験として説明できる強さが落ちます。

## 下書きと公開記事を分けた

次に整理したのは、ディレクトリの役割です。

このリポジトリでは、Zennと連携する公開記事を `articles/` に置き、構成メモや候補管理は `drafts/` に置いています。Zenn CLIの都合だけで分けているのではなく、作業の段階を分けるためです。

```text
技術記事/
├── articles/          # 公開記事（zenn-cli が管理）
├── books/             # Zenn の本
├── drafts/            # 公開前の下書き・構成メモ
├── images/            # 記事用画像
├── .agents/skills/    # Codex 側の記事作成スキル
├── .claude/rules/     # Claude Code 側の執筆ルール
└── .codex/hooks.json  # Codex 側 hook 設定
```

`drafts/` には、本文の手前にあるものを置きます。たとえば、構成案、コード例の準備状況、参考リンク候補、公開ログです。一方で `articles/` には、Zennに渡せる形式の記事だけを置きます。

この分離を入れる前は、「まだ構成中なのか」「公開してよい記事なのか」「公開後に確認が必要なのか」が混ざっていました。今は、完成前の思考は `drafts/`、Zennに見せる成果物は `articles/`、公開後の追跡は `drafts/published-log.md` という分担にしています。

## ルールを分けて判断を軽くした

記事作成で毎回迷う観点も、ファイルに分けました。

ルートの指示ファイルにすべてを書くと、記事を書くたびに長いルールを読み直すことになります。そこで、テーマ選定、文体、公開フロー、守秘義務、事実確認を別ファイルにしました。

```text
.claude/rules/
├── topic-policy.md
├── writing-style.md
├── zenn-workflow.md
├── article-requirements.md
├── privacy.md
└── article-fact-check.md
```

特に効いたのは、テーマ選定方針を独立させたことです。このリポジトリでは「実際に詰まって、自分で考えて、こう解決した」という体験ベースの記事を優先しています。これを先に決めたことで、「便利なTips集」や「入門記事」に寄りそうになったとき、候補段階で止めやすくなりました。

事実確認ルールも分けています。個人開発リポジトリの実コードに言及する記事では、中心主張をファイル全体や依存関係で確認してから書く、というルールです。以前、実装差分を扱う記事で中心主張を組み直すことになったため、執筆前の確認項目として固定しました。

## skillsとhookでレビュー観点を作業に埋め込んだ

ルールを置くだけでは、作業中に見落とします。そのため、Codex側には記事作成用のskillを分けて置きました。

```text
.agents/skills/
├── article-plan/
├── article-review/
└── article-publish/
```

`article-plan` は候補から構成メモを作る役割です。`article-review` は公開前にフロントマター、文体、必須要素、守秘義務、相互レビューを確認します。`article-publish` は公開後にREADME更新案、Lapras確認予定、公開ログを扱います。

保存時の軽いチェックにはhookを使っています。たとえば `articles/*.md` を保存したとき、文体ルールで避けたい語が入っていないかだけを検出します。

```bash
# articles/*.md でなければ何もしない
case "$file" in
  *articles/*.md|*articles\\*.md) ;;
  *) exit 0 ;;
esac

# 実ファイルが無ければ何もしない（Edit 直前でファイルが消えているケース対応）
[ -f "$file" ] || exit 0

# NG 語パターン（writing-style.md と同期）
pattern='...'

hits=$(grep -nE "$pattern" "$file" 2>/dev/null)
[ -z "$hits" ] && exit 0
```

hookで全部を判定しようとはしていません。保存時に重いレビューが走ると、執筆の流れが止まります。そこで、機械的に見つけやすく、修正コストが低い文体だけをhookに寄せました。構成や事実確認は、公開前レビューとして別に見るようにしています。

## 公開して終わりにしない

記事を書き溜める目的は、公開本数を増やすことだけではありません。自分の場合は、Laprasの技術力スコアや就職選考での説明材料にもつなげたいので、公開後の状態も残しています。

`drafts/published-log.md` には、URL、テーマ系統、文字数、関連リポジトリ、想定読者、Lapras確認予定日を書きます。Zennの実サイトで200を返しているかも、ローカルの `published: true` とは分けて記録しています。

```markdown
### YouTube Data API のクォータ枯渇を RSS で99%削減した話

- URL: https://zenn.dev/harness/articles/youtube-data-api-rss-quota-reduction
- テーマ系統: 個人開発 / API クォータ設計
- 文字数: 約4,500字
- 関連リポジトリ: [youtube-schedule](https://github.com/harness17/youtube-schedule)
- 想定読者: 個人開発で外部 API を使うエンジニア、YouTube Data API を扱う人
- Lapras確認予定日: 2026-05-16
```

このログがあると、後から「どの記事がどの技術領域を示しているか」を説明しやすくなります。公開した記事を単発のアウトプットで終わらせず、ポートフォリオや職務経歴書の材料として再利用できます。

:::message
`published: true` にするのは、相互レビューと公開指示がそろってからにしています。Zenn連携リポジトリでは、mainにpushした時点で公開に進むため、下書きストックでは `published: false` を維持します。
:::

## まとめ

Zenn記事リポジトリは、Markdownを置くだけの場所ではなく、候補管理、下書き、レビュー、公開後確認をつなぐ作業台にできます。

自分の場合は、`drafts/article-candidates.md` で候補と状態を管理し、`articles/` にはZenn形式の記事を置き、ルールとskillでレビュー観点を分けました。公開後は `drafts/published-log.md` に残すことで、記事をポートフォリオ資産として扱いやすくしています。

次に同じ運用を整えるなら、最初から大きな仕組みにする必要はありません。まずは候補表、公開前チェック、公開ログの3つだけでも、記事を書くたびに思い出す負荷を減らせます。

## 参考リンク

- [harness17/zenn-articles](https://github.com/harness17/zenn-articles): この記事で扱ったZenn記事管理リポジトリ
- [Zenn CLI](https://zenn.dev/zenn/articles/zenn-cli-guide): Zenn公式のCLI利用ガイド
- [AI 2 台クロスレビューで技術記事の盲点を拾う](https://zenn.dev/harness/articles/ai-cross-review-handoff-workflow): 相互レビュー運用に寄せた別記事
- [AIとの設計判断をMy-Skill-Graphに残して再利用する](https://zenn.dev/harness/articles/codex-claude-skill-graph-worklog): 設計判断の永続化に寄せた別記事
