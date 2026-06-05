---
title: ASP.NET Core縺ｮ繝ｭ繧ｰ繧､繝ｳCookie繧偵し繝ｼ繝舌・蛛ｴPlaywright縺ｫ貂｡縺・tags:
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

## 閭梧勹

ASP.NET Core MVC 縺ｮ邨ｱ險医・繝ｼ繧ｸ・郁ｪ崎ｨｼ蠢・茨ｼ峨ｒ繧ｵ繝ｼ繝舌・蛛ｴ Playwright 縺ｧPDF蛹悶☆繧句ｮ溯｣・ｒ騾ｲ繧√※縺・∪縺励◆縲・
Playwright 縺ｧ `http://localhost:{port}/Statistics` 縺ｫ繧｢繧ｯ繧ｻ繧ｹ縺吶ｋ縺ｨ縲∬ｪ崎ｨｼ縺輔ｌ縺ｦ縺・↑縺・◆繧・*繝ｭ繧ｰ繧､繝ｳ繝壹・繧ｸ縺ｫ繝ｪ繝繧､繝ｬ繧ｯ繝・*縺輔ｌ縺ｦ縺励∪縺・∪縺吶１DF 縺ｨ縺励※蜃ｺ蜉帙＆繧後ｋ縺ｮ縺ｯ繝ｭ繧ｰ繧､繝ｳ繝輔か繝ｼ繝縺ｮ逕ｻ髱｢縺ｧ縺励◆縲・
## 蝠城｡鯉ｼ啀laywright 縺後Ο繧ｰ繧､繝ｳ縺励※縺・↑縺・
繝悶Λ繧ｦ繧ｶ縺ｮ繝ｪ繧ｯ繧ｨ繧ｹ繝医→驕輔＞縲￣laywright 縺瑚ｵｷ蜍輔☆繧・Chromium 繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ縺ｯ繝ｦ繝ｼ繧ｶ繝ｼ縺ｮ繧ｻ繝・す繝ｧ繝ｳ繧呈戟縺｣縺ｦ縺・∪縺帙ｓ縲・
`[Authorize]` 螻樊ｧ縺御ｻ倥＞縺溘・繝ｼ繧ｸ縺ｯ隱崎ｨｼ貂医∩繧ｻ繝・す繝ｧ繝ｳ縺後↑縺・→ 302 竊・繝ｭ繧ｰ繧､繝ｳ繝壹・繧ｸ縺ｸ繝ｪ繝繧､繝ｬ繧ｯ繝医＠縺ｾ縺吶・
隱崎ｨｼ繝輔Ο繝ｼ繧・Playwright 蜀・〒蜀榊ｮ溯｡後☆繧具ｼ・D縺ｨ繝代せ繝ｯ繝ｼ繝峨〒繝ｭ繧ｰ繧､繝ｳ縺吶ｋ・画婿豕輔ｂ縺ゅｊ縺ｾ縺吶′縲√し繝ｼ繝舌・蜀・〒螳檎ｵ舌☆繧句・逅・↑繧峨・*迴ｾ蝨ｨ縺ｮ繝ｪ繧ｯ繧ｨ繧ｹ繝医′謖√▽隱崎ｨｼ Cookie 繧・Playwright 縺ｫ貂｡縺・*譁ｹ縺檎｢ｺ螳溘〒縺吶・
## 隗｣豎ｺ・夂樟蝨ｨ縺ｮ繝ｪ繧ｯ繧ｨ繧ｹ繝医°繧・`.AspNetCore.*` Cookie 繧貞叙繧雁・縺励※貂｡縺・
ASP.NET Core Identity 縺ｮ隱崎ｨｼ Cookie 縺ｯ `.AspNetCore.Identity.Application` 縺ｨ縺・≧蜷榊燕縺ｧ縲√そ繝・す繝ｧ繝ｳ Cookie 縺ｯ `.AspNetCore.Session` 縺ｨ縺・≧蜷榊燕縺ｧ縺吶ゅ％繧後ｉ繧・`Request.Cookies` 縺九ｉ蜿悶ｊ蜃ｺ縺励※ Playwright 縺ｮ `BrowserContext` 縺ｫ險ｭ螳壹＠縺ｾ縺吶・
```csharp
// using PWCookie = Microsoft.Playwright.Cookie; 縺ｧ繧ｨ繧､繝ｪ繧｢繧ｹ繧貞ｮ夂ｾｩ縺励※縺翫￥

// PDF陦ｨ遉ｺ縺ｫ蠢・ｦ√↑隱崎ｨｼCookie縺縺代ｒ Playwright 逕ｨ縺ｫ螟画鋤
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
        Secure = false,   // 繝ｫ繝ｼ繝励ヰ繝・け縺ｪ縺ｮ縺ｧ false 縺ｫ荳頑嶌縺・        HttpOnly = true
    })
    .ToList();
```

蜿悶ｊ蜃ｺ縺励◆ Cookie 繧・`BrowserContext` 縺ｫ貂｡縺励∪縺吶・
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

縺薙ｌ縺ｧ縲￣laywright 縺ｮ Chromium 繧､繝ｳ繧ｹ繧ｿ繝ｳ繧ｹ縺瑚ｪ崎ｨｼ貂医∩繧ｻ繝・す繝ｧ繝ｳ繧呈戟縺｣縺溽憾諷九〒繝壹・繧ｸ繧帝幕縺代∪縺吶・
## 縺ｪ縺・`Secure = false` 縺ｫ荳頑嶌縺阪☆繧九°

繝悶Λ繧ｦ繧ｶ縺・ASP.NET Core 縺ｫ騾√▲縺ｦ縺阪◆ Cookie 縺ｯ `Secure` 繝輔Λ繧ｰ縺御ｻ倥＞縺ｦ縺・ｋ縺薙→縺後≠繧翫∪縺呻ｼ・TTPS 謗･邯壹〒逋ｺ陦後＆繧後◆縺溘ａ・峨・
縺励°縺・Playwright 縺後い繧ｯ繧ｻ繧ｹ縺吶ｋ縺ｮ縺ｯ `http://localhost:...` 縺ｨ縺・≧繝ｫ繝ｼ繝励ヰ繝・け縺ｮ HTTP URL 縺ｧ縺吶ＡSecure = true` 縺ｮ Cookie 縺ｯ `http://` 繧ｹ繧ｭ繝ｼ繝縺ｧ縺ｯ騾∽ｿ｡縺輔ｌ縺ｪ縺・◆繧√√％縺薙〒 `false` 縺ｫ荳頑嶌縺阪＠縺ｾ縺吶・
繝ｫ繝ｼ繝励ヰ繝・け蜀・Κ騾壻ｿ｡縺ｮ縺ｿ縺ｪ縺ｮ縺ｧ縲？TTPS 縺ｪ縺励〒隱崎ｨｼ Cookie 繧呈ｸ｡縺吶％縺ｨ縺ｮ繧ｻ繧ｭ繝･繝ｪ繝・ぅ繝ｪ繧ｹ繧ｯ縺ｯ縺ゅｊ縺ｾ縺帙ｓ縲・
## 縺ｪ縺懷・ Cookie 繧呈ｸ｡縺輔↑縺・°

`Request.Cookies` 縺ｫ縺ｯ繧｢繝励Μ蝗ｺ譛峨・ Cookie 莉･螟悶↓繧ゅ√し繝ｼ繝峨ヱ繝ｼ繝・ぅ繝・・繝ｫ縲∝・譫舌ち繧ｰ縲，SRF 繝医・繧ｯ繝ｳ縲√ョ繝舌ャ繧ｰ Cookie 縺ｪ縺ｩ縺梧ｷｷ蜈･縺励※縺・ｋ縺薙→縺後≠繧翫∪縺吶・
蜈ｨ Cookie 繧堤┌譚｡莉ｶ縺ｧ Playwright 縺ｫ貂｡縺吶→・・- 荳崎ｦ√↑ Cookie 繧偵Ν繝ｼ繝励ヰ繝・け繝ｪ繧ｯ繧ｨ繧ｹ繝医↓蜷ｫ繧√ｋ縺薙→縺ｫ縺ｪ繧・- 繧｢繝励Μ縺御ｺ域悄縺励↑縺・Cookie 繧貞女縺大叙縺｣縺ｦ隱､蜍穂ｽ懊☆繧句庄閭ｽ諤ｧ縺後≠繧・
繝励Ξ繝輔ぅ繝・け繧ｹ縺ｧ繝輔ぅ繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ縺励※蠢・ｦ√↑ Cookie 縺縺代ｒ貂｡縺吶・縺悟ｮ牙・縺ｧ縺吶・
## URL 縺ｮ邨・∩遶九※譁ｹ

繝帙せ繝亥錐縺ｯ `Request.Host` 縺九ｉ蜿悶ｋ縺ｮ縺ｧ縺ｯ縺ｪ縺上√Ν繝ｼ繝励ヰ繝・け繧｢繝峨Ξ繧ｹ繧貞崋螳壹＠縺ｾ縺吶・
```csharp
// IIS 縺ｪ縺ｩ縲？ost 繝倥ャ繝繝ｼ縺ｫ繝昴・繝育分蜿ｷ縺悟性縺ｾ繧後↑縺・ｴ蜷医ｂ縺ゅｋ縺溘ａ
// 螳滄圀縺ｮ蠕・女繝昴・繝医ｒ繝輔か繝ｼ繝ｫ繝舌ャ繧ｯ縺ｫ菴ｿ縺・var loopbackHost = "127.0.0.1";
var loopbackPort = Request.Host.Port ?? HttpContext.Connection.LocalPort;
if (loopbackPort <= 0) loopbackPort = 80;

var url = $"http://{loopbackHost}:{loopbackPort}/Statistics?print=1&weekStart={weekStart}";
```

`Host` 繝倥ャ繝繝ｼ繧剃ｿ｡鬆ｼ縺励※ URL 縺ｫ蜷ｫ繧√ｋ縺ｨ縲√Ρ繧､繝ｫ繝峨き繝ｼ繝峨ヰ繧､繝ｳ繝・ぅ繝ｳ繧ｰ・・http://*:5000` 遲会ｼ峨ｄ IIS 繝ｪ繝舌・繧ｹ繝励Ο繧ｭ繧ｷ讒区・縺ｧ URI 隗｣譫舌↓螟ｱ謨励☆繧九こ繝ｼ繧ｹ縺後≠繧翫∪縺吶・
## 縺ｾ縺ｨ繧・
- 繧ｵ繝ｼ繝舌・蛛ｴ Playwright 縺ｧ隱崎ｨｼ蠢・医・繝ｼ繧ｸ繧帝幕縺上↓縺ｯ縲∫樟蝨ｨ縺ｮ HTTP 繝ｪ繧ｯ繧ｨ繧ｹ繝医°繧・Cookie 繧貞叙繧雁・縺励※貂｡縺・- `.AspNetCore.Identity.Application` / `.AspNetCore.Session` 繝励Ξ繝輔ぅ繝・け繧ｹ縺ｧ繝輔ぅ繝ｫ繧ｿ繝ｪ繝ｳ繧ｰ縺吶ｋ
- 繝ｫ繝ｼ繝励ヰ繝・け縺ｪ縺ｮ縺ｧ `Secure = false` 縺ｫ荳頑嶌縺阪☆繧・- URL 縺ｯ繝帙せ繝医ｒ `127.0.0.1` 縺ｧ蝗ｺ螳壹＠縺ｦ繝昴・繝医□縺代ｒ蜍慕噪縺ｫ豎ｺ繧√ｋ

螳溯｣・・ Phycock 縺ｮ `PdfExportService.cs` / `StatisticsController.cs` 縺ｫ縺ゅｊ縺ｾ縺吶・hart.js 縺ｮ謠冗判螳御ｺ・ｾ・■縺ｫ縺､縺・※縺ｯ蛻･險倅ｺ九↓縺ｾ縺ｨ繧√※縺・∪縺吶・
