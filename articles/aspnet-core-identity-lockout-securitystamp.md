---
title: "ASP.NET Core Identityのユーザー無効化でLockoutEndだけ変えたら既存Cookieが残った"
emoji: "🔒"
type: "tech"
topics: ["aspnetcore", "identity", "csharp", "security"]
published: true
---

## はじめに

ASP.NET Core 10 で個人開発している Web アプリに、管理者がユーザーを無効化する機能を実装した。`LockoutEnd` を遠い未来（9999年）に設定すれば、そのユーザーはログインできなくなる。ここまでは期待通りだった。

問題は「既にログインしているユーザー」のほうだった。管理画面から無効化しても、そのユーザーがブラウザを開いたままなら、ページを更新してもまだ操作できる。無効化したはずなのにセッションが切れない。

この記事では、`LockoutEnd` と `SecurityStamp` の役割の違い、既存 Cookie が残る仕組み、そして `UpdateSecurityStampAsync` を併用する修正案を書く。

**対象読者**: ASP.NET Core Identity の Cookie 認証で、ユーザー無効化や強制ログアウトを実装する開発者。

**リポジトリ**: [harness17/phycock](https://github.com/harness17/phycock)（療養中に自主制作した体調管理ツール）

## 最初の実装: LockoutEnd だけ設定した

ユーザー無効化は `UserManager` の API で実装した。

```csharp
private static readonly DateTimeOffset DisabledLockoutEnd =
    new DateTime(9999, 12, 31, 23, 59, 59, DateTimeKind.Utc);

public async Task<IdentityResult> DisableUserAsync(string id)
{
    if (id == Const.SystemAdminUserId)
        return IdentityResult.Failed(new IdentityError
            { Description = "初期管理者ユーザーは無効化できません。" });

    var user = await _userManager.FindByIdAsync(id);
    if (user == null)
        return IdentityResult.Failed(new IdentityError
            { Description = "ユーザーが見つかりません。" });

    user.LockoutEnabled = true;
    user.LockoutEnd = DisabledLockoutEnd;
    user.AccessFailedCount = 0;

    return await _userManager.UpdateAsync(user);
}
```

初期 Admin は無効化禁止にしている。`LockoutEnd` を 9999 年に設定し、`UpdateAsync` で保存。次回ログインは確かにブロックされる。

しかし、管理画面で無効化した直後に、そのユーザーのブラウザでページ遷移してみると、まだ普通に動く。

## 原因: Cookie 認証の SecurityStamp 検証間隔

ASP.NET Core Identity の Cookie 認証は、リクエストごとに DB を叩かない。Cookie 内に SecurityStamp のコピーを持ち、一定間隔で DB の SecurityStamp と突き合わせる。

```csharp
// Program.cs
builder.Services.ConfigureApplicationCookie(options =>
{
    options.LoginPath = "/Account/Login";
    options.ExpireTimeSpan = TimeSpan.FromMinutes(1440); // 24時間
    // SecurityStampValidationInterval は未指定 → 既定30分
});
```

この仕組みを整理すると、3つの独立した概念がある。

| 概念 | DB カラム | Cookie に含まれるか | 変更タイミング |
|------|----------|-------------------|-------------|
| LockoutEnd | `LockoutEnd` | 含まれない | `UpdateAsync` で直接変更 |
| SecurityStamp | `SecurityStamp` | コピーが含まれる | パスワード変更、`UpdateSecurityStampAsync` 等 |
| Cookie 有効期限 | なし | `ExpireTimeSpan` で制御 | Cookie 発行時に固定 |

`LockoutEnd` は「次回認証時のブロック」であり、Cookie の有効性には直接影響しない。Cookie が無効化されるのは以下のどれか。

1. Cookie の `ExpireTimeSpan` が切れた（このアプリでは24時間）
2. SecurityStamp 検証で DB と不一致になった
3. ユーザーが自分でログアウトした

`LockoutEnd` を変えても SecurityStamp は変わらないので、Cookie 内の SecurityStamp と DB の SecurityStamp は一致したままになる。つまり、検証間隔ごとの突き合わせで「問題なし」と判定され、Cookie はそのまま有効。

## 検討した代替案

### 案 1: SecurityStampValidationInterval を短くする

```csharp
options.Events.OnValidatePrincipal =
    SecurityStampValidator.ValidatePrincipalAsync;
// または .AddSecurityStampValidatorOptions で間隔を変更
```

検証間隔を 1 分にすれば、無効化から最大 1 分で Cookie が切れる。しかし間隔を短くするほど DB アクセスが増える。このアプリはローカル運用の個人ツールなので負荷は問題にならないが、設計として「無効化のために全ユーザーの検証頻度を上げる」のは本末転倒だった。

### 案 2: UpdateSecurityStampAsync を併用する（採用）

無効化するユーザーの SecurityStamp だけを変えれば、そのユーザーの Cookie だけが次の検証で無効化される。全体の検証間隔は変えなくていい。

## 修正案: UpdateSecurityStampAsync を追加

```csharp
public async Task<IdentityResult> DisableUserAsync(string id)
{
    if (id == Const.SystemAdminUserId)
        return IdentityResult.Failed(new IdentityError
            { Description = "初期管理者ユーザーは無効化できません。" });

    var user = await _userManager.FindByIdAsync(id);
    if (user == null)
        return IdentityResult.Failed(new IdentityError
            { Description = "ユーザーが見つかりません。" });

    user.LockoutEnabled = true;
    user.LockoutEnd = DisabledLockoutEnd;
    user.AccessFailedCount = 0;

    var result = await _userManager.UpdateAsync(user);
    if (!result.Succeeded) return result;

    // DB側のSecurityStampを更新し、次の検証間隔でCookieを無効化する
    await _userManager.UpdateSecurityStampAsync(user);
    return result;
}
```

`UpdateSecurityStampAsync` は DB の `SecurityStamp` カラムを新しいランダム値に書き換える。次にブラウザからリクエストが来たとき、Cookie 内の古い SecurityStamp と DB の新しい SecurityStamp が不一致になり、`SecurityStampValidator` が Cookie を無効化する。

### 即時失効ではない点

`UpdateSecurityStampAsync` を呼んでも、次の検証間隔（既定30分）までは Cookie が生きている。「即時ログアウト」が必要なら検証間隔を短くするか、SignalR 等でクライアントに通知するしかない。

このアプリでは、管理者がユーザーを無効化する頻度は低く、30分の猶予は許容範囲だった。管理画面に「無効化しました。既存セッションは最大30分後に無効化されます」と表示するだけで十分だった。

## 一般化: LockoutEnd と SecurityStamp の使い分け

| やりたいこと | LockoutEnd | SecurityStamp |
|------------|-----------|---------------|
| 次回ログインをブロック | ✅ 必要 | 不要 |
| 既存 Cookie を無効化 | ❌ 効果なし | ✅ 必要 |
| パスワード変更後の全端末ログアウト | 不要 | ✅ 自動で変わる |

パスワード変更（`ResetPasswordAsync`）は内部で SecurityStamp を更新するため、全端末のセッションが切れる。しかし `LockoutEnd` の変更は SecurityStamp に触れない。この非対称性に気づかないと、「無効化したのにまだ操作できる」という穴が開く。

## まとめ

- `LockoutEnd` は次回ログインのブロック。既存 Cookie の無効化は SecurityStamp の仕事
- Cookie 認証はリクエストごとに DB を叩かない。検証間隔（既定30分）で SecurityStamp を突き合わせる
- ユーザー無効化時は `UpdateSecurityStampAsync` を併用して、既存 Cookie を検証間隔内に無効化する

## 参考リンク

- [harness17/phycock](https://github.com/harness17/phycock) — 療養中に自主制作した体調管理ツール
- [ASP.NET Core Identity — SecurityStamp](https://learn.microsoft.com/ja-jp/aspnet/core/security/authentication/identity)
- [SecurityStampValidator Source](https://github.com/dotnet/aspnetcore/blob/main/src/Identity/Core/src/SecurityStampValidator.cs)
