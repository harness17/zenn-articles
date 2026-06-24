---
title: 'Chrome拡張のバッチ処理でchunk失敗時にcursorを進めたら再試行対象が飛んだ'
tags:
  - JavaScript
  - Chrome拡張
  - ManifestV3
  - バッチ処理
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

バックグラウンドで全件巡回するバッチ処理を8件ずつのchunkに分けていた。chunk内で3件連続 `unknown` になると `throw` して処理を止めるが、cursorの永続化を `probeInline()` の中でやっていたため、失敗したchunkの分もcursorが進んでいた。次のサイクルでは飛ばされた件が再試行されない。

```js
// 修正前: probeInline() の中で常にcursorを進めていた
await storageSet({
  [CACHE_KEY]: { ...prevCache, ...newCache },
  [BG_PROBE_QUEUE_KEY]: nextQueue(queue, chunk.length), // 失敗してもここで進む
});
```

修正後は、cursorの永続化を呼び出し元に委ね、成功パスだけで保存する。

対象リポジトリ: [harness17/kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)

## 起きたこと

Chrome拡張で、登録済みシリーズを定期的に全件巡回し、Amazonの商品ページから続刊・セール状態を取得している。1回の巡回で全件を処理するが、連続リクエストの負荷を抑えるため内部では8件ずつのchunkに分けている。

cursorは「前回どこまで処理したか」を `chrome.storage.local` に保存し、Service Workerが再起動しても途中から再開できるようにしている。

```js
const CHUNK_SIZE = 8;

function nextQueue(queue, chunkLength) {
  let cursor = queue.cursor + chunkLength;
  let lastCycleAt = queue.lastCycleAt;
  if (cursor >= queue.eligibleLength) {
    cursor = 0;
    lastCycleAt = Date.now();
  }
  return { cursor, lastCycleAt };
}
```

問題は、chunk処理が途中で失敗しても cursorが進んでしまうケースがあったこと。3件連続 `unknown` で `throw` した後、次のサイクルでは失敗したchunkの先頭ではなく、その次のchunkから再開されていた。

## 原因

v0.3.0 では、`probeInline()` の中でchunk処理の結果保存とcursor更新を一緒にやっていた。

```js
// v0.3.0: probeInline() 内でcursorを永続化
await storageSet({
  [CACHE_KEY]: { ...prevCache, ...newCache },
  [BG_PROBE_QUEUE_KEY]: nextQueue(queue, chunk.length),
  [BG_BADGE_COUNT_KEY]: badgeCount,
});
```

`nextQueue()` は常に `cursor + chunkLength` を返す。chunk処理の途中で `throw` する前にこの `storageSet` が呼ばれるかどうかは実装の書き方次第だが、構造として「chunk処理の責務」と「cursor永続化の責務」が同じ関数に混ざっているのが根本原因だった。

cursorの管理は巡回全体を制御する `runBackgroundProbeOnce()` の仕事であり、chunkの中身を処理する関数の仕事ではない。

## 修正

chunk処理関数は戻り値としてcursor情報を返すだけにし、永続化は呼び出し元が成功時にだけ行う。

```js
// probeInline() は結果を返すだけ
return {
  done: true,
  badgeCount,
  badgeKeys,
  cacheEntries: newCache,
  failedCount,
  unknownStreak,
  queue: nextQueue(queue, chunk.length),
};
```

呼び出し元の `runBackgroundProbeOnce()` では、chunkの戻り値からcursorを受け取り、ループ内で次のchunkへ渡す。

```js
let unknownStreak = 0;

do {
  const chunk = eligible.slice(queue.cursor, queue.cursor + CHUNK_SIZE);
  const response = await probeInline(
    chunk, prevCache, badgeCount, queue, unknownStreak
  );

  unknownStreak = Number(response.unknownStreak) || 0;
  queue = {
    ...(response.queue || nextQueue(queue, chunk.length)),
    eligibleLength: eligible.length,
  };
} while (queue.cursor !== 0);
```

`probeInline()` が `throw` した場合、`runBackgroundProbeOnce()` の `catch` ブロックに入る。そこでは実行状態を `failed` として保存するが、cursorは更新しない。

```js
try {
  // chunk処理ループ
} catch (error) {
  const failedEntry = {
    ...runState,
    status: 'failed',
    finishedAt: Date.now(),
    error: String(error?.message || error).slice(0, 200),
  };
  await storageSet({ [BG_PROBE_RUN_STATE_KEY]: failedEntry });
  throw error;
}

// ここに来るのは全chunk成功時だけ
await markBgProbeCompleted(runState);
```

`markBgProbeCompleted()` だけがcursorを含む最終状態を永続化する。失敗時は `throw` で抜けるため、cursorは前回成功時の位置のまま残る。

## 確認ポイント

- `probeInline()` / offscreen の `probeChunk()` が `storageSet` でcursorを直接永続化していないか
- `runBackgroundProbeOnce()` の `catch` ブロックで `BG_PROBE_QUEUE_KEY` を更新していないか
- 3件連続 `unknown` で `throw` した後、次のサイクルで同じcursor位置から再開するか
- `nextQueue()` が `eligibleLength` を超えたときに `cursor = 0` へ戻るか

## 参考

- [harness17/kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)
- [Chrome Extensions: chrome.storage](https://developer.chrome.com/docs/extensions/reference/api/storage)
- [Chrome Extensions: Extension service worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle)
