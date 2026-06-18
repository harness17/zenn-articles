---
title: IISのASP.NET CoreでMigrateAsyncが失敗するときはAppPool IDをSQL Serverログインに登録する
tags:
  - ASP.NET_Core
  - IIS
  - SQLServer
  - EntityFrameworkCore
  - Windows
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

## 何が起きたか

ASP.NET Core アプリを IIS InProcess で配置し、起動時に `MigrateAsync` で DB を自動作成・マイグレーションする構成にしていた。

```csharp
using var scope = app.Services.CreateScope();
var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
await context.Database.MigrateAsync();
```

開発環境（Visual Studio + Kestrel）では問題なく動いていたが、IIS に配置した途端に HTTP 500 が出た。

## 原因

接続文字列に `Integrated Security=True`（Windows 統合認証）を使っていた。

開発環境では Visual Studio の実行ユーザーで SQL Server に接続していた。IIS では **アプリプールの ID**（`IIS AppPool\<プール名>`）が実行ユーザーになる。この ID は SQL Server に登録されていなかった。

## 解決

SQL Server Management Studio または T-SQL で、AppPool ID をログインに登録し、対象 DB の `db_owner` を付与する。

```sql
-- 1. ログインを作成する
CREATE LOGIN [IIS APPPOOL\MyApp] FROM WINDOWS;

-- 2. 対象 DB のユーザーに追加し、db_owner を付与する
USE [MyAppDb];
CREATE USER [IIS APPPOOL\MyApp] FOR LOGIN [IIS APPPOOL\MyApp];
ALTER ROLE [db_owner] ADD MEMBER [IIS APPPOOL\MyApp];
```

DB がまだ存在しない場合は `MigrateAsync` が `CREATE DATABASE` を試みるため、サーバーロール `dbcreator` も必要になる。

```sql
-- DB が未作成の場合のみ。作成後に外す
ALTER SERVER ROLE [dbcreator] ADD MEMBER [IIS APPPOOL\MyApp];
```

DB 作成後は `dbcreator` を外す。サーバーレベルの権限は最小限にする。

```sql
ALTER SERVER ROLE [dbcreator] DROP MEMBER [IIS APPPOOL\MyApp];
```

## 罠: Error 1801「データベースは既に存在します」

DB は実在するのに `MigrateAsync` がエラーになるケースがある。

```
Error Number:1801 データベース 'MyAppDb' は既に存在します。
```

原因は、ログインに対象 DB 内のユーザーマッピングがないこと。EF Core は DB の存在確認で SQL Server へ接続するが、ログインがあっても DB 内のユーザーがなければ「DB にアクセスできない＝存在しない」と判断し、`CREATE DATABASE` にフォールバックする。

**ログインだけでなく、DB 内の `CREATE USER` + `ALTER ROLE` も必ず実行する。**

## 確認

設定後に IIS からアプリプールをリサイクルし、ブラウザでアクセスして 500 が出ないことを確認する。

イベントビューアの「アプリケーション」ログで `Microsoft-IIS-AspNetCoreModuleV2` のエラーが出なくなっていれば、MigrateAsync の権限問題は解消している。

## 参考

- [ASP.NET Core を IIS でホストする（公式）](https://learn.microsoft.com/ja-jp/aspnet/core/host-and-deploy/iis/)
- [DevNext — ASP.NET Core 10 テンプレート](https://github.com/harness17/DevNext)
