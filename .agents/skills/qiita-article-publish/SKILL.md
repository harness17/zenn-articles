---
name: qiita-article-publish
description: Qiita記事公開後の連動アクションを順に実行するスキル。`npm run qiita:publish` 案内、qiita-article-candidates 更新、URL確認、関連リポジトリ README更新案、Lapras確認予約までを案内する。「Qiita記事を公開した」「Qiitaに公開した」と言われたとき、または `/qiita-article-publish` で発動する。
---

# qiita-article-publish

記事を Qiita に公開した直後の連動アクションを案内・実行する。Lapras スコアと検索流入の両方を取りに行くのが目的。

## 起動条件

- ユーザーが「Qiita記事公開した」「Qiitaに公開済み」「ignorePublish 解除した」と言ったとき
- `/qiita-article-publish` で呼ばれたとき
- `qiita/public/<slug>.md` の `ignorePublish: false` でコミットされた直後

## 入力

- 公開した記事のファイルパス（`qiita/public/<slug>.md`）
- 公開URL（`https://qiita.com/harnesswinner/items/<id>`、Qiita CLI で初回 publish 時に発番）

## 実行ステップ

### 0. 公開コマンドの案内（未実行なら）

ユーザーが `ignorePublish: false` を立てただけで `npm run qiita:publish` を未実行の場合：

```powershell
npm run qiita:publish -- <slug>
```

を案内する。Zenn と違い、Qiita は GitHub 連携ではなく **CLI 経由でAPIに送信** する必要がある。`QIITA_TOKEN` 認証は `npx qiita --config qiita login` で済んでいる前提。

### 1. 公開記録の作成

`drafts/published-log.md`（無ければ作成）に追記。Qiita 用エントリは `媒体: Qiita` を明示する：

```markdown
## YYYY-MM-DD 公開（Qiita）
- 媒体: Qiita
- タイトル: <記事タイトル>
- URL: https://qiita.com/harnesswinner/items/<id>
- slug: <slug>
- テーマ系統: Chrome拡張 / Electron / ASP.NET Core / 等
- 文字数: XXXX
- 関連リポジトリ: youtube-schedule / DevNext / 等
- 元 Zenn 記事: <あれば slug>
- Lapras確認予定日: YYYY-MM-DD（公開から3〜7日後）
```

### 2. 候補管理表の更新

`drafts/qiita-article-candidates.md` を更新する。

- `既存 Qiita 公開記事` に公開日、slug、タイトル、元記事、URL を追加する
- `レビュー待ち` から該当行を削除する
- 候補表の該当行の `次の扱い` を `公開済み` にする
- 公開直後に公開URLへ直接アクセスし、HTTP 200 とタイトル一致を確認する
- 確認できなかった場合は `実公開未確認` として残し、後で再確認する

### 3. 関連リポジトリの README 更新案を提示

Codex.local.md の「個人開発リポジトリ」表で対応するリポジトリを特定し、README に追加すべき行を提案する：

```markdown
## 関連記事

- [<記事タイトル>](https://qiita.com/harnesswinner/items/<id>) (Qiita, YYYY-MM-DD)
```

既に Zenn 記事が同題材で載っている場合は、Qiita を追記する形にする。コミット・push までは本スキルでは行わない。

### 4. Lapras スコア確認のリマインド

公開から3〜7日後に以下を確認するよう案内：

| 確認項目 | 期待される変化 |
|---------|--------------|
| 技術力スコア | +0.02〜0.10（Zennより寄与は小さいが、本数が効く） |
| 記事スコア欄 | Qiita 記事が認識されるか |
| Qiita 側 LGTM / ストック | 検索流入の手応えを見る |

LAPRAS が Qiita を認識するまでにラグがある場合、再連携 or プロフィールURL確認を案内する。

### 5. 親プロジェクト連携の案内

非公開のキャリア管理プロジェクトの自己研鑽記録に以下を追記する案を提示：

```markdown
## 公開記事
- [<記事タイトル>](URL) - YYYY-MM-DD公開（Qiita）
```

実際の編集は親プロジェクトのセッションで行うため、本スキルは案内のみ。

### 6. 職経書の自己PR追記検討

- Zenn と Qiita 合算で **3記事目以降**：「Zenn / Qiita で技術記事を継続的に公開（合計X本）」を自己PR欄に追加検討
- 1〜2記事目：まだ追記しない

判断基準を提示してユーザーに確認を求める。

## 出力フォーマット

```
## Qiita公開後アクション

### 0. 公開コマンド
✅ npm run qiita:publish -- <slug> 実行済み / または未実行

### 1. 公開ログ追記
✅ drafts/published-log.md にエントリ追加（媒体: Qiita）

### 2. 候補管理表更新
✅ drafts/qiita-article-candidates.md の既存リスト追加 / レビュー待ち削除 / 候補状態更新
公開URL: 200 / 公開確認 または 実公開未確認

### 3. 関連リポジトリ README 更新案
以下を <リポジトリ名> の README.md に貼ってください：
[コードブロック]

### 4. Lapras 確認予定
📅 YYYY-MM-DD（公開から5日後）にチェック予定

### 5. 親プロジェクト連携
非公開のキャリア管理プロジェクトの自己研鑽記録に以下を追記：
[コードブロック]

### 6. 職経書追記
Zenn + Qiita 合算 X 記事目: 追記する / まだ見送る
```

## やらないこと

- 親プロジェクトリポジトリへの直接書き込み
- 別リポジトリ（DevNext 等）への直接コミット
- `npm run qiita:publish` の自動実行（QIITA_TOKEN 認証情報に触れるため、ユーザー手動実行を促す）

## 完了条件

- `drafts/published-log.md` に媒体: Qiita のエントリが追加された
- `drafts/qiita-article-candidates.md` の既存リスト・候補状態・公開URL確認結果が反映された
- README 更新案・親プロジェクト追記案・Lapras 確認日がユーザーに提示された
