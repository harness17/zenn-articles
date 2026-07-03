---
title: 外部HTML解析が3件連続unknownなら成功扱いにしない
tags:
  - JavaScript
  - キャッシュ
  - Chrome拡張
  - ManifestV3
private: false
updated_at: '2026-07-03T20:32:59+09:00'
id: afcd4a02f58cf2313f5b
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

外部HTML解析で `unknown` が返ったとき、1件や2件なら既存キャッシュを保持して続行する。ただし3件連続したら、ページ構造変更や通信異常の可能性が高いので処理を失敗扱いにする。

```js
const MAX_CONSECUTIVE_UNKNOWN = 3;

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
```

対象リポジトリ: [harness17/kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)

## 起きたこと

Chrome拡張で、Amazonの商品ページをバックグラウンドから解析し、シリーズごとの続刊・セール状態をキャッシュしている。

外部HTML解析では、次のように `unknown` が返ることがある。

- ページ構造が一時的に変わった
- ネットワークが不安定だった
- 検索結果が一時的に期待した形で返らなかった

最初は、`unknown` のとき既存キャッシュを保持するようにした。これで、1件の解析失敗で「続刊あり」や「セール中」の確定情報を消さずに済む。

しかし、全件が `unknown` になるような異常まで成功扱いにすると別の問題が起きる。バックグラウンド処理が「正常に一巡した」と記録され、次回実行が設定間隔まで遅れてしまう。

## 原因

`unknown` は「結果が得られなかった」状態であり、正常結果ではない。ただし、1件だけ `unknown` になった時点で処理全体を止めると、外部サイトの一時的な揺れに弱くなる。

必要だったのは、次の2つを分けることだった。

| 状況 | 扱い |
| --- | --- |
| 1件または2件の `unknown` | 既存キャッシュを保持して続行 |
| 3件連続の `unknown` | 処理全体を失敗扱いにして再試行 |

このために `unknownStreak` を持たせた。

## 修正

background側では、chunk処理の中で `unknownStreak` をインクリメントする。成功結果が取れたら0に戻す。

```js
let unknownStreak = Number(initialUnknownStreak) || 0;

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
```

ポイントは3つ。

- `unknown` を既存キャッシュの上書きに使わない（`prevCache[series.key] == null` のガード）
- 連続数としては数える（`unknownStreak += 1`）
- 3件連続で閾値に達したら処理を止める（`throw`）

## 成功時刻を更新しない

3件連続で `unknown` になった場合は `throw` する。`runBackgroundProbeOnce()` 側では catch で実行状態を `failed` にし、その後の `markBgProbeCompleted()` には進まない。

```js
try {
  // chunkを順に処理する
} catch (error) {
  const failedEntry = {
    ...runState,
    status: 'failed',
    finishedAt: Date.now(),
    error: String(error?.message || error).slice(0, 200),
  };
  await storageSet({ [BG_PROBE_RUN_STATE_KEY]: failedEntry });
  await appendProbeHistory(failedEntry);
  throw error;
}

await markBgProbeCompleted(runState);
```

`markBgProbeCompleted()` だけが最終成功時刻を保存する。

```js
async function markBgProbeCompleted(runState) {
  const finishedAt = Date.now();
  const entry = {
    ...runState,
    status: 'completed',
    finishedAt,
  };
  await storageSet({
    [BG_PROBE_LAST_RUN_KEY]: finishedAt,
    [BG_PROBE_RUN_STATE_KEY]: entry,
  });
  await appendProbeHistory(entry);
}
```

つまり、3件連続 `unknown` は「キャッシュを壊さない」だけでなく、「成功したことにしない」ための条件でもある。

## 確認ポイント

- `MAX_CONSECUTIVE_UNKNOWN` が `3` になっている
- 1件目・2件目の `unknown` では既存キャッシュを保持して続行する
- 3件目の `unknown` で `throw` する
- `catch` では `BG_PROBE_RUN_STATE_KEY` を `failed` にする
- 失敗時は `markBgProbeCompleted()` に進まず、`kstBgProbeLastRunAt` を更新しない

この確認は `verify-background-probe.mjs` の担当範囲にしている。

## 参考

- [harness17/kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)
- [Chrome Extensions: chrome.storage](https://developer.chrome.com/docs/extensions/reference/api/storage)
- [Chrome Extensions: Extension service worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle)
