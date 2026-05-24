---
title: YouTubeプレイリストのDOM順を一度保存して通常順に戻す実装
tags:
  - JavaScript
  - Chrome
  - dom
  - YouTube
  - ChromeExtension
private: false
updated_at: '2026-05-24T10:22:11+09:00'
id: fa3a124e5fa50229a887
organization_url_name: null
slide: false
ignorePublish: false
---

## 何に詰まったか

YouTube プレイリストを投稿日順に並び替える Chrome 拡張を作っていたときに、もう一つ詰まったのが「通常順に戻す」機能でした。

並び替え自体は、各動画ページの HTML から投稿日を抽出して sort し、`parent.insertBefore()` で DOM を入れ替えるだけです。問題は、その後にユーザーが「並び替えを解除して、プレイリスト所有者が指定した順に戻したい」と言ったときに、元の順序を再構築する手段がなかったことです。

YouTube Data API を使えばプレイリストの公式な順序を取れますが、API キーやクォータ管理が増えます。そもそも DOM を並び替えただけなので、ページをリロードすれば元に戻ります。ただし「リロード無しで元の順に戻す」をやろうとすると、自前で順序を覚えておく必要がありました。

## 解決：抽出時に originalIndex を埋め込む

プレイリストの行を取得した瞬間に、ループのインデックスをそのまま `originalIndex` として保存します。

```js
function extractPlaylistItemsFromDocument(documentRef) {
  if (!documentRef) return [];

  const isPlaylistPage =
    documentRef.location && documentRef.location.pathname === '/playlist';
  const selector = isPlaylistPage
    ? 'ytd-playlist-video-renderer a[href*="/watch"][href*="v="]'
    : 'ytd-playlist-panel-video-renderer a[href*="/watch"][href*="v="]';

  const anchors = Array.from(documentRef.querySelectorAll(selector));
  const seen = new Set();
  const items = [];

  for (const anchor of anchors) {
    const videoId = getVideoIdFromUrl(anchor.href);
    if (!videoId || seen.has(videoId)) continue;
    seen.add(videoId);

    items.push({
      videoId,
      title: extractTitle(anchor),
      originalIndex: items.length,
    });
  }

  return items;
}
```

`extractTitle(anchor)` は本記事では説明用に省略している。実際は `#video-title` / `span[title]` / `aria-label` を順に見て取れたものを採用する処理だが、本記事の中心は `originalIndex` の振り方なので別関数に切り出した形で書いている。

ポイントは、`originalIndex` を「重複除外後の順序」で振ることです。YouTube のプレイリスト DOM はサムネイル要素や `a` タグが重複して取れることがあり、`anchors.length` を使うとずれます。`items.length` を使って「実際に items に積んだ順」で番号を振ると、後の sort と整合します。

## sort のときは tie-breaker としても使う

投稿日が同じ動画は割と出ます。同じ日に複数本投稿された動画を扱うとき、`originalIndex` を tie-breaker に入れておくと、表示が安定します。

```js
function sortItemsByPublishDate(items, dateByVideoId, order) {
  const multiplier = order === 'desc' ? -1 : 1;
  return [...items].sort((a, b) => {
    const aDate = toDateMs(dateByVideoId[a.videoId]);
    const bDate = toDateMs(dateByVideoId[b.videoId]);
    const aUnknown = !Number.isFinite(aDate);
    const bUnknown = !Number.isFinite(bDate);
    if (aUnknown !== bUnknown) return aUnknown ? 1 : -1;
    if (aDate !== bDate) return (aDate - bDate) * multiplier;
    return a.originalIndex - b.originalIndex;
  });
}
```

- 投稿日が取れなかった動画は末尾に回す
- 投稿日が同じなら `originalIndex` 順、つまりプレイリスト所有者が指定した順に揃える

## 通常順に戻す

「戻す」は、`sortedItems` を `originalIndex` で sort し直して、同じ DOM 再配置関数に渡すだけです。

```js
function restoreNativeOrder() {
  state.badgesEnabled = false;
  state.visualMode = 'idle';
  applyOrderByItems(
    [...state.sortedItems].sort((left, right) => left.originalIndex - right.originalIndex),
    'native order'
  );
  clearDecorations();
}
```

`applyOrderByItems` は並び替えと同じ DOM 再配置関数を共用しています。`parent.insertBefore()` を逆順ループで呼んで、目的の順序に近づけます。

```js
const marker = document.createComment('ytpds-native-order-marker');
parent.insertBefore(marker, sortedRows[0]);
for (let i = desiredOrder.length - 1; i >= 0; i -= 1) {
  const row = rowByVideoId.get(desiredOrder[i]);
  if (row && row.parentElement === parent) {
    parent.insertBefore(row, marker.nextSibling);
  }
}
marker.remove();
```

`marker` を入れる理由は、`parent` の先頭が他の要素（広告、おすすめ）で占められている可能性があるからです。「自分が並び替えたい範囲の先頭」をコメントノードで覚えておき、逆順に `insertBefore(row, marker.nextSibling)` していくと、`marker` の直後に正しい順で並びます。

## 詰まった点と注意点

- `originalIndex` を「DOM の `querySelectorAll` のインデックス」で振ると、重複除外でずれて元の順に戻らなくなる。`items.length` で振るほうが堅い
- 「通常順に戻す」と「投稿日順に並び替える」は、ロジックの大半が共通になる。再配置関数を 1 つに寄せて、入力の items だけ差し替えるとバグが減る
- DOM 上に「広告」「おすすめ」などプレイリスト外の行が混ざることがある。`rowByVideoId` で videoId を持つ行だけ管理し、`marker` で自分が並び替える範囲の起点を覚えるとずれにくい

## まとめ

- 「並び替えを元に戻す」のために API を呼ぶより、抽出時に `originalIndex` を埋め込んでおいて、戻すときはそれで sort するほうが軽い
- `originalIndex` は sort の tie-breaker としても使える。同日投稿の動画で表示が暴れない
- 並び替えと復元は同じ DOM 再配置関数を共用できる。差分は入力 items の順序だけ

## 参考リンク

- [Node.insertBefore - MDN](https://developer.mozilla.org/docs/Web/API/Node/insertBefore)
- [Array.prototype.sort - MDN](https://developer.mozilla.org/docs/Web/JavaScript/Reference/Global_Objects/Array/sort)
- [document.createComment - MDN](https://developer.mozilla.org/docs/Web/API/Document/createComment)
