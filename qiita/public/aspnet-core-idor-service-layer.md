---
title: ASP.NET Core MVCでIDOR対策をService層に置いた話
tags:
  - C#
  - WebAPI
  - Security
  - mvc
  - aspnetcore
private: false
updated_at: '2026-06-20T19:49:45+09:00'
id: 15a56a10da8909183505
organization_url_name: null
slide: false
ignorePublish: false
---

## 背景

療養中に自主制作した体調管理ツール（Phycock）を ASP.NET Core MVC で開発しています。

予定の編集・削除機能を実装したとき、ログイン済みの別ユーザーが URL を直打ちすると他人の予定データを操作できてしまう問題（IDOR）が起きる状態でした。

## 問題：`[Authorize]` だけでは他ユーザーのデータを守れない

最初の Controller はこうでした。

```csharp
[Authorize]
public IActionResult EditPartial(long id)
{
    var model = _repository.SelectById(id);
    return PartialView("_EditPartial", model);
}
```

`[Authorize]` は「ログインしているか」だけを確認します。`id=5` の予定が自分のものかどうかは確認しません。

別のログイン済みユーザーが `/ScheduleEntry/EditPartial?id=5` にアクセスすると、他人の予定が取得できます。これが **IDOR（Insecure Direct Object Reference）** です。

## 解決：Service 層でオーナーチェック

所有者チェックを Service 層に置きました。

```csharp
/// <summary>編集対象の通所予定を取得する。所有者でも Admin でもない場合は null。</summary>
public ScheduleEntryFormViewModel? GetForEdit(long id, string currentUserId, bool isAdmin)
{
    var entity = _repository.SelectById(id);
    if (entity == null || (!isAdmin && entity.UserId != currentUserId)) return null;

    return ToFormViewModel(entity);
}
```

データが存在しない場合と、所有者でも Admin でもない場合をまとめて `null` で返します。呼び出し側は「取れたかどうか」だけ見ればよくなります。

更新・削除も同じパターンです。

```csharp
/// <summary>通所予定を更新する。所有者でも Admin でもない場合は false。</summary>
public bool Update(ScheduleEntryFormViewModel model, string currentUserId, bool isAdmin)
{
    var entity = _repository.SelectById(model.Id);
    if (entity == null || (!isAdmin && entity.UserId != currentUserId)) return false;

    entity.Date = model.Date;
    // 省略
    _repository.Update(entity);
    return true;
}

/// <summary>通所予定を論理削除する。所有者でも Admin でもない場合は false。</summary>
public bool Delete(long id, string currentUserId, bool isAdmin)
{
    var entity = _repository.SelectById(id);
    if (entity == null || (!isAdmin && entity.UserId != currentUserId)) return false;

    _repository.LogicalDelete(entity);
    return true;
}
```

## Controller はシンプルになる

Service がオーナーチェックを担うと、Controller は「取れたか / 操作できたか」を処理するだけになります。

```csharp
[HttpGet]
public IActionResult EditPartial(long id)
{
    var model = _service.GetForEdit(id, GetCurrentUserId(), User.IsInRole("Admin"));
    if (model == null) return StatusCode(StatusCodes.Status403Forbidden);
    return PartialView("_EditPartial", model);
}

[HttpPost]
[ValidateAntiForgeryToken]
public IActionResult Edit(ScheduleEntryFormViewModel model)
{
    // バリデーション省略
    var updated = _service.Update(model, GetCurrentUserId(), User.IsInRole("Admin"));
    if (!updated) return StatusCode(StatusCodes.Status403Forbidden);
    return Json(new { success = true });
}

[HttpPost]
[ValidateAntiForgeryToken]
public IActionResult Delete(long id)
{
    var deleted = _service.Delete(id, GetCurrentUserId(), User.IsInRole("Admin"));
    if (!deleted) return StatusCode(StatusCodes.Status403Forbidden);
    return Json(new { success = true });
}
```

## なぜ Controller ではなく Service に置くか

Controller にチェックを書くと、同じロジックを複数のアクションメソッドに書くことになります。

Service に置くと：
- チェック漏れが起きにくい（Repository を直接触れるのは Service だけ）
- テストが書きやすい（Controller 層をモックしなくてよい）

テストはこうなります。

```csharp
[Fact]
public void GetForEdit_WithOtherUsersId_ReturnsNull()
{
    var repository = new Mock<ScheduleEntryRepository>(null!);
    repository.Setup(x => x.SelectById(1))
        .Returns(new ScheduleEntryEntity { Id = 1, UserId = "owner-user" });
    var service = new ScheduleEntryService(repository.Object);

    var result = service.GetForEdit(1, "other-user", isAdmin: false);

    Assert.Null(result);
}
```

## まとめ

- `[Authorize]` は「ログイン済みか」しか確認しない。IDOR の防止にはリソースの所有者チェックが別途必要
- Service の Get / Update / Delete でオーナーチェックを行い、権限がない場合は `null` / `false` を返す
- Controller は戻り値を見て `403 Forbidden` を返すだけ

実装は Phycock の `ScheduleEntryService.cs` / `ScheduleEntryController.cs` にあります。
