---
title: ASP.NET Core MVC のフォームで Entity を直接使うのをやめて FormViewModel を分けた話
tags:
  - C#
  - ASP.NET
  - mvc
  - 個人開発
  - aspnetcore
private: false
updated_at: '2026-06-05T23:04:10+09:00'
id: c05c947d8115f23bff90
organization_url_name: null
slide: false
ignorePublish: false
---

## 何を整理したか

体調管理ツール Phycock（ASP.NET Core 10 / MVC）を作るとき、入力フォームをどう実装するか改めて整理した。

「フォームに Entity を直接バインドする」方法は手っ取り早く見えるが、以下の問題が積み重なる：

- DB 都合のプロパティ（作成日、削除フラグ）がフォームに露出する
- バリデーション属性（`[Required]` など）を Entity に書くとドメインロジックが汚れる
- 画面専用のデフォルト値（「今日の日付を初期値にする」など）の置き場がない
- Edit フォームで「取得した Entity → フォーム → 再マッピング → 保存」の流れが追いにくい

Phycock の通所予定フォームで、Entity と FormViewModel を明確に分けた実装をしたので整理する。

## Entity と FormViewModel の役割

### ScheduleEntryEntity — DB 構造の担当

```csharp
[Table("ScheduleEntry")]
public class ScheduleEntryEntity : PhycockEntityBase
{
    [Required]
    [MaxLength(450)]
    public string UserId { get; set; } = "";

    public DateOnly Date { get; set; }
    public ScheduleSession Session { get; set; }
    public bool IsAtHome { get; set; }
    public ScheduleStatus Status { get; set; }
    public ActivityType ActivityType { get; set; }
    public ProgramType? ProgramType { get; set; }

    [MaxLength(200)]
    public string? ActivityNote { get; set; }

    public TimeOnly? StartTime { get; set; }
    public TimeOnly? EndTime { get; set; }

    [MaxLength(1000)]
    public string? Notes { get; set; }
}
```

`PhycockEntityBase` が `Id`・`CreatedAt`・`UpdatedAt`・`IsDeleted` を持つ。テーブル構造を表すだけで、画面都合のバリデーションや表示名は持たない。

### ScheduleEntryFormViewModel — フォームの担当

```csharp
public class ScheduleEntryFormViewModel
{
    public long Id { get; set; }
    public string UserId { get; set; } = "";

    [Required(ErrorMessage = "日付は必須です")]
    [Display(Name = "日付")]
    public DateOnly Date { get; set; } = DateOnly.FromDateTime(DateTime.Today);

    [Display(Name = "時間帯")]
    public ScheduleSession Session { get; set; } = ScheduleSession.AM;

    [Display(Name = "在宅利用")]
    public bool IsAtHome { get; set; }

    [Display(Name = "状態")]
    public ScheduleStatus Status { get; set; } = ScheduleStatus.Planned;

    [Display(Name = "活動種別")]
    public ActivityType ActivityType { get; set; } = ActivityType.Program;

    [Display(Name = "プログラム種別")]
    public ProgramType? ProgramType { get; set; }

    [MaxLength(200, ErrorMessage = "活動内容は200文字以内で入力してください")]
    [Display(Name = "活動内容")]
    public string? ActivityNote { get; set; }

    [Display(Name = "開始時刻")]
    public TimeOnly? StartTime { get; set; }

    [Display(Name = "終了時刻")]
    public TimeOnly? EndTime { get; set; }

    [MaxLength(1000, ErrorMessage = "振り返りは1000文字以内で入力してください")]
    [Display(Name = "振り返り")]
    public string? Notes { get; set; }
}
```

Entity と比べると：

| 観点 | Entity | FormViewModel |
|------|--------|---------------|
| `[Required]` / `[MaxLength]` | DB 制約としてのみ | 画面バリデーションのエラーメッセージ付き |
| `[Display(Name = ...)]` | なし | View で `asp-for` を使うと自動でラベルに展開される |
| デフォルト値 | なし | `DateOnly.FromDateTime(DateTime.Today)` など |
| 作成日・削除フラグ | 基底クラスに持つ | 持たない（フォームに不要） |

## Controller — FormViewModel だけ受け取る

```csharp
[HttpGet]
public async Task<IActionResult> CreatePartial(DateTime? date)
{
    var userId = await ResolveTargetUserIdAsync();
    if (string.IsNullOrWhiteSpace(userId)) return StatusCode(403);
    return PartialView("_CreatePartial", _service.BuildCreateForm(userId, date));
}

[HttpPost]
[ValidateAntiForgeryToken]
public async Task<IActionResult> Create(ScheduleEntryFormViewModel model)
{
    ValidateProgramType(model);
    ValidateTimeRange(model);
    if (!ModelState.IsValid) return PartialView("_CreatePartial", model);

    _service.Create(model, GetCurrentUserId(), User.IsInRole("Admin"));
    return Json(new { success = true });
}
```

GET では `_service.BuildCreateForm(userId, date)` が返す ViewModel をそのまま View に渡す。POST では受け取った ViewModel のバリデーションを確認してからサービスに渡す。Controller は Entity の存在を知らない。

## Service — デフォルト値の生成とマッピング

Controller から Entity 操作を切り離す際に、3 つの役割を Service 層に置いた。

### ① デフォルト値付きフォームの生成

```csharp
public ScheduleEntryFormViewModel BuildCreateForm(string currentUserId, DateOnly? date = null)
{
    return new ScheduleEntryFormViewModel
    {
        UserId = currentUserId,
        Date = date ?? DateOnly.FromDateTime(DateTime.Today),
        Session = ScheduleSession.AM,
        ActivityType = ActivityType.Program,
        ProgramType = ProgramType.SelfWork,
        StartTime = new TimeOnly(9, 0),
        EndTime = new TimeOnly(12, 0),
    };
}
```

「新規登録時のデフォルト値」はビジネスルールなので Controller ではなく Service に置いた。「AM セッションで 9:00〜12:00 が初期値」という仕様はここだけに書かれている。

### ② FormViewModel → Entity への変換

```csharp
private static ScheduleEntryEntity ToEntity(ScheduleEntryFormViewModel model)
{
    return new ScheduleEntryEntity
    {
        UserId = model.UserId,
        Date = model.Date,
        Session = model.Session,
        IsAtHome = model.IsAtHome,
        Status = model.Status,
        ActivityType = model.ActivityType,
        ProgramType = model.ActivityType == ActivityType.Program ? model.ProgramType : null,
        ActivityNote = model.ActivityNote,
        StartTime = model.StartTime,
        EndTime = model.EndTime,
        Notes = model.Notes,
    };
}
```

`ProgramType` の処理がポイントで、`ActivityType` が `Program` でなければ `null` に正規化する。ViewModel は「選択値をそのまま保持」し、Entity 保存時にビジネスルールで整形するという分担になっている。

### ③ Entity → FormViewModel への変換（Edit 用）

```csharp
public ScheduleEntryFormViewModel? GetForEdit(long id, string currentUserId, bool isAdmin)
{
    var entity = _repository.SelectById(id);
    if (entity == null || (!isAdmin && entity.UserId != currentUserId)) return null;
    return ToFormViewModel(entity);
}
```

認可チェックと ViewModel 変換を同時に行う。`null` が返れば Controller は 403 を返す。

## まとめ

この整理で得られた効果：

- **Entity は DB 構造だけ担う** — マイグレーション対象を明確に絞れる
- **FormViewModel はフォーム都合だけ担う** — `[Display]` / `[Required]` / デフォルト値が View 寄りの層に集まる
- **Controller は変換ロジックを知らない** — `ViewModel → Service → 保存` の流れが単純
- **Service のテストが書きやすい** — `BuildCreateForm` / `ToEntity` / `GetForEdit` を単体でテストできる

どこに何を置くかの迷いが少なくなった。

## 参考リンク

- [Phycock リポジトリ](https://github.com/harness17/phycock) — 本文のコードはここから
- [ASP.NET Core モデル バインドの概要（公式）](https://learn.microsoft.com/ja-jp/aspnet/core/mvc/models/model-binding)
- [ASP.NET Core のモデルの検証（公式）](https://learn.microsoft.com/ja-jp/aspnet/core/mvc/models/validation)
