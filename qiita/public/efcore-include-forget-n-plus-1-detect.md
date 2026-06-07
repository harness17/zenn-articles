---
title: EF CoreでInclude忘れ→Lazy Loading追加→N+1が生まれていた話
tags:
  - C#
  - SQL
  - パフォーマンス
  - aspnetcore
  - EFCore
private: false
updated_at: '2026-06-07T00:11:25+09:00'
id: f1e6cfcee4704f806e3a
organization_url_name: null
slide: false
ignorePublish: false
---

## 何が起きたか

ASP.NET Core MVC の一覧画面で、各行に「作成者名」を表示する処理を書いた。EF Core でエンティティを取得し、ナビゲーションプロパティ経由でユーザー名を表示していた。

```csharp
// Controller
var items = await _context.Items.ToListAsync();
return View(items);
```

```html
<!-- View -->
@foreach (var item in Model)
{
    <td>@item.CreatedByUser?.Name</td>
}
```

最初の問題は **ユーザー名が空表示になった** こと。EF Core のデフォルトは遅延読み込み (Lazy Loading) が無効なので、`Include` を書かずにナビゲーションプロパティにアクセスすると null が返る。View 側で `?.` を使っていたためエラーにはならず、作成者名の列だけが空になった。

「null になるなら遅延読み込みを有効にすれば？」と思い、`Microsoft.EntityFrameworkCore.Proxies` パッケージを追加し、`UseLazyLoadingProxies()` を設定した。ナビゲーションプロパティを `virtual` にすると表示は直った。しかしテスト用に 100 件入れたあたりで画面表示が明らかに遅くなった。

## 原因: Include 忘れ × Lazy Loading = N+1

流れを整理するとこうなる。

| 状態 | Include なし + Lazy Loading 無効（デフォルト） | Include なし + Lazy Loading 有効 |
|------|----------------------------------------------|----------------------------------|
| ナビゲーションプロパティ | null（空表示） | 自動で SELECT 発行（N+1） |

EF Core のデフォルトでは、`Include` を忘れても **null が返るだけで余計な SQL は出ない**。問題が表面化するのは `UseLazyLoadingProxies()` を有効にした場合。各行でナビゲーションプロパティにアクセスするたびに個別の SELECT が発行される。これが N+1 問題。

```
-- 発行されるSQL（N+1パターン）
SELECT * FROM Items;                          -- 1回
SELECT * FROM Users WHERE Id = 1;             -- +N回
SELECT * FROM Users WHERE Id = 2;
SELECT * FROM Users WHERE Id = 3;
...
```

5 件なら 6 回の SQL で済むが、100 件なら 101 回。ネットワーク往復とクエリ実行を 100 回繰り返すことになる。

## SQLログで気づいた方法

EF Core は設定ひとつで発行 SQL をコンソールに出力できる。

### 1. appsettings.Development.json にログレベルを追加

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.EntityFrameworkCore.Database.Command": "Information"
    }
  }
}
```

### 2. コンソール出力を確認

開発サーバーを起動して一覧画面を開くと、コンソールに SQL が流れる。

```
info: Microsoft.EntityFrameworkCore.Database.Command[20101]
      Executed DbCommand (1ms) [Parameters=[], ...]
      SELECT [i].[Id], [i].[Title], [i].[CreatedByUserId]
      FROM [Items] AS [i]

info: Microsoft.EntityFrameworkCore.Database.Command[20101]
      Executed DbCommand (0ms) [Parameters=[@__p_0='1'], ...]
      SELECT [u].[Id], [u].[Name]
      FROM [Users] AS [u]
      WHERE [u].[Id] = @__p_0

info: Microsoft.EntityFrameworkCore.Database.Command[20101]
      ...（以下、行数分繰り返し）
```

同じテーブルへの SELECT が大量に繰り返されていたら N+1 を疑う。

## 解決: Include と Select の使い分け

### パターン1: Include（関連エンティティ全体が必要なとき）

```csharp
var items = await _context.Items
    .Include(x => x.CreatedByUser)
    .ToListAsync();
```

```sql
-- 発行されるSQL（JOINで1回）
SELECT [i].[Id], [i].[Title], [i].[CreatedByUserId],
       [u].[Id], [u].[Name], [u].[Email]
FROM [Items] AS [i]
LEFT JOIN [Users] AS [u] ON [i].[CreatedByUserId] = [u].[Id]
```

### パターン2: Select（一部プロパティだけ必要なとき）

```csharp
var items = await _context.Items
    .Select(x => new ItemListDto
    {
        Id = x.Id,
        Title = x.Title,
        CreatedByUserName = x.CreatedByUser.Name
    })
    .ToListAsync();
```

```sql
-- 発行されるSQL（必要なカラムだけ）
SELECT [i].[Id], [i].[Title], [u].[Name]
FROM [Items] AS [i]
LEFT JOIN [Users] AS [u] ON [i].[CreatedByUserId] = [u].[Id]
```

`Select` の方が SQL が軽い（不要なカラムを取得しない）。一覧画面のように表示項目が決まっている場面では `Select` + DTO を使うほうが効率がよい。

## 注意点

- **EF Core のデフォルトは Lazy Loading 無効**。`Include` を忘れるとナビゲーションプロパティは null になり、エラーにならず空表示になる。「null を直したい」と安易に `UseLazyLoadingProxies()` を追加すると N+1 が生まれる
- **Lazy Loading を有効にするには `Microsoft.EntityFrameworkCore.Proxies` パッケージが必要**で、かつナビゲーションプロパティを `virtual` にする必要がある。この2つが揃わないと `UseLazyLoadingProxies()` を呼んでも Lazy Loading は動かない
- **「Include がなければ常に null」とは限らない**。同じ `DbContext` 内で先に読み込まれたエンティティがあると、EF Core の relationship fixup により自動的にナビゲーションプロパティが設定される場合がある。ただし一覧画面で初回取得する典型的なパターンでは null になる
- **変更後は SQL ログで 1 クエリに集約されたことを確認する**。Include を書いても、ループ内でさらにナビゲーションプロパティを辿ると二段目の N+1 が起きることがある
- `AsSplitQuery()` は 1:N で結果行が膨れるときにクエリを分割するオプション。N+1 の解消ではなく、JOIN 結果のデータ重複を減らすために使う
- 正しい対処は `UseLazyLoadingProxies()` の追加ではなく、必要なナビゲーションプロパティを `Include` または `Select` で明示的に取得すること

## 参考リンク

- [EF Core - Loading Related Data](https://learn.microsoft.com/en-us/ef/core/querying/related-data)
- [EF Core - Lazy Loading](https://learn.microsoft.com/en-us/ef/core/querying/related-data/lazy)
- [EF Core - Split Queries](https://learn.microsoft.com/en-us/ef/core/querying/single-split-queries)
- [Phycock](https://github.com/harness17/phycock) - Include / Select パターンの実装例（Lazy Loading は使用していない）
- [DevNext](https://github.com/harness17/DevNext) - ASP.NET Core 10 テンプレート
