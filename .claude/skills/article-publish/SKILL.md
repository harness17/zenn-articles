---
name: article-publish
description: 記事公開後の連動アクションを順に実行するスキル。GitHub README更新、Lapras確認の予約、職経書追記検討までを案内する。「記事を公開した」「Zennに公開した」「公開後の手続きを」と言われたとき、または `/article-publish` で発動する。
---

# article-publish

記事を Zenn に公開した直後の連動アクションを案内・実行する。Lapras スコア向上を最大化することが目的。

## 起動条件

- ユーザーが「記事公開した」「Zennに公開済み」「公開した後何すればいい」と言ったとき
- `/article-publish` で呼ばれたとき
- 記事フロントマターが `published: true` でコミットされた直後

## 入力

- 公開した記事のファイルパス（articles/<slug>.md）
- 公開URL（Zenn 上の記事URL、GitHub 連携で自動生成される）

## 実行ステップ

### 1. 公開記録の作成

`drafts/published-log.md`（無ければ作成）に追記：

```markdown
## YYYY-MM-DD 公開
- タイトル: <記事タイトル>
- URL: https://zenn.dev/harness17/articles/<slug>
- テーマ系統: SQL Server / ASP.NET Core 10 / 個人開発 のいずれか
- 文字数: XXXX
- 関連リポジトリ: DevNext / youtube-schedule / 等
- Lapras確認予定日: YYYY-MM-DD（公開から3〜7日後）
```

### 2. 関連リポジトリの README 更新案を提示

CLAUDE.local.md の「個人開発リポジトリ」表で対応するリポジトリを特定し、README に追加すべき行を提案する：

```markdown
## 関連記事

- [<記事タイトル>](https://zenn.dev/harness17/articles/<slug>) (YYYY-MM-DD)
```

実際の更新は別リポジトリで行うため、ユーザーに「DevNext リポを開いて貼ってください」と案内する。コミット・push までは本スキルでは行わない。

### 3. Lapras スコア確認のリマインド

公開から3〜7日後に以下を確認するよう案内：

| 確認項目 | 期待される変化 |
|---------|--------------|
| 技術力スコア | +0.05〜0.15（記事1本で計算開始） |
| 市場価値スコア | +0.02〜0.05 |
| 記事スコア欄 | 0.00 → 1.0+（計算開始のサイン） |

スクリーンショットを残すよう推奨（職経書の自己PRエビデンスになる）。

### 4. 親プロジェクト連携の案内

`F:/Dropbox/Job-hunting/CLAUDE_CODE_HANDOFF.md` の自己研鑽セクションに以下を追記する案を提示：

```markdown
## 公開記事
- [<記事タイトル>](URL) - YYYY-MM-DD公開
```

実際の編集は親プロジェクトのセッションで行うため、本スキルは案内のみ。

### 5. 職経書の自己PR追記検討

- 1記事目：まだ追記しない（記事数を貯めてから）
- 2記事目以降：「Zenn で技術記事を継続的に公開（X本）」を自己PR欄に追加検討

判断基準を提示してユーザーに確認を求める。

## 出力フォーマット

```
## 公開後アクション

### 1. 公開ログ追記
✅ drafts/published-log.md にエントリ追加

### 2. 関連リポジトリ README 更新案
以下を DevNext の README.md に貼ってください：
[コードブロック]

### 3. Lapras 確認予定
📅 YYYY-MM-DD（公開から5日後）にチェック予定
- 技術力スコア / 市場価値スコア / 記事スコア欄を確認
- スクリーンショット保存推奨

### 4. 親プロジェクト連携
F:/Dropbox/Job-hunting/CLAUDE_CODE_HANDOFF.md の自己研鑽セクションに以下を追記：
[コードブロック]

### 5. 職経書追記
今回（X記事目）: 追記する / まだ見送る
```

## やらないこと

- 親プロジェクトリポジトリへの直接書き込み（このプロジェクトは記事執筆に特化）
- DevNext 等の別リポジトリへの直接コミット
- Zenn API への直接操作（GitHub 連携で自動公開される前提）

## 完了条件

- `drafts/published-log.md` にエントリが追加された
- README 更新案・親プロジェクト追記案・Lapras 確認日がユーザーに提示された
