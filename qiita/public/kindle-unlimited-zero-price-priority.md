---
title: Kindle Unlimitedの0円表示を購入価格として拾ってしまうので価格候補の優先順を分けた
tags:
  - JavaScript
  - Chrome拡張
  - Kindle
  - テスト
private: false
updated_at: '2026-07-26T13:16:39+09:00'
id: a4d26b3c187c3139938c
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

Amazon検索結果のHTMLでは、Kindle Unlimitedの`￥0`と購入価格が同じカード内に出ることがある。最初に見つかった価格を採用すると、購入価格を0円として誤認する。

`Kindle Unlimited`表示がある場合は、0円の後に出る正の価格を購入価格として優先した。

```js
let price = prices[0];
if (hasKindleUnlimited && price === 0) {
  const purchasePrice = prices.find((candidate) => candidate > 0);
  if (purchasePrice !== undefined) price = purchasePrice;
}
return yenText(price);
```

## 起きたこと

Kindleの続刊候補をAmazon検索結果から取得し、価格や割引率を表示する処理を作っていた。カード本文には価格らしき文字列が複数出る。

たとえば、Kindle Unlimited対象の本では次のような情報が同じ検索結果カード内に混在する。

```text
Kindle Unlimited ￥0 Kindle版 ￥748
```

ここで最初の価格だけを拾うと、購入価格が`￥0`になる。セール判定や完結コスト計算に使う価格なので、この誤認は画面の判断を直接壊す。

## 原因

価格候補を「見つかった順」に扱っていたことが原因だった。

`￥0`は読み放題として読めることを表す表示であり、購入価格ではない。購入価格が別に出ているなら、そちらを採用する必要がある。

## 解決

カード本文に`Kindle Unlimited`または`読み放題`がある場合だけ、0円の扱いを変える。

```js
function selectCurrentPriceText(node, selectors) {
  const domPrices = queryTexts(node, selectors)
    .map((text) => parseYenPrice(text))
    .filter((price) => price !== null);

  const signalText = collectSignalText(node, { excludeTitles: true, excludeCoupons: true });
  const hasKindleUnlimited = /Kindle\s*Unlimited|読み放題/i.test(signalText);
  const prices = hasKindleUnlimited ? [...domPrices, ...parseYenPrices(signalText)] : domPrices;
  if (prices.length === 0) return '';

  let price = prices[0];
  if (hasKindleUnlimited && price === 0) {
    const purchasePrice = prices.find((candidate) => candidate > 0);
    if (purchasePrice !== undefined) price = purchasePrice;
  }

  return yenText(price);
}
```

通常カードでは最初に取れたDOM価格を使う。Kindle Unlimited表示があるカードだけ、0円を読み放題表示として扱い、正の価格を探す。

## 回帰テスト

ブラウザを起動しなくても確認できるよう、`textContent`、`querySelector`、`querySelectorAll`だけを持つ合成ノードでテストした。

```js
{
  name: 'Kindle Unlimited の0円DOM表示より購入価格DOMを優先する',
  ok: (() => {
    const node = {
      textContent: 'Kindle Unlimited ￥0 Kindle版 ￥748',
      querySelector(selector) {
        if (selector.includes('a-text-price') || selector.includes('a-text-strike')) return null;
        if (selector.includes(':not') || selector.includes('data-a-color') || selector.includes('.a-price')) {
          return { textContent: '￥0' };
        }
        return null;
      },
      querySelectorAll(selector) {
        if (selector.includes('a-text-price') || selector.includes('a-text-strike')) return [];
        return [{ textContent: '￥0' }, { textContent: '￥748' }];
      },
    };
    const offer = extractSearchResultOffer(node);
    return offer.priceText === '￥748' && offer.listPriceText === '' && offer.discountRate === null;
  })(),
}
```

実HTMLそのものを固定するのではなく、抽出関数が依存する最小のDOM風インターフェースを固定している。

## 注意点

タイトルに`20%OFF`のような文字列が含まれるケースもある。カード全体のテキストだけから割引率を拾うと、商品名の一部を割引として誤認する。

そのため、価格抽出ではタイトルやクーポン領域を除外したテキストを集めている。

```js
const signalText = collectSignalText(node, { excludeTitles: true });
const hasKindleUnlimited = /Kindle\s*Unlimited|読み放題/i.test(signalText);
```

検索結果HTMLは外部サイト依存なので、セレクタは変わる前提で見る。今回のテストは「0円より購入価格を優先する契約」を守るためのもの、と範囲を切った。

## 参考

- [kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)
- [MDN: Element.querySelector()](https://developer.mozilla.org/docs/Web/API/Element/querySelector)
