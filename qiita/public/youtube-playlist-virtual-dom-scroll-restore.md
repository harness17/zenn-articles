---
title: YouTubeプレイリストの101件以降が消えるためスクロール復元を抽出後へ遅らせた
tags:
  - JavaScript
  - dom
  - YouTube
  - ChromeExtension
  - 個人開発
private: false
updated_at: '2026-06-14T19:57:28+09:00'
id: 7127920c6c559bce0356
organization_url_name: null
slide: false
ignorePublish: false
---

## 何に詰まったか

YouTube プレイリストを投稿日順に並び替える Chrome 拡張で、処理上限を 100 件から 300 件へ増やした。しかし、101 件目以降を安定して取得できなかった。

末尾までスクロールすると追加行は読み込まれる。それでも、抽出前に元のスクロール位置へ戻すと、後半の行が DOM から外れて再び約100件に戻ることがあった。

## 結論

仮想化された一覧では、次の順序が必要だった。

1. 末尾方向へスクロールして追加行を読み込む
2. 読み込んだ状態のまま動画 ID を抽出する
3. 抽出が終わってからスクロール位置を戻す

上限値を増やすだけではなく、スクロール復元のタイミングを遅らせるのが修正点だった。

## 失敗した順序

最初の実装は、行を読み込む関数の中でスクロール位置まで復元していた。

```js
async function refresh() {
  await loadAllPlaylistRows(300); // この中で元位置へ戻す
  const items = await waitForPlaylistItems();
  return extractVideoIds(items);
}
```

画面上は元の位置へ戻るが、YouTube 側が表示範囲外の行を破棄した後に抽出するため、追加で読み込んだ行を失う。

YouTube の DOM は公開 API ではないため、常に同じ件数で仮想化されるとは限らない。ここで扱う「約100件」は、実装時に確認した挙動である。

## 復元処理を関数として返す

`loadAllPlaylistRows()` ではスクロール位置を保存し、末尾まで読み込んだ後に復元関数を返す。

```js
async function loadAllPlaylistRows(maxItems) {
  const targets = findScrollableTargets();
  const positions = targets.map((target) => ({
    target,
    top: target === window ? window.scrollY : target.scrollTop,
  }));

  let previousCount = 0;

  while (true) {
    const count = document.querySelectorAll(
      'ytd-playlist-video-renderer a#video-title'
    ).length;

    if (count >= maxItems || count === previousCount) break;
    previousCount = count;

    const lastRow = document.querySelector(
      'ytd-playlist-video-renderer:last-of-type'
    );
    lastRow?.scrollIntoView({ block: 'end' });
    await sleep(500);
  }

  return function restoreScroll() {
    for (const { target, top } of positions) {
      if (target === window) {
        window.scrollTo({ top });
      } else {
        target.scrollTop = top;
      }
    }
  };
}
```

実際の YouTube ページでは、`window` 以外の要素がスクロール領域になる場合もある。そのため、対象候補を複数保持する実装にした。

## 抽出後にfinallyで戻す

呼び出し側は、DOM の抽出が終わるまで復元しない。

```js
async function refreshSortedItems() {
  const restoreLoadedScroll = await loadAllPlaylistRows(300);

  try {
    const items = await waitForPlaylistItems();
    return extractVideoIds(items);
  } finally {
    restoreLoadedScroll();
  }
}
```

`finally` に置くことで、抽出処理が例外になっても利用者のスクロール位置は戻せる。

## 確認方法

実装では次を確認した。

- 150 件分の動画リンクを用意したテストで、150 個の一意な ID を抽出できる
- `waitForPlaylistItems()` の完了後に復元関数が呼ばれる
- 最大取得件数は 300 件で停止する
- 途中で例外が起きても `finally` で位置を戻す

この修正は、既存記事の「元の DOM 順を保存して通常順へ戻す処理」とは別の問題である。この記事は、追加行を抽出するまで仮想化 DOM を維持するタイミングだけを扱っている。

## 注意点

- YouTube の DOM セレクタと仮想化方式は変更される可能性がある
- 待機時間を固定しすぎると、低速回線で追加読み込みを取りこぼす
- 件数が増えないことを終了条件にする場合、読み込み中との区別が必要
- 自動スクロール中は画面が一時的に動くため、完了後の復元を必ず行う

## 参考

- [Element.scrollIntoView()](https://developer.mozilla.org/docs/Web/API/Element/scrollIntoView)
- [最初に100件超へ対応したコミット](https://github.com/harness17/youtube-playlist-date-sorter/commit/bfe51f34c7bbcfeabd716a171967a695638d77a4)
- [復元を抽出後へ移したコミット](https://github.com/harness17/youtube-playlist-date-sorter/commit/53aef58f413216f721dd0140f2995e10395f6ff3)
