---
title: chrome.storage.localのquota超過を保存データの重複削減で直した
tags:
  - JavaScript
  - 設計
  - ChromeExtension
  - 個人開発
  - ManifestV3
private: false
updated_at: '2026-06-14T19:57:06+09:00'
id: f2fa36ff24d5226b725c
organization_url_name: null
slide: false
ignorePublish: false
---

## 何に詰まったか

Chrome 拡張で取得結果を `chrome.storage.local` へ保存していたところ、データ件数が増えた環境で次のエラーになった。

```text
Resource::kQuotaBytes quota exceeded
```

原因は件数だけではなかった。同じ書籍配列を全体一覧とシリーズ別データへ重複保存し、表示に使っていない画像 URL やタイトルも各要素へ持たせていた。

## 結論

`unlimitedStorage` 権限や IndexedDB を追加する前に、保存境界でデータを最小化した。

- 書籍ごとに必要な識別・集計項目だけ保存する
- シリーズ側へ書籍配列を複製しない
- 画像 URL は表示に必要な代表値だけ残す
- quota エラー時は古い結果を削除して1回だけ再試行する
- 再試行も失敗したら、シリーズ集計だけを保存する

この変更では保存 JSON が従来のおよそ4分の1になった。

## 保存前の構造

概念的には次のような重複があった。

```js
{
  books: [
    {
      asin: '...',
      title: '...',
      author: '...',
      productImage: 'https://...',
      seriesKey: '...',
      volume: 1
    }
  ],
  series: [
    {
      key: '...',
      books: [/* 同じ書籍情報を再度保持 */]
    }
  ]
}
```

書籍数が増えると、長いタイトルや URL の重複がそのまま保存量へ効く。

## 保存用DTOを作る

画面表示用オブジェクトをそのまま永続化せず、保存専用の最小形へ変換した。

```js
function toMinimalBook(book) {
  return {
    asin: book.asin,
    seriesKey: book.seriesKey,
    volume: book.volume,
    imprint: book.imprint,
    author: book.author,
  };
}
```

シリーズ集計には書籍配列を持たせず、必要な値だけ残す。

```js
function toStoredSeries(group) {
  return {
    key: group.key,
    title: group.title,
    highestVolume: group.highestVolume,
    latestOwnedThumbnailUrl: group.latestOwnedThumbnailUrl,
  };
}
```

ポイントは、取得時の完全なオブジェクトと保存形式を分けることだった。CSV や表示で本当に必要な項目は残し、「いつか使うかもしれない」値は保存しない。

## 保存量を計測する

Chrome では `getBytesInUse()` で保存済みデータの概算バイト数を取得できる。

```js
const bytes = await chrome.storage.local.getBytesInUse('scanResult');
console.log(`scanResult: ${bytes} bytes`);
```

保存前の比較には JSON のバイト数も使える。

```js
function jsonBytes(value) {
  return new TextEncoder().encode(JSON.stringify(value)).byteLength;
}

console.log({
  full: jsonBytes(fullPayload),
  minimal: jsonBytes(minimalPayload),
});
```

文字数ではなく UTF-8 のバイト数で比較すると、日本語を含むデータでも差を把握しやすい。

## quotaエラー時の回復処理

保存失敗を握りつぶさず、quota 系エラーだけを判定する。

```js
function isQuotaError(error) {
  const message = String(error?.message || error);
  return /quota|QUOTA_BYTES|kQuotaBytes/i.test(message);
}
```

古い結果を削除して1回だけ再試行する。

```js
async function saveResult(result) {
  try {
    await chrome.storage.local.set({ scanResult: result });
    return { degraded: false };
  } catch (error) {
    if (!isQuotaError(error)) throw error;
  }

  await chrome.storage.local.remove('scanResult');

  try {
    await chrome.storage.local.set({ scanResult: result });
    return { degraded: false };
  } catch (error) {
    if (!isQuotaError(error)) throw error;

    const degraded = {
      ...result,
      items: [],
      itemsOmittedForQuota: result.items.length,
    };
    await chrome.storage.local.set({ scanResult: degraded });
    return { degraded: true };
  }
}
```

無限再試行にせず、縮退保存したことを呼び出し側へ返す。画面では「シリーズ一覧は保存したが、書籍明細は再スキャンが必要」と表示できる。

## テストしたこと

- 保存した書籍のキーが想定した5項目だけである
- 各シリーズへ `items` や `books` の配列を複製していない
- 未使用の `productImage` を保存していない
- quota 以外の例外は再試行せず上位へ返す
- quota 時の再試行も失敗したら明細なしで保存する

## 注意点

Chrome の現在の公式ドキュメントでは `storage.local` の上限は 10 MB で、Chrome 113 以前は 5 MB だった。`unlimitedStorage` で上限を緩和できるが、不要な重複を残したまま権限だけ増やすと、データ構造の問題を先送りする。

保存対象が大きな本文、画像、履歴へ広がるなら IndexedDB も候補になる。今回は設定と集計結果が中心だったため、`chrome.storage.local` のままスキーマを小さくした。

## 参考

- [chrome.storage API](https://developer.chrome.com/docs/extensions/reference/api/storage)
- [保存データを軽量化したコミット](https://github.com/harness17/kindle-series-sale-tracker/commit/37e40bd3c7744141332e396a303962d3a3f189e9)
