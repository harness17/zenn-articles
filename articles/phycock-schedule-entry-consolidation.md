---
title: "ASP.NET Core MVCでScheduleEntryに寄せた設計判断"
emoji: "🗂️"
type: "tech"
topics: ["aspnetcore", "csharp", "efcore", "mvc", "database"]
published: true
---

## はじめに

ASP.NET Core MVC で作っている個人開発アプリで、予定入力まわりのモデルを見直しました。

最初は、汎用的な予定を表す `Schedule` 系のテーブルと、実際の入力単位を表す `ScheduleEntry` を分けるつもりでした。汎用的な `Schedule` を置いておけば、あとから別種類の予定にも使えそうに見えたためです。

ただ、実装を進めると、画面・入力フォーム・カレンダー表示・テストで本当に扱っている中心は `ScheduleEntry` でした。結果として、旧 `Schedule` 系のテーブルを削除し、`ScheduleEntry` に寄せる判断をしました。

この記事では、そのときに見た判断軸をまとめます。実装は個人開発アプリの一部ですが、ドメイン固有の説明は避け、予定入力を扱う ASP.NET Core MVC アプリとして一般化して書きます。

## 最初は汎用的な予定モデルを置いていた

最初に考えていた構成は、汎用的な予定を持つ `Schedule` 系と、具体的な入力単位である `ScheduleEntry` を分ける形でした。

考え方としては自然です。予定という抽象概念を先に置いておけば、会議、作業、外出、リマインダーなどを同じ仕組みで扱えそうに見えます。

ただ、今回のアプリで実際に必要だったのは、かなり具体的な入力でした。

| 観点 | 汎用 `Schedule` 系 | `ScheduleEntry` |
|---|---|---|
| 主な目的 | 予定全般を表す | 1件の予定入力を表す |
| 日付・時間 | 開始日時・終了日時を汎用的に持つ | 日付、時間帯、開始時刻、終了時刻を入力画面に合わせて持つ |
| 表示 | 将来の複数用途を想定 | FullCalendar にそのまま渡す DTO の元になる |
| 検証 | 汎用ルールになりやすい | 入力画面の必須項目や組み合わせをそのまま検証できる |

抽象度だけを見ると、`Schedule` を残すほうがきれいに見えます。

しかし、実装中に頻繁に触るのは `ScheduleEntry` でした。作成フォームの初期値、編集、削除、カレンダー表示、今日の予定表示、色分け、入力値の検証がすべて `ScheduleEntry` 起点で進みます。

この時点で、「汎用的な予定モデルを残す理由」よりも、「実際の入力単位に寄せたほうが追いやすい理由」のほうが強くなりました。

## ScheduleEntry は画面の操作単位と一致していた

最終的に残した `ScheduleEntryEntity` は、画面から作る1件の予定入力に対応しています。実際のコードでは、日付、時間帯、状態、種別、開始・終了時刻、メモなどを持たせています。

以下は実コードを少し簡略化した例です。

```csharp:ScheduleEntryEntity.cs
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

この形にしたことで、画面で作成する単位と DB に保存する単位が揃いました。

フォーム側も同じ単位です。

```csharp:ScheduleEntryFormViewModel.cs
public class ScheduleEntryFormViewModel
{
    public long Id { get; set; }
    public string UserId { get; set; } = "";

    [Required(ErrorMessage = "日付は必須です")]
    public DateOnly Date { get; set; } = DateOnly.FromDateTime(DateTime.Today);

    public ScheduleSession Session { get; set; } = ScheduleSession.AM;
    public bool IsAtHome { get; set; }
    public ScheduleStatus Status { get; set; } = ScheduleStatus.Planned;
    public ActivityType ActivityType { get; set; } = ActivityType.Program;
    public ProgramType? ProgramType { get; set; }
    public TimeOnly? StartTime { get; set; }
    public TimeOnly? EndTime { get; set; }
    public string? Notes { get; set; }
}
```

ここで大事だったのは、`ScheduleEntry` が単なるテーブル名ではなく、操作単位そのものになっていたことです。

ユーザーが画面で作るのも `ScheduleEntry`、Service が保存するのも `ScheduleEntry`、カレンダーに出すのも `ScheduleEntry` から変換した DTO です。名前と責務が一致していると、修正時に追う場所が減ります。

## 汎用モデルを残すと変更範囲が増える

モデルを分けると、1つの変更で見る場所が増えます。

たとえば、予定の入力項目を1つ増やすとします。`Schedule` と `ScheduleEntry` が分かれている場合、どちらに持たせるのかを毎回判断する必要があります。

- 入力フォームの項目なのか
- 汎用予定の属性なのか
- カレンダー表示だけに必要な値なのか
- 履歴や参加者のような別テーブルに逃がすべき値なのか

この判断が必要な設計自体は悪くありません。複数の予定種別を本当に扱うなら、むしろ必要になる場面もあります。

ただ、今回の段階では、分けることで得られる拡張性より、分けたことで増える確認コストのほうが大きくなっていました。

現在の Service では、作成・更新・カレンダー表示が `ScheduleEntry` 起点でまとまっています。

```csharp:ScheduleEntryService.cs
public void Create(
    ScheduleEntryFormViewModel model,
    string currentUserId,
    bool isAdmin = false)
{
    var entity = ToEntity(model);
    entity.UserId = isAdmin && !string.IsNullOrWhiteSpace(model.UserId)
        ? model.UserId
        : currentUserId;

    _repository.Insert(entity);
}

public List<ScheduleEntryJsonDto> GetEventsForCalendar(
    string userId,
    DateOnly startDate,
    DateOnly endDate)
{
    return _repository.GetByUserAndRange(userId, startDate, endDate)
        .Select(ToJsonDto)
        .ToList();
}
```

作成時はフォームから Entity に変換して保存する。表示時は Entity から FullCalendar 用 DTO に変換する。この流れを `ScheduleEntryService` の中で追えます。

もしここに汎用 `Schedule` を挟むと、「フォームの値はどちらに入るのか」「DTO はどちらから作るのか」「更新時はどちらを正とするのか」が増えます。今回の用途では、その複雑さを払う理由が弱いと判断しました。

## 削除したのは ScheduleEvent 系の3テーブル

最終的には、旧 `Schedule` 系として使っていたテーブルを migration で削除しました。

実際には `ScheduleEvent`、`ScheduleEventHistory`、`ScheduleEventParticipant` を落としています。以下は migration の一部です。

```csharp:RemoveScheduleEventTables.cs
protected override void Up(MigrationBuilder migrationBuilder)
{
    migrationBuilder.DropTable(
        name: "ScheduleEvent");

    migrationBuilder.DropTable(
        name: "ScheduleEventHistory");

    migrationBuilder.DropTable(
        name: "ScheduleEventParticipant");
}
```

この変更で、予定入力の保存先は `ScheduleEntry` に絞られました。

もちろん、テーブルを落とす判断は軽くありません。既存データがある場合は、移行手順や退避、変換処理が必要です。今回は個人開発中の初期段階で、旧テーブルを使った運用データを前提にしていなかったため、削除を選びました。

:::message alert
業務アプリなら、ここは別判断になります。

- 既存データを `ScheduleEntry` に移す migration が必要か
- 履歴テーブルを残す必要があるか
- 参照している画面やバッチがないか
- ロールバック時に復元できるか

テーブル削除は、Entity クラスを消すだけでは終わりません。Controller、Service、Repository、View、テスト、seed data、migration の履歴まで見ます。
:::

今回も最終的な確認では、`DBContext` に残る予定系の `DbSet` が `ScheduleEntry` だけになっていることを見ました。

```csharp:ApplicationDbContext.cs
// 予定入力
public DbSet<ScheduleEntryEntity> ScheduleEntry { get; set; }
```

この状態になっていると、「予定入力の保存先はどこか」という問いに迷いがありません。

## 表示と検証も ScheduleEntry 起点にできた

`ScheduleEntry` に寄せてよかった点は、カレンダー表示や入力検証も同じ単位で考えられることでした。

FullCalendar に渡す DTO は `ScheduleEntryEntity` から作っています。

```csharp:ScheduleEntryService.cs
private static ScheduleEntryJsonDto ToJsonDto(ScheduleEntryEntity entity)
{
    var start = CombineDateAndTime(entity.Date, entity.StartTime);
    var end = CombineDateAndTime(entity.Date, entity.EndTime);
    var color = GetColor(entity.ActivityType, entity.ProgramType, entity.IsAtHome);

    return new ScheduleEntryJsonDto
    {
        Id = entity.Id.ToString(),
        Title = BuildTitle(entity),
        Start = start?.ToString("yyyy-MM-ddTHH:mm:ss")
            ?? entity.Date.ToString("yyyy-MM-dd"),
        End = end?.ToString("yyyy-MM-ddTHH:mm:ss"),
        Color = color.BackgroundColor,
        BackgroundColor = color.BackgroundColor,
        TextColor = color.TextColor,
    };
}
```

表示色は、活動種別や補助的な分類から決めています。これも `ScheduleEntry` の状態を見れば判断できます。

また、入力検証も同じ単位で扱えます。

```csharp:ScheduleEntryValidation.cs
private void ValidateProgramType(ScheduleEntryFormViewModel model)
{
    if (model.ActivityType == ActivityType.Program && !model.ProgramType.HasValue)
    {
        ModelState.AddModelError(
            nameof(model.ProgramType),
            "種別を選択してください。");
    }
}

private void ValidateTimeRange(ScheduleEntryFormViewModel model)
{
    if (model.StartTime.HasValue
        && model.EndTime.HasValue
        && model.EndTime.Value <= model.StartTime.Value)
    {
        ModelState.AddModelError(
            nameof(model.EndTime),
            "終了時刻は開始時刻より後に設定してください。");
    }
}
```

このあたりは、汎用 `Schedule` に置くより `ScheduleEntry` のフォームと並べて考えるほうが自然でした。

予定入力の分類があるから表示色が決まる。開始時刻と終了時刻があるから時間範囲を検証する。画面で入力する項目と、保存する項目と、表示に使う項目が同じモデルを向いています。

## テストで守りたい振る舞いも明確になった

`ScheduleEntry` に寄せたことで、テスト対象も分かりやすくなりました。

たとえば、作成時に投稿された `UserId` をそのまま信じないテストがあります。一般ユーザーの場合は、フォームに別の `UserId` が入っていても、現在のユーザー ID で保存します。

```csharp:ScheduleEntryServiceTests.cs
[Fact]
public void Create_AsMember_IgnoresPostedUserId()
{
    var repository = new Mock<ScheduleEntryRepository>(null!);
    ScheduleEntryEntity? inserted = null;
    repository.Setup(x => x.Insert(It.IsAny<ScheduleEntryEntity>()))
        .Callback<ScheduleEntryEntity>(entity => inserted = entity);
    var service = new ScheduleEntryService(repository.Object);

    service.Create(new ScheduleEntryFormViewModel
    {
        UserId = "posted-user",
        Date = new DateOnly(2026, 5, 3),
        Session = ScheduleSession.AM,
        Status = ScheduleStatus.Planned,
        ActivityType = ActivityType.Program,
    }, "current-user", isAdmin: false);

    Assert.NotNull(inserted);
    Assert.Equal("current-user", inserted.UserId);
}
```

これは予定入力そのものの権限制御です。汎用 `Schedule` と `ScheduleEntry` が分かれていると、どちらの Service で守るのかが曖昧になりやすい部分です。

ほかにも、初期フォームのプリセットや、カレンダー表示色を `ScheduleEntryService` のテストとして確認しています。

```csharp:ScheduleEntryServiceTests.cs
[Fact]
public void BuildCreateForm_SetsAmTimePreset()
{
    var repository = new Mock<ScheduleEntryRepository>(null!);
    var service = new ScheduleEntryService(repository.Object);

    var result = service.BuildCreateForm(
        "user-1",
        new DateOnly(2026, 5, 3));

    Assert.Equal(ScheduleSession.AM, result.Session);
    Assert.Equal(ActivityType.Program, result.ActivityType);
    Assert.Equal(ProgramType.SelfWork, result.ProgramType);
    Assert.Equal(new TimeOnly(9, 0), result.StartTime);
    Assert.Equal(new TimeOnly(12, 0), result.EndTime);
}
```

テスト名を見たときに、どの振る舞いを守っているのかが `ScheduleEntry` 起点で読める。この状態は、後から修正するときに効きます。

## 汎用化を捨てたわけではない

今回の判断は、「汎用的な予定モデルは不要」と言いたいわけではありません。

複数の予定種別を同じ仕組みで扱うアプリなら、汎用 `Schedule` や `Event` を中心に置く設計は有効です。参加者、繰り返し、公開範囲、履歴、通知などを共通化したいなら、抽象モデルを置いたほうが見通しがよくなる場面もあります。

今回違ったのは、そこまでの共通化がまだ必要なかったことです。

実際に必要だったのは、1つの予定入力画面を安定して作ることでした。その段階で汎用モデルを残すと、将来の可能性のために現在の読みやすさを払うことになります。

自分の判断軸は次の4つでした。

- 画面の操作単位と保存単位が一致しているか
- 検証ルールをどのモデルに置くか説明できるか
- 表示 DTO の変換元が明確か
- 変更時に見る Controller / Service / Repository / Test が増えすぎていないか

この4つを見ると、今回は `ScheduleEntry` に寄せるほうが自然でした。

## まとめ

`Schedule` と `ScheduleEntry` を分ける設計は、最初は拡張しやすそうに見えました。

ただ、実装を進めると、作成フォーム、DB 保存、カレンダー表示、入力検証、テストの中心は `ScheduleEntry` でした。そこで旧 `ScheduleEvent` 系のテーブルを削除し、予定入力の責務を `ScheduleEntry` に寄せました。

テーブルやモデルを分けるか迷ったときは、名前の抽象度だけではなく、「実際の変更時にどこを見ることになるか」を見ると判断しやすくなります。

今回のアプリは、ASP.NET Core MVC テンプレート [DevNext](https://github.com/harness17/DevNext) を元に作っています。関連するカレンダー表示の話は、以前書いた [FullCalendarでDTOの色が反映されない時に見たこと](https://zenn.dev/harness/articles/fullcalendar-event-color-rendering) にもまとめています。
