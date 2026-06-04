---
title: "ASP.NET Coreの認証必須ページをPlaywrightでPDF化した話"
emoji: "📄"
type: "tech"
topics: ["aspnetcore", "csharp", "playwright", "pdf", "dotnet"]
published: true
---

## はじめに

療養中に自主制作した体調管理ツール（Phycock）に、週次・月次の統計グラフをPDFで出力する機能を追加しました。

最初は PDF 出力ライブラリ（PdfSharp、iText7 等）を使って HTML→PDF を生成することを考えていましたが、グラフが Chart.js による Canvas 描画だったため、スタティックなHTML→PDF変換では対応が難しい状況でした。

そこで選んだのが、**サーバー側で Playwright（Chromium）を起動して内部 URL をレンダリングし、`Page.PdfAsync` でPDF化する**方法です。

この方法でいくつかの課題を解決しました。この記事ではその判断と実装をまとめます。

対象読者：ASP.NET Core MVC で認証が必要なページのPDF出力を検討しているエンジニア。

## サーバー側 Playwright という選択

Playwright をサーバー側で動かすと次のことができます。

- ブラウザが描画するものをそのままPDF化する（Chart.js の Canvas グラフを含む）
- 認証済みの状態でページを開ける（Cookie を渡す）
- 印刷専用レイアウト（`?print=1`）でアクセスしてからPDF化できる

デメリットは Chromium プロセスをサーバー側で起動するためのリソースコストと、`playwright install` による依存関係の導入が必要な点です。個人開発ツールでは許容範囲でした。

## DI 設計：IPlaywright は Singleton、Browser は per-request

`IPlaywright` の生成は `Playwright.CreateAsync()` を一度だけ呼ぶため Singleton で管理します。`Browser` と `BrowserContext` は per-request で起動・破棄します。

```csharp
// Program.cs
builder.Services.AddSingleton<IPlaywrightFactory, PlaywrightFactory>();
builder.Services.AddScoped<PdfExportService>();
```

`PlaywrightFactory` は二重初期化を防ぐためセマフォで排他制御します。

```csharp
public class PlaywrightFactory : IPlaywrightFactory, IAsyncDisposable
{
    private IPlaywright? _instance;
    private readonly SemaphoreSlim _lock = new(1, 1);

    public async Task<IPlaywright> GetAsync()
    {
        if (_instance is not null) return _instance;
        await _lock.WaitAsync();
        try
        {
            _instance ??= await Playwright.CreateAsync();
            return _instance;
        }
        finally
        {
            _lock.Release();
        }
    }

    public ValueTask DisposeAsync()
    {
        _instance?.Dispose();
        _instance = null;
        _lock.Dispose();
        return ValueTask.CompletedTask;
    }
}
```

## 課題1：認証済みページへのアクセス

`[Authorize]` が付いたページに Playwright が素直にアクセスすると、認証されていないためログインページにリダイレクトされます。

### 解決：現在のリクエストから認証 Cookie を取り出して Playwright に渡す

ASP.NET Core Identity の認証 Cookie は `.AspNetCore.Identity.Application` というプレフィックスを持ちます。これを現在の HTTP リクエストから取り出して Playwright の `BrowserContext` に設定します。

```csharp
using PWCookie = Microsoft.Playwright.Cookie;

// Controller 側での Cookie 変換
var allowedCookiePrefixes = new[]
{
    ".AspNetCore.Identity.Application",
    ".AspNetCore.Session"
};

var loopbackHost = "127.0.0.1";
var loopbackPort = Request.Host.Port ?? HttpContext.Connection.LocalPort;

var pwCookies = Request.Cookies
    .Where(c => allowedCookiePrefixes.Any(
        prefix => c.Key.StartsWith(prefix, StringComparison.Ordinal)))
    .Select(c => new PWCookie
    {
        Name = c.Key,
        Value = c.Value,
        Domain = loopbackHost,
        Path = "/",
        Secure = false,   // ループバック HTTP なので false に上書き
        HttpOnly = true
    })
    .ToList();
```

**`Secure = false` にする理由**：ブラウザからの HTTP リクエストで発行された Cookie は `Secure` フラグが付いていないことが多いですが、HTTPS 経由のセッションでは `Secure=true` になります。Playwright がアクセスするのは `http://127.0.0.1:...` というループバックの HTTP URL のため、`Secure=true` の Cookie は送信されません。ループバック内部通信なので `false` に上書きしてもリスクはありません。

**全 Cookie を渡さない理由**：`Request.Cookies` にはサードパーティツールや CSRF トークンなど不要なものが混入します。プレフィックスで必要な Cookie だけに絞ります。

### URL の組み立て

`Request.Host` ヘッダーをそのまま URL に使うと、IIS リバースプロキシ構成や `http://*:5000` のようなワイルドカードバインディングで失敗します。ループバックアドレスとポートを別々に組み立てます。

```csharp
var pathBase = Request.PathBase.HasValue ? Request.PathBase.Value : string.Empty;
var url = $"http://{loopbackHost}:{loopbackPort}{pathBase}/Statistics?print=1&weekStart={ws}";
```

## 課題2：Chart.js のグラフが白紙でPDFに入る

`NetworkIdle` までページが読み込まれても、Chart.js はその後 JS でグラフを描画するため、Playwright がそのタイミングで PDF化するとグラフが空白になります。

### 解決：`window.chartsReady` フラグ + `WaitForFunctionAsync`

印刷モード（`?print=1`）のリクエストでは：

1. **Chart.js のアニメーションを無効化**する（描画が同期的に完了する）
2. 全チャートを生成した後、**`requestAnimationFrame` を2回**挟んでレイアウトを確定させる
3. `window.chartsReady = true` をセットする

```js
const isPrintMode = new URLSearchParams(location.search).get('print') === '1';

new Chart(ctx, {
    type: 'bar',
    data: { /* ... */ },
    options: {
        animation: isPrintMode ? false : undefined  // 印刷モードではアニメーション不要
    }
});

if (isPrintMode) {
    createAllCharts();
    requestAnimationFrame(() => requestAnimationFrame(() => {
        window.chartsReady = true;
    }));
}
```

Playwright 側では `WaitForFunctionAsync` でフラグを待ってからPDF化します。

```csharp
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

## `PdfExportService` の全体像

課題1・2の解決を組み込んだ `PdfExportService` の実装です。

```csharp
public async Task<byte[]> RenderPdfAsync(
    string url,
    IEnumerable<Cookie> cookies,
    string readyFlagJs = "() => window.chartsReady === true",
    int timeoutMs = 30000)
{
    var playwright = await _playwrightFactory.GetAsync();
    await using var browser = await playwright.Chromium.LaunchAsync(
        new BrowserTypeLaunchOptions { Headless = true });

    var context = await browser.NewContextAsync(new BrowserNewContextOptions
    {
        ViewportSize = new ViewportSize { Width = 1280, Height = 800 }
    });

    // Cookie を Playwright context に設定（Secure=false でループバック向け）
    await context.AddCookiesAsync(cookies.Select(c => new Cookie
    {
        Name = c.Name,
        Value = c.Value,
        Domain = c.Domain,
        Path = c.Path ?? "/",
        Secure = false,
        HttpOnly = c.HttpOnly,
        SameSite = SameSiteAttribute.Lax
    }));

    var page = await context.NewPageAsync();
    try
    {
        var response = await page.GotoAsync(url, new PageGotoOptions
        {
            WaitUntil = WaitUntilState.NetworkIdle,
            Timeout = timeoutMs
        });

        if (response is null || !response.Ok)
            throw new InvalidOperationException($"印刷ページの取得に失敗 (status={response?.Status})");

        // グラフ描画完了を待つ
        await page.WaitForFunctionAsync(readyFlagJs, null,
            new PageWaitForFunctionOptions { Timeout = timeoutMs });

        return await page.PdfAsync(new PagePdfOptions
        {
            Format = "A4",
            Landscape = true,
            PrintBackground = true,
            Margin = new Margin { Top = "8mm", Bottom = "8mm", Left = "8mm", Right = "8mm" }
        });
    }
    finally
    {
        await context.CloseAsync();
    }
}
```

## ファイル名の組み立て

Admin がメンバーのPDFを出力する場合は、選択中のメンバー名をファイル名に使います。ファイル名に使えない文字は除去します。

```csharp
// Admin の場合は選択中のメンバー名を使う
string userLabel = User.IsInRole("Admin")
    ? members.FirstOrDefault(m => m.Value == selectedId)?.Text ?? "user"
    : User.Identity?.Name ?? "user";

var safeUser = new string(userLabel.Where(c =>
    !Path.GetInvalidFileNameChars().Contains(c) && c != ' ').ToArray());
var fileName = $"Phycock_週次レポート_{safeUser}_{weekStart}.pdf";

return File(pdfBytes, "application/pdf", fileName);
```

## まとめ

この実装で解決した課題を整理します。

| 課題 | 解決策 |
|------|--------|
| 認証済みページにアクセスできない | `.AspNetCore.*` Cookie を現リクエストから取り出して Playwright に渡す |
| ループバック HTTP で Cookie が送られない | Cookie の `Secure` フラグを `false` に上書きする |
| Chart.js グラフが白紙 | 印刷モードでアニメーションを無効化 + `requestAnimationFrame` x2 + `window.chartsReady` フラグ |
| URL 組み立てが IIS で失敗 | `Request.Host` ではなくループバック IP + `Connection.LocalPort` を使う |

サーバー側 Playwright はリソースを使いますが、Canvas グラフを含む認証必須ページのPDF化では選択肢が限られます。`IPlaywright` を Singleton で管理することで起動コストを最小化しています。

実装の詳細は Phycock の以下のファイルを参照してください。

- `Phycock/Service/PdfExportService.cs`
- `Phycock/Controllers/StatisticsController.cs`
- `Phycock/Views/Statistics/Index.cshtml`（JS側の `window.chartsReady`）

ASP.NET Core MVC のテンプレートは [DevNext](https://github.com/harness17/DevNext) をベースにしています。
