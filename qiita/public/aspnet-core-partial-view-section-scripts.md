---
title: 部分ビューの@section Scriptsが読み込まれずクリック処理が動かなかった
tags:
  - mvc
  - Razor
  - aspnetcore
  - 部分ビュー
private: false
updated_at: '2026-06-21T20:08:30+09:00'
id: c018947a6ae23717b693
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

ASP.NET Core MVC の Partial View に `@section Scripts { }` を書いても、親ビューの `@RenderSection("Scripts")` には渡らない。

Partial View で共有したいのは HTML だけにして、script は親ビューの `Scripts` section から読み込む。

## 何に詰まったか

個人蔵書管理アプリの ISBN 検索機能を、Create 画面と Edit 画面の両方で使いたかった。フォームの一部を Partial View に切り出し、クリック処理も同じ Partial View の末尾に置いた。

```cshtml
@* _IsbnSearch.cshtml *@
<input id="isbn" name="Isbn" class="form-control" />
<button id="searchByIsbn" type="button">ISBN検索</button>

@section Scripts {
    <script>
        document.getElementById("searchByIsbn").addEventListener("click", async () => {
            // ISBN検索APIを呼び出す
        });
    </script>
}
```

親ビュー側は `@await Html.PartialAsync("_IsbnSearch")` と書けば、layout の `Scripts` section に流れると思っていた。しかしボタンを押しても何も起きない。DevTools で見ると、`<script>` が出力されていなかった。

## 原因

原因は Razor の section のスコープだった。`@section Scripts` は、ビューとその直近の Layout の間で使う仕組みである。Partial View で定義した section は、親ビューや Layout から参照できない。

期待していたのは「Partial View の `@section Scripts` が親 View を経由して `_Layout.cshtml` の `@RenderSection("Scripts")` へ届く」流れだった。実際には、Partial View 内の section は親ビューへ上がらない。Microsoft Learn でも、Partial View に定義した Razor section は親の markup file から見えないと説明されている。

## 解決策: scriptだけ親ビューのsectionで読む

HTML 用 Partial と script 用 Partial を分けた。HTML 側は入力欄とボタンだけを持つ。

```cshtml
<script>
    document.getElementById("searchByIsbn")?.addEventListener("click", async () => {
        const isbn = document.getElementById("isbn")?.value;
        if (!isbn) return;
        await fetch(`/Books/SearchByIsbn?isbn=${encodeURIComponent(isbn)}`);
    });
</script>
```

Create / Edit の親ビューでは、HTML と script をそれぞれ置く。

```cshtml
@await Html.PartialAsync("_IsbnSearch")

@section Scripts {
    @await Html.PartialAsync("_SearchScripts")
}
```

この形なら、`@section Scripts` は親ビューに存在する。Layout の `@RenderSection("Scripts", required: false)` から見えるため、script がページ末尾へ出力される。

## 確認したこと

修正後は、Create / Edit の両画面で `<script>` が出力され、ISBN 検索ボタンが動くことを確認した。原因はイベント登録ミスではなく、Razor の section が Partial View から親 View へ伝播しない仕様の見落としだった。

## まとめ

Partial View は HTML の共通化には向いているが、`@section Scripts` の受け渡し場所にはならない。

クリック処理をページ末尾で読みたい場合は、親ビューの `Scripts` section に書く。共通化したい場合も、script partial を作り、親ビューの section 内で `@await Html.PartialAsync()` する。

## 参考

- [Partial views in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/partial)
- [Layout in ASP.NET Core](https://learn.microsoft.com/en-us/aspnet/core/mvc/views/layout)
- [harness17/DevNext](https://github.com/harness17/DevNext) — ASP.NET Core 10 製のテンプレート
