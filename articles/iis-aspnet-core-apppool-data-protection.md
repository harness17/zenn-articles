---
title: "ASP.NET CoreをIISに配置したら500が出た — AppPool専用化・SQL権限・Data Protectionの3点セット"
emoji: "🔧"
type: "tech"
topics: ["aspnetcore", "iis", "windows", "csharp", "個人開発"]
published: false
---

## はじめに

ASP.NET Core アプリを IIS の InProcess モードで動かしたら、初回アクセスで HTTP 500 が返った。開発環境の Kestrel では問題なく動いていたのに、IIS に配置した途端に壊れる。

イベントログを追いかけると、原因は1つではなく **3つ同時** だった。

1. InProcess ホスティングの「1プール1アプリ」制約
2. `MigrateAsync` 実行時の SQL Server 権限不足
3. Data Protection キーの書き込み権限不足

1つ直しても次の500が出る。この記事では、ASP.NET Core を IIS に配置するときに同時に揃える必要がある3つの設定を、実際に踏んだ順に書く。

**対象読者**: ASP.NET Core を IIS InProcess で初めて配置する人。特に Windows 統合認証（`Integrated Security=True`）で SQL Server に接続する構成を想定する。

## 前提: InProcess ホスティングとは

IIS で ASP.NET Core を動かす方式は2つある。

| 方式 | 動作 | 性能 |
|------|------|------|
| InProcess | IIS Worker Process（w3wp.exe）内で直接実行 | 高速 |
| OutOfProcess | Kestrel を別プロセスで起動し、IIS がリバースプロキシ | やや遅い |

InProcess はリクエストが IIS → アプリに直接渡るため高速だが、いくつかの制約がある。今回はその制約に3回引っかかった。

## 原因①: 1つのアプリプールに複数アプリを入れた

最初のエラーはこれだった。

```
Only one in-process application is allowed per IIS application pool
```

InProcess モードでは、**1つのアプリプールに1つのアプリ** しか配置できない。既存の別アプリと同じプールに入れていたため、後から追加したアプリが起動できなかった。

**解決**: IIS マネージャーで専用のアプリプールを作成し、対象アプリだけを割り当てた。

```
アプリプール名: MyApp（例）
.NET CLR バージョン: マネージド コードなし
マネージドパイプラインモード: 統合
```

「マネージド コードなし」にするのは、ASP.NET Core は自前のランタイムで動くため。

## 原因②: MigrateAsync が SQL Server に接続できない

専用プールにしたら起動はした。しかし今度は別の 500 が出る。イベントログを見ると、EF Core の `MigrateAsync` が失敗していた。

`Program.cs` でやっていたのはこういう処理だ。

```csharp
// 起動時に DB が無ければ作成し、マイグレーションを適用する
using var scope = app.Services.CreateScope();
var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
await context.Database.MigrateAsync();
```

開発環境では Visual Studio の実行ユーザーで SQL Server に接続していた。IIS では **アプリプールの ID**（`IIS AppPool\MyApp`）が実行ユーザーになる。この ID は SQL Server に登録されていない。

### 解決: SQL Server ログインを登録する

```sql
-- 1. ログインを作成する
CREATE LOGIN [IIS APPPOOL\MyApp] FROM WINDOWS;

-- 2. 対象 DB のユーザーに追加し、db_owner を付与する
USE [MyAppDb];
CREATE USER [IIS APPPOOL\MyApp] FOR LOGIN [IIS APPPOOL\MyApp];
ALTER ROLE [db_owner] ADD MEMBER [IIS APPPOOL\MyApp];
```

DB がまだ存在しない場合、今回の構成では `MigrateAsync` が `CREATE DATABASE` を試みたため、サーバーロール `dbcreator` も追加した。

```sql
-- DB が未作成の場合のみ。作成後に外す
ALTER SERVER ROLE [dbcreator] ADD MEMBER [IIS APPPOOL\MyApp];
```

DB 作成後は `dbcreator` を外す。サーバーレベルの権限を持ち続ける必要はない。

```sql
ALTER SERVER ROLE [dbcreator] DROP MEMBER [IIS APPPOOL\MyApp];
```

この構成は **個人開発の単一サーバー環境** で採用した。本番環境では、アプリに `db_owner` や `dbcreator` を常時付与する運用は Microsoft が非推奨としている。本番では `dotnet ef migrations bundle` で生成した migration bundle を配置工程で実行するか、SQL スクリプトを `dotnet ef migrations script` で出力して DBA が適用する方法が推奨される。

### 罠: Error 1801「データベースは既に存在します」

DB は実在するのに `MigrateAsync` が「DB がない」と判断して `CREATE DATABASE` を試み、`1801: データベースは既に存在します` エラーになることがある。

今回の構成では、ログインに対象 DB 内のユーザーマッピングがないことが原因だった。EF Core（SQL Server プロバイダー）は DB の存在確認で接続に失敗すると `CREATE DATABASE` を試みる経路がある。ログインを作るだけでなく、**DB 内のユーザーとロールも設定する** のが確実だ。接続先 DB やプロバイダー構成によってエラー番号は変わるため、実際のイベントログで確認する。

## 原因③: Data Protection キーの書き込み権限

SQL Server の問題を直したら、アプリは起動した。しかし Cookie 認証が動かない。ログインしても即座にログアウトされる。

ASP.NET Core の Cookie 認証は、**Data Protection** という仕組みで Cookie を暗号化する。暗号化キーの保存先はホスト環境によって異なり、IIS では `PersistKeysToFileSystem` で明示指定するか、レジストリやデフォルトパスが使われる。今回は `PersistKeysToFileSystem` でアプリ直下のフォルダを指定していたため、そのパスへの書き込み権限が AppPool ID に必要だった。

イベントログの「アプリケーション」で Data Protection のキー保存失敗ログが出ていたことで、この原因にたどり着いた。

```csharp
builder.Services.AddDataProtection()
    .PersistKeysToFileSystem(
        new DirectoryInfo(Path.Combine(builder.Environment.ContentRootPath, "DataProtectionKeys")))
    .SetApplicationName("MyApp");
```

### 解決: icacls で書き込み権限を付与する

```powershell
# DataProtectionKeys フォルダに AppPool ID の Modify 権限を継承付きで付与する
icacls "C:\inetpub\MyApp\DataProtectionKeys" /grant "IIS AppPool\MyApp:(OI)(CI)M"
```

`(OI)(CI)` はサブフォルダ・ファイルへの継承指定。`M` は Modify 権限（読み書き削除）。

`PersistKeysToFileSystem` を指定していない場合、IIS 環境ではレジストリ（`HKLM\SOFTWARE\Microsoft\ASP.NET\DataProtection`）やプロファイルフォルダなど、構成によって保存先が変わる。IIS のアプリプール設定で「ユーザー プロファイルの読み込み」が有効かどうかでも動作が異なるため、キーの保存先は明示的に指定して確認するのが確実だ。

なお、この記事は **単一サーバー構成** を前提としている。Web Farm（複数サーバー）構成では、共有キーリング（Redis や Azure Blob Storage など）と DPAPI-NG 等でのキー暗号化が別途必要になる。

## 3点セットのチェックリスト

IIS InProcess + Windows 統合認証で ASP.NET Core を配置するときは、この3つを同時に確認する。

- [ ] **専用アプリプール** を作成し、対象アプリだけを割り当てた
- [ ] **SQL Server ログイン** に `IIS AppPool\<プール名>` を登録し、`db_owner` を付与した
- [ ] **Data Protection キーのフォルダ** に AppPool ID の Modify 権限を `icacls` で付与した

追加で確認すること:

- [ ] DB 未作成なら `dbcreator` を付与し、作成後に外した
- [ ] `App_Data` 等の書き込みフォルダがあれば、同様に Modify 権限を付与した

## まとめ

- InProcess は高速だが「1プール1アプリ」の制約がある。既存アプリとプールを共有しない
- Windows 統合認証で `MigrateAsync` を使うなら、AppPool ID を SQL Server ログインに登録して `db_owner` を付与する
- Data Protection キーの保存先に AppPool ID の書き込み権限がないと、Cookie 認証が壊れる

3つとも ASP.NET Core の公式ドキュメントに個別には書いてある。しかし開発環境では全部 Visual Studio の実行ユーザーで通っているため、IIS に配置して初めて同時に踏む。「1つ直しても次の500が出る」のは、3つが独立した原因だからだ。

## 参考リンク

- [ASP.NET Core を IIS でホストする（公式）](https://learn.microsoft.com/ja-jp/aspnet/core/host-and-deploy/iis/)
- [ASP.NET Core Data Protection の構成（公式）](https://learn.microsoft.com/ja-jp/aspnet/core/security/data-protection/configuration/overview)
- [DevNext — ASP.NET Core 10 テンプレート](https://github.com/harness17/DevNext)
