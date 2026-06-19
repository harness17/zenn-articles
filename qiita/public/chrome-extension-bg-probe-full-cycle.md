---
title: Chrome拡張の定期照会を8件ずつのalarmから1回で全件巡回へ変えた
tags:
  - JavaScript
  - Chrome
  - ChromeExtension
  - 個人開発
  - ManifestV3
private: false
updated_at: '2026-06-19T10:48:37+09:00'
id: 1ccbf636a49f50353036
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

24時間ごとの alarm で8件だけ処理すると、80件の対象を一巡するまで約10日かかる。1回の alarm を1サイクルとして全件巡回し、8件チャンクは負荷制御と進捗保存の単位として残した。

```js
let processedThisRun = 0;

do {
  const chunk = targets.slice(queue.cursor, queue.cursor + CHUNK_SIZE);
  const result = await probeChunk(chunk, queue);

  queue = result.queue;
  processedThisRun += chunk.length;
  await saveProgress(result, queue);

  if (queue.cursor !== 0) await delay(REQUEST_DELAY_MS);
} while (queue.cursor !== 0 && processedThisRun < targets.length);
```

## 再現条件

[Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) では、登録シリーズの続刊とセール情報をバックグラウンドで確認している。

初期実装の条件は次のとおりだった。

- Manifest V3 の `chrome.alarms` を利用
- 設定間隔は12時間、24時間、48時間
- 1回の alarm で最大8シリーズを照会
- 次の開始位置を `chrome.storage.local` の cursor に保存
- シリーズ間に350msの待機を置く

8件に分けた理由は、Service Worker の途中停止と外部サイトへの連続アクセスを考慮したためである。進捗保存の設計自体は機能していた。

問題は、対象が80シリーズまで増えた時に表面化した。

```text
80シリーズ ÷ 8シリーズ/alarm = 10回
10回 × 24時間 = 約10日
```

24時間設定でも、同じシリーズを再確認するまで約10日かかる。利用者が選んだ間隔と、実際の全件更新間隔が一致していなかった。

## 原因はalarmとチャンクを同じ単位にしたこと

初期実装では、1回の alarm が次の2つの意味を持っていた。

1. 定期確認を始めるスケジュール単位
2. 最大8件を処理する負荷制御単位

設定画面の「24時間」は全対象の確認間隔に見えるが、実装上は次の8件へ進む間隔だった。

単純に `CHUNK_SIZE` を80や100へ増やす案は採用しなかった。対象数が増えるたびに上限を変更する必要があり、チャンクごとの待機、進捗保存、中断再開を失うためである。

## 1回のalarm内で8件チャンクを繰り返す

変更後は、alarm を全件巡回サイクルの開始として扱った。8件を処理したら状態を保存し、cursor が0へ戻るまで同じ実行内で次のチャンクへ進む。

```js
async function runBackgroundProbeOnce(targets, initialQueue) {
  let queue = initialQueue;
  let processed = queue.cursor;

  do {
    const chunk = targets.slice(queue.cursor, queue.cursor + 8);
    const response = await probeChunk(chunk, queue);

    queue = {
      ...response.queue,
      eligibleLength: targets.length,
    };
    processed += chunk.length;

    await chrome.storage.local.set({
      kstCatalogCache: response.cache,
      kstBgProbeQueue: queue,
      kstBgProbeRunState: {
        status: "running",
        total: targets.length,
        processed: Math.min(processed, targets.length),
      },
    });

    if (queue.cursor !== 0) await delay(350);
  } while (queue.cursor !== 0 && processed < targets.length);
}
```

全件を処理し終えた時だけ最終実行時刻と `completed` を保存する。チャンク通信が失敗した場合は `failed` を保存し、最終実行時刻を更新しない。個別シリーズの取得失敗は件数へ加え、残りは続行する。

## 確認方法

17シリーズを対象に実行し、1回の起動で次の順に処理されることを確認した。

```text
chunk 1: 8件 / cursor 8
chunk 2: 8件 / cursor 16
chunk 3: 1件 / cursor 0
status: completed
```

確認点は次のとおりである。

- alarm 1回で cursor が0へ戻るまで処理される
- 各チャンク後に cache、cursor、実行件数が保存される
- 全件完了後だけ最終実行時刻が進む
- 取得失敗が1件あっても残りを処理する
- 同一コンテキスト内の重複実行を抑止する

設定間隔は「次のチャンクまでの時間」ではなく「次の全件巡回までの時間」になった。8件チャンクは廃止せず、スケジュールとは別の責務として残した。

## 参考

- [chrome.alarms API](https://developer.chrome.com/docs/extensions/reference/api/alarms) - 定期処理の起点
- [Extension service worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle) - Service Workerの停止条件
- [chrome.storage API](https://developer.chrome.com/docs/extensions/reference/api/storage) - チャンク進捗の保存先
- [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) - 元になった実装
- [google-chrome-extensions](https://github.com/harness17/google-chrome-extensions) - 関連するChrome拡張
