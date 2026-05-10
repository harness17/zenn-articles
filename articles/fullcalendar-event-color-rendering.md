---
title: "FullCalendarでDTOの色が反映されない時に見たこと"
emoji: "🎨"
type: "tech"
topics: ["fullcalendar", "aspnetcore", "csharp", "javascript", "ui"]
published: true
---

## はじめに

ASP.NET Core MVC で作っている個人開発アプリで、FullCalendar に予定を色分け表示する機能を実装しました。

サーバー側の JSON DTO には色を返している。テストでも `backgroundColor` や `textColor` は入っている。それなのにブラウザで見ると、背景色が期待どおりに出ない。文字色も設計した色ではなく、白っぽく見える。

この記事では、そのときに見たポイントをまとめます。結論はシンプルで、FullCalendar の色表示は **DTO だけでなく、表示形式・カスタム描画・実ブラウザ上の computed style まで見る** 必要がありました。

## 最初は DTO に色を返せば十分だと思っていた

実装していたのは、予定の種類ごとにカレンダー上の色を変える機能です。たとえば、社外との会議系の予定は薄い赤、在宅作業の予定はティール系、その他の自由入力は白背景にする、といった形です。

サーバー側では FullCalendar に渡す DTO を用意しました。

```csharp
public class ScheduleEntryJsonDto
{
    public string Id { get; set; } = "";
    public string Title { get; set; } = "";
    public string Start { get; set; } = "";
    public string? End { get; set; }

    public string Color { get; set; } = "";
    public string BackgroundColor { get; set; } = "";
    public string BorderColor { get; set; } = "";
    public string TextColor { get; set; } = "";

    public ScheduleEntryExtendedProps ExtendedProps { get; set; } = new();
}
```

`Color` だけでなく、`BackgroundColor` / `BorderColor` / `TextColor` も返すようにしています。FullCalendar の Event Object には `backgroundColor`、`borderColor`、`textColor` があるため、最終的にはこの3つを明示しておく方が見通しがよいと判断しました。

実際の変換処理では、イベント分類と業務種別から色を決めています。

```csharp
private static ScheduleEntryColor GetColor(
    EventCategory category,
    WorkType? workType,
    bool isRemote)
{
    if (isRemote)
        return new("#DDEFEF", "#2C9A9A", "#134F4F");

    if (category != EventCategory.Work)
    {
        return category switch
        {
            EventCategory.Training => new("#F4E5F8", "#8E44AD", "#4A235A"),
            EventCategory.Meeting => new("#FCE4D6", "#ED7D31", "#7A3B00"),
            _ => new("#E7E6E6", "#A6A6A6", "#3C3C3C"),
        };
    }

    return workType switch
    {
        WorkType.Conference => new("#F4CCCC", "#C00000", "#7F1D1D"),
        WorkType.Other => new("#FFFFFF", "#ADB5BD", "#343A40"),
        _ => new("#E7E6E6", "#A6A6A6", "#3C3C3C"),
    };
}

private sealed record ScheduleEntryColor(
    string BackgroundColor,
    string BorderColor,
    string TextColor);
```

テストでも DTO の色は確認しました。

```csharp
[Fact]
public void GetEventsForCalendar_WorkEntry_SetsBackgroundBorderAndTextColors()
{
    var result = service.GetEventsForCalendar(
        "user-1",
        new DateOnly(2026, 5, 1),
        new DateOnly(2026, 5, 31));

    var item = Assert.Single(result);
    Assert.Equal("#F4CCCC", item.BackgroundColor);
    Assert.Equal("#C00000", item.BorderColor);
    Assert.Equal("#7F1D1D", item.TextColor);
    Assert.Equal(item.BackgroundColor, item.Color);
}
```

ここまで見ると、サーバー側は問題なさそうです。ただ、画面ではまだ期待した見た目になっていませんでした。

## 原因1: dayGrid の時間付きイベントは dot 表示になる

最初に見落としていたのは、FullCalendar の `eventDisplay` です。

FullCalendar の dayGrid では、既定の `auto` 表示だと、時間付きイベントは面ではなく dot 表示になります。つまり、DTO に背景色を渡していても、「背景色の面」がそもそも表示されない状態になります。

今回の予定は `09:00 - 12:00` のように時刻を持つイベントでした。そのため、月表示では dot event として描画されていました。

修正は、カレンダー側で `eventDisplay: 'block'` を指定することでした。

```javascript
calendar = new FullCalendar.Calendar(document.getElementById('calendar'), {
    initialView: 'dayGridMonth',
    locale: 'ja',
    height: 'auto',
    selectable: true,
    eventDisplay: 'block',
    dayMaxEvents: false,
    events: scheduleEntryUrls.events,
    eventContent: PhycockCalendar.renderRecordEvent,
    eventDidMount: function (info) {
        PhycockCalendar.applyEventColors(info);
    }
});
```

ここで一つ学びがありました。

JSON の `backgroundColor` が正しいことと、カレンダー上で背景色が面として見えることは別です。FullCalendar の表示形式が dot なら、背景色の設計は見た目に出ません。

## 原因2: eventContent のカスタム描画が文字色を上書きしていた

もう一つの原因は `eventContent` でした。

今回の予定は、タイトルだけでなく、時間帯・場所・状態・活動内容を複数行で出したかったため、FullCalendar の標準表示ではなくカスタム DOM を返しています。

```javascript
function renderRecordEvent(info) {
    const props = info.event.extendedProps || {};
    const container = document.createElement('div');
    container.className = 'record-calendar-event';

    appendLine(container, 'record-calendar-event__title',
        props.primaryText || info.event.title);
    appendLine(container, 'record-calendar-event__meta',
        props.secondaryText || info.timeText);
    appendLine(container, 'record-calendar-event__note',
        props.noteText);

    return { domNodes: [container] };
}
```

この構成自体は問題ありません。ただ、以前の実装では `eventContent` 側や CSS 側で文字色を固定していたため、DTO の `textColor` を渡しても見た目に反映されませんでした。

そこで、色の反映を `eventDidMount` に集約しました。

```javascript
function applyEventColors(info) {
    const main = info.el.querySelector('.fc-event-main');

    if (info.event.backgroundColor) {
        info.el.style.backgroundColor = info.event.backgroundColor;
    }
    if (info.event.borderColor) {
        info.el.style.borderColor = info.event.borderColor;
    }
    if (info.event.textColor) {
        info.el.style.color = info.event.textColor;
        if (main) {
            main.style.color = info.event.textColor;
        }
    }
}
```

FullCalendar に色を渡すだけでなく、自分で作った DOM のどこに色が効いているかを見る必要がありました。`eventContent` で DOM を差し替えるなら、その DOM に対する CSS も自分の責任になります。

## 原因3: 表示仕様に必要なデータ制約が足りなかった

色表示を直している途中で、別の問題も見つかりました。

イベント分類が「業務」の予定は、`WorkType` によって色を分けます。ところが、`EventCategory=Work` なのに `WorkType=null` の予定を作れると、色分け不能なデータができます。

これは表示側だけでは直せません。フォーム初期値とサーバー側バリデーションを入れました。

```csharp
public ScheduleEntryFormViewModel BuildCreateForm(
    string userId,
    DateOnly? date = null)
{
    return new ScheduleEntryFormViewModel
    {
        UserId = userId,
        Date = date ?? DateOnly.FromDateTime(DateTime.Today),
        Session = ScheduleSession.AM,
        Category = EventCategory.Work,
        WorkType = WorkType.Focused,
        StartTime = new TimeOnly(9, 0),
        EndTime = new TimeOnly(12, 0),
    };
}

private void ValidateWorkType(ScheduleEntryFormViewModel model)
{
    if (model.Category == EventCategory.Work && !model.WorkType.HasValue)
        ModelState.AddModelError(nameof(model.WorkType),
            "業務種別を選択してください。");
}
```

「色が出ない」という UI の問題から始まりましたが、最終的にはデータ制約にも手を入れることになりました。

表示仕様がデータの意味に依存している場合、CSS だけで直すと後でまた崩れます。今回なら、業務予定には業務種別が必要、という制約をサーバー側でも保証する必要がありました。

## 最後はブラウザで computed style まで確認した

この手の修正は、ユニットテストだけでは終われません。

サーバー側のテストでは、DTO に色が入っていることは確認できます。

- `BackgroundColor` が `#F4CCCC`
- `BorderColor` が `#C00000`
- `TextColor` が `#7F1D1D`
- 在宅作業の予定ではティール系の色が優先される
- その他の入力では白背景になる

ただし、FullCalendar が実際にどう DOM を作るか、CSS がどう当たるかはブラウザで見ないと分かりません。

最終確認では、ブラウザ上で予定を作成し、DOM の computed style を見ました。

```text
background-color: rgb(244, 204, 204)
border-color: rgb(192, 0, 0)
color: rgb(127, 29, 29)
```

さらに、在宅予定では次のように確認しました。

```text
background-color: rgb(221, 239, 239)
border-color: rgb(44, 154, 154)
color: rgb(19, 79, 79)
```

ここまで見て、ようやく「DTO も、FullCalendar の表示形式も、カスタム DOM も、実際の見た目も揃った」と判断できました。

## まとめ

FullCalendar の色表示で詰まったとき、今回見るべきだったポイントは3つでした。

1. **DTO の色が正しいか**  
   `backgroundColor` / `borderColor` / `textColor` を分けて返す。

2. **FullCalendar の表示形式が期待どおりか**  
   dayGrid の時間付きイベントは既定だと dot 表示になるため、面として見せたいなら `eventDisplay: 'block'` を指定する。

3. **カスタム描画と CSS が色を上書きしていないか**  
   `eventContent` で DOM を作るなら、`eventDidMount` や CSS まで含めて確認する。

「JSON は正しいのに UI が違う」ときは、サーバー側で止まらず、ブラウザ上の DOM と computed style まで見るのが近道でした。

今回の実装は個人開発アプリの一部です。基盤にしている ASP.NET Core MVC テンプレートは [DevNext](https://github.com/harness17/DevNext) に置いています。

## 参考リンク

- [FullCalendar: Event Display](https://fullcalendar.io/docs/event-display)
- [FullCalendar: eventDisplay](https://fullcalendar.io/docs/eventDisplay)
- [FullCalendar: Event Object](https://fullcalendar.io/docs/event-object)
- [DevNext](https://github.com/harness17/DevNext)
