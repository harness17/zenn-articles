---
title: Playwright縺ｧChart.js縺ｮ謠冗判螳御ｺ・ｒ蠕・▲縺ｦ縺九ｉPDF蛹悶☆繧・tags:
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

## 閭梧勹

ASP.NET Core MVC 縺ｧ菴懊▲縺ｦ縺・ｋ縲∫凾鬢贋ｸｭ縺ｫ閾ｪ荳ｻ蛻ｶ菴懊＠縺滉ｽ楢ｪｿ邂｡逅・ヤ繝ｼ繝ｫ・・hycock・峨↓縲・ｱ谺｡繝ｻ譛域ｬ｡縺ｮ邨ｱ險医げ繝ｩ繝輔ｒPDF縺ｧ蜃ｺ蜉帙☆繧区ｩ溯・繧定ｿｽ蜉縺励∪縺励◆縲・
繧ｵ繝ｼ繝舌・蛛ｴ縺ｧ Playwright 繧貞虚縺九＠縲∫ｵｱ險医・繝ｼ繧ｸ繧貞・驛ｨURL縺ｧ繝ｬ繝ｳ繝繝ｪ繝ｳ繧ｰ縺励※縺九ｉ `Page.PdfAsync` 縺ｧPDF蛹悶☆繧区ｧ区・縺ｧ縺吶・
螳溯｣・＠縺ｦ縺ｿ繧九→縲￣DF 繧帝幕縺上→繧ｰ繝ｩ繝暮Κ蛻・′**逋ｽ邏・*縺ｫ縺ｪ縺｣縺ｦ縺・∪縺励◆縲・
## 蝠城｡鯉ｼ啻NetworkIdle` 螳御ｺ・ｾ後ｂ繧ｰ繝ｩ繝輔′譛ｪ謠冗判

譛蛻昴・繧ｳ繝ｼ繝峨・縺薙≧縺ｧ縺励◆縲・
```csharp
var response = await page.GotoAsync(url, new PageGotoOptions
{
    WaitUntil = WaitUntilState.NetworkIdle,
    Timeout = 30000
});

var pdfBytes = await page.PdfAsync(new PagePdfOptions { Format = "A4" });
```

`WaitUntil = NetworkIdle` 縺ｯ縲・遘剃ｻ･荳翫ロ繝・ヨ繝ｯ繝ｼ繧ｯ謗･邯壹′0譛ｬ縺ｫ縺ｪ縺｣縺溽憾諷九阪〒螳御ｺ・→縺ｿ縺ｪ縺励∪縺吶・
Chart.js 縺ｯ繝壹・繧ｸ隱ｭ縺ｿ霎ｼ縺ｿ蠕後↓ JS 縺ｧ謠冗判繧帝幕蟋九☆繧九◆繧√～NetworkIdle` 縺瑚ｧ｣豎ｺ縺励◆繧ｿ繧､繝溘Φ繧ｰ縺ｧ縺ｯ繧｢繝九Γ繝ｼ繧ｷ繝ｧ繝ｳ騾比ｸｭ縺ｮ縺薙→縺後≠繧翫∪縺吶１DF蛹悶・縺昴・繧ｿ繧､繝溘Φ繧ｰ縺ｧ襍ｰ繧九・縺ｧ縲√げ繝ｩ繝輔′遨ｺ逋ｽ縺矩比ｸｭ縺ｮ迥ｶ諷九〒繧ｭ繝｣繝励メ繝｣縺輔ｌ縺ｾ縺吶・
## 隗｣豎ｺ・啻window.chartsReady` 繝輔Λ繧ｰ + `WaitForFunctionAsync`

繧ｰ繝ｩ繝輔・謠冗判螳御ｺ・ｒ JS 蛛ｴ縺九ｉ騾夂衍縺吶ｋ莉慕ｵ・∩繧剃ｽ懊ｊ縺ｾ縺励◆縲・
### 邨ｱ險医・繝ｼ繧ｸ蛛ｴ・・S・・
URL縺ｫ `?print=1` 繧剃ｻ倥￠縺溷魂蛻ｷ繝｢繝ｼ繝峨・蝣ｴ蜷医・ Chart.js 繧｢繝九Γ繝ｼ繧ｷ繝ｧ繝ｳ繧堤┌蜉ｹ蛹悶＠縲√☆縺ｹ縺ｦ縺ｮ繝√Ε繝ｼ繝医ｒ逕滓・縺励◆蠕後～requestAnimationFrame` 繧・蝗樊検繧薙〒縺九ｉ `window.chartsReady` 繧堤ｫ九※縺ｾ縺吶・
```javascript
const isPrintMode = new URLSearchParams(location.search).get('print') === '1';

// 蜊ｰ蛻ｷ繝｢繝ｼ繝峨〒縺ｯ繧｢繝九Γ繝ｼ繧ｷ繝ｧ繝ｳ繧堤┌蜉ｹ蛹厄ｼ域緒逕ｻ縺悟叉蠎ｧ縺ｫ螳御ｺ・☆繧具ｼ・new Chart(ctx, {
    type: 'bar',
    data: { /* ... */ },
    options: {
        animation: isPrintMode ? false : undefined
    }
});

if (isPrintMode) {
    createAllCharts();  // 蜈ｨ繝√Ε繝ｼ繝医ｒ逕滓・
    // requestAnimationFrame 繧・蝗樊検繧薙〒繝ｬ繧､繧｢繧ｦ繝育｢ｺ螳壹ｒ蠕・▽
    requestAnimationFrame(() => requestAnimationFrame(() => {
        window.chartsReady = true;
    }));
}
```

繧｢繝九Γ繝ｼ繧ｷ繝ｧ繝ｳ繧堤┌蜉ｹ蛹悶☆繧九％縺ｨ縺ｧ Chart.js 縺ｮ謠冗判縺ｯ蜷梧悄逧・↓螳御ｺ・＠縺ｾ縺吶ゅ◎縺ｮ蠕・`requestAnimationFrame` 繧・蝗樊検繧縺ｮ縺ｯ縲，anvas 縺ｮ繝ｬ繧､繧｢繧ｦ繝郁ｨ育ｮ励′遒ｺ螳壹☆繧九・繧貞ｾ・▽縺溘ａ縺ｧ縺吶・
### 繧ｵ繝ｼ繝舌・蛛ｴ・・laywright・・
`WaitForFunctionAsync` 縺ｧ `window.chartsReady === true` 縺ｫ縺ｪ繧九∪縺ｧ蠕・■縺ｾ縺吶・
```csharp
// GotoAsync 縺ｧ NetworkIdle 縺ｾ縺ｧ蠕・ｩ・var response = await page.GotoAsync(url, new PageGotoOptions
{
    WaitUntil = WaitUntilState.NetworkIdle,
    Timeout = timeoutMs
});

// 縺輔ｉ縺ｫ JS 繝輔Λ繧ｰ縺・true 縺ｫ縺ｪ繧九∪縺ｧ蠕・ｩ・await page.WaitForFunctionAsync(
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

`WaitForFunctionAsync` 縺ｯ JS 蠑上ｒ繝昴・繝ｪ繝ｳ繧ｰ縺励》ruthy 縺ｫ縺ｪ繧九∪縺ｧ蠕・■縺ｾ縺吶・
## URL縺ｮ險ｭ險茨ｼ壼魂蛻ｷ繝｢繝ｼ繝峨ｒ蛻・￠繧・
Playwright 縺後い繧ｯ繧ｻ繧ｹ縺吶ｋ URL 縺ｫ `?print=1` 繧剃ｻ倥￠繧九％縺ｨ縺ｧ・・
1. 繧ｵ繝ｼ繝舌・蛛ｴ縺ｧ縲訓laywright 縺ｫ繧医ｋPDF逕滓・逕ｨ繝ｪ繧ｯ繧ｨ繧ｹ繝医阪→蛻､譁ｭ縺ｧ縺阪ｋ
2. JS 蛛ｴ縺ｧ繧｢繝九Γ繝ｼ繧ｷ繝ｧ繝ｳ繧・ｸ崎ｦ√↑UI隕∫ｴ・医・繝・ム繝ｼ繝ｻ繝懊ち繝ｳ遲会ｼ峨ｒ髱櫁｡ｨ遉ｺ縺ｫ縺ｧ縺阪ｋ
3. `@media print` CSS 繧貞ｽ薙※繧峨ｌ繧・
```csharp
var url = $"http://localhost:{port}/Statistics?print=1&weekStart={weekStart}&section={section}";
```

## 縺ｾ縺ｨ繧・
- Playwright 縺ｮ `NetworkIdle` 縺ｯ Chart.js 縺ｮ謠冗判螳御ｺ・ｒ菫晁ｨｼ縺励↑縺・- 蜊ｰ蛻ｷ繝｢繝ｼ繝会ｼ・?print=1`・峨〒縺ｯ Chart.js 繧｢繝九Γ繝ｼ繧ｷ繝ｧ繝ｳ繧堤┌蜉ｹ蛹悶＠縲～requestAnimationFrame` x2 蠕後↓ `window.chartsReady = true` 繧偵そ繝・ヨ縺吶ｋ
- `WaitForFunctionAsync("() => window.chartsReady === true")` 縺ｧ蠕・▲縺ｦ縺九ｉPDF蛹悶☆繧・
隱崎ｨｼ縺悟ｿ・ｦ√↑繝壹・繧ｸ縺ｸ縺ｮ Playwright 繧｢繧ｯ繧ｻ繧ｹ譁ｹ豕包ｼ・ookie 貂｡縺暦ｼ峨↓縺､縺・※縺ｯ蛻･險倅ｺ九↓縺ｾ縺ｨ繧√※縺・∪縺吶・
螳溯｣・・菴楢ｪｿ邂｡逅・ヤ繝ｼ繝ｫ Phycock 縺ｮ `PdfExportService.cs` / `StatisticsController.cs` 縺ｫ縺ゅｊ縺ｾ縺吶・
