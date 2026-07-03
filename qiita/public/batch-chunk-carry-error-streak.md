---
title: chunk境界でunknown連続数をリセットして異常を見逃した
tags:
  - JavaScript
  - Chrome拡張
  - バッチ処理
  - ManifestV3
private: false
updated_at: '2026-07-03T20:33:12+09:00'
id: 68078a55d246ab05f18e
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

バックグラウンド処理を8件ずつのchunkに分けるとき、`unknownStreak` をchunk内のローカル変数だけにすると、chunk境界で連続数が0に戻る。3件連続 `unknown` を検知したいなら、chunkの戻り値として連続数を返し、次chunkの `initialUnknownStreak` に渡す。

```js
let unknownStreak = 0;

const response = await sendRuntimeMessage({
  type: 'kst:bgProbeChunk',
  chunk,
  prevCache,
  currentBadgeCount: badgeCount,
  initialUnknownStreak: unknownStreak,
  queue,
});

unknownStreak = Number(response.unknownStreak) || 0;
```

対象リポジトリ: [harness17/kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)

## 起きたこと

Chrome拡張のバックグラウンド処理で、登録済みシリーズを全件巡回して続刊・セール状態を確認している。

1回の実行で全件を処理するが、Amazonへの連続リクエストをまとめすぎないよう、内部では8件ずつのchunkに分けている。

```js
const CHUNK_SIZE = 8;
```

ここで、3件連続 `unknown` なら処理を失敗扱いにするロジックを入れた。しかし最初の設計では、`unknownStreak` をchunk処理の中だけで持っていたため、chunkをまたぐ連続失敗を検知できない危険があった。

## 原因

たとえば、次のような並びを考える。

```text
chunk 1: ... unknown, unknown
chunk 2: unknown, ...
```

利用者から見ると3件連続 `unknown` なので、ページ構造変更や通信異常として処理を止めたい。

しかしchunk 2の先頭で `unknownStreak` が0に戻ると、chunk 2の `unknown` は1件目として扱われる。結果として、3件連続の閾値に届かず、異常を見逃す。

`CHUNK_SIZE` は負荷制御の単位であって、異常判定の単位ではない。ここを混ぜると、たまたまchunk境界にかかった失敗だけ検知できなくなる。

## 修正

`runBackgroundProbeOnce()` 側で、1回の巡回全体に対する `unknownStreak` を持つ。

```js
let unknownStreak = 0;

do {
  const chunk = eligible.slice(queue.cursor, queue.cursor + CHUNK_SIZE);
  const response =
    mode === 'offscreen'
      ? await sendRuntimeMessage({
          type: 'kst:bgProbeChunk',
          chunk,
          prevCache,
          currentBadgeCount: badgeCount,
          initialUnknownStreak: unknownStreak,
          queue,
        })
      : await probeInline(chunk, prevCache, badgeCount, queue, unknownStreak);

  if (response?.done !== true) {
    throw new Error(response?.error || 'Background catalog probe chunk failed');
  }

  unknownStreak = Number(response.unknownStreak) || 0;
  queue = {
    ...(response.queue || nextQueue(queue, chunk.length)),
    eligibleLength: eligible.length,
  };
} while (queue.cursor !== 0);
```

chunkを処理する側は、受け取った `initialUnknownStreak` から開始し、戻り値に次の `unknownStreak` を含める。

```js
async function probeInline(
  chunk,
  prevCache,
  currentBadgeCount,
  queue,
  initialUnknownStreak
) {
  const catalog = globalThis.__KST_CATALOG__;
  const card = globalThis.__KST_CARD__;
  const newCache = {};
  const badgeKeys = {};
  let badgeCount = Number(currentBadgeCount) || 0;
  let failedCount = 0;
  let unknownStreak = Number(initialUnknownStreak) || 0;
  let isFirst = true;

  for (const series of chunk) {
    if (!isFirst) await delay(REQUEST_DELAY_MS);
    isFirst = false;
    let result;
    try {
      result = await card.probeSeries(catalog, series);
    } catch (error) {
      failedCount += 1;
      unknownStreak = 0;
      continue;
    }

    if (result?.status === 'unknown') {
      unknownStreak += 1;
      if (unknownStreak >= MAX_CONSECUTIVE_UNKNOWN) {
        throw new Error(
          `Catalog results were indeterminate for ${MAX_CONSECUTIVE_UNKNOWN} consecutive series; retry later`
        );
      }
      continue;
    }

    unknownStreak = 0;
    const cacheEntry = { ...result, checkedAt: Date.now() };
    newCache[series.key] = cacheEntry;
  }

  return {
    done: true,
    badgeCount,
    badgeKeys,
    cacheEntries: newCache,
    failedCount,
    unknownStreak,
    queue: nextQueue(queue, chunk.length),
  };
}
```

実装では inline と offscreen の両方で同じ考え方にしている。Chromeでは offscreen document にchunkを渡し、Firefox相当のinline処理では同じ関数呼び出しで `unknownStreak` を渡す。

## offscreen側も戻り値で返す

offscreen document側でも、messageから初期値を受け取り、最後に戻り値として返す。

```js
async function probeChunk(message) {
  const catalog = window.__KST_CATALOG__;
  const card = window.__KST_CARD__;
  const chunk = Array.isArray(message.chunk) ? message.chunk : [];
  const prevCache = message.prevCache || {};
  const newCache = {};
  const badgeKeys = {};
  let badgeCount = Number(message.currentBadgeCount) || 0;
  let failedCount = 0;
  let unknownStreak = Number(message.initialUnknownStreak) || 0;

  for (const series of chunk) {
    let result;
    try {
      result = await card.probeSeries(catalog, series);
    } catch (error) {
      failedCount += 1;
      unknownStreak = 0;
      continue;
    }
    if (result?.status === 'unknown') {
      unknownStreak += 1;
      if (unknownStreak >= MAX_CONSECUTIVE_UNKNOWN) {
        throw new Error(
          `Catalog results were indeterminate for ${MAX_CONSECUTIVE_UNKNOWN} consecutive series; retry later`
        );
      }
      if (prevCache[series.key] == null) {
        newCache[series.key] = { ...result, checkedAt: Date.now() };
      }
      continue;
    }

    unknownStreak = 0;
    newCache[series.key] = { ...result, checkedAt: Date.now() };
  }

  const updatedQueue = nextQueue(message.queue || {}, chunk.length);
  return {
    done: true,
    badgeCount,
    badgeKeys,
    cacheEntries: newCache,
    failedCount,
    unknownStreak,
    queue: updatedQueue,
  };
}
```

これで、Chromeのoffscreen経由でもchunk境界をまたいだ連続数を維持できる。

## 確認ポイント

- `runBackgroundProbeOnce()` の先頭で `unknownStreak = 0` を初期化する
- chunk呼び出し時に `initialUnknownStreak: unknownStreak` を渡す
- chunk処理の戻り値に `unknownStreak` を含める
- 呼び出し元で `unknownStreak = Number(response.unknownStreak) || 0` として次chunkへ引き継ぐ
- inline と offscreen の両方で同じ契約にする

この確認は `verify-background-probe.mjs` の「chunk継続」「失敗継続」の観点に含めている。

## 参考

- [harness17/kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)
- [Chrome Extensions: Offscreen API](https://developer.chrome.com/docs/extensions/reference/api/offscreen)
- [Chrome Extensions: Extension service worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle)
