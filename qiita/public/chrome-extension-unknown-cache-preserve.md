---
title: '外部HTML解析がunknownのとき既存キャッシュを上書きして表示が消えた'
tags:
  - Chrome拡張
  - JavaScript
  - キャッシュ
  - ManifestV3
private: false
updated_at: '2026-06-20'
id: 1e8682fbb0e9d6195e9f
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

Zenn向けの記事では設計判断とChrome / Firefoxの実行方式差まで扱うが、この記事では検索で来たときに直せるよう、`unknown` で既存キャッシュを壊さない最小実装に絞る。

```js
if (result?.status === 'unknown') {
  unknownStreak += 1;
  if (unknownStreak >= MAX_CONSECUTIVE_UNKNOWN) {
    throw new Error('Catalog results were indeterminate; retry later');
  }
  if (prevCache[series.key] == null) {
    newCache[series.key] = { ...result, checkedAt: Date.now() };
  }
  continue;
}
```

## 起きたこと

Chrome拡張のバックグラウンド処理で、外部サイトのHTMLを定期的に解析してchrome.storageにキャッシュしていた。ある日、外部サイトのページ構造が変わり、解析結果がすべて `unknown`（解析不能）になった。

`unknown` を通常の結果と同じようにキャッシュへ書き込んでいたため、前回の照会で得られていた確定情報（「続刊あり」「セール中」など）が `unknown` で上書きされ、ユーザーの画面からデータが消えた。

## 原因

キャッシュ更新処理が、結果のステータスを区別せずに一律で上書きしていた。

```js
// 修正前: unknownでも上書き
const cacheEntry = { ...result, checkedAt: Date.now() };
newCache[series.key] = cacheEntry;
```

外部サイトのHTML解析は、ページ構造の変更やネットワーク障害で `unknown` を返すことがある。これは「結果が得られなかった」状態であり、前回の確定結果を置き換えてよいデータではない。

## 修正

### 1. unknownのとき既存キャッシュを保持する

既存のキャッシュがあれば書き込まず、前回の値をそのまま残す。

```js
const MAX_CONSECUTIVE_UNKNOWN = 3;

if (result?.status === 'unknown') {
  unknownStreak += 1;
  if (unknownStreak >= MAX_CONSECUTIVE_UNKNOWN) {
    throw new Error(
      `Catalog results were indeterminate for ${MAX_CONSECUTIVE_UNKNOWN} consecutive series; retry later`
    );
  }
  // 既存キャッシュがなければunknownを記録、あれば何もしない
  if (prevCache[series.key] == null) {
    newCache[series.key] = { ...result, checkedAt: Date.now() };
  }
  continue;
}

// 成功時はカウンタリセット
unknownStreak = 0;
const cacheEntry = { ...result, checkedAt: Date.now() };
newCache[series.key] = cacheEntry;
```

ストレージへの保存時に `{ ...prevCache, ...newCache }` でマージするため、`newCache` に書き込まなかったキーは `prevCache` の値が残る。

### 2. 3件連続unknownでfailed扱いにする

1-2件のunknownは個別ページの問題で起きうるが、3件連続はサイト全体の障害を示唆する。閾値を超えたら処理を中断し、再試行キューに回す。

```js
// エラー（例外）ではカウンタをリセット
} catch (error) {
  failedCount += 1;
  unknownStreak = 0; // エラーとunknownは別の原因
  continue;
}
```

## バッチ処理での注意点

複数件をchunk単位で処理する場合、chunk間で `unknownStreak` を引き継ぐ必要がある。chunk Aの末尾2件がunknown → chunk Bの先頭1件がunknown のとき、通算3件連続だがchunk内では検知できない。

```js
// chunk処理の戻り値に unknownStreak を含める
return {
  done: true,
  cacheEntries: newCache,
  failedCount,
  unknownStreak, // 次のchunkへ引き継ぐ
};

// 呼び出し側で次のchunkに渡す
unknownStreak = Number(response.unknownStreak) || 0;
```

## 結果

- ページ構造変更が起きても、前回の確定情報がユーザーの画面から消えなくなった
- 3件連続unknownでサイト全体の障害を検知し、不要な照会を止められるようになった
- エラーとunknownを分離したことで、ネットワーク障害1件でサイト障害と誤判定しなくなった

## 参考リンク

- [kindle-series-sale-tracker リポジトリ](https://github.com/harness17/kindle-series-sale-tracker)
- [Chrome Extensions - chrome.storage API](https://developer.chrome.com/docs/extensions/reference/api/storage)
