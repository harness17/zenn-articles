---
title: ASP.NET Core IdentityでLockoutEndを設定しても既存Cookieが残った
tags:
  - C#
  - Security
  - cookie
  - ASP.NETCore
  - identity
private: false
updated_at: '2026-06-24T18:01:19+09:00'
id: 1bee38e9cabc8a56e82f
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

ASP.NET Core Identity でユーザーを無効化するとき、`LockoutEnd` を遠い未来に設定しただけでは既存のログイン済み Cookie が無効にならない。Cookie の SecurityStamp 検証は既定で 30 分間隔のため、その間は無効化されたユーザーが操作を続けられる。`UpdateSecurityStampAsync()` を併用すると、次の検証タイミングで Cookie が無効化される。

```csharp
user.LockoutEnabled = true;
user.LockoutEnd = new DateTime(9999, 12, 31, 23, 59, 59, DateTimeKind.Utc);
await _userManager.UpdateAsync(user);
// これだけでは既存Cookieが残る

await _userManager.UpdateSecurityStampAsync(user);
// DB側のSecurityStampが変わり、次の検証でCookieが無効化される
```

## 起きたこと

ASP.NET Core 10 で作っている個人開発の Web アプリに、管理者がユーザーを無効化する機能を実装した。

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
    user.LockoutEnd = DisabledLockoutEnd; // 9999-12-31
    user.AccessFailedCount = 0;

    return await _userManager.UpdateAsync(user);
}
```

管理画面からユーザーを無効化した後、そのユーザーのブラウザでページを更新したら、まだ操作できた。ログアウトされていない。

## 原因

ASP.NET Core Identity の Cookie 認証は、リクエストのたびに DB に問い合わせるのではなく、一定間隔で Cookie 内の SecurityStamp と DB の SecurityStamp を突き合わせて検証する。

```csharp
// Program.cs — この設定だと SecurityStampValidationInterval は既定値
builder.Services.ConfigureApplicationCookie(options =>
{
    options.ExpireTimeSpan = TimeSpan.FromMinutes(1440); // 24時間
    // SecurityStampValidationInterval は未指定 → 既定30分
});
```

| 設定 | 既定値 | 意味 |
|------|--------|------|
| `ExpireTimeSpan` | 14日 | Cookie の有効期限 |
| `SecurityStampValidationInterval` | 30分 | Cookie のSecurityStamp を DB と突き合わせる間隔 |

`LockoutEnd` を変えても SecurityStamp は変わらない。Cookie 内の SecurityStamp と DB の SecurityStamp が一致し続ける限り、Cookie は有効とみなされる。

つまり、`LockoutEnd` は「次回ログイン時」のブロックであり、「既存セッションの即時無効化」ではない。

## 修正

`DisableUserAsync` に `UpdateSecurityStampAsync` を追加する。

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

`UpdateSecurityStampAsync` は DB の `SecurityStamp` カラムを新しいランダム値に書き換える。次にブラウザからリクエストが来たとき、Cookie 内の SecurityStamp と DB の SecurityStamp が不一致になり、Cookie が無効化される。

ただし「即時」ではなく、`SecurityStampValidationInterval` の間隔（既定30分）まで遅延する。より短い間隔が必要なら設定を変えるが、リクエストごとに DB 問い合わせが発生するトレードオフがある。

## 確認ポイント

- `DisableUserAsync` で `UpdateSecurityStampAsync` を呼んでいるか
- `SecurityStampValidationInterval` の設定値を把握しているか（未指定なら既定30分）
- 「即時失効」ではなく「次の検証間隔で失効」であることをユーザーに説明できるか
- パスワードリセット時にも SecurityStamp が変わるか（`ResetPasswordAsync` は内部で更新する）

## 参考

- [harness17/phycock](https://github.com/harness17/phycock) — 療養中に自主制作した体調管理ツール
- [ASP.NET Core Identity — SecurityStamp](https://learn.microsoft.com/ja-jp/aspnet/core/security/authentication/identity)
- [SecurityStampValidator](https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.identity.securitystampvalidator)
