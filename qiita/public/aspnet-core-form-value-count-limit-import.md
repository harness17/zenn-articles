---
title: 'ASP.NET Coreで大量データの確認POSTが「Form value count limit 1024 exceeded」で落ちた'
tags:
  - ASP.NET Core
  - MVC
  - フォーム
  - 一括インポート
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

## 起きたこと

個人蔵書管理アプリ（ASP.NET Core 10）で、ISBNの一括インポート機能を作っていた。プレビュー画面で多数のチェックボックス付きリストを表示し、確認ボタンを押すと確定POSTが走る。

テスト中に数百件で動くことを確認して安心していたが、本番に近い件数を流したところ、確認ボタンを押した瞬間にエラーが返った。

```text
InvalidDataException: Form value count limit 1024 exceeded.
```

POSTされたフォーム値の数が1,024件を超えたため、ASP.NET Coreがリクエストを拒否した。

## 原因

ASP.NET Coreの `FormOptions.ValueCountLimit` の既定値は **1,024** になっている。これはDoS対策としてフレームワークが設けている上限で、通常のフォームでは問題にならないが、一括インポートのように大量のhidden fieldやチェックボックスを送信する画面では簡単に超える。

たとえば、各行にチェックボックス（`selectedIsbns[i]`）とhidden field（`previewRows[i].Isbn`、`previewRows[i].Title`）を持つフォームでは、1行あたり2〜3フィールドが必要になる。数千行を送るとフォーム値は1万件を超えやすく、1,024の上限を大幅に超える。

## 修正

### アクション単位で上限を引き上げる

`[RequestFormLimits]` 属性を対象のアクションメソッドだけに付ける。

```csharp
public class ImportController : Controller
{
    public const int MaxIsbnCount = 20_000;

    [HttpPost]
    [ValidateAntiForgeryToken]
    [RequestFormLimits(ValueCountLimit = MaxIsbnCount * 2 + 4)]
    public async Task<IActionResult> IsbnConfirm(IsbnImportPreviewViewModel model)
    {
        // 確定処理
    }
}
```

`MaxIsbnCount * 2 + 4` としているのは、1件あたりチェックボックスとISBN値の2フィールドに加え、`__RequestVerificationToken` 等の固定フィールド分を加算しているため。

### グローバルに変更しない理由

`Program.cs` でグローバルに上限を変える方法もある。

```csharp
// これはやらなかった
builder.Services.Configure<FormOptions>(options =>
{
    options.ValueCountLimit = 50000;
});
```

グローバルに引き上げると、一括インポート以外の全エンドポイントでも大量フォーム送信を受け付けてしまう。DoS攻撃に対する防御が全面的に弱まるため、**必要なアクションだけ引き上げる**のが安全側の選択だった。

### テストで属性を検証する

上限値はセキュリティに関わるため、テストで属性の存在と値を検証した。

```csharp
[Fact]
public void IsbnConfirm_HasCorrectFormLimits()
{
    var method = typeof(ImportController).GetMethod(nameof(ImportController.IsbnConfirm));
    var attribute = method!
        .GetCustomAttributes(typeof(RequestFormLimitsAttribute), false)
        .Cast<RequestFormLimitsAttribute>()
        .Single();
    Assert.Equal(ImportController.MaxIsbnCount * 2 + 4, attribute.ValueCountLimit);
}
```

属性を外したり値を変えたりしたときにテストが落ちるので、意図しない変更を防げる。

## hidden fieldの代替案

もう1つの解決策として、大量のhidden fieldを送る代わりに、選択されたデータをJSONに集約して1フィールドで送る方法も採用した。

```html
<!-- hidden fieldの代わりにJSON1本にまとめる -->
<input type="hidden" id="selectedRecordsJson" name="SelectedRecordsJson" />
```

```js
// 送信前にJSON化
const selected = Array.from(document.querySelectorAll('.isbn-checkbox:checked'))
  .map(cb => cb.value);
document.getElementById('selectedRecordsJson').value = JSON.stringify(selected);
```

この方法なら `ValueCountLimit` を引き上げる必要がない。ただし、サーバー側でJSONのデシリアライズとバリデーションが必要になるため、既存のモデルバインディングをそのまま使いたい画面では `[RequestFormLimits]` のほうが変更が少なかった。

## まとめ

- ASP.NET Coreの `ValueCountLimit` 既定値は1,024。一括インポートでは簡単に超える
- `[RequestFormLimits]` をアクション単位で付けて、対象のエンドポイントだけ上限を引き上げる
- グローバル変更はDoS防御が弱まるため避ける
- 大量hidden fieldの代替として、JSON集約で1フィールドにまとめる方法もある

## 参考リンク

- [Microsoft Learn - Configure options for the ASP.NET Core Kestrel web server](https://learn.microsoft.com/en-us/aspnet/core/mvc/models/file-uploads#multipart-body-length-limit)
- [RequestFormLimitsAttribute Class](https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.mvc.requestformlimitsattribute)
- [harness17/DevNext](https://github.com/harness17/DevNext) — ASP.NET Core 10 製のテンプレート
