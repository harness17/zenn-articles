---
title: インデックスを貼ったのにScanされていた — WHERE句の関数がインデックスを殺す話
tags:
  - SQL
  - SQLServer
  - Database
  - パフォーマンス
  - インデックス
private: false
updated_at: '2026-06-13T19:36:50+09:00'
id: 7f8c787b4383f2d4db80
organization_url_name: null
slide: false
ignorePublish: false
---

## 何が起きたか

日付カラム `CreatedAt` にインデックスを貼った。特定の年月のデータだけ取得するクエリを書いた。

```sql
-- インデックスあり
CREATE INDEX IX_Orders_CreatedAt ON Orders (CreatedAt);

-- 年月で絞り込み
SELECT * FROM Orders
WHERE YEAR(CreatedAt) = 2025 AND MONTH(CreatedAt) = 6;
```

実行計画を見ると **Index Scan**（全行走査）だった。インデックスを貼ったはずなのに Seek（ピンポイント検索）にならない。

## 原因: SARGable でないクエリ

SARGable とは **Search ARGument ABLE** の略で、「インデックスの検索引数として使える」という意味。WHERE 句でカラムに関数を適用すると、SQL Server はインデックスのソート順を利用できなくなる。

```
インデックスの並び順:
2025-05-31 23:59:59
2025-06-01 00:00:00  ← ここから探したい
2025-06-15 08:30:00
2025-06-30 23:59:59
2025-07-01 00:00:00

YEAR(CreatedAt) = 2025 AND MONTH(CreatedAt) = 6 を適用すると:
→ 各行に関数を適用してから比較する
→ インデックスの並び順が使えない
→ 全行スキャン
```

### よくある NG パターン

```sql
-- ❌ カラムに関数を適用（Index Scan になりやすい）
WHERE YEAR(CreatedAt) = 2025
WHERE MONTH(CreatedAt) = 6
WHERE LEFT(UserName, 3) = 'ABC'
WHERE Price + 100 > 500
WHERE ISNULL(DeletedAt, '9999-12-31') > GETDATE()
```

共通点は **カラム側を加工している** こと。インデックスは「カラムの元の値」でソートされているため、加工後の値では検索できない。

なお `CONVERT(DATE, CreatedAt) = '2025-06-15'` は、SQL Server のバージョンによってはオプティマイザが内部的に範囲条件に書き換えて Index Seek になる場合がある。確実に Scan になるのは `YEAR()` や `MONTH()` のように結果の型が元の並び順と無関係な関数。

## 再現と確認

架空のテーブルで確認する。

```sql
-- 確認用テーブル
CREATE TABLE Orders (
    Id INT IDENTITY PRIMARY KEY,
    CreatedAt DATETIME2 NOT NULL,
    Amount DECIMAL(10,2)
);

CREATE INDEX IX_Orders_CreatedAt ON Orders (CreatedAt);

-- 10万件のテストデータ（2025年1月〜12月にランダム分布）
INSERT INTO Orders (CreatedAt, Amount)
SELECT TOP(100000)
    DATEADD(MINUTE, ABS(CHECKSUM(NEWID())) % 525600, '2025-01-01'),
    CAST(ABS(CHECKSUM(NEWID())) % 10000 AS DECIMAL(10,2)) / 100
FROM sys.all_objects a CROSS JOIN sys.all_objects b;
```

実行計画と IO 統計を比較する。

```sql
SET STATISTICS IO ON;

-- ❌ NG: Index Scan（カラムに関数を適用）
SELECT * FROM Orders
WHERE YEAR(CreatedAt) = 2025 AND MONTH(CreatedAt) = 6;
-- logical reads: 数百（全行走査、件数やページサイズで変動）

-- ✅ OK: Index Seek（範囲指定）
SELECT * FROM Orders
WHERE CreatedAt >= '2025-06-01' AND CreatedAt < '2025-07-01';
-- logical reads: 数ページ〜数十ページ（該当月のデータだけ読む）
```

SSMS で「実際の実行プランを含める」を有効にして実行すると、NG パターンは `Index Scan`、OK パターンは `Index Seek` のオペレーターが確認できる。logical reads の差は環境（データ量・ページサイズ）で変わるが、`YEAR()` / `MONTH()` での Scan と範囲指定での Seek の違いは再現する。

## 解決: カラム側を加工しない書き方

### 年・月の絞り込み

```sql
-- ❌ NG
WHERE YEAR(CreatedAt) = 2025 AND MONTH(CreatedAt) = 6

-- ✅ OK: 範囲指定に書き換える
WHERE CreatedAt >= '2025-06-01' AND CreatedAt < '2025-07-01'
```

### 特定日の絞り込み

```sql
-- ❌ NG（バージョンによっては Seek に変換される場合もあるが、避けた方が安全）
WHERE CONVERT(DATE, CreatedAt) = '2025-06-15'

-- ✅ OK: 範囲指定
WHERE CreatedAt >= '2025-06-15' AND CreatedAt < '2025-06-16'
```

### 文字列の前方一致

```sql
-- ❌ NG
WHERE LEFT(UserName, 3) = 'ABC'

-- ✅ OK: LIKE の前方一致はインデックスが効く
WHERE UserName LIKE 'ABC%'
```

### ISNULL の回避

```sql
-- ❌ NG
WHERE ISNULL(DeletedAt, '9999-12-31') > GETDATE()

-- ✅ OK
WHERE (DeletedAt IS NULL OR DeletedAt > GETDATE())
```

## EF Core での注意

EF Core の LINQ でも同じ問題が起きる。

```csharp
// ❌ NG: CONVERT に変換される
.Where(x => x.CreatedAt.Date == targetDate)

// ✅ OK: 範囲指定
.Where(x => x.CreatedAt >= startOfDay && x.CreatedAt < startOfNextDay)
```

EF Core が生成する SQL は `appsettings.Development.json` で `"Microsoft.EntityFrameworkCore.Database.Command": "Information"` を設定すればコンソールに出力される。WHERE 句に `CONVERT` や `DATEPART` が含まれていたら SARGable でない可能性がある。

## まとめ

- インデックスを貼っても WHERE 句でカラムに関数を適用すると、一般的に Scan になる（オプティマイザのバージョンや統計情報で例外はあるが、基本は Scan と考えてよい）
- 実行計画で `Index Scan` が出たら、WHERE 句のカラム側に関数がないか確認する
- 日付の絞り込みは `YEAR()` / `MONTH()` / `CONVERT(DATE, col)` ではなく範囲指定に書き換える
- EF Core の `.Date` プロパティも `CONVERT` に変換されるため、範囲指定で書く

## 参考リンク

- [SQL Server Index Architecture and Design Guide](https://learn.microsoft.com/en-us/sql/relational-databases/sql-server-index-design-guide)
- [SARGable - Wikipedia](https://en.wikipedia.org/wiki/Sargable)
- [EF Core - Querying Data](https://learn.microsoft.com/en-us/ef/core/querying/)
