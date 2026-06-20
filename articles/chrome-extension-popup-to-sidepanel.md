---
title: "Chrome拡張のポップアップをサイドパネルへ移したのは状態保存では根本解決にならなかったため"
emoji: "🧭"
type: "tech"
topics: ["chrome-extension", "sidepanel", "manifest-v3", "firefox"]
published: true
---

## はじめに

Chrome 拡張の UI を `default_popup` で作ると、ツールバーからすぐ開ける。しかし popup はフォーカスを失うと閉じる。リンクを開く、別タブを見る、ページ側で確認する、といった操作をすると UI ごと消える。

[Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) では、Kindle 蔵書からシリーズ候補を出し、続刊やセールを確認する UI を popup に置いていた。最初は `chrome.storage.local` に状態を保存して閉じても復元できるようにしたが、使ってみると「復元できる」だけでは足りなかった。

この記事では、状態保存で粘ったあとに Chrome の Side Panel API と Firefox の `sidebar_action` へ移した体験を書く。関連する Chrome 拡張群は [google-chrome-extensions](https://github.com/harness17/google-chrome-extensions) にもあるが、現行実装は Kindle Series Sale Tracker 側で確認した。

## 困ったこと

最初の manifest は、`action.default_popup` から `popup/popup.html` を開く構成だった。一覧から Amazon の商品ページや Kindle 一覧を開き、戻って次のシリーズを見る。ところがリンクを開いた瞬間に popup は閉じる。もう一度拡張アイコンを押せば戻れるが、判断中の文脈が毎回切れる。

痛かったのは、データが消えることではなかった。作業中の一覧が、リンク遷移のたびに視界から消えることだった。

## 試したこと: storageで復元する

まず、閉じても戻せるようにした。スキャン結果、並び順、完了済みシリーズ、除外シリーズを `chrome.storage.local` に保存し、popup を開き直したときに再構築する。

これはデータ保持としては効いた。閉じてもスキャン結果は残るし、Manifest V3 の Service Worker が止まっても storage に逃がした値は読める。

ただし、操作体験は直らなかった。リンクを開くたびに popup が閉じ、再度アイコンを押し、同じ場所を探す必要がある。storage は「壊れない」ための対策であって、「閉じずに作業を続ける」ための対策ではなかった。

## 移行したこと: 表示面を変える

問題は保存ではなく表示面の寿命だった。そこで popup を延命するのではなく、閉じない前提の UI に移した。

Chrome 版では `default_popup` を外し、同じ `popup/popup.html` を `side_panel.default_path` に指定した。

```json
{
  "permissions": ["activeTab", "storage", "sidePanel"],
  "action": {
    "default_title": "__MSG_actionTitle__"
  },
  "side_panel": {
    "default_path": "popup/popup.html"
  },
  "background": { "service_worker": "background/background.js" }
}
```

ツールバーアイコンを押したときにサイドパネルを開くため、background 側では `chrome.sidePanel.setPanelBehavior()` を呼んだ。

```js
const sidePanelApi = chrome["sidePanel"];

if (sidePanelApi && typeof sidePanelApi.setPanelBehavior === "function") {
  sidePanelApi
    .setPanelBehavior({ openPanelOnActionClick: true })
    .catch((e) => console.error(e));
}
```

Firefox には Chrome の `sidePanel` API がないため、Firefox 版 manifest では `sidebar_action` を使った。

```json
{
  "sidebar_action": {
    "default_panel": "popup/popup.html",
    "default_title": "__MSG_actionTitle__"
  }
}
```

Chrome と Firefox で manifest は分けたが、一覧表示やボタン処理は同じ HTML / JS を使った。

## CSSも420px固定から変えた

popup 時代の CSS は `body` を 420px 固定にしていた。サイドパネルはユーザーが幅を変えられるため、固定幅のままだと余白やはみ出しが出る。

```css
body {
  width: 100%;
  min-width: 300px;
  margin: 0;
  background: var(--bg);
  color: var(--fg);
}
```

長いシリーズ名が狭い幅で崩れないように、タイトル部分には `min-width: 0` と `overflow-wrap: anywhere` も入れた。サイドパネル化は、小窓前提の固定レイアウトを可変幅へ直す作業でもあった。

## 結果

移行前は `default_popup` に一覧 UI を置いていた。痛みは、リンクを開くたびに閉じ、作業中の文脈が切れることだった。移行後はサイドパネル/サイドバーへ移し、ページ確認中も一覧を残せた。

移行後も `chrome.storage.local` は使っている。ただし役割は変わった。以前は「閉じても何とか戻す」ために使っていた。移行後は「パネルをまたいでも同じデータを見る」ために使っている。

## まとめ

popup が閉じる問題を、最初は状態保存で解決しようとした。保存すればデータは戻るが、リンクを開くたびに UI が消える体験は残った。

Chrome では `side_panel.default_path` と `chrome.sidePanel.setPanelBehavior()`、Firefox では `sidebar_action.default_panel` へ移した。ページを見比べながら進める UI では、状態保存より先に表示面の寿命を疑うべきだった。

## 参考リンク

- [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) - この記事で確認した現行実装
- [google-chrome-extensions](https://github.com/harness17/google-chrome-extensions) - 関連する Chrome 拡張群
- [chrome.sidePanel API](https://developer.chrome.com/docs/extensions/reference/api/sidePanel)
- [MDN: sidebar_action](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/sidebar_action)
