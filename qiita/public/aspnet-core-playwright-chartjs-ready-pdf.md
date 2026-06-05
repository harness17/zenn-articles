---
title: PlaywrightでChart.jsの描画完了を待ってからPDF化する
tags:
  - C#
  - PDF
  - chartjs
  - aspnetcore
  - Playwright
private: false
updated_at: '2026-06-04T22:39:47+09:00'
id: 1c60b2da24f194939485
organization_url_name: null
slide: false
ignorePublish: false
---

## 背景

ASP.NET Core MVC で作っている、療養中に自主制作した体調管理ツール（Phycock）に、週次・月次の統計グラフをPDFで出力する機能を追加しました。

サーバー側で Playwright を動かし、統計ページを内部URLでレンダリングしてから `Page.PdfAsync` でPDF化する構成です。

実装してみると、PDF を開くとグラフ部分が**白紙**になっていました。

## 問題：`NetworkIdle` 完了後もグラフが未描画

最初のコードはこうでした。

```csharp
var response = await page.GotoAsync(url, new PageGotoOptions
{
    WaitUntil = WaitUntilState.NetworkIdle,
    Timeout = 30000
});

var pdfBytes = await page.PdfAsync(new PagePdfOptions { Format = "A4" });
```

`WaitUntil = NetworkIdle` は「2秒以上ネットワーク接続が0本になった状態」で完了とみなします。

Chart.js はページ読み込み後に JS で描画を開始するため、`NetworkIdle` が解決したタイミングではアニメーション途中のことがあります。PDF化はそのタイミングで走るので、グラフが空白か途中の状態でキャプチャされます。

## 解決：`window.chartsReady` フラグ + `WaitForFunctionAsync`

グラフの描画完了を JS 側から通知する仕組みを作りました。

### 統計ページ側（JS）

URLに `?print=1` を付けた印刷モードの場合は Chart.js アニメーションを無効化し、すべてのチャートを生成した後、`requestAnimationFrame` を2回挟んでから `window.chartsReady` を立てます。

```javascript
const isPrintMode = new URLSearchParams(location.search).get('print') === '1';

// 印刷モードではアニメーションを無効化（描画が即座に完了する）
new Chart(ctx, {
    type: 'bar',
    data: { /* ... */ },
    options: {
        animation: isPrintMode ? false : undefined
    }
});

if (isPrintMode) {
    createAllCharts();  // 全チャートを生成
    // requestAnimationFrame を2回挟んでレイアウト確定を待つ
    requestAnimationFrame(() => requestAnimationFrame(() => {
        window.chartsReady = true;
    }));
}
```

アニメーションを無効化することで Chart.js の描画は同期的に完了します。その後 `requestAnimationFrame` を2回挟むのは、Canvas のレイアウト計算が確定するのを待つためです。

### サーバー側（Playwright）

`WaitForFunctionAsync` で `window.chartsReady === true` になるまで待ちます。

```csharp
// GotoAsync で NetworkIdle まで待機
var response = await page.GotoAsync(url, new PageGotoOptions
{
    WaitUntil = WaitUntilState.NetworkIdle,
    Timeout = timeoutMs
});

// さらに JS フラグが true になるまで待機
await page.WaitForFunctionAsync(
    "() => window.chartsReady === true",
    null,
    new PageWaitForFunctionOptions { Timeout = timeoutMs }
);

var pdfBytes = await page.PdfAsync(new PagePdfOptions
{
    Format = "A4",
    Landscape = true,
    PrintBackground = true,
    Margin = new Margin { Top = "8mm", Bottom = "8mm", Left = "8mm", Right = "8mm" }
});
```

`WaitForFunctionAsync` は JS 式をポーリングし、truthy になるまで待ちます。

## URLの設計：印刷モードを分ける

Playwright がアクセスする URL に `?print=1` を付けることで：

1. サーバー側で「Playwright によるPDF生成用リクエスト」と判断できる
2. JS 側でアニメーションや不要なUI要素（ヘッダー・ボタン等）を非表示にできる
3. `@media print` CSS を当てられる

```csharp
var url = $"http://localhost:{port}/Statistics?print=1&weekStart={weekStart}&section={section}";
```

## まとめ

- Playwright の `NetworkIdle` は Chart.js の描画完了を保証しない
- 印刷モード（`?print=1`）では Chart.js アニメーションを無効化し、`requestAnimationFrame` x2 後に `window.chartsReady = true` をセットする
- `WaitForFunctionAsync("() => window.chartsReady === true")` で待ってからPDF化する

認証が必要なページへの Playwright アクセス方法（Cookie 渡し）については別記事にまとめています。

実装は体調管理ツール Phycock の `PdfExportService.cs` / `StatisticsController.cs` にあります。
