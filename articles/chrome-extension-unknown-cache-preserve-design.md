---
title: "外部サイトの解析結果が全件unknownになったので「既存値保持」と「連続失敗」を分けた"
emoji: "🛡️"
type: "tech"
topics: ["chrome-extension", "manifest-v3", "cache", "javascript"]
published: true
---

## はじめに

Chrome拡張でAmazonの商品ページを定期的に解析し、Kindleシリーズの続刊やセール情報をキャッシュに保存する機能を作っていた。ある日、解析結果がすべて `unknown` になり、それまで蓄積した「続刊あり」「セール中」の確定情報がまるごと消えた。

原因はAmazon側のページ構造変更だった。解析ロジックが想定するDOMが見つからず、全シリーズが `unknown`（解析不能）として返ってきた。そしてキャッシュ更新処理が `unknown` を正常な結果と同じように上書きしたため、確定済みの情報が失われた。

この記事では、この問題を「既存値保持」と「連続失敗検知」の2つの仕組みで解決した設計判断を書く。

**対象読者**: 外部サイトをスクレイピングしてキャッシュする機能を作っている開発者、Chrome拡張のバックグラウンド処理を設計している人。

**リポジトリ**: [kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)

## 何が起きたか

バックグラウンドの定期照会は、登録されたシリーズを順番に外部サイトへ問い合わせ、結果をchrome.storageにキャッシュする。結果のステータスは3種類ある。

| ステータス | 意味 | 例 |
|-----------|------|-----|
| `has-next` | 続刊あり | 次巻が見つかった |
| `no-next` | 続刊なし | 最新巻を所有済み |
| `unknown` | 解析不能 | ページ構造が変わった、ネットワーク障害 |

問題は、`unknown` を受け取ったときの処理にあった。

```js
// 修正前: unknownでも常にキャッシュを上書きしていた
const cacheEntry = { ...result, checkedAt: Date.now() };
newCache[series.key] = cacheEntry;
```

前回の照会で `has-next`（続刊あり）だったシリーズが、ページ構造の変更で `unknown` になると、キャッシュが `unknown` で上書きされる。ユーザーから見ると、「続刊あり」と表示されていたカードが突然「不明」に変わる。

## 「unknownは結果ではない」という判断

修正の方針を決めるにあたり、`unknown` の意味を整理した。

- `has-next` / `no-next` は**解析が成功した結果**。信頼できる
- `unknown` は**解析できなかった状態**。結果ではなく、結果が得られなかったことを示す

「解析できなかった」ときに、前回の「解析できた結果」を捨てるのはおかしい。HTTPの `stale-if-error` と同じ発想で、**エラー時は古い値を保持する**のが合理的だった。

## 設計: 2つの仕組み

### 1. 既存値保持

`unknown` が返ったとき、そのシリーズに既存のキャッシュがあれば何も書き込まない。既存のキャッシュがない（初回照会）場合だけ、`unknown` をキャッシュに入れる。

```js
if (result?.status === 'unknown') {
  unknownStreak += 1;
  if (unknownStreak >= MAX_CONSECUTIVE_UNKNOWN) {
    throw new Error(
      `Catalog results were indeterminate for ${MAX_CONSECUTIVE_UNKNOWN} consecutive series; retry later`
    );
  }
  // 既存キャッシュがあれば保持、なければunknownを記録
  if (prevCache[series.key] == null) {
    newCache[series.key] = { ...result, checkedAt: Date.now() };
  }
  continue;
}
```

`{ ...prevCache, ...newCache }` でマージするため、`newCache` に書き込まなければ `prevCache` の値がそのまま残る。

### 2. 連続失敗検知

既存値を保持するだけでは、「サイトが完全に落ちていて全件unknownが続く」状況を検知できない。そこで連続unknown数をカウントし、閾値を超えたら処理を中断して再試行キューに回す。

```js
const MAX_CONSECUTIVE_UNKNOWN = 3;
```

閾値を3件にした理由は、1-2件の `unknown` は個別の商品ページの問題（販売終了、ページ構造の部分的変更）で起きうるが、3件連続は外部サイト全体の障害を示唆するため。

成功（`has-next` / `no-next`）またはエラー（例外スロー）が来たらカウンタをリセットする。

```js
// 成功時
unknownStreak = 0;
const cacheEntry = { ...result, checkedAt: Date.now() };
newCache[series.key] = cacheEntry;

// エラー時（ネットワーク障害など）
} catch (error) {
  failedCount += 1;
  unknownStreak = 0;  // エラーはunknownとは別扱い
  continue;
}
```

エラー（例外）でもカウンタをリセットするのは、エラーと `unknown` は原因が異なるため。ネットワーク障害で1件失敗しても、次の照会が `unknown` を返すとは限らない。

## chunk境界での引き継ぎ

バックグラウンド照会は8件単位のchunkで処理する。Service Workerの実行時間制限対策として、1 chunkごとにstorageへ保存し、次のchunkへ進む。

ここで問題になったのが、chunkの切れ目で `unknownStreak` がリセットされてしまうこと。chunk Aの最後の2件が `unknown` → chunk Bの最初の1件が `unknown` のとき、通算3件連続なのに各chunk内では閾値に達しない。

解決策として、chunkの戻り値に `unknownStreak` を含め、次のchunkの入力に引き継ぐようにした。

```js
// chunk処理の呼び出し側
unknownStreak = Number(response.unknownStreak) || 0;
// ↓ 次のchunkへ引き継ぎ
initialUnknownStreak: unknownStreak,
```

## Chrome / Firefox で同じ契約

この拡張はChromeとFirefoxの両方に対応している。Chromeでは `offscreen document` 経由でDOM解析を行い、Firefoxではインラインで実行する。実行方式は違うが、unknown判定・既存値保持・連続失敗検知のロジックは同一にした。

```js
// background.js (Firefox向け probeInline)
if (result?.status === 'unknown') {
  unknownStreak += 1;
  if (unknownStreak >= MAX_CONSECUTIVE_UNKNOWN) { throw new Error(...); }
  if (prevCache[series.key] == null) { newCache[series.key] = ...; }
  continue;
}

// offscreen.js (Chrome向け probeChunk) — 同一ロジック
if (result?.status === 'unknown') {
  unknownStreak += 1;
  if (unknownStreak >= MAX_CONSECUTIVE_UNKNOWN) { throw new Error(...); }
  if (prevCache[series.key] == null) { newCache[series.key] = ...; }
  continue;
}
```

「保存結果の契約」を揃えることで、ブラウザごとに異なるバグが生まれるリスクを減らした。

## 採用しなかった方法

### unknownを一定時間キャッシュして再利用する

unknown結果にTTLを設けて「30分間はunknownのまま再照会しない」案も検討した。しかし、TTL管理が複雑になるうえに、30分後に再照会しても同じunknownが返る（ページ構造変更は数時間〜数日続く）可能性が高い。「既存値を保持して次の成功まで待つ」ほうが単純で堅牢だった。

### すべてのunknownを一律failedにする

1件でもunknownが出たら即座にfailed扱いにする案は、正常な照会まで巻き添えにする。個別の商品ページだけ構造が変わるケースは実際にあるため、「連続した場合だけfailed」のほうが実態に合っていた。

## まとめ

- 外部サイトの解析結果が `unknown` のとき、既存キャッシュを上書きしない。確定情報を守る
- 3件連続 `unknown` で処理を中断し、再試行キューに回す。サイト全体の障害を検知する
- chunk境界で連続カウンタを引き継ぎ、分割処理でも正しく検知する
- Chrome / Firefox で同じ判定ロジックを維持し、ブラウザ間の挙動差を防ぐ

## 参考リンク

- [kindle-series-sale-tracker リポジトリ](https://github.com/harness17/kindle-series-sale-tracker)
- [Chrome Extensions - Offscreen Documents](https://developer.chrome.com/docs/extensions/reference/api/offscreen)
- [HTTP Conditional Requests - stale-if-error](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Cache-Control#stale-if-error)
