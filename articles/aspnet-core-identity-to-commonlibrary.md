---
title: "ASP.NET Core移行でIdentityエンティティを共通化した判断"
emoji: "🪪"
type: "tech"
topics: ["aspnetcore", "csharp", "identity", "dotnet", "architecture"]
published: true
---

## はじめに

個人で .NET Framework 版の業務系テンプレート [DevNet](https://github.com/harness17/DevNet) と、ASP.NET Core 10 版の後継テンプレート [DevNext](https://github.com/harness17/DevNext) を保守しています。

二世代のテンプレートで、`ApplicationUser` の置き場所を変えました。DevNet では `Site/Entity/ApplicationUser.cs` と Web プロジェクト側に置いていたのが、DevNext では `CommonLibrary/Entity/ApplicationUser.cs` と共通ライブラリ側に寄せました。

ASP.NET Core Identity は、ログイン、ロール、パスワード、ユーザー管理を扱うための標準的な認証・認可基盤です。`ApplicationUser` は、そのユーザー情報をアプリ側で拡張するための型です。この記事で扱うのは Identity の導入手順ではなく、その型を Web プロジェクトに置くか、共通ライブラリに置くかという境界の判断です。

最初は「共通ライブラリを Identity から完全に切り離した」という話として書こうとしていました。しかし実ファイルを確認すると、DevNet の `CommonLibrary` も `Microsoft.AspNet.Identity` や OWIN にすでに依存していました。

そのため、本記事の論点は「Identity 依存を入れたかどうか」ではありません。**監査カラムや補助処理は共通基盤に含めていた状態から、`ApplicationUser` や `ApplicationRole` という認証エンティティ本体まで共通化した判断**の記録です。

## 二世代の `ApplicationUser` を並べる

まず、二世代で `ApplicationUser` の場所がどう変わったかを並べます。DevNet 側です。主要部分だけ抜粋します。

```csharp:DevNet/Site/Entity/ApplicationUser.cs
using System.Collections.Generic;
using Microsoft.AspNet.Identity;
using Microsoft.AspNet.Identity.EntityFramework;

namespace Site.Entity
{
    public class ApplicationUser : IdentityUser
    {
        public ApplicationUser() : base()
        {
            PreviousUserPasswords = new List<UserPreviousPassword>();
        }

        public virtual IList<UserPreviousPassword> PreviousUserPasswords { get; set; }
        public DateTime? ResetPasswordTimeOut { get; set; }
        public DateTime? PasswordAvailableEndDate { get; set; }
        public String ApplicationRoleName { get; set; }
        public String UpdateApplicationUserId { get; set; }
    }
}
```

namespace は `Site.Entity`。`ApplicationUser` は Web プロジェクト側にあります。
`String` は DevNet 側の当時の表記のまま載せています。

DevNext 側はこうです。

```csharp:DevNext/CommonLibrary/Entity/ApplicationUser.cs
using Microsoft.AspNetCore.Identity;

namespace Dev.CommonLibrary.Entity
{
    public class ApplicationUser : IdentityUser
    {
        public ApplicationUser() : base()
        {
            PreviousUserPasswords = new List<UserPreviousPassword>();
        }

        public virtual IList<UserPreviousPassword> PreviousUserPasswords { get; set; }
        public DateTime? ResetPasswordTimeOut { get; set; }
        public DateTime? PasswordAvailableEndDate { get; set; }
        public string? ApplicationRoleName { get; set; }
        public string? UpdateApplicationUserId { get; set; }
    }
}
```

namespace は `Dev.CommonLibrary.Entity`。`ApplicationUser` だけでなく、`ApplicationRole`、`UserPreviousPassword`、`SiteEntityBase` も `CommonLibrary/Entity/` 配下に置いています。

この差は、単なるファイル移動ではありません。`UserManager<ApplicationUser>`、`IdentityDbContext<ApplicationUser, ApplicationRole, string>`、サンプルプロジェクトの `AddIdentity<ApplicationUser, ApplicationRole>()` が、すべて `Dev.CommonLibrary.Entity` の型を前提にできます。

## DevNetのCommonLibraryは純粋共通ではなかった

ここは一度、間違えた前提で書きかけました。

DevNet の `ApplicationUser` は `Site` 側にありました。そのため「DevNet の `CommonLibrary` は Identity 非依存だった」と捉えたくなります。しかし実際には、`CommonLibrary.csproj` には次の参照が入っています。

- `Microsoft.AspNet.Identity.Core`
- `Microsoft.AspNet.Identity.EntityFramework`
- `Microsoft.AspNet.Identity.Owin`
- `EntityFramework`

さらに `CommonLibrary/Entity/EntityBase.cs` では、更新者・登録者を入れるために `Microsoft.AspNet.Identity` を using し、`GetUserId()` を呼んでいます。つまり DevNet の `CommonLibrary` は、Identity と無関係な純粋ライブラリではありませんでした。

正確には、**監査カラムや共通処理では Identity 周辺に依存していたが、`ApplicationUser` / `ApplicationRole` という認証モデル本体は `Site` 側に残していた**、という状態です。

この境界を、DevNext で見直しました。

## ASP.NET Coreで境界を動かした判断

DevNext では、`ApplicationUser` と `ApplicationRole` を `CommonLibrary` に寄せました。判断軸は3つです。

### 1. すでに共通基盤はユーザーIDに依存していた

DevNet の時点で、共通 Entity は `CreateApplicationUserId` / `UpdateApplicationUserId` を持ち、実行時のログインユーザー ID を参照していました。

この時点で、`CommonLibrary` は完全なドメイン非依存ライブラリではありません。業務系テンプレートの共通基盤として、ユーザー、監査、Repository、画面補助をまとめる方向にすでに寄っていました。

それなら、DevNext で `ApplicationUser` だけを Web プロジェクト側に残すより、ユーザーIDを扱う共通 Entity と同じ場所に認証エンティティ本体も寄せた方が、テンプレート全体の見通しは良くなります。

### 2. Samplesから同じIdentity型を参照したかった

DevNext は `Samples/` 配下に複数のサブプロジェクトを抱えています。`DatabaseSample`、`ApiSample`、`MailSample`、`WizardSample` などです。

それぞれのサンプルでログイン、監査カラム、`UserManager<ApplicationUser>` を使います。`ApplicationUser` をメイン Web プロジェクト側に置いたままだと、サンプル側がメイン Web プロジェクトに依存するか、各サンプルで同じ Identity 型を再定義するか、どちらかになります。

どちらもテンプレートとして扱いにくい構成です。

`CommonLibrary` に寄せれば、参照グラフは一方向にできます。メイン Web プロジェクトも、各サンプルも、同じ `CommonLibrary` の `ApplicationUser` / `ApplicationRole` を参照します。

### 3. CommonLibraryを「純粋共通」ではなく「テンプレート系列の共通基盤」と見なした

DevNext の `CommonLibrary.csproj` は、実際に `Microsoft.AspNetCore.Identity.EntityFrameworkCore` と `Microsoft.EntityFrameworkCore` を参照しています。

つまり、`CommonLibrary` は「どの .NET プロジェクトにもそのまま持ち込める純粋共通」ではありません。DevNext という業務系テンプレート系列で使う共通基盤です。

ここを曖昧にすると、設計判断がぶれます。

「将来どこかで Identity を使わないかもしれない」という想定のために `ApplicationUser` だけを外へ置くより、現在のテンプレートで何度も使う型を共通化する方を選びました。
起きていない要求のために境界を複雑にするより、実際に複数回出ている参照関係を単純にする判断です。

## 共通化して何が変わったか

良かった点：

- 認証絡みの拡張フィールド（`PasswordAvailableEndDate`, `ApplicationRoleName` 等）が一箇所で管理できる
- `Samples/` から同じ `ApplicationUser` / `ApplicationRole` を参照できる
- 利用側 `DbContext` は `IdentityDbContext<ApplicationUser, ApplicationRole, string>` を継承すればよく、認証モデルを再定義しなくて済む
- `UserManager<ApplicationUser>` を使うサービスや Controller の型が、メイン Web プロジェクトとサンプルで揃う

引き換えに受け入れたコスト：

- `CommonLibrary` の責務が「共通基盤 + Identity / EF Core 拡張」に広がる
- `CommonLibrary` を参照するプロジェクトは、Identity / EF Core 系の依存も受け入れる前提になる
- 将来、Identity を別認証基盤に置き換えるなら、`CommonLibrary` の認証エンティティを切り出す作業が必要になる

このコストは軽くありません。ただ、DevNext を「複数サンプルを含む業務系テンプレート」として使う限り、受け入れた方が全体の見通しは良いと判断しました。

:::message
この記事の判断は「共通ライブラリにフレームワーク依存を入れてよい」という一般論ではありません。DevNext では、共通基盤がすでにユーザーIDやEF Coreに寄っており、複数サンプルから同じ Identity 型を参照したい実需があったため、認証エンティティ本体も `CommonLibrary` に寄せました。
:::

## いま戻れるなら何を変えるか

`ApplicationUser` と `ApplicationRole` を `CommonLibrary` に寄せた判断自体は維持します。ただし、境界の名前はもう少し丁寧に切りたいです。

たとえば、将来テンプレートをさらに横展開するなら、次の分割は検討します。

- `CommonLibrary.Core`
  - Entity / Repository / Extension のうち、認証に直接依存しない部分
- `CommonLibrary.Identity`
  - `ApplicationUser`、`ApplicationRole`、`UserPreviousPassword` など Identity 周辺
- `CommonLibrary.Web`
  - HttpContext、Cookie、画面補助、フィルターなど Web 実行環境に近い部分

ただし、今すぐ分けるつもりはありません。

実際に「Identity を使わないサンプルだけを切り出したい」「別認証基盤版を作りたい」という要求が出るまでは、1つの `CommonLibrary` で運用します。分割そのものも保守コストになるからです。

## まとめ

要点は3つです。

- DevNet の `CommonLibrary` は完全な Identity 非依存ではなく、監査カラムや共通処理の時点で Identity 周辺に依存していた
- DevNext では、`ApplicationUser` / `ApplicationRole` まで `CommonLibrary` に寄せ、複数サンプルから同じ認証モデルを参照できるようにした
- 「純粋共通ライブラリ」ではなく「テンプレート系列の共通基盤」と割り切ることで、扱いやすさと依存のコストを明確にした

個人で2世代分のテンプレートを保守すると、過去の境界を見直す機会がそのまま設計の言語化になります。Core 移行は、同じ実装を移し替えるだけでなく、どこまでを共通基盤に含めるかを再評価するプロセスでした。

## 参考リンク

- [harness17/DevNet](https://github.com/harness17/DevNet) — .NET Framework 版テンプレート
- [harness17/DevNext](https://github.com/harness17/DevNext) — ASP.NET Core 10 版テンプレート
- [DevNet `Site/Entity/ApplicationUser.cs`](https://github.com/harness17/DevNet/blob/master/Site/Entity/ApplicationUser.cs)
- [DevNext `CommonLibrary/Entity/ApplicationUser.cs`](https://github.com/harness17/DevNext/blob/master/CommonLibrary/Entity/ApplicationUser.cs)
- [Microsoft.AspNetCore.Identity 公式ドキュメント](https://learn.microsoft.com/aspnet/core/security/authentication/identity)
