# 構成メモ: ASP.NET MVC の自作 Helper を ASP.NET Core に移植したときに見たこと

## メタ情報

- **slug 案**: `devnext-mvc-helper-extensions`
- **type**: tech
- **emoji**: 🧩
- **topics**: `aspnetcore` / `csharp` / `razor` / `mvc` / `htmlhelper`
- **想定文字数**: 2500〜3500字
- **想定執筆時間**: 4〜5時間
- **ステータス**: 構成中

## タイトル案

| 案 | タイトル | 強み |
|----|---------|------|
| **A**（推奨） | ASP.NET MVC の自作 Helper を ASP.NET Core に移植したときに見たこと | 体験ベースで、移植時の詰まりが伝わる |
| B | MVC Helper Extensions を ASP.NET Core に移植して DevNext に入れた話 | DevNext の宣伝と実装元が分かりやすい |
| C | Razor の共通表示を `TagBuilder` と `IHtmlContent` で移植した話 | 技術要素が前に出る |

→ **A 推奨**。単なる Helper 解説ではなく、「旧 MVC の資産を Core に移すとき、どこをそのまま持ち込めて、どこを作法に合わせ直したか」という体験記事にできる。

---

## 想定読者

ASP.NET MVC から ASP.NET Core MVC に移行していて、Razor View の自作 Helper、ページャー、ラジオボタン・チェックボックス生成をどう持ち込むかで迷っている C# エンジニア。

---

## 記事の核

旧 MVC で使っていた Helper を ASP.NET Core に移植するとき、最初は「同じ HTML を出せればよい」と考えがちです。実際には、単純な文字列連結ではなく、次の3点を Core 側の作法に寄せる必要がありました。

1. **出力型を `MvcHtmlString` ではなく `IHtmlContent` にする**
2. **input / label / pager は `TagBuilder` と既存の `IHtmlHelper` を使って組み立てる**
3. **部分ビューでは `TemplateInfo.HtmlFieldPrefix` を維持して、model binding の name を壊さない**

記事の主張は「Helper は便利メソッド集として移植するのではなく、Razor のエンコード、`name` / `id` 生成、model binding に沿わせて移植する」です。

---

## 構成

### はじめに（200〜300字）

- DevNext は ASP.NET Core 10 製の業務系 Web アプリ向けテンプレート。
- 既存の MVC 資産として、Razor View で使う自作 Helper 群があった。
- `feat: port mvc helper extensions` で Helper を Core 側に移植した。
- この記事では、移植時に見た `IHtmlContent` / `TagBuilder` / `HtmlFieldPrefix` の3点を書く。
- 導入文では「HTML が出れば終わりではなく、POST 時の model binding まで含めて移植する必要があった」と置く。

### セクション1: Helper の戻り値を `IHtmlContent` に寄せる（500〜600字）

- 伝えること:
  - ASP.NET Core の Razor では、HTML として出したい内容を `IHtmlContent` として返す。
  - 改行表示のような単純な Helper でも、エンコードしてから `<br />` に変換する順序を崩さない。
- 具体例:

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

- 書くポイント:
  - 先に HTML エンコードし、入力文字列中のタグをそのまま実行しない。
  - その後で改行だけを `<br />` に変換する。
  - 「表示を少し便利にするだけ」の Helper でも、エンコード順序を間違えると XSS の入口になる。

### セクション2: ラジオボタン・チェックボックスは name/id 生成を壊さない（700〜900字）

- 伝えること:
  - 複数選択や Enum 表示は共通化したくなるが、`name` と `id` を雑に作ると model binding や label の関連付けが壊れる。
  - `ModelExpressionProvider` と `TemplateInfo.GetFullHtmlFieldName` を使い、Razor の命名規則に寄せる。
- 具体例:

```csharp
var name = GetExpressionText(htmlHelper, expression);
var fullName = htmlHelper.ViewContext.ViewData.TemplateInfo.GetFullHtmlFieldName(name);
var id = $"{NormalizeId(fullName)}-{item.Value}";

var checkBox = new TagBuilder("input");
checkBox.TagRenderMode = TagRenderMode.SelfClosing;
checkBox.MergeAttribute("id", id);
checkBox.MergeAttribute("type", "checkbox");
checkBox.MergeAttribute("name", fullName, replaceExisting: true);
checkBox.MergeAttribute("value", item.Value);
```

- 書くポイント:
  - `Html.NameFor(...)` 相当の値を、自前の文字列連結だけで組まない。
  - ネストした ViewModel や部分ビュー内でも、POST される `name` が崩れないようにする。
  - `label for` と `input id` の対応を維持し、クリック領域とアクセシビリティを壊さない。
  - チェックボックスでは hidden input を併設し、未選択時の送信も考える。

### セクション3: ページャーは `TagBuilder` で状態を持たせる（500〜700字）

- 伝えること:
  - ページャーはリンクを並べるだけに見えて、現在ページ・無効状態・アクセシビリティ属性が必要になる。
  - HTML 文字列を連結するより、`TagBuilder` で `li` / `a` / `span` を作るほうが状態を分けやすい。
- 具体例:

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

- 書くポイント:
  - 現在ページはリンクではなく `span` にし、同じページへの不要な遷移を避ける。
  - disabled では `aria-disabled` と `tabindex` を付け、見た目だけの無効状態にしない。
  - `currentPage` と `totalPages` は `Math.Clamp` / `Math.Max` で境界を丸め、ページ番号の異常値を HTML 側へ流さない。

### セクション4: `PartialFor` では `HtmlFieldPrefix` を引き継ぐ（600〜800字）★重要セクション

- 伝えること:
  - 部分ビューを共通化するときに一番壊れやすいのは、見た目ではなく POST 時の model binding。
  - サブモデルの部分ビューでは `TemplateInfo.HtmlFieldPrefix` を設定し、`Parent.Child.Property` のような `name` を維持する。
- 具体例:

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

- 書くポイント:
  - 部分ビューの再利用は便利だが、prefix がないと POST 後に値が戻らない。
  - `JoinPrefix` で既存 prefix と追加 prefix をつなぎ、親側の文脈を落とさない。
  - `PartialAsync(...).GetAwaiter().GetResult()` は移植時の妥協として紹介し、改善余地として非同期 Helper 化に触れる。

### セクション5: `_ViewImports.cshtml` に登録して View 側から使えるようにする（200〜300字）

- 伝えること:
  - Helper を作っても、Razor 側で namespace を見えるようにしないと使えない。
- 具体例:

```razor
@using Dev.CommonLibrary.Extensions.Helper
@addTagHelper *, Microsoft.AspNetCore.Mvc.TagHelpers
```

- 書くポイント:
  - DevNext では `DevNext/Views/_ViewImports.cshtml` に追加した。
  - 各 View に個別 `@using` を散らさず、Helper の入口を `_ViewImports.cshtml` に寄せる。

### まとめ（150〜250字）

- 要点3つ:
  1. HTML Helper の戻り値は `IHtmlContent` に寄せる
  2. input / label / pager は Core の `TagBuilder` と命名規則を使って組み立てる
  3. 部分ビュー共通化では `HtmlFieldPrefix` を維持しないと model binding が崩れる
- DevNext のようなテンプレートでは、Helper 移植は「古い資産を残す作業」ではなく、Razor の共通部品を Core の作法に合わせ直す作業だった、と締める。

---

## コード例の準備状況

| セクション | 出典ファイル | 行範囲 | 準備状況 |
|----------|------------|-------|---------|
| §1 改行表示 | `CommonLibrary/Extensions/Helper/HtmlExtensions.cs` | `FormatNewLines` | ✅ 抜粋済み |
| §2 チェックボックス | `CommonLibrary/Extensions/Helper/HtmlExtensionsForCheckBox.cs` | `BuildCheckBox` | ✅ 抜粋済み |
| §2 ラジオボタン | `CommonLibrary/Extensions/Helper/HtmlExtensionsForRadioButton.cs` | `RadioButtonForEnum` / `RadioButtonForSelectList` | 未着手 |
| §3 ページャー | `CommonLibrary/Extensions/Helper/PagerHtmlExtensions.cs` | `CreatePageItem` | ✅ 抜粋済み |
| §4 部分ビュー | `CommonLibrary/Extensions/Helper/HtmlExtensions.cs` | `PartialFor` | ✅ 抜粋済み |
| §5 ViewImports | `DevNext/Views/_ViewImports.cshtml` | `@using Dev.CommonLibrary.Extensions.Helper` | ✅ 抜粋済み |

---

## 参考リンク候補

- [DevNext](https://github.com/harness17/DevNext)
- [ASP.NET Core: Tag Helpers in forms](https://learn.microsoft.com/aspnet/core/mvc/views/working-with-forms)
- [ASP.NET Core: Partial views](https://learn.microsoft.com/aspnet/core/mvc/views/partial)
- [IHtmlContent Interface](https://learn.microsoft.com/dotnet/api/microsoft.aspnetcore.html.ihtmlcontent)
- [TagBuilder Class](https://learn.microsoft.com/dotnet/api/microsoft.aspnetcore.mvc.rendering.tagbuilder)

---

## 残タスク（執筆前に確認すること）

- [ ] 記事タイトル A/B/C を確定する
- [ ] 旧 ASP.NET MVC 側の Helper がどこにあったか、必要なら DevNet から1例だけ確認する
- [ ] `PartialFor` を同期ラッパーとして紹介する際、改善余地として `PartialAsync` 利用に触れるか決める
- [ ] 実際の View で Helper を使っている箇所があれば1例追加する
- [ ] `/article-review` で文体・必須要素・守秘義務を確認する

---

## 執筆順序（推奨）

1. はじめにで「Helper 移植は `name` / `id` / model binding の移植でもあった」と先に置く
2. §1 `IHtmlContent` → §2 input 系 → §4 `PartialFor` の順で、フォームまわりの詰まりに寄せて書く
3. §3 ページャーは補助例として短めにする
4. まとめで DevNext へのリンクを入れる
