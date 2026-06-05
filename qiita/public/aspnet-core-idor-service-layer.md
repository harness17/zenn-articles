---
title: ASP.NET Core MVCでIDOR対策をService層に置ぁE��話
tags:
  - C#
  - WebAPI
  - Security
  - mvc
  - aspnetcore
private: false
updated_at: '2026-06-04T22:40:02+09:00'
id: 15a56a10da8909183505
organization_url_name: null
slide: false
ignorePublish: false
---

## 背景

療養中に自主制作した体調管琁E��ール�E�Ehycock�E�を ASP.NET Core MVC で開発してぁE��す、E
予定�E編雁E�E削除機�Eを実裁E��たとき、ログイン済みの別ユーザーぁEURL を直打ちすると他人の予定データを操作できてしまぁE��題！EDOR�E�が起きる状態でした、E
## 問題：`[Authorize]` だけでは他ユーザーのチE�Eタを守れなぁE
最初�E Controller はこうでした、E
```csharp
[Authorize]
public IActionResult EditPartial(long id)
{
    var model = _repository.SelectById(id);
    return PartialView("_EditPartial", model);
}
```

`[Authorize]` は「ログインしてぁE��か」だけを確認します。`id=5` の予定が自刁E�Eも�EかどぁE��は確認しません、E
別のログイン済みユーザーぁE`/ScheduleEntry/EditPartial?id=5` にアクセスすると、他人の予定が取得できます。これが **IDOR�E�Ensecure Direct Object Reference�E�E* です、E
## 解決�E�Service 層でオーナ�EチェチE��

所有老E��ェチE��めEService 層に置きました、E
```csharp
/// <summary>編雁E��象の通所予定を取得する。所有老E��めEAdmin でもなぁE��合�E null、E/summary>
public ScheduleEntryFormViewModel? GetForEdit(long id, string currentUserId, bool isAdmin)
{
    var entity = _repository.SelectById(id);
    if (entity == null || (!isAdmin && entity.UserId != currentUserId)) return null;

    return ToFormViewModel(entity);
}
```

チE�Eタが存在しなぁE��合と、所有老E��めEAdmin でもなぁE��合をまとめて `null` で返します。呼び出し�Eは「取れたかどぁE��」だけ見ればよくなります、E
更新・削除も同じパターンです、E
```csharp
/// <summary>通所予定を更新する。所有老E��めEAdmin でもなぁE��合�E false、E/summary>
public bool Update(ScheduleEntryFormViewModel model, string currentUserId, bool isAdmin)
{
    var entity = _repository.SelectById(model.Id);
    if (entity == null || (!isAdmin && entity.UserId != currentUserId)) return false;

    entity.Date = model.Date;
    // 省略
    _repository.Update(entity);
    return true;
}

/// <summary>通所予定を論理削除する。所有老E��めEAdmin でもなぁE��合�E false、E/summary>
public bool Delete(long id, string currentUserId, bool isAdmin)
{
    var entity = _repository.SelectById(id);
    if (entity == null || (!isAdmin && entity.UserId != currentUserId)) return false;

    _repository.LogicalDelete(entity);
    return true;
}
```

## Controller はシンプルになめE
Service がオーナ�EチェチE��を担ぁE��、Controller は「取れたぁE/ 操作できたか」を処琁E��るだけになります、E
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
    // バリチE�Eション省略
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

## なぁEController ではなぁEService に置くか

Controller にチェチE��を書くと、同じロジチE��を褁E��のアクションメソチE��に書くことになります、E
Service に置くと�E�E- チェチE��漏れが起きにくい�E�Eepository を直接触れるのは Service だけ！E- チE��トが書きやすい�E�Eontroller 層をモチE��しなくてよい�E�E
チE��ト�Eこうなります、E
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

## まとめE
- `[Authorize]` は「ログイン済みか」しか確認しなぁE��EDOR の防止にはリソースの所有老E��ェチE��が別途忁E��E- Service の Get / Update / Delete でオーナ�EチェチE��を行い、権限がなぁE��合�E `null` / `false` を返す
- Controller は戻り値を見て `403 Forbidden` を返すだぁE
実裁E�E Phycock の `ScheduleEntryService.cs` / `ScheduleEntryController.cs` にあります、E
