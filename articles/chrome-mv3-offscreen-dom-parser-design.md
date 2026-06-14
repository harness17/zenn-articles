---
title: "Chrome MV3のDOM解析をoffscreen documentへ分離した"
emoji: "🪟"
type: "tech"
topics: ["chrome拡張", "manifestv3", "javascript", "webextension", "個人開発"]
published: true
---

## はじめに

Chrome 拡張の background を Manifest V3 の Service Worker へ移したとき、既存の HTML 解析処理が `DOMParser is not defined` で止まった。Service Worker には DOM がないため、ブラウザ上の文書を扱う前提のコードをそのまま呼べない。

対象は [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) で使っていた、取得済み HTML から書籍情報を読む処理だった。Firefox 版の background script では動いていたため、Chrome 版だけ正規表現パーサーへ書き換えると、同じ HTML に対する解析ロジックが二重になる。

この記事では、DOM 解析だけを offscreen document へ分け、Service Worker は処理の調整と保存に残した判断を書く。Manifest V3 の基本構造と `chrome.runtime.sendMessage()` を知っている読者を想定している。

## Service Workerへ移すとDOMParserが使えなかった

Manifest V3 の Service Worker は、イベントが発生したときだけ起動するバックグラウンド実行環境である。`window` や `document` を持たないため、次のコードは実行できない。

```js:parser.js
export function parseItems(html) {
  const document = new DOMParser().parseFromString(html, "text/html");
  return [...document.querySelectorAll("[data-item]")].map((element) => ({
    id: element.getAttribute("data-item"),
    title: element.textContent.trim(),
  }));
}
```

最初に考えた代替案は2つあった。

| 選択肢 | 採用しなかった理由 |
| --- | --- |
| 正規表現でHTMLを読む | 属性順や空白の変化へ弱く、既存のDOMパーサーと二重管理になる |
| content scriptへ解析を寄せる | 利用者が対象ページを開いていることが前提になり、バックグラウンド処理と合わない |

必要だったのは「Service Worker に DOM を持たせること」ではなく、「DOM が必要な処理だけを別の実行環境へ渡すこと」だった。

## offscreen documentはDOM解析だけを担当する

Chrome の offscreen document は、画面を開かずに DOM API を使える拡張ページである。Chrome 109 以降の Manifest V3 で利用でき、manifest に `offscreen` 権限が必要になる。

```json:manifest.json
{
  "manifest_version": 3,
  "permissions": ["offscreen", "storage"],
  "background": {
    "service_worker": "background.js"
  }
}
```

記事で示す最小構成は次の責務分担にした。実装の起点になったコミットでは、offscreen 側が複数件の照会処理まで担当している。以下はそのままの抜粋ではなく、Chrome 公式資料の制約に合わせて DOM 解析の境界だけを取り出したサンプルである。

| 実行環境 | 担当 |
| --- | --- |
| Service Worker | HTML取得、offscreen生成、メッセージ送信、結果保存 |
| offscreen document | `DOMParser`による解析、解析結果の返信 |
| 共有パーサー | HTMLから必要な値を抽出する処理 |

Chrome 公式資料では、offscreen document でサポートされる拡張 API は `chrome.runtime` に限られる。そのため、公開用サンプルでは解析結果を Service Worker へ返してから `chrome.storage.local` へ保存する。

```js:background.js
async function parseAndSave(html) {
  await ensureOffscreenDocument();

  try {
    const response = await chrome.runtime.sendMessage({
      type: "parse-html",
      target: "offscreen",
      html,
    });

    if (!response?.ok) {
      throw new Error(response?.error || "HTML parse failed");
    }

    await chrome.storage.local.set({ parsedItems: response.items });
  } finally {
    await chrome.offscreen.closeDocument();
  }
}
```

offscreen 側は対象メッセージだけを受け取り、既存パーサーを呼ぶ。
この例は単発処理を前提にしている。同時に複数の解析を走らせる場合は、処理を直列化するか参照数を持ち、別処理の途中で document を閉じないようにする。

```js:offscreen.js
chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
  if (message?.target !== "offscreen" || message?.type !== "parse-html") {
    return false;
  }

  try {
    sendResponse({ ok: true, items: parseItems(message.html) });
  } catch (error) {
    sendResponse({ ok: false, error: String(error?.message || error) });
  }
  return true;
});
```

## 生成競合とブラウザ差分を境界で吸収した

offscreen document は通常プロファイルにつき1つしか開けない。複数イベントが同時に発生すると、存在確認から生成までの間に別処理が割り込み、二重生成になる可能性がある。

そのため、生成中の Promise を共有した。

```js:background.js
let creatingOffscreen;

async function ensureOffscreenDocument() {
  const url = chrome.runtime.getURL("offscreen.html");
  const contexts = await chrome.runtime.getContexts({
    contextTypes: ["OFFSCREEN_DOCUMENT"],
    documentUrls: [url],
  });
  if (contexts.length > 0) return;

  creatingOffscreen ??= chrome.offscreen.createDocument({
    url: "offscreen.html",
    reasons: ["DOM_PARSER"],
    justification: "Parse fetched HTML with the shared DOM parser.",
  }).finally(() => {
    creatingOffscreen = null;
  });

  await creatingOffscreen;
}
```

`chrome.runtime.getContexts()` は Chrome 116 以降で使える。Chrome 109〜115 も対象にする場合は、公式例にある `clients.matchAll()` の分岐が必要になる。

Firefox 版は DOM を使える background script の経路を維持した。ブラウザごとに解析ロジックを分けるのではなく、「どの実行環境で共有パーサーを呼ぶか」だけを分けた。

## 確認したこと

公開用の最小構成では次を確認した。

- Service Worker から `DOMParser` を直接呼んでいない
- 同時呼び出しでも offscreen document を重複生成しない
- 単発処理の完了後に offscreen document を閉じる
- 解析失敗を Service Worker 側で例外として扱える
- offscreen 側が `chrome.runtime` のメッセージ処理と DOM 解析に閉じている
- Firefox 側は従来の background 経路で同じパーサーを使える

以前の記事「Chrome拡張をFirefoxにも出すためにmanifestをファイル分離した話」は配布物の差分を扱った。今回は、manifest 分離後に必要になった実行時の責務分担に絞っている。

:::message
offscreen documentへ処理を集めすぎると、Service Workerとの境界が再び曖昧になる。DOMが必要な最小処理だけを置く。
:::

## まとめ

- Manifest V3 の Service Worker では `DOMParser` を使えないため、DOM 解析だけを offscreen document へ分けた
- 正規表現への書き換えではなく共有パーサーを再利用し、Chrome / Firefox 間の二重実装を避けた
- 公開用の最小構成では、offscreen document を解析、Service Worker を調整と保存に限定すると責務を追いやすい

実装の起点は [offscreen documentを追加したコミット](https://github.com/harness17/kindle-series-sale-tracker/commit/56798b840863bd52d1e9681af6af5d7f05678958) に残している。

## 参考リンク

- [chrome.offscreen API](https://developer.chrome.com/docs/extensions/reference/api/offscreen) - 対応バージョン、権限、ライフサイクル
- [Extension service workers](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers) - Service Workerの実行モデル
- [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) - 記事で扱った拡張
