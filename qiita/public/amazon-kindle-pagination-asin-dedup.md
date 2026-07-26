---
title: Amazon Kindle蔵書取得が1万件付近で止まるので複数ソートをASINでマージした
tags:
  - JavaScript
  - Chrome拡張
  - Kindle
  - Amazon
private: false
updated_at: '2026-07-26T13:16:30+09:00'
id: ee3c128f5a2d0964c034
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

Amazon Kindle蔵書のAjax取得で、単一ソート順のページングだけに頼ると約1万件付近で頭打ちになる。取得日・タイトル・著者の昇順/降順を複数パスで取得し、ASINをキーに`Map`で重複排除した。

```js
const byAsin = new Map();

for (const pass of SORT_PASSES) {
  for (let startIndex = 0; startIndex < MAX_START_INDEX; startIndex += BATCH_SIZE) {
    const { batch } = await fetchOwnershipPage(csrfToken, pass, startIndex);
    if (batch.length === 0) break;

    for (const book of batch) {
      if (!byAsin.has(book.asin)) byAsin.set(book.asin, book);
    }
  }
}
```

## 起きたこと

Kindle Series Sale Trackerでは、Amazon.co.jpのKindle蔵書一覧から所有本を取得して、シリーズ候補を作っている。最初は取得日降順だけをページングすれば全件取れると考えていた。

しかし、大きい蔵書では単一ソート順で見える範囲に上限があり、`startIndex`を増やすだけでは抜けが出る。さらに複数回取得すると同じASINが重複して返るため、単純に配列へ追加すると所有冊数も水増しされる。

## 再現条件

実装では1回100件ずつ取得する。

```js
const BATCH_SIZE = 100;
// Amazon の Ajax は1ソート順あたり約1万件で頭打ちになる。安全上限はその少し上に置く。
const MAX_START_INDEX = 10500;
const REQUEST_DELAY_MS = 120;
```

取得時に指定しているのは、`sortOrder`と`sortIndex`である。

```js
const SORT_PASSES = [
  { sortOrder: 'DESCENDING', sortIndex: 'DATE' },
  { sortOrder: 'ASCENDING', sortIndex: 'DATE' },
  { sortOrder: 'ASCENDING', sortIndex: 'TITLE' },
  { sortOrder: 'DESCENDING', sortIndex: 'TITLE' },
  { sortOrder: 'ASCENDING', sortIndex: 'AUTHOR' },
  { sortOrder: 'DESCENDING', sortIndex: 'AUTHOR' },
];
```

取得日降順だけでは「最近取得した本の先頭1万件」に偏る。昇順にすると古い側、タイトルや著者順にすると別の先頭が見える。

## 原因

ページング上限に対して、1つの並び順だけを前提にしていたのが原因だった。

`startIndex`を大きくしても、同じソート順で見える範囲が変わらなければ限界を越えられない。別のソート軸で取得し直し、同じASINを1冊として扱う必要があった。

## 解決

全件取得モードでは、複数のソートパスを順番に走査し、ASINでマージする。

```js
async function collectAllBooks(csrfToken) {
  const byAsin = new Map();
  let reportedTotal = 0;
  let collectedAll = false;

  for (let passIndex = 0; passIndex < SORT_PASSES.length && !collectedAll; passIndex += 1) {
    const pass = SORT_PASSES[passIndex];

    for (let startIndex = 0; startIndex < MAX_START_INDEX; startIndex += BATCH_SIZE) {
      const { batch, numberOfItems } = await fetchOwnershipPage(csrfToken, pass, startIndex);
      if (Number.isFinite(numberOfItems)) {
        reportedTotal = Math.max(reportedTotal, numberOfItems);
      }
      if (batch.length === 0) break;

      for (const book of batch) {
        if (!byAsin.has(book.asin)) byAsin.set(book.asin, book);
      }

      if (reportedTotal > 0 && byAsin.size >= reportedTotal) {
        collectedAll = true;
        break;
      }
      if (batch.length < BATCH_SIZE) break;
      await delay(REQUEST_DELAY_MS);
    }
  }

  return Array.from(byAsin.values());
}
```

`reportedTotal`に到達したら残りのパスは打ち切る。小さい蔵書では余分なリクエストを投げず、大きい蔵書だけ追加パスが効く。

## 注意点

複数ソートを使うとリクエスト数が増える。連続リクエスト間には短い待ち時間を入れ、追加ソート軸が失敗しても最初の取得が成功していれば全体は止めない。

```js
} catch (error) {
  if (byAsin.size === 0) throw error;
  console.warn('[KST] ソートパスをスキップしました', pass, error?.message || error);
}
```

初回取得が0件ならログイン切れやCSRFトークン取得失敗の可能性が高いため、そこでだけ致命的な失敗として扱う。

## 確認

ASIN重複を冊数に二重計上しないことは検証スクリプトで固定した。

```js
{
  name: '簡易マージ: 同一ASIN再取得は重複計上しない（added=0）',
  ok: (() => {
    const existing = [normalizeBook({ title: '鬼滅の刃 1', authors: ['吾峠呼世晴'], asin: 'K1' })].map(toMinimalBook);
    const merged = mergeScan(existing, [normalizeBook({ title: '鬼滅の刃 1', authors: ['吾峠呼世晴'], asin: 'K1' })]);
    return merged.added === 0 && merged.minimalBooks.length === 1;
  })(),
}
```

## 参考

- [kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)
- [Chrome Extensions Storage API](https://developer.chrome.com/docs/extensions/reference/api/storage)
