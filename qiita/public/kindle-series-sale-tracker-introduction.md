---
title: Kindle蔵書から続刊候補を自動抽出するChrome拡張を公開した
tags:
  - JavaScript
  - Amazon
  - Kindle
  - Chrome拡張
  - 個人開発
private: false
updated_at: '2026-06-04T22:27:34+09:00'
id: 789671e35f8b2bb1bce9
organization_url_name: null
slide: false
ignorePublish: false
---

Amazon.co.jp の Kindle 蔵書から購入済みシリーズを検出し、次巻候補の価格・割引率・発売日をまとめて表示する Chrome / Firefox 拡張を作って公開しました。

Zenn に同じ拡張の紹介記事を書いています。こちらはモジュール設計と実装の詰まりどころに絞った内容です。

原文：[Kindleの続刊セールを見逃さないためにChrome拡張を作った](https://zenn.dev/harness/articles/kindle-series-sale-tracker-introduction)

---

## 拡張の概要

- Chrome Web Store: https://chromewebstore.google.com/detail/kindle-series-sale-tracke/aiemlodfimjjbeejdghomifkhhhaekfm
- Firefox Add-ons: https://addons.mozilla.org/ja/firefox/addon/kindle-series-sale-tracker/
- GitHub: https://github.com/harness17/kindle-series-sale-tracker

操作は「Kindle 一覧を開く」→「このページをスキャン」の2ステップです。Amazon.co.jp にログインした状態で実行すると、購入済み Kindle 本の一覧を取得し、次巻候補を検索して一覧表示します。

## モジュール構成と分けた理由

`extension/shared/` に3つのモジュールを置いています。

| モジュール | 責務 |
|---|---|
| `kindle-library.js` | Amazon デジタルコンソールの Ajax から蔵書一覧を取得・正規化 |
| `catalog-probe.js` | Amazon 商品検索で続刊候補を取得・シリーズ照合 |
| `series-card.js` | UI カードの生成 |

蔵書取得は Amazon のデジタルコンソールのページ構造に依存していて、Amazon 側の変更で壊れる前提があります。続刊の商品検索は別の原因で壊れるため、同じモジュールに混ぜると原因の切り分けが難しくなります。壊れ方を局所化するために分けました。

## 書誌データの正規化（kindle-library.js）

Amazon の書誌には全角英数と HTML エンティティの二重エンコードが混在しています。タイトルの表記ゆれをそのままにするとシリーズ照合がずれるため、`kindle-library.js` に正規化処理を集約しています。

```javascript
// 全角英数を半角に正規化（例：「２巻」→「2巻」）
function normalizeAsciiAlphanumerics(value) {
  return String(value ?? '').replace(/[０-９Ａ-Ｚａ-ｚ]/g, (ch) =>
    String.fromCharCode(ch.charCodeAt(0) - 0xfee0)
  );
}

// &amp;amp; のような二重エンコードを変化しなくなるまで復号する（最大5回）
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

上限5回は暴走防止です。単一エンコードに対しては冪等で動作します。

## シリーズ照合の実装（catalog-probe.js）

### スピンオフの誤判定を防ぐ

部分一致でシリーズを判定すると、スピンオフを同一シリーズと誤判定します。たとえば「小林さんちのメイドラゴン」を部分一致のキーにすると、スピンオフの「エルマのOL日記」も続刊として拾われます。正規化した seriesKey の完全一致のみに絞りました。

```javascript
// 完全一致のみ。末尾のハイフン・波線類を除去してから比較する
function sameSeries(a, b) {
  if (!a || !b) return false;
  const normalizeKey = (value) =>
    kdl.normalizeSeriesKey(value).replace(/\s+/g, '').replace(/[-‐－―—~～]+$/g, '');
  const na = normalizeKey(a);
  const nb = normalizeKey(b);
  return na !== '' && na === nb;
}
```

### 単話版の除外

単話版（1話ずつの分冊配信）を除外しないと、完結済みの作品でも話数を追って延々と「続刊あり」と表示されます。

```javascript
// 単話版・分冊版を続刊候補から除外する
// 判定は加工前の rawTitle で行う（stripNoise で除去される前の文字列）
function isSplitVolumeEdition(rawTitle) {
  return /単話|分冊|話売り/.test(String(rawTitle || ''));
}
```

タイトル正規化の前の rawTitle で判定しているのは、`stripNoise` で「【単話版】」が消える前でないと判定できないためです。

### 別レーベル版の除外

所有しているレーベルと異なるレーベルの候補は除外します。

```javascript
// 所有レーベルと候補レーベルが両方あり、かつ異なるときだけ除外する
// 片方が空（情報不足）なら拾う（改題・改称の取りこぼし最小化）
function isDifferentImprint(ownedImprint, candidateImprint) {
  return Boolean(ownedImprint) && Boolean(candidateImprint) && ownedImprint !== candidateImprint;
}
```

## 検証スクリプト

本番コードを変更するたびに3つの検証スクリプトを使っています。

```powershell
node .\verify-kindle-library.mjs   # 蔵書取得・正規化のロジック
node .\verify-catalog-probe.mjs    # シリーズ照合・フィルタのロジック
node .\verify-series-card.mjs      # カード生成のロジック
```

fixture と照合して回帰を確認する構成で、Amazon 側の変更で壊れたとき、どのモジュールが原因かをすぐに絞り込めます。

## 公開状況

Chrome Web Store に Manifest V3 対応で審査を出し、通過しました。Firefox 版も Firefox Add-ons の審査を通過し、同じ拡張を公開しています。

リポジトリ: https://github.com/harness17/kindle-series-sale-tracker
