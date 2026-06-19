---
title: "Chrome MV3の定期処理を8件分割から全件巡回へ変えた"
emoji: "⏱️"
type: "tech"
topics: ["chrome拡張", "manifestv3", "javascript", "設計", "個人開発"]
published: true
---

## はじめに

Chrome 拡張 [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) に、登録したシリーズの続刊とセール情報を定期確認する機能を追加した。

Manifest V3 の Service Worker は常駐プロセスではない。Chrome は通常、30秒間操作がない場合などに Service Worker を停止するため、メモリ上の変数だけで長い処理の進捗を管理できない。

そこで最初は、1回の `chrome.alarms` 発火で8シリーズだけ照会し、進捗を `chrome.storage.local` に保存する設計にした。この方法は中断再開には強かったが、対象が80シリーズなら24時間設定でも一巡に約10日かかる。

この記事では、初期設計が合理的だった理由と、1回の alarm で全件巡回する方式へ変えた判断を書く。Manifest V3 の Service Worker と `chrome.alarms` の基本を知っている読者を想定している。

## 初期設計はalarmごとに8件だけ処理した

最初に優先したのは、Service Worker が途中で停止しても次回へ進捗を引き継げることだった。

対象シリーズを安定した順序に並べ、`cursor` から8件だけ取り出す。チャンク処理後は、照会結果、次の `cursor`、バッジ件数を1回の `chrome.storage.local.set()` で保存した。

```js:offscreen.js
const chunk = eligible.slice(queue.cursor, queue.cursor + CHUNK_SIZE);
const nextCursor = queue.cursor + chunk.length;

await chrome.storage.local.set({
  kstCatalogCache: { ...previousCache, ...newCache },
  kstBgProbeQueue: {
    cursor: nextCursor >= eligible.length ? 0 : nextCursor,
    lastCycleAt: nextCursor >= eligible.length ? Date.now() : queue.lastCycleAt,
  },
  kstBgBadgeCount: badgeCount,
});
```

`cursor` をグローバル変数ではなく storage に置いたのは、Service Worker の再起動後も状態を読めるようにするためである。Chrome の公式資料でも、Service Worker 終了時にグローバル変数は失われるため、値を storage へ保存するよう案内している。

この時点では、次の2案を比較した。

| 案 | 判断 |
| --- | --- |
| 1回のalarmで全件処理 | 長時間化し、途中停止時の影響が大きいと考えて見送った |
| alarmごとに8件処理 | 進捗を細かく確定できるため採用した |

8件という単位は、Amazon への連続アクセスを抑える待機と、中断時にやり直す範囲を両立するために置いた。対象件数と実行時間が読めない段階では、安全側に倒す判断として機能した。

## 設定間隔がチャンク間隔になっていた

運用で問題になったのは、利用者が設定した12時間、24時間、48時間という値の意味だった。

初期実装では、24時間ごとに処理されるのは全対象ではなく最大8シリーズである。80シリーズなら必要な alarm は10回なので、一巡には約10日かかる。

```text
80シリーズ ÷ 8シリーズ/alarm = 10回
10回 × 24時間 = 約10日
```

利用者が「24時間ごと」を選ぶと、全シリーズが1日ごとに更新されると解釈する。しかし実装上は、同じシリーズへ戻るまで約10日かかっていた。設定間隔が「全件の再確認間隔」ではなく「次の8件を処理する間隔」になっていた。

前回実行時刻も、全件巡回が終わった時刻なのか、8件だけ進んだ時刻なのか区別できない。問題は8件チャンクではなく、チャンク境界とスケジュール境界を同じものとして扱ったことだった。

## 1回のalarmで全件巡回しチャンクは残した

変更後は、1回の alarm を1サイクルとして扱い、その中で8件チャンクを繰り返す。`CHUNK_SIZE=8` とチャンク間の待機は残した。

```js:background.js
let processedThisRun = 0;

do {
  const chunk = eligible.slice(queue.cursor, queue.cursor + CHUNK_SIZE);
  const response = await probeChunk(chunk, queue, previousCache);

  previousCache = { ...previousCache, ...response.cacheEntries };
  queue = response.queue;
  processedThisRun += chunk.length;

  await chrome.storage.local.set({
    kstCatalogCache: previousCache,
    kstBgProbeQueue: queue,
    kstBgProbeRunState: {
      status: "running",
      total: eligible.length,
      processed: processedThisRun,
    },
  });

  if (queue.cursor !== 0) await delay(REQUEST_DELAY_MS);
} while (queue.cursor !== 0 && processedThisRun < eligible.length);
```

設計上の単位を分けたことが変更の中心である。

| 単位 | 役割 |
| --- | --- |
| alarm | 全対象を再確認する1サイクル |
| 8件チャンク | 負荷制御と進捗保存 |
| cursor | 中断した位置から再開するための状態 |
| 最終実行時刻 | 全件巡回が完了した時だけ更新 |

全件を最後にだけ保存する案は、途中の照会結果と cursor を失うため採用しなかった。チャンク完了ごとに保存しながら、同じサイクル内で次の8件へ進む。同じ実行コンテキストで alarm が重なった場合は進行中の Promise を共有するが、停止後の再開を担うのは storage の cursor である。

## 確認したこと

17シリーズを対象にした検証では、1回の実行で `8件 → 8件 → 1件` の3チャンクを処理し、完了後に cursor が0へ戻ることを確認した。

- チャンクごとに cache と cursor が保存される
- cursor が0以外なら同じサイクル内で次のチャンクへ進む
- 全件完了後だけ `kstBgProbeLastRunAt` を更新する
- 個別シリーズの取得失敗は件数へ記録し、残りのシリーズを続行する
- チャンク通信の失敗時は状態を `failed` とし、最終実行時刻を進めない
- 同一コンテキスト内の重複呼び出しは二重実行しない

:::message
この設計でも、Service Workerが処理の途中で停止しないことは保証しない。チャンクごとの永続化を残し、次回起動時に未完位置を読めることを前提にする。
:::

初期設計を廃止したのは、SW kill 対策が不要になったからではない。対象件数と利用者が設定間隔へ期待する意味が明確になり、スケジュール境界だけを変更する必要が出たためである。

## まとめ

- 初期設計では、Service Worker の中断に備えて alarm ごとに8件を処理し、cursor を storage に保存した
- 運用すると、設定間隔が全件巡回ではなくチャンク間隔になり、80シリーズでは一巡に約10日かかった
- 変更後は1回の alarm で全件巡回し、8件チャンクを負荷制御と中断再開の単位として残した

superseded になった設計も、当時の不確実性に対する合理的な選択だった。条件が変わったときは、守るべき性質を残したまま、どの境界を変更するかを分けて考えると設計意図を引き継ぎやすい。

## 参考リンク

- [Extension service worker lifecycle](https://developer.chrome.com/docs/extensions/develop/concepts/service-workers/lifecycle) - Service Workerの停止条件と状態永続化
- [chrome.alarms API](https://developer.chrome.com/docs/extensions/reference/api/alarms) - 定期実行APIの仕様
- [chrome.storage API](https://developer.chrome.com/docs/extensions/reference/api/storage) - Service Workerから利用できる永続ストレージ
- [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) - 記事で扱った実装
- [google-chrome-extensions](https://github.com/harness17/google-chrome-extensions) - Chrome拡張の関連リポジトリ
