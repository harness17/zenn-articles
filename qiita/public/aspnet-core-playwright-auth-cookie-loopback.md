---
title: ASP.NET CoreのログインCookieをサーバー側Playwrightに渡す
tags:
  - C#
  - PDF
  - authentication
  - aspnetcore
  - Playwright
private: false
updated_at: '2026-06-04T22:38:50+09:00'
id: 816cadce66a4199dd08a
organization_url_name: null
slide: false
ignorePublish: false
---

## 背景

ASP.NET Core MVC の統計ページ（認証必須）をサーバー側 Playwright でPDF化する実装を進めていました。

Playwright で `http://localhost:{port}/Statistics` にアクセスすると、認証されていないため**ログインページにリダイレクト**されてしまいます。PDF として出力されるのはログインフォームの画面でした。

## 問題：Playwright がログインしていない

ブラウザのリクエストと違い、Playwright が起動する Chromium インスタンスはユーザーのセッションを持っていません。

`[Authorize]` 属性が付いたページは認証済みセッションがないと 302 → ログインページへリダイレクトします。

認証フローを Playwright 内で再実行する（IDとパスワードでログインする）方法もありますが、サーバー内で完結する処理なら、**現在のリクエストが持つ認証 Cookie を Playwright に渡す**方が確実です。

## 解決：現在のリクエストから `.AspNetCore.*` Cookie を取り出して渡す

ASP.NET Core Identity の認証 Cookie は `.AspNetCore.Identity.Application` という名前で、セッション Cookie は `.AspNetCore.Session` という名前です。これらを `Request.Cookies` から取り出して Playwright の `BrowserContext` に設定します。

```csharp
// using PWCookie = Microsoft.Playwright.Cookie; でエイリアスを定義しておく

// PDF表示に必要な認証Cookieだけを Playwright 用に変換
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
        Secure = false,   // ループバックなので false に上書き
        HttpOnly = true
    })
    .ToList();
```

取り出した Cookie を `BrowserContext` に渡します。

```csharp
var context = await browser.NewContextAsync(new BrowserNewContextOptions
{
    ViewportSize = new ViewportSize { Width = 1280, Height = 800 }
});

await context.AddCookiesAsync(pwCookies);

var page = await context.NewPageAsync();
var response = await page.GotoAsync(url, new PageGotoOptions
{
    WaitUntil = WaitUntilState.NetworkIdle,
    Timeout = 30000
});
```

これで、Playwright の Chromium インスタンスが認証済みセッションを持った状態でページを開けます。

## なぜ `Secure = false` に上書きするか

ブラウザが ASP.NET Core に送ってきた Cookie は `Secure` フラグが付いていることがあります（HTTPS 接続で発行されたため）。

しかし Playwright がアクセスするのは `http://localhost:...` というループバックの HTTP URL です。`Secure = true` の Cookie は `http://` スキームでは送信されないため、ここで `false` に上書きします。

ループバック内部通信のみなので、HTTPS なしで認証 Cookie を渡すことのセキュリティリスクはありません。

## なぜ全 Cookie を渡さないか

`Request.Cookies` にはアプリ固有の Cookie 以外にも、サードパーティツール、分析タグ、CSRF トークン、デバッグ Cookie などが混入していることがあります。

全 Cookie を無条件で Playwright に渡すと：
- 不要な Cookie をループバックリクエストに含めることになる
- アプリが予期しない Cookie を受け取って誤動作する可能性がある

プレフィックスでフィルタリングして必要な Cookie だけを渡すのが安全です。

## URL の組み立て方

ホスト名は `Request.Host` から取るのではなく、ループバックアドレスを固定します。

```csharp
// IIS など、Host ヘッダーにポート番号が含まれない場合もあるため
// 実際の待受ポートをフォールバックに使う
var loopbackHost = "127.0.0.1";
var loopbackPort = Request.Host.Port ?? HttpContext.Connection.LocalPort;
if (loopbackPort <= 0) loopbackPort = 80;

var url = $"http://{loopbackHost}:{loopbackPort}/Statistics?print=1&weekStart={weekStart}";
```

`Host` ヘッダーを信頼して URL に含めると、ワイルドカードバインディング（`http://*:5000` 等）や IIS リバースプロキシ構成で URI 解析に失敗するケースがあります。

## まとめ

- サーバー側 Playwright で認証必須ページを開くには、現在の HTTP リクエストから Cookie を取り出して渡す
- `.AspNetCore.Identity.Application` / `.AspNetCore.Session` プレフィックスでフィルタリングする
- ループバックなので `Secure = false` に上書きする
- URL はホストを `127.0.0.1` で固定してポートだけを動的に決める

実装は Phycock の `PdfExportService.cs` / `StatisticsController.cs` にあります。Chart.js の描画完了待ちについては別記事にまとめています。
