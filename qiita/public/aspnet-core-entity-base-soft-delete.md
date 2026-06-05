---
title: ASP.NET Core の Entity 基底クラスで論理削除と監査カラムの設定を自動化した話
tags:
  - CSharp
  - ASP.NET
  - AspNetCore
  - EntityFrameworkCore
  - 個人開発
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

## 何を解決したか

体調管理ツール Phycock（ASP.NET Core 10 / EF Core）を作るとき、「全テーブルに論理削除フラグと監査カラム（作成日・更新日・操作者）を持たせる」という方針を最初に決めた。

何も仕組みを入れないと、Insert のたびに `CreatedAt = DateTime.Now` を書き、Delete のたびに `IsDeleted = true` を書くことになる。書き忘れが起きやすく、かつコードが散らばる。

**Entity 基底クラスと Repository 基底クラスに仕組みを閉じ込めることで、呼び出し側は意識しなくてよくした。**

## Entity 基底クラスの設計

```csharp
public abstract class EntityBase : IEntity
{
    public bool DelFlag { get; set; }

    public string? UpdateApplicationUserId { get; set; }
    public string? CreateApplicationUserId { get; set; }
    public DateTime UpdateDate { get; set; }
    public DateTime CreateDate { get; set; }

    public void SetForCreate()
    {
        var userId = GetCurrentUserId();
        CreateApplicationUserId = userId ?? "";
        UpdateApplicationUserId = userId ?? "";
        CreateDate = DateTime.Now;
        UpdateDate = CreateDate;
    }

    public void SetForUpdate()
    {
        var userId = GetCurrentUserId();
        UpdateApplicationUserId = userId ?? "";
        UpdateDate = DateTime.Now;
    }

    public void SetForLogicalDelete()
    {
        DelFlag = true;
        SetForUpdate();
    }

    private string? GetCurrentUserId()
        => HttpContextAccessor?.HttpContext?.User?
            .FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier)?.Value;

    public static IHttpContextAccessor? HttpContextAccessor { get; set; }
}
```

`SetForCreate` は「作成時に使うカラムを全て設定する」、`SetForLogicalDelete` は「DelFlag を立てた後に更新日時・更新者も書く」。呼び出し順を間違えにくいようにメソッド 1 つで完結させている。

## Repository 基底クラスが自動的に呼ぶ

```csharp
public abstract class RepositoryBase<TEntity, TCondModel>
    where TEntity : class, IEntity
{
    // Insert は SetForCreate を自動呼び出し
    public virtual TEntity Insert(TEntity entity, bool isSaveChanges = true)
    {
        entity.SetForCreate();
        return InsertSimple(entity, isSaveChanges);
    }

    // Update は SetForUpdate を自動呼び出し
    public virtual TEntity Update(TEntity entity, bool isSaveChanges = true)
    {
        entity.SetForUpdate();
        return UpdateSimple(entity, isSaveChanges);
    }

    // LogicalDelete は SetForLogicalDelete を自動呼び出し
    public virtual TEntity LogicalDelete(TEntity entity, bool isSaveChanges = true)
    {
        entity.SetForLogicalDelete();
        dbSet.Attach(entity);
        context.Entry(entity).State = EntityState.Modified;
        if (isSaveChanges) context.SaveChanges();
        return entity;
    }
}
```

Service 層が `_repository.Insert(entity)` と書くだけで、監査カラムが設定される。`_repository.LogicalDelete(entity)` と書くだけで DelFlag が立ち、更新日時も更新される。

## 各エンティティの継承

```csharp
public abstract class PhycockEntityBase : EntityBase, IEntity
{
    public long Id { get; set; }  // 全テーブル共通のサロゲートキー
}

[Table("ScheduleEntry")]
public class ScheduleEntryEntity : PhycockEntityBase
{
    [Required]
    [MaxLength(450)]
    public string UserId { get; set; } = "";

    public DateOnly Date { get; set; }
    // ...
}
```

各テーブルのエンティティは `PhycockEntityBase` を継承するだけで、論理削除フラグと監査カラムを自動的に持つ。マイグレーションで全テーブルに同じカラムが生成される。

## 検索時の除外

論理削除レコードを除外するクエリはリポジトリの `GetBaseQuery` で統一する。

```csharp
public override IQueryable<ScheduleEntryEntity> GetBaseQuery(
    ScheduleEntryCondModel? cond = null, bool includeDelete = false)
{
    var query = dbSet.AsQueryable();
    if (!includeDelete) query = query.Where(e => !e.DelFlag);
    // ...
    return query;
}
```

通常の検索では `includeDelete = false`（省略値）で呼ぶ。管理画面などで削除済みも見たい場合だけ `true` を渡す。

## HttpContextAccessor の登録

EntityBase が `IHttpContextAccessor` を使ってログイン中のユーザー ID を取るため、起動時に DI コンテナから取得して設定する必要がある。

```csharp
// Program.cs
var app = builder.Build();

var httpContextAccessor = app.Services.GetRequiredService<IHttpContextAccessor>();
EntityBase.HttpContextAccessor = httpContextAccessor;
```

`static` プロパティに代入する方式のため、テスト時はモックした `IHttpContextAccessor` を差し替えればよい。

## まとめ

- `EntityBase` が監査カラムの設定ロジックを `SetForCreate` / `SetForUpdate` / `SetForLogicalDelete` に閉じ込める
- `RepositoryBase` が `Insert` / `Update` / `LogicalDelete` の中でこれらを自動呼び出しする
- 呼び出し側（Service 層）は `_repository.Insert(entity)` と書くだけで監査カラムが埋まる

Entity の継承ツリーで「全テーブルに同じ仕組みを持たせる」という設計判断を最初に固めたことで、テーブルが増えるたびに同じコードを書かなくてよくなった。

## 参考リンク

- [Phycock リポジトリ](https://github.com/harness17/phycock)
- [EF Core — 変更の保存（公式）](https://learn.microsoft.com/ja-jp/ef/core/saving/)
- [ASP.NET Core — 依存関係の挿入（公式）](https://learn.microsoft.com/ja-jp/aspnet/core/fundamentals/dependency-injection)
