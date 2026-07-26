---
title: "Kindle蔵書の1万件上限を複数ソートとASINマージで越えた話"
emoji: "📚"
type: "tech"
topics: ["chrome拡張", "kindle", "javascript", "amazon", "個人開発"]
published: true
---

## はじめに

Kindle 蔵書からシリーズ候補を作る Chrome / Firefox 拡張を作っている。最初は Amazon.co.jp のデジタルコンソール Ajax を取得日降順で順番に読めば、全件取れると思っていた。

ところが、大きい蔵書では単一のソート順だけだと約 1 万件で頭打ちになる。続刊チェックの精度は「持っている巻」をどれだけ正しく取れるかに依存するため、ここで抜けが出ると、既に持っている巻を未購入扱いにしたり、所有巻数を少なく見積もったりする。

この記事では、単一ソートのページングを伸ばすのではなく、複数のソート順で取得して ASIN をキーにマージする設計にした判断を書く。

**対象読者**: ブラウザ拡張で外部サイトの一覧データを扱っていて、ページング上限や重複取得に悩んでいる開発者。

**リポジトリ**: [kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)

## 何が困ったか

Kindle Series Sale Tracker は、Amazon.co.jp の Kindle 蔵書一覧から購入済み本を取得し、タイトル・著者・巻数を正規化してシリーズ候補を作る。取得にはデジタルコンソールの Ajax を使う。

1回のリクエストでは 100 件ずつ取得する。単純なページングだけなら、`startIndex` を 0, 100, 200... と増やせばよい。

```js
const BATCH_SIZE = 100;
const AJAX_URL = 'https://www.amazon.co.jp/hz/mycd/digital-console/ajax';
// Amazon の Ajax は1ソート順あたり約1万件で頭打ちになる。安全上限はその少し上に置く。
const MAX_START_INDEX = 10500;
// 連続リクエストの間隔。複数ソートパスで負荷が倍増するため throttle / 403 を避ける。
const REQUEST_DELAY_MS = 120;
```

この方式の問題は、単一のソート順で見える範囲に上限があることだった。`MAX_START_INDEX` を無制限に伸ばしても、同じソート順で見える範囲が変わらなければ、同じ境界にぶつかるだけになる。

## 捨てた選択肢

最初に考えたのは、取得日の降順だけで最後まで粘る方法だった。しかし、これはページング上限そのものを越えられない。

次に、取得件数をユーザーに分けてもらう案も考えた。たとえば「最近の本だけ取得」「全件取得は重いので手動で再実行」のような UI にする方法である。ただ、シリーズ続刊チェックの基礎データとしては、持っている巻が抜けるほど誤判定が増える。機能の根本に関わるため、UI で妥協する前に取得戦略を変える必要があった。

採用したのは、ソート順を変えて別の「先頭」を見る方法だった。

## 複数ソート順で別の1万件を見る

実装では、取得日・タイトル・著者の各軸を昇順/降順で走査する。

```js
// 各ソート順は1万件で頭打ちになる。異なる軸（取得日・タイトル・著者）×昇順/降順で
// 取得して ASIN マージすると、それぞれ別の「先頭1万件」が見えるため壁を越えられる。
// 取得日2軸だけなら最大2万件、6パスなら理論上6万件規模までカバーできる。
// reportedTotal 到達で全パス即終了するため、蔵書が少ないユーザーでは先頭の数パスで止まる
// （追加パスは大規模ライブラリでのみ作動する）。
const SORT_PASSES = [
  { sortOrder: 'DESCENDING', sortIndex: 'DATE' },
  { sortOrder: 'ASCENDING', sortIndex: 'DATE' },
  { sortOrder: 'ASCENDING', sortIndex: 'TITLE' },
  { sortOrder: 'DESCENDING', sortIndex: 'TITLE' },
  { sortOrder: 'ASCENDING', sortIndex: 'AUTHOR' },
  { sortOrder: 'DESCENDING', sortIndex: 'AUTHOR' },
];
```

ここで重要なのは、「ソート順を増やせば重複も増える」と割り切ることだった。取得結果を配列に足すだけだと、同じ本が何度も入る。そこで、ASIN を一意キーにして `Map` へマージする。

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

`reportedTotal` に到達した時点で全パスを止める。小さい蔵書では最初のソート順だけで終わり、大きい蔵書のときだけ追加パスが効く。

## 追加ソート軸の失敗は全体失敗にしない

外部サイトの内部 Ajax に依存しているため、すべてのソート軸が常に通るとは限らない。タイトル順や著者順が拒否されても、取得日順で既に一部取れているなら、全体を失敗させるより続行したほうがよい。

ただし、最初の1件も取れていない場合はログイン切れや CSRF トークン取得失敗の可能性が高い。その場合は致命的な失敗として投げ直す。

```js
try {
  // sort passごとのページング
} catch (error) {
  // 追加ソート軸（TITLE/AUTHOR 等）が API に拒否されても全体を止めない。
  // ただし1件も取得できていない＝最初の取得自体の失敗（ログイン切れ等）は致命的なので投げ直す。
  if (byAsin.size === 0) throw error;
  console.warn('[KST] ソートパスをスキップしました', pass, error?.message || error);
}
```

ここは外部サイト依存の機能では大事な境界だった。追加パスは「精度を上げるための手段」であって、初回取得の成立条件ではない。

## 簡易モードは別の割り切りにした

全件取得は重いので、普段の更新では取得日降順だけを見る簡易モードも用意した。既知 ASIN が連続して一定数出たら、新着領域を抜けたと判断して止める。

```js
// 簡易モード: 取得日 降順で先頭から取得し、既知 ASIN が連続して規定数出たら停止する。
// 新刊（最近の購入）はリストの先頭付近に集まるため、新着分だけを短時間で拾える。
// 限界: 配信が後から確定して「古い取得日」で現れる本（ゴースト配信）や、返品・削除は
// 降順の先頭には来ないため拾えない。これらの整合にはフルモードが要る。
async function collectRecentBooks(csrfToken, knownAsins) {
  const pass = { sortOrder: 'DESCENDING', sortIndex: 'DATE' };
  const newByAsin = new Map();
  let consecutiveKnown = 0;
  let scanned = 0;
  // ...
}
```

簡易モードは速い代わりに、古い取得日として現れる本や削除・返品の整合には弱い。そこはフルモードの責務として分けた。

## 回帰テストで固定したこと

取得パスの実リクエストは外部サイトに依存するため、テストではマージ後のロジックを固定した。特に、同じ ASIN を再取得しても重複計上しないことは重要だった。

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

外部サイトの実レスポンスそのものは変わる。だからこそ、取得後に守りたい契約をテストに落とした。

## まとめ

- 単一ソート順のページングを伸ばすだけでは、約1万件の上限を越えられなかった
- 取得日・タイトル・著者の昇順/降順を走査し、ASIN をキーに `Map` でマージした
- 追加ソート軸の失敗は全体失敗にせず、最初の取得失敗だけを致命的に扱った
- 普段の更新は簡易モード、整合性の回復はフルモードに分けた

## 参考リンク

- [kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)
- [Chrome Extensions - Storage API](https://developer.chrome.com/docs/extensions/reference/api/storage)
- [Amazon Kindle デジタルコンテンツ管理](https://www.amazon.co.jp/hz/mycd/digital-console/contentlist/booksAll/dateDsc/)
