---
title: 'Chrome拡張のpopupがリンクを開くたび閉じるのでsidePanelへ移した'
tags:
  - Chrome拡張
  - sidePanel
  - ManifestV3
  - JavaScript
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

Chrome 拡張の `default_popup` は、フォーカスを失うと閉じる。リンクを開きながら一覧を見たい UI では、`chrome.storage.local` に状態を保存しても操作の中断感は残る。

既存の `popup/popup.html` を再利用するなら、Chrome では `side_panel.default_path` に移す。

## 何に詰まったか

[Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) では、Kindle 蔵書からシリーズ候補を出し、続刊やセール状態を確認する UI を作っていた。最初は `action.default_popup` で `popup/popup.html` を開いていた。

しかし一覧から Amazon の商品ページを開くたびに popup が閉じる。データが消えるだけなら storage に保存すればよい。問題は、確認作業のたびに画面が消えて流れが切れることだった。

## 原因

popup はツールバーアイコンから一時的に開く UI であり、ページ横に常駐するパネルではない。`chrome.storage.local` で並び順や結果を復元しても、popup 自体が閉じる動作は変わらない。

## sidePanelへ移す

Chrome 版では `default_popup` を外して `side_panel.default_path` を追加した。HTML は既存の `popup/popup.html` を使った。

```json
{
  "permissions": ["activeTab", "storage", "sidePanel"],
  "action": { "default_title": "Kindle Series Sale Tracker" },
  "side_panel": {
    "default_path": "popup/popup.html"
  }
}
```

ツールバーアイコンを押したときに sidePanel を開くため、background で `setPanelBehavior()` を呼ぶ。

```js
const sidePanelApi = chrome["sidePanel"];

if (sidePanelApi && typeof sidePanelApi.setPanelBehavior === "function") {
  sidePanelApi
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch((e) => console.error(e));
}
```

`chrome.sidePanel` がない環境でも落ちないように、存在確認してから呼んでいる。

## CSSも固定幅から変える

popup 用に `body { width: 420px; }` のような固定幅を書いていると、sidePanel では扱いづらい。実装では `width: 100%` と `min-width: 300px` に変え、狭い幅で文字がはみ出さないことも確認した。

## Firefoxはsidebar_actionにした

Firefox 版では Chrome の `sidePanel` API を使わず、manifest に `sidebar_action.default_panel: "popup/popup.html"` を書いた。同じ HTML と JavaScript を使い、ブラウザごとの差分は manifest と起動方法に閉じ込めた。

## まとめ

popup が閉じる問題は、状態保存だけでは解決しなかった。一覧を見ながらページを確認する UI では、`default_popup` より sidePanel のほうが合っていた。

## 参考

- [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker)
- [google-chrome-extensions](https://github.com/harness17/google-chrome-extensions)
- [chrome.sidePanel API](https://developer.chrome.com/docs/extensions/reference/api/sidePanel)
- [MDN: sidebar_action](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/sidebar_action)
