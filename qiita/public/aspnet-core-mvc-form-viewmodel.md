---
title: "ASP.NET Core MVCのフォームにEntityを直接使ぁE�EをやめてFormViewModelを�Eけた話"
tags:
  - AspNetCore
  - csharp
  - mvc
  - design
  - security
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

## 背景

療養中に自主制作した体調管琁E��ール�E�Ehycock�E�で、フォームからの入力受付を Entity クラス�E�EScheduleEntryEntity`�E�で直接受け取ってぁE��時期がありました、E
DB のチE�Eブル定義と一致してぁE��記述が一箁E��に収まるよぁE��見えましたが、実裁E��進めると問題が重なりました、E
## 問顁E�E�バリチE�Eション属性ぁEEntity に入り込む

`[Required(ErrorMessage = "日付�E忁E��でぁE)]` のような、画面向けのバリチE�EションメチE��ージめEEntity に書く忁E��が出てきます、E
Entity はチE�Eブルとのマッピングが目皁E��ので、本来は `[MaxLength(200)]`�E�カラム長制紁E���Eような DB 向けの属性を置く場所です。「�E力フォームのエラーメチE��ージ」を Entity に書くと、UI の都合と DB の都合が一つのクラスに混在します、E
```csharp
// Entity にフォーム用の属性が混入してぁE��例（避けたぁE��ターン�E�E[Table("ScheduleEntry")]
public class ScheduleEntryEntity
{
    [Required(ErrorMessage = "日付�E忁E��でぁE)]  // ↁEUIの都吁E    [Display(Name = "日仁E)]                      // ↁEUIの都吁E    public DateOnly Date { get; set; }

    [MaxLength(200)]  // ↁEDBの都吁E    public string? ActivityNote { get; set; }
}
```

## 問顁E�E�フォームのチE��ォルト値めEEntity に持てなぁE
「作�Eフォームを開ぁE��とき時間帯は AM にしておく」「状態�E予定済みにしておく」とぁE��ぁEUI のチE��ォルト値めEEntity に持たせると、DB から取得したデータにチE��ォルト値が混入するリスクがあります、E
```csharp
// Entity にUIチE��ォルトを書くと DB 読み取り時にも影響する
public ScheduleSession Session { get; set; } = ScheduleSession.AM;  // 問顁E```

## 問顁E�E�UserId が外部から bind されめE
`[Authorize]` でログイン確認�Eしても、フォームに含まれる `UserId` フィールドをそ�Eまま受け取ると、クライアントが任意�E `UserId` めEPOST できます！EDOR につながる�E�、E
`[Bind(Exclude="UserId")]` で除外する方法もありますが、どのフィールドを除外するかを呼び出し�Eに毎回意識させる形になります、E
## 解決�E�FormViewModel を�Eける

```csharp
/// <summary>通所予定�E作�E・編雁E��ォーム ViewModel、E/summary>
public class ScheduleEntryFormViewModel
{
    public long Id { get; set; }
    public string UserId { get; set; } = "";

    [Required(ErrorMessage = "日付�E忁E��でぁE)]
    [Display(Name = "日仁E)]
    public DateOnly Date { get; set; } = DateOnly.FromDateTime(DateTime.Today);

    [Display(Name = "時間帯")]
    public ScheduleSession Session { get; set; } = ScheduleSession.AM;

    [Display(Name = "状慁E)]
    public ScheduleStatus Status { get; set; } = ScheduleStatus.Planned;

    [Display(Name = "活動種別")]
    public ActivityType ActivityType { get; set; } = ActivityType.Program;

    [MaxLength(200, ErrorMessage = "活動�E容は200斁E��以冁E��入力してください")]
    [Display(Name = "活動�E容")]
    public string? ActivityNote { get; set; }

    [Display(Name = "開始時刻")]
    public TimeOnly? StartTime { get; set; }

    [Display(Name = "終亁E��刻")]
    public TimeOnly? EndTime { get; set; }

    [MaxLength(1000, ErrorMessage = "振り返りは1000斁E��以冁E��入力してください")]
    [Display(Name = "振り返り")]
    public string? Notes { get; set; }
}
```

ViewModel には�E�E- `[Required(ErrorMessage = "...")]` など UI 向けのバリチE�Eション属性を置ぁE- フォームを開ぁE��とき�EチE��ォルト値を持たせめE- `UserId` はフィールドとして持つが、Controller 側で `GetCurrentUserId()` で上書きすめE
Entity からは、UI 向けの属性を除きます、E
```csharp
[Table("ScheduleEntry")]
public class ScheduleEntryEntity : PhycockEntityBase
{
    [Required]
    [MaxLength(450)]
    public string UserId { get; set; } = "";

    public DateOnly Date { get; set; }
    public ScheduleSession Session { get; set; }
    // 省略

    [MaxLength(200)]
    public string? ActivityNote { get; set; }
}
```

## Service でのマッピング

フォームと Entity の変換は Service 層でめE��ます、Eontroller に変換コードが散ら�EらなぁE��ぁE��します、E
```csharp
public void Create(ScheduleEntryFormViewModel model, string currentUserId, bool isAdmin = false)
{
    var entity = ToEntity(model);
    // ポイント：フォームに含まれる UserId を無視して currentUserId を使ぁE    entity.UserId = isAdmin && !string.IsNullOrWhiteSpace(model.UserId)
        ? model.UserId
        : currentUserId;

    _repository.Insert(entity);
}

private static ScheduleEntryEntity ToEntity(ScheduleEntryFormViewModel model)
{
    return new ScheduleEntryEntity
    {
        UserId = model.UserId,
        Date = model.Date,
        Session = model.Session,
        ActivityType = model.ActivityType,
        ProgramType = model.ActivityType == ActivityType.Program ? model.ProgramType : null,
        ActivityNote = model.ActivityNote,
        StartTime = model.StartTime,
        EndTime = model.EndTime,
        Notes = model.Notes,
    };
}
```

## 比輁E
| 観点 | Entity 直接バインチE| FormViewModel を�Eける |
|------|------------------|---------------------|
| バリチE�Eション | Entity に UI 属性が混入 | ViewModel に UI 属性、Entity に DB 属性 |
| チE��ォルト値 | Entity のチE��ォルト値がDB読み取りに影響 | ViewModel のチE��ォルト値はフォーム専用 |
| UserId のセキュリチE�� | 外部からバインドされるリスク | Service 側で `currentUserId` を使ぁE��とを一箁E��で保証できる |
| 変更箁E�� | フォーム追加 = Entity 変更 | フォーム追加 = ViewModel 変更�E�Entity は影響を受けにくい�E�E|

## まとめE
- Entity はチE�Eブルマッピング、FormViewModel はフォームバインドと刁E��めE- バリチE�Eション属性とチE��ォルト値は ViewModel に置ぁE- フォームから渡されぁE`UserId` は Controller / Service で `currentUserId` に差し替える

実裁E�E Phycock の `ScheduleEntryViewModels.cs` / `ScheduleEntryEntity.cs` / `ScheduleEntryService.cs` にあります、E
