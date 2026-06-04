---
title: "Kindleの続刊セールを見逃さないためにChrome拡張を作った"
emoji: "📚"
type: "tech"
topics: ["chrome拡張", "kindle", "javascript", "amazon", "個人開発"]
published: true
---

## はじめに

Kindle で読み続けているシリーズがあって、続刊が出るたびにセール価格で買おうと思っていたのに、気づいたら何冊も通常価格を見逃していた。そういう失敗が積み重なって、「蔵書から続刊を自動でリストアップしてくれる拡張がほしい」と思い、Chrome / Firefox 拡張として作りました。

**Kindle Series Sale Tracker** は、Amazon.co.jp の Kindle 蔵書から購入済みシリーズを検出し、次巻候補の価格・割引率・発売日をまとめて表示するブラウザ拡張です。

- Chrome：[Chrome Web Store](https://chromewebstore.google.com/detail/kindle-series-sale-tracke/aiemlodfimjjbeejdghomifkhhhaekfm)
- Firefox：[Firefox Add-ons](https://addons.mozilla.org/ja/firefox/addon/kindle-series-sale-tracker/)
- GitHub：[harness17/kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker)

## できること

拡張ポップアップから「Kindle 一覧を開く」→「このページをスキャン」の2ステップで動きます。

- 購入済み Kindle 本の一覧を Amazon.co.jp のデジタルコンソールから取得
- タイトルと著者からシリーズ候補と所有巻数を推定
- 次巻候補を探す Amazon 検索リンクを自動生成
- 続刊候補が見つかったとき、価格・割引率・発売日・表紙を表示
- 結果を CSV / JSON でエクスポート

## 実装の核心：蔵書取得と続刊検索を別モジュールに分けた

拡張の実装は `extension/shared/` 以下に3つのモジュールを置く構成にしました。

| モジュール | 責務 |
|---|---|
| `kindle-library.js` | Amazon デジタルコンソールから蔵書一覧を取得・正規化 |
| `catalog-probe.js` | Amazon 商品検索で続刊候補を取得・シリーズ照合 |
| `series-card.js` | 結果の UI カード生成 |

蔵書取得は Amazon のデジタルコンソール上の Ajax に依存していて、Amazon 側のページ変更で壊れる前提があります。続刊の商品検索とは壊れる原因が別なので、同じモジュールに混ぜると原因の切り分けが難しくなります。

### 蔵書取得側で詰まった点：書誌データの表記ゆれ

Amazon の書誌には全角英数や HTML エンティティの二重エンコードが混在しています。そのままにするとタイトルが一致せず、シリーズ照合がずれます。`kindle-library.js` に正規化処理を集約しました。

```javascript
// 全角英数を半角に正規化（例：「２巻」→「2巻」）
function normalizeAsciiAlphanumerics(value) {
  return String(value ?? '').replace(/[０-９Ａ-Ｚａ-ｚ]/g, (ch) =>
    String.fromCharCode(ch.charCodeAt(0) - 0xfee0)
  );
}

// &amp;amp; のような二重エンコードを、変化しなくなるまで復号する
function decodeHtmlEntities(value) {
  let current = String(value ?? '');
  for (let i = 0; i < 5; i += 1) {
    const next = decodeOnce(current);
    if (next === current) break;
    current = next;
  }
  return current;
}
```

### 続刊検索側で詰まった点：スピンオフと単話版の除外

シリーズ判定を部分一致にすると、スピンオフを同一シリーズと誤判定する問題が出ました。たとえば「小林さんちのメイドラゴン」でキーを部分一致にすると、スピンオフの「エルマのOL日記」も「続刊あり」として出てきてしまいます。正規化した seriesKey の完全一致のみに絞りました。

```javascript
// 同一シリーズ判定：完全一致のみ
// 部分一致にするとスピンオフを誤判定する
function sameSeries(a, b) {
  if (!a || !b) return false;
  const normalizeKey = (value) =>
    kdl.normalizeSeriesKey(value).replace(/\s+/g, '').replace(/[-‐－―—~～]+$/g, '');
  const na = normalizeKey(a);
  const nb = normalizeKey(b);
  return na !== '' && na === nb;
}
```

単話版（1話ずつの分冊配信）の除外も必要でした。これを入れないと、完結済みの作品でも話数を追って延々と「続刊あり」と判定されます。

```javascript
// 単話版・分冊版を続刊候補から除外する
// 例：「Lv1魔王とワンルーム勇者【単話版】71」など
function isSplitVolumeEdition(rawTitle) {
  return /単話|分冊|話売り/.test(String(rawTitle || ''));
}
```

## Chrome Web Store / Firefox Add-ons への公開

Manifest V3 対応で Chrome Web Store に審査を出し、通過しました。Firefox 版も Firefox Add-ons の審査を通過し、同じ拡張を公開しています。

## まとめ

- Kindle 蔵書から続刊候補を自動リストアップする Chrome / Firefox 拡張を作り、Chrome Web Store と Firefox Add-ons に公開しました
- 蔵書取得（`kindle-library.js`）と続刊検索（`catalog-probe.js`）を分けることで、Amazon 側の変更の影響範囲を局所化しています
- 書誌データの表記ゆれ、スピンオフ誤判定、単話版の混入が実装上の詰まりどころでした
- Firefox 版も公開済みです

Kindle で読み続けているシリーズが多い人に試してもらえたら。

## 参考

- [Kindle Series Sale Tracker - Chrome Web Store](https://chromewebstore.google.com/detail/kindle-series-sale-tracke/aiemlodfimjjbeejdghomifkhhhaekfm)
- [Kindle Series Sale Tracker - Firefox Add-ons](https://addons.mozilla.org/ja/firefox/addon/kindle-series-sale-tracker/)
- [harness17/kindle-series-sale-tracker - GitHub](https://github.com/harness17/kindle-series-sale-tracker)
