---
title: "Chrome拡張の容量超過を権限追加ではなく保存スキーマ削減で直した"
emoji: "📦"
type: "tech"
topics: ["chrome拡張", "manifestv3", "javascript", "設計", "個人開発"]
published: true
---

## はじめに

Chrome 拡張で取得結果を `chrome.storage.local` へ保存していたところ、データ件数が多い環境で次のエラーになった。

```text
Resource::kQuotaBytes quota exceeded
```

対象は [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) の書籍一覧とシリーズ集計だった。最初は「件数が多いから上限へ達した」と考えたが、保存 JSON を見ると、同じ書籍情報を全体一覧とシリーズ別データへ重複保存していた。表示に使っていない画像 URL や長いタイトルも各所に残っていた。

この記事では、`unlimitedStorage` 権限や IndexedDB を追加する前に、保存形式を画面用データから分離して容量を約4分の1へ減らした判断を書く。

## 件数より保存構造の重複が効いていた

問題の構造を単純化すると次の形だった。

```js
const result = {
  books: [
    {
      asin: "...",
      title: "...",
      productImage: "https://...",
      seriesKey: "...",
      volume: 1,
    },
  ],
  series: [
    {
      key: "...",
      books: [/* booksと同じ書籍情報 */],
    },
  ],
};
```

画面では完全な書籍オブジェクトが便利だった。しかし、その構造を永続化へ流用すると、長い文字列と配列が重複する。

Chrome の現在の公式資料では `storage.local` の上限は 10 MB で、Chrome 113 以前は 5 MB だった。`unlimitedStorage` 権限を追加すれば上限を広げられるが、不要な重複を残したまま権限だけ増やすと、件数が増えたときに同じ問題が戻る。

そこで、先に保存対象を分類した。

| データ | 保存判断 |
| --- | --- |
| ASIN、シリーズキー、巻数 | 再計算や照合に必要なので残す |
| 著者、レーベル | 表示と絞り込みに必要なので残す |
| 全書籍の画像URL | 一覧表示に不要なので落とす |
| シリーズ内の書籍配列 | 全体一覧と重複するため持たない |
| 代表サムネイル | シリーズ表示に必要な1件だけ残す |

## 画面モデルと保存DTOを分けた

保存専用の変換関数を用意し、取得時のオブジェクトをそのまま `storage.local` へ渡さないようにした。

```js:storage-schema.js
function toStoredBook(book) {
  return {
    asin: book.asin,
    seriesKey: book.seriesKey,
    volume: book.volume,
    imprint: book.imprint,
    author: book.author,
  };
}

function toStoredSeries(group) {
  return {
    key: group.key,
    title: group.title,
    highestVolume: group.highestVolume,
    latestOwnedThumbnailUrl: group.latestOwnedThumbnailUrl,
  };
}
```

この分離で、「取得時に必要な情報」と「次回起動後も必要な情報」を別々に判断できるようになった。追加フィールドが画面に必要になっても、自動的に保存対象へ増えない。

採用しなかった案は次の2つである。

- `unlimitedStorage` を追加する: 最小権限を維持したく、重複構造の改善にならない
- IndexedDB へ移す: 大きな本文や履歴を保存する用途ではなく、移行と例外対応のコストが上回る

今回のデータは設定と集計結果が中心だったため、保存先は `chrome.storage.local` のままにした。

## 保存量をバイト数で比較した

日本語や URL を含むため、文字数ではなく UTF-8 のバイト数で比較した。

```js:measure-storage.js
function jsonBytes(value) {
  return new TextEncoder().encode(JSON.stringify(value)).byteLength;
}

console.table({
  fullPayload: jsonBytes(fullPayload),
  storedPayload: jsonBytes(storedPayload),
});
```

保存後の値は `getBytesInUse()` でも確認できる。

```js
const bytes = await chrome.storage.local.getBytesInUse("scanResult");
console.log(`scanResult: ${bytes} bytes`);
```

実装時の比較では、保存 JSON は従来のおよそ4分の1になった。単に圧縮したのではなく、同じ情報を複数箇所へ持たない構造へ変えた効果が大きかった。

## quotaエラー時は1回だけ再試行して縮退保存する

スキーマを小さくしても、将来の件数増加や古いデータの残留で保存に失敗する可能性はある。そこで、quota 系エラーだけを判定し、古い結果を削除して1回だけ再試行する。

```js:save-result.js
async function saveResult(result) {
  try {
    await chrome.storage.local.set({ scanResult: result });
    return { degraded: false };
  } catch (error) {
    if (!/quota|QUOTA_BYTES|kQuotaBytes/i.test(String(error))) throw error;
  }

  await chrome.storage.local.remove("scanResult");

  try {
    await chrome.storage.local.set({ scanResult: result });
    return { degraded: false };
  } catch (error) {
    if (!/quota|QUOTA_BYTES|kQuotaBytes/i.test(String(error))) throw error;
    const degraded = { ...result, items: [], itemsOmittedForQuota: result.items.length };
    await chrome.storage.local.set({ scanResult: degraded });
    return { degraded: true };
  }
}
```

再試行も失敗した場合は、書籍明細を落としてシリーズ集計だけ保存する。無限に再試行せず、呼び出し側へ `degraded: true` を返すことで、画面に「明細は再スキャンが必要」と表示できる。

:::message alert
quota以外の例外まで削除と再試行で隠さない。権限エラーや実装ミスは上位へ返し、原因を分けて扱う。
:::

## 確認したこと

変更後は次をテストした。

- 保存した書籍が必要なキーだけを持つ
- シリーズへ書籍配列を複製していない
- 未使用の画像 URL を保存していない
- quota 以外の例外は再試行しない
- 再試行も quota で失敗した場合だけ縮退保存する

容量上限を広げる前に保存境界を見直したことで、権限を増やさずに通常保存へ戻せた。保存形式が明示されたため、今後フィールドを追加するときも容量への影響をレビューしやすくなった。

## まとめ

- `chrome.storage.local` の quota 超過は、件数だけでなく配列と長い文字列の重複が原因だった
- 画面用オブジェクトと保存DTOを分け、永続化に必要な項目だけ残した
- 権限追加や保存先変更の前にスキーマを小さくし、失敗時は1回再試行して縮退保存する

変更内容は [保存データを軽量化したコミット](https://github.com/harness17/kindle-series-sale-tracker/commit/37e40bd3c7744141332e396a303962d3a3f189e9) に残している。

## 参考リンク

- [chrome.storage API](https://developer.chrome.com/docs/extensions/reference/api/storage) - 容量上限、`unlimitedStorage`、`getBytesInUse()`
- [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) - 記事で扱った拡張
