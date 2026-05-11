# Schedule と ScheduleEntry を分けるのをやめた理由

## メタ情報

- type: tech
- topics: [aspnetcore, csharp, mvc, design, database]
- 想定文字数: 3000〜4000字
- 想定執筆時間: 5〜6時間
- ステータス: 初稿作成済み・公開前レビュー待ち
- 想定 slug: `phycock-schedule-entry-consolidation`

## 想定読者

ASP.NET Core MVC の個人開発や業務アプリで、予定・履歴・入力記録のテーブル分割に迷っているエンジニア。

## 詰まったこと

当初は汎用的な `Schedule` と、実際の入力単位である `ScheduleEntry` を分けて扱っていた。

ただ、アプリで本当に扱いたいのは「抽象的な予定」ではなく、日付・区分・種別・メモなどを持つ具体的な予定入力だった。汎用 `Schedule` を残すほど、Controller / Service / View / Test の責務が分散し、修正時に見る場所が増えていた。

## 判断軸

- 汎用化した名前が、実際のユースケースを説明できているか
- 1画面の操作に対して、更新すべきモデルが増えすぎていないか
- 将来の拡張可能性より、現在の入力・表示・検証の一貫性を優先すべき場面か
- テストで守りたい振る舞いが、どちらのモデルに属するか明確か

## 構成

### はじめに（250〜350字）

- ASP.NET Core MVC で作っている個人開発アプリで、予定入力のモデルを見直した話として始める
- `Schedule` と `ScheduleEntry` を分けていたが、最終的に `ScheduleEntry` に寄せたことを書く
- 医療・支援・体調の詳細には踏み込まず、「予定入力を扱うアプリ」として一般化する

### 本論セクション1: 最初は汎用 Schedule を置いていた（600〜800字）

- 伝えること: 汎用的な名前のモデルを置くと、最初は拡張しやすそうに見える
- 具体例: `Schedule` と `ScheduleEntry` の責務を表で比較する
- 例:

| モデル | 期待していた責務 | 実際に持っていた責務 |
|--------|------------------|----------------------|
| `Schedule` | 予定全体の概念を表す | 画面や入力処理から直接使う場面が少なかった |
| `ScheduleEntry` | 予定の入力単位を表す | 日付、区分、種別、表示色、検証の中心になっていた |

### 本論セクション2: 分けたことで修正範囲が広がった（700〜900字）

- 伝えること: モデルを分けると、DB・Controller・Service・View・Test の変更箇所も分かれる
- 具体例: 予定作成・編集・カレンダー表示で、どの層が `ScheduleEntry` を中心に動いていたかを書く
- コード候補: `ScheduleEntryFormViewModel`、カレンダー DTO、Service の作成処理

### 本論セクション3: ScheduleEntry に寄せると判断した理由（800〜1000字）

- 伝えること: 抽象概念を残すより、実際の入力単位を集約の中心にしたほうが保守しやすかった
- 具体例: `ScheduleEntry` に日付・区分・業務種別・メモ・表示用情報を寄せる
- 判断軸:
  - 画面から作成される単位と DB に保存する単位が一致する
  - 検証ルールを `ScheduleEntry` 起点で説明できる
  - カレンダー表示 DTO への変換元が明確になる

### 本論セクション4: 削除時に見たポイント（600〜800字）

- 伝えること: テーブル削除はモデル削除だけでは終わらない
- 具体例: migration、参照している Controller / Service / View / Test、seed data を確認する
- コード候補:

```csharp
public class ScheduleEntryFormViewModel
{
    public DateOnly Date { get; set; }
    public ScheduleSession Session { get; set; }
    public EventCategory Category { get; set; }
    public WorkType? WorkType { get; set; }
    public string? Memo { get; set; }
}
```

### 本論セクション5: 汎用化を捨てるときの注意点（500〜700字）

- 伝えること: 汎用モデルを消す判断は、将来拡張を完全に捨てることではない
- 具体例: 今後別種の予定が増えるなら、その時点で `ScheduleEntry` の分類や別集約を検討する
- 注意点: 「今は使わない抽象化」を残すコストと、「後で必要になったら分ける」コストを比べる

### まとめ（200〜300字）

- 汎用的な `Schedule` は、実際の入力単位とズレると保守コストになる
- 今回は `ScheduleEntry` が画面・DB・検証・表示の中心だったため、そこに集約した
- テーブルやモデルの分割は、名前のきれいさより変更時に見る場所の少なさで判断するとよい

## コード例の準備状況

| セクション | コード言語 | 出典 | 準備状況 |
|------------|------------|------|----------|
| `Schedule` / `ScheduleEntry` の責務比較 | markdown table | Phycock の設計履歴から一般化 | 未着手 |
| 入力 ViewModel | csharp | Phycock から引用または簡略化 | 未着手 |
| カレンダー DTO 変換 | csharp | 既存 FullCalendar 記事と接続 | 未着手 |
| migration / 削除対象一覧 | csharp / text | Phycock の変更差分から抽出 | 未着手 |
| Service テスト | csharp | 作成・編集・表示の回帰テスト | 未着手 |

## 参考リンク候補

- DevNext: https://github.com/harness17/DevNext
- Phycock: 公開可否とリンク先を執筆前に確認する
- ASP.NET Core MVC 公式ドキュメント
- Entity Framework Core migrations 公式ドキュメント
- 既存記事: `articles/fullcalendar-event-color-rendering.md`

## 守秘義務・個人情報リスク

- アプリの利用文脈は「予定入力を扱う個人開発アプリ」程度に一般化する
- 支援機関名、通所先、個人の体調記録の詳細は書かない
- サンプルコードは実データではなく、抽象化した enum / memo / date を使う

## 次アクション

1. Phycock 側の実コードから、`ScheduleEntryFormViewModel`、Service、migration、テストを確認する
2. 記事本文を `articles/phycock-schedule-entry-consolidation.md` に `published: false` で作成する
3. 本文化後に ClaudeCode へ相互レビュー依頼を handoff に残す
