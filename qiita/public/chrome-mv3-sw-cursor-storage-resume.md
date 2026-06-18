---
title: Chrome MV3でService Worker停止後にcursorから処理を再開する
tags:
  - JavaScript
  - Chrome
  - ChromeExtension
  - ManifestV3
  - ServiceWorker
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

Manifest V3 の Service Worker で複数件を順番に処理するときは、次の開始位置をメモリではなく `chrome.storage.local` に保存する。

```js
const queue = await chrome.storage.local.get("probeCursor");
const cursor = Number(queue.probeCursor) || 0;
const chunk = targets.slice(cursor, cursor + 8);

const result = await probeChunk(chunk);
const nextCursor = cursor + chunk.length >= targets.length ? 0 : cursor + chunk.length;

await chrome.storage.local.set({
  probeCache: { ...previousCache, ...result.cacheEntries },
  probeCursor: nextCursor,
});
```

Service Worker が停止しても storage は残る。次の alarm で `probeCursor` を読み直せば、中断したチャンクの次から処理を再開できる。

## 再現条件

[Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) のバックグラウンド照会で、次の条件を扱った。

- Chrome 拡張は Manifest V3
- `chrome.alarms` で定期処理を起動
- 対象は数十件以上になる
- 外部サイトへの連続アクセスを避けるため、1チャンクを8件に制限
- チャンクごとに取得結果を `chrome.storage.local` へ保存

Manifest V3 の Service Worker は常駐しない。Chrome は通常、30秒間操作がない場合などに Service Worker を停止する。グローバル変数に置いた cursor は、その時点で失われる。

```js
// Service Workerが再起動すると0へ戻る
let cursor = 0;

chrome.alarms.onAlarm.addListener(async () => {
  const chunk = targets.slice(cursor, cursor + 8);
  await probeChunk(chunk);
  cursor += chunk.length;
});
```

これでは途中まで処理しても、次回は先頭から始まる。同じ対象を繰り返し照会し、後半へ到達できない可能性がある。

## 原因は進捗をService Workerの寿命に結び付けたこと

Chrome の公式資料は、Service Worker 終了時にグローバル変数が失われるため、値を storage に保存するよう案内している。

採用しなかった方法は、ポート接続などで Service Worker を意図的に起こし続ける方法である。ブラウザが停止できる前提に逆らい、Chrome のバージョンごとのライフサイクル差にも依存する。

処理を「停止させない」のではなく、「停止しても再開できる」形に変えた。

## cursorと結果を同じ保存境界で更新する

実装では、対象を安定した順序へ並べたうえで cursor から8件を取り出した。処理後は cache、cursor、バッジ件数を1回の `storage.local.set()` へ渡した。

```js
function nextQueue(queue, chunkLength) {
  const next = queue.cursor + chunkLength;
  return {
    cursor: next >= queue.eligibleLength ? 0 : next,
    lastCycleAt: next >= queue.eligibleLength ? Date.now() : queue.lastCycleAt,
  };
}

await chrome.storage.local.set({
  kstCatalogCache: { ...previousCache, ...newCache },
  kstBgProbeQueue: nextQueue(queue, chunk.length),
  kstBgBadgeCount: badgeCount,
});
```

cache と cursor を別々に保存すると、片方だけ成功した時に整合しなくなる。たとえば cache 更新後、cursor 更新前に例外が起きると、次回は同じ対象を再処理する。

`chrome.storage.local.set()` は複数キーを1回で渡せる。ただし外部リクエストまでトランザクションになるわけではないため、同じ対象を再照会しても壊れない実装にする。

## 確認方法

開発ビルドでは、対象数を17件にして cursor の遷移を確認した。

```text
開始: cursor = 0
1回目: 8件処理後 cursor = 8
2回目: 8件処理後 cursor = 16
3回目: 1件処理後 cursor = 0
```

Service Worker の DevTools を閉じ、次の alarm 発火後に storage の cursor と cache を確認する。保存値から進み、完了時に0へ戻れば再開経路が動いている。対象一覧が減った場合に備え、範囲外の cursor は読み込み時に0へ戻す。

## 参考

- [Extension service worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle) - 停止条件と状態永続化
- [chrome.alarms API](https://developer.chrome.com/docs/extensions/reference/api/alarms) - 定期実行の起点
- [chrome.storage API](https://developer.chrome.com/docs/extensions/reference/api/storage) - cursorの保存先
- [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) - 元になった実装
- [google-chrome-extensions](https://github.com/harness17/google-chrome-extensions) - 関連するChrome拡張
