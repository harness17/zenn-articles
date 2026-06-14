---
title: Chrome MV3でDOMParserを使うためoffscreen documentへ分けた
tags:
  - JavaScript
  - Chrome
  - ChromeExtension
  - WebExtensions
  - ManifestV3
private: false
updated_at: '2026-06-14T19:56:56+09:00'
id: bd32b9284ba7a3f3d682
organization_url_name: null
slide: false
ignorePublish: false
---

## 何に詰まったか

Chrome 拡張の Service Worker で HTML を取得し、既存の `DOMParser` ベースの処理へ渡そうとした。しかし、Manifest V3 の Service Worker は DOM へアクセスできない。

既存パーサーを正規表現へ書き換えると、HTML 構造の変化へ追従しにくくなる。そこで、DOM 解析だけを offscreen document へ分けた。

## 結論

Chrome 109 以降の Manifest V3 では、次の分担にすると既存の DOM パーサーを再利用できる。

- Service Worker: offscreen document の生成、メッセージ送信、結果保存
- offscreen document: `DOMParser` を使う処理、結果返信

offscreen document で利用できる拡張 API は `chrome.runtime` に限られるため、`chrome.storage.local` への保存は Service Worker 側へ戻す。

## manifestへ権限を追加する

`offscreen` 権限と Service Worker を指定する。

```json
{
  "manifest_version": 3,
  "permissions": ["offscreen", "storage"],
  "background": {
    "service_worker": "background.js"
  }
}
```

offscreen document の URL は、拡張パッケージ内の静的 HTML である必要がある。

```html
<!-- offscreen.html -->
<!doctype html>
<html lang="ja">
  <body>
    <script src="parser.js"></script>
    <script src="offscreen.js"></script>
  </body>
</html>
```

## Service Workerからoffscreen documentを作る

同時に複数回作成しないよう、生成中の Promise を共有する。Chrome 116 以降なら `chrome.runtime.getContexts()` で既存 document を確認できる。

```js
const OFFSCREEN_PATH = 'offscreen.html';
let creatingOffscreen;

async function ensureOffscreenDocument() {
  const offscreenUrl = chrome.runtime.getURL(OFFSCREEN_PATH);

  if ('getContexts' in chrome.runtime) {
    const contexts = await chrome.runtime.getContexts({
      contextTypes: ['OFFSCREEN_DOCUMENT'],
      documentUrls: [offscreenUrl],
    });
    if (contexts.length > 0) return;
  }

  if (!creatingOffscreen) {
    creatingOffscreen = chrome.offscreen.createDocument({
      url: OFFSCREEN_PATH,
      reasons: ['DOM_PARSER'],
      justification: 'Parse fetched HTML with the existing DOM parser.',
    }).finally(() => {
      creatingOffscreen = null;
    });
  }

  await creatingOffscreen;
}
```

Chrome 109 から 115 も対象にする場合は、公式ドキュメントにある `clients.matchAll()` の分岐を追加する。

## メッセージでHTMLを渡す

Service Worker は取得済み HTML を送り、解析結果を受け取って保存する。

```js
async function parseAndSave(html) {
  await ensureOffscreenDocument();

  try {
    const response = await chrome.runtime.sendMessage({
      type: 'parse-html',
      target: 'offscreen',
      html,
    });

    if (!response?.ok) {
      throw new Error(response?.error || 'HTML parse failed');
    }

    await chrome.storage.local.set({ parsedItems: response.items });
  } finally {
    await chrome.offscreen.closeDocument();
  }
}
```

offscreen 側では対象メッセージだけを処理する。

```js
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.target !== 'offscreen' || message?.type !== 'parse-html') {
    return false;
  }

  try {
    const document = new DOMParser().parseFromString(message.html, 'text/html');
    const items = [...document.querySelectorAll('[data-item]')].map((element) => ({
      id: element.getAttribute('data-item'),
      title: element.textContent.trim(),
    }));
    sendResponse({ ok: true, items });
  } catch (error) {
    sendResponse({ ok: false, error: String(error?.message || error) });
  }

  return true;
});
```

## 確認したこと

実装では次を確認した。

1. Service Worker から既存の DOM ベース解析処理を直接呼ばない
2. offscreen document が重複生成されない
3. 解析完了後に document を破棄する
4. 保存処理は Service Worker 側で行う
5. Firefox 側は DOM を使える background script の経路を維持する

対象実装では Chrome と Firefox の経路を分け、共有パーサー自体は変更しなかった。

## 注意点

- offscreen document は通常プロファイルにつき1つだけ開ける
- `hasDocument()` は公式リファレンスで Pending のため、安定 API として前提にしない
- DOM 解析以外の責務まで offscreen 側へ寄せると、Service Worker との境界が分かりにくくなる
- HTML の取得元が外部サイトなら、別途 `host_permissions` が必要になる

## 参考

- [chrome.offscreen API](https://developer.chrome.com/docs/extensions/reference/api/offscreen)
- [Extension service workers](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers)
- [実装の起点になったコミット](https://github.com/harness17/kindle-series-sale-tracker/commit/56798b840863bd52d1e9681af6af5d7f05678958)
