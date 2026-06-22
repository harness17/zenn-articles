---
title: AIにマイグレーションを書かせる前に「後から変えにくい4項目」を先に決める
tags:
  - EntityFramework
  - 設計
  - Database
  - AI
  - ClaudeCode
private: false
updated_at: '2026-06-20T19:49:45+09:00'
id: d17e2e9ce8f782ad61e9
organization_url_name: null
slide: false
ignorePublish: false
---

## 詰まったこと

AI コーディングエージェントに「このエンティティのテーブルを作って」と頼むと、マイグレーションをすぐ生成してくれます。ところが、生成されたスキーマには **後から変更コストが極めて高い決定** が黙って含まれていました。

- ユーザーデータのテーブルなのに物理削除（`IsDeleted` フラグ無し）で生成された
- 主キーが `long` 自動採番で、外部公開する ID にそのまま使われていた
- `DateTime` がローカル時刻保存で、タイムゾーンの扱いがバラバラ
- 必須項目が `NULL` 許容で生成され、後からデータが入った状態で `NOT NULL` 化に苦労した

コードのバグは後から直せますが、**データ構造の決定は本番にデータが入った後だと変更が困難** です。論理削除へ後付け移行する、ID 型を変える、全レコードのタイムゾーンを補正する——どれも既存データの移行を伴い、コードを直すのとはコストの桁が違います。

## 結論: マイグレーション生成の前に4項目を人間が決める

AI にスキーマを生成させる前に、次の4項目だけは人間が先に確定させる、というゲートを設けました。

| 決定事項 | 内容 | 既定の選び方 |
| --- | --- | --- |
| 削除方式 | 物理削除 or 論理削除（`IsDeleted` / `DeletedAt`） | ユーザーデータは論理削除 |
| ID 型 | `long` 自動採番 / `Guid` / 複合キー | 外部公開する ID は `Guid` |
| タイムゾーン | UTC 保存 or ローカル時刻 | 原則 UTC 保存・表示時に変換 |
| Null 許容 | 各カラムの Nullable 要否 | 必須項目は `NOT NULL` |

この4項目を決めてからプロンプトに含めると、AI は迷わず意図どおりのスキーマを出します。

## プロンプトに4項目を渡す

「テーブル作って」ではなく、4項目を明示して依頼します。

```
このエンティティのマイグレーションを書いてください。
データ設計の前提:
- 削除方式: 論理削除（IsDeleted bool + DeletedAt DateTime?）
- ID 型: Guid（外部公開するため）
- 日時: UTC で保存（DateTimeKind.Utc）
- Null 許容: Title / UserId は NOT NULL、Note は NULL 可
```

生成結果はこうなります。

```csharp
public class Memo
{
    public Guid Id { get; set; }                 // ID 型: Guid
    public Guid UserId { get; set; }             // NOT NULL
    public string Title { get; set; } = "";      // NOT NULL
    public string? Note { get; set; }            // NULL 可
    public DateTime CreatedAtUtc { get; set; }   // UTC 保存
    public bool IsDeleted { get; set; }          // 論理削除
    public DateTime? DeletedAtUtc { get; set; }
}
```

## 生成後はレビューゲートを通す

AI が出したスキーマは、マイグレーションを実行する前に必ず人間がレビューします。チェック項目はこの4つを軸にします。

- 論理削除が必要なテーブルに `IsDeleted` / `DeletedAt` があるか
- 外部公開する ID が推測可能な連番になっていないか
- `DateTime` が UTC 保存に揃っているか（`DateTimeKind.Unspecified` の混入がないか）
- 必須カラムが `NOT NULL` になっているか

特に「既存テーブルにカラムを追加する」変更では、既存データに対するデフォルト値（`NULL` 追加時の扱い）と、アプリ側の既存クエリへの影響を確認してから適用します。

## 捨てた選択肢: 生成してから直す

最初は「とりあえず AI に生成させて、おかしければ後で直す」でやっていました。これは却下しました。マイグレーションは適用するとスキーマ履歴が積み上がり、本番にデータが入ると後戻りが効きません。「後で直せばいい」が通用しないのがデータ構造の決定なので、**生成より前に決める** 順序にしたのが要点です。

## まとめ

- AI が生成するスキーマには、削除方式・ID 型・TZ・Null 許容という「後から変えにくい4項目」が黙って含まれる
- この4項目だけは、マイグレーション生成の前に人間が確定させる
- 4項目をプロンプトに明示し、生成後もこの4軸でレビューゲートを通してから適用する
- 「生成してから直す」は、データ構造の決定には通用しない

このゲートは個人開発のコーディングルール（[zenn-articles リポジトリ](https://github.com/harness17/zenn-articles) などの `rules/` で運用）に「データ設計レビュー」として記録し、エンティティを新規作成するたびに参照しています。

## 参考リンク

- [EF Core — Migrations Overview](https://learn.microsoft.com/ja-jp/ef/core/managing-schemas/migrations/)
- [EF Core — DateTime と UTC の扱い](https://learn.microsoft.com/ja-jp/ef/core/modeling/value-conversions)
