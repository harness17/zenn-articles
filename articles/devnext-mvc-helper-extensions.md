---
title: "ASP.NET MVCの自作HelperをASP.NET Coreに移植した話"
emoji: "🧩"
type: "tech"
topics: ["aspnetcore", "csharp", "razor", "mvc", "htmlhelper"]
published: true
---

## はじめに

ASP.NET Core MVC で作っているテンプレート [DevNext](https://github.com/harness17/DevNext) に、ASP.NET MVC 時代に使っていた自作 Helper 群を移植しました。

移植したのは、改行表示、Enum のラジオボタン化、選択リストのチェックボックス化、ページャー、部分ビュー用の `PartialFor` などです。最初は「同じ HTML を出せればよい」と考えがちですが、実際に移してみると、HTML 文字列を作るだけでは足りませんでした。

Razor のエンコード、`name` / `id` の生成、`label` との関連付け、POST 時の model binding まで含めて移植する必要がありました。

この記事を通したテーマは「画面に表示するだけでなく、POST で値が正しくサーバーへ戻る“フォームの契約”を Helper 側で守る」ことです。以降の各セクションは、戻り値・選択部品・ページャー・部分ビューという別々の話に見えますが、いずれもこの契約を崩さないための移植作業として読めます。

## Helperの戻り値をIHtmlContentに寄せる

まず見直したのは、Helper の戻り値です。

ASP.NET Core の Razor で HTML として出したい内容は、文字列ではなく `IHtmlContent` として返す形に寄せました。たとえば、テキストの改行を `<br />` に変換する Helper は次のようにしています。

```csharp
public static IHtmlContent FormatNewLines(this IHtmlHelper helper, string? text)
{
    var encodedText = WebUtility.HtmlEncode(text ?? string.Empty)
        .Replace("\r\n", "<br />")
        .Replace("\r", "<br />")
        .Replace("\n", "<br />");

    return new HtmlString(encodedText);
}
```

ここで大事なのは、先に `WebUtility.HtmlEncode` を通してから、改行だけを `<br />` に置き換えている点です。

入力文字列に `<script>` のような文字が入っていても、そのまま HTML として実行されないようにする。そのうえで、表示上必要な改行だけを HTML に変換します。

表示を少し便利にするだけの Helper でも、エンコード順序を雑にすると XSS の入口になります。移植時は「以前と同じ表示になるか」だけでなく、「Core 側で HTML として安全に扱えているか」も見る必要がありました。

## ラジオボタンとチェックボックスは実用部分まで見る

ラジオボタンやチェックボックスの Helper は、今回の記事で一番実用寄りに書ける部分です。

選択肢を並べるだけなら、HTML 文字列を連結しても画面には出ます。ただ、フォーム部品として使うなら、それだけでは足りません。

- POST 時に model binding される `name` になっているか
- `label for` と `input id` が対応しているか
- 既存値があるときに checked になるか
- チェックボックスの未選択時をどう扱うか

このあたりまで見ないと、「表示はできるがフォームとしては弱い Helper」になります。

DevNext のチェックボックス Helper では、式からプロパティ名を取り出し、`TemplateInfo.GetFullHtmlFieldName` で Razor 側の命名規則に合わせています。`TemplateInfo` は Razor が View 内で input の `name` / `id` をどう組み立てるかを保持する情報で、`GetFullHtmlFieldName` はプロパティ名を、実際に出力される完全な `name` 属性（親モデルの prefix を含んだ形）へ変換します。標準の `Html.CheckBoxFor` などが内部で行っている命名を、自作 Helper でも同じ規則で再現するために必要です。

```csharp
var name = GetExpressionText(htmlHelper, expression);
var metadata = GetMetadata(htmlHelper, expression);
var fullName = htmlHelper.ViewContext.ViewData.TemplateInfo.GetFullHtmlFieldName(name);
var id = $"{NormalizeId(fullName)}-{item.Value}";

var checkBox = new TagBuilder("input");
checkBox.TagRenderMode = TagRenderMode.SelfClosing;
checkBox.MergeAttribute("id", id);
checkBox.MergeAttribute("type", "checkbox");
checkBox.MergeAttribute("name", fullName, replaceExisting: true);
checkBox.MergeAttribute("value", item.Value);
```

`name` を自前の文字列だけで組み立てると、通常の View では動いても、部分ビューやネストした ViewModel で崩れることがあります。`GetFullHtmlFieldName` を通すことで、親側の prefix を含めた名前にできます。

選択状態も、単に `SelectListItem.Selected` だけを見るのではなく、現在の Model に含まれる値も見ています。

```csharp
if (item.Selected || IsSelected(metadata.Model, item.Value))
{
    checkBox.MergeAttribute("checked", "checked");
}

private static bool IsSelected(object? model, string? value)
{
    return model is IEnumerable<string> selectedValues && selectedValues.Any(x => x == value);
}
```

編集画面では、画面を開いた時点で保存済みの値がチェック済みになっている必要があります。ここを落とすと、新規作成では動いているように見えても、編集画面で使いにくくなります。

チェックボックスでは hidden input も併設しています。

```csharp
var hidden = new TagBuilder("input");
hidden.TagRenderMode = TagRenderMode.SelfClosing;
hidden.MergeAttribute("type", "hidden");
hidden.MergeAttribute("name", fullName, replaceExisting: true);

var label = htmlHelper.Label(id, item.Text, labelHtmlAttributes).ToHtmlString();
var content = checkBox.ToHtmlString() + hidden.ToHtmlString();
```

チェックボックスは未選択だと値が送信されません。複数選択の仕様によっては別の扱いにする余地もありますが、Helper としては「未選択時に何が送られるか」を意識しておく必要があります。

ラジオボタンも同じで、`id` と `label for` を対応させています。

```csharp
var id = $"{idFullName}_{item.Value}";
var radio = htmlHelper.RadioButtonFor(expression, item.Value, attributes).ToHtmlString();
var label = htmlHelper.Label(id, item.Text, labelhtmlAttributes).ToHtmlString();
sb.Append($"<div class=\"{divClass}\"> {radio} {label} </div>");
```

ラジオボタン・チェックボックスは、見た目だけならすぐ作れます。ただ、実用できる Helper として見るなら、`name`、`id`、`label`、checked 判定、未選択時の送信まで含めて確認したほうがよいと感じました。

## ページャーはTagBuilderで状態を分ける

ページャーも HTML 文字列連結だけで作りたくなる部品です。

ただ、現在ページ、無効状態、前へ・次へ、ページ番号リンクを扱うと、状態分岐が増えます。DevNext では `TagBuilder` を使い、`li` / `a` / `span` を組み立てる形にしました。

```csharp
if (active)
{
    link = new TagBuilder("span");
    link.MergeAttribute("aria-current", "page");
}
else
{
    link = new TagBuilder("a");
    link.MergeAttribute("href", pageUrlFactory(zeroBasedPage + 1));
}

link.AddCssClass("page-link");
if (disabled)
{
    link.MergeAttribute("tabindex", "-1");
    link.MergeAttribute("aria-disabled", "true");
}
```

現在ページはリンクではなく `span` にしています。同じページへのリンクを出すより、現在位置として表したほうが意図が明確です。

また、無効状態では class だけでなく `aria-disabled` と `tabindex` も付けています。見た目だけ無効にするのではなく、HTML としても状態を持たせるためです。

ページ番号の境界も Helper 内で丸めています。

```csharp
totalPages = Math.Max(totalPages, 1);
currentPage = Math.Clamp(currentPage, 1, totalPages);
```

呼び出し側から `0` や総ページ数を超える値が来ても、ページャー側で破綻しないようにしています。共通 Helper に入れるなら、こうした境界値の扱いも部品側に寄せたほうが使いやすくなります。

## PartialForではHtmlFieldPrefixを引き継ぐ

移植時に特に注意したのが、部分ビュー用の `PartialFor` です。

部分ビューを共通化すると、見た目はすぐ再利用できます。ただ、POST 後に値が戻らない場合があります。原因になりやすいのが、input の `name` から親モデルの prefix が落ちることです。

DevNext では、サブモデルの部分ビューを出すときに `TemplateInfo.HtmlFieldPrefix` を引き継ぐようにしました。

```csharp
public static IHtmlContent PartialFor<TModel, TProperty>(
    this IHtmlHelper<TModel> helper,
    Expression<Func<TModel, TProperty>> expression,
    string partialViewName)
{
    var name = GetExpressionText(helper, expression);
    var metadata = GetMetadata(helper, expression);
    var viewData = new ViewDataDictionary(helper.ViewData)
    {
        Model = metadata.Model
    };
    viewData.TemplateInfo.HtmlFieldPrefix =
        JoinPrefix(helper.ViewData.TemplateInfo.HtmlFieldPrefix, name);

    return helper.PartialAsync(partialViewName, metadata.Model, viewData)
        .GetAwaiter()
        .GetResult();
}
```

`Parent.Child.Name` のような形で bind されるべき項目が、部分ビュー内で `Name` だけになると、POST 時に親モデルへ戻せません。Helper 側で prefix をつなぐことで、部分ビューを共通化しても model binding の文脈を保てます。

この実装では `PartialAsync(...).GetAwaiter().GetResult()` を使っています。移植時には同期 Helper として扱いやすい一方、改善するなら非同期 Helper として呼び出す形も検討できます。記事としては、ここを「現時点の実装」と「今後の改善余地」に分けて書くと正直です。

## ViewImportsに登録して入口をまとめる

Helper を作っただけでは、Razor View からは使えません。

DevNext では `_ViewImports.cshtml` に namespace を追加しました。

```razor
@using Site.Models
@using Site.Common
@using Site.Entity
@using Dev.CommonLibrary.Entity
@using Dev.CommonLibrary.Extensions.Helper
@using Microsoft.AspNetCore.Mvc.Rendering
@addTagHelper *, Microsoft.AspNetCore.Mvc.TagHelpers
```

各 View に `@using` を散らすと、あとから Helper の置き場所を変えるときに修正範囲が広がります。テンプレートとして使う DevNext では、View 側の入口を `_ViewImports.cshtml` に寄せるほうが管理しやすいと判断しました。

## まとめ

ASP.NET MVC の自作 Helper を ASP.NET Core に移植するとき、見るべきポイントは「同じ HTML が出るか」だけではありませんでした。

1. Helper の戻り値を `IHtmlContent` に寄せ、エンコード順序を崩さない
2. ラジオボタン・チェックボックスは `name` / `id` / `label` / checked 判定まで実用できる形にする
3. 部分ビューでは `HtmlFieldPrefix` を維持して model binding を壊さない

DevNext では、旧 MVC の資産をそのまま残すのではなく、Razor のエンコード、フォーム部品の命名規則、POST 時の model binding に合わせ直す作業として Helper を移植しました。

フォーム部品の Helper は地味ですが、業務系 Web アプリでは繰り返し出てきます。だからこそ、表示だけでなく、送信・編集・再利用まで含めて確認しておく価値がありました。

## 参考リンク

- [DevNext](https://github.com/harness17/DevNext) - 本記事で扱った ASP.NET Core MVC テンプレート
- [ASP.NET Core のフォーム Tag Helpers](https://learn.microsoft.com/aspnet/core/mvc/views/working-with-forms) - `name` / `id` / model binding の標準挙動を確認する資料
- [ASP.NET Core の Partial views](https://learn.microsoft.com/aspnet/core/mvc/views/partial) - 部分ビューの扱いと `PartialFor` 移植時の前提を確認する資料
- [IHtmlContent Interface](https://learn.microsoft.com/dotnet/api/microsoft.aspnetcore.html.ihtmlcontent) - Helper の戻り値を HTML として扱うための型
- [TagBuilder Class](https://learn.microsoft.com/dotnet/api/microsoft.aspnetcore.mvc.rendering.tagbuilder) - input や pager の HTML 要素を組み立てるために使った型
