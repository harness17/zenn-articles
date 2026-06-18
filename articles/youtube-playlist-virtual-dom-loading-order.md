---
title: "YouTubeプレイリスト101件以降を取るためDOM抽出順序を見直した"
emoji: "📜"
type: "tech"
topics: ["chrome拡張", "javascript", "youtube", "dom", "個人開発"]
published: true
---

## はじめに

[YouTube Playlist Date Sorter](https://github.com/harness17/youtube-playlist-date-sorter) では、表示中のプレイリストを投稿日順や再生時間順に並べ替えている。長いプレイリストへ対応するため処理上限を増やしたところ、101件目以降を安定して抽出できなかった。

末尾まで自動スクロールすると行は追加される。それでも元のスクロール位置へ戻した後に DOM を読むと、追加された後半行が外れ、再び約100件へ戻ることがあった。

この記事では、上限値を増やすだけでは直らなかった理由と、「読み込み、抽出、スクロール復元」の順序を変えた判断を書く。YouTube の内部 DOM は公開 API ではないため、約100件という値は実装時の観測であり、固定仕様としては扱わない。

## 上限を増やしても取得件数が増えなかった

最初の処理は、行を読み込む関数の中でスクロール位置まで戻していた。

```js
async function refreshItems() {
  await loadPlaylistRows(300); // 読み込み後に元位置へ戻す
  const items = await waitForPlaylistItems();
  return extractVideoIds(items);
}
```

画面はすぐ元の位置へ戻るため、利用者の操作感はよかった。しかし、YouTube 側の一覧は表示範囲に応じて DOM を入れ替える。追加行を読み込んでも、抽出前に上へ戻ると後半行が DOM から外れる。

ここで問題だったのは `300` という上限値ではなく、DOM が存在している時間帯だった。

採用しなかった案は2つある。

| 選択肢 | 採用しなかった理由 |
| --- | --- |
| 待機時間だけ延ばす | 上へ戻した後に待っても、外れた行は抽出できない |
| スクロール位置を戻さない | 取得はできるが、利用者の閲覧位置を壊す |

必要なのは、追加行が DOM にある間に識別子だけ先に確保し、その後で画面を戻すことだった。

## 読み込み関数は復元処理を返す

`loadPlaylistRows()` はスクロール位置を記録し、末尾方向へ読み込んだ後、すぐには元へ戻さない。代わりに復元用の関数を返す。

```js:load-playlist-rows.js
async function loadPlaylistRows(maxItems) {
  const positions = findScrollableTargets().map((target) => ({
    target,
    top: target === window ? window.scrollY : target.scrollTop,
  }));

  let previousCount = 0;
  while (true) {
    const rows = document.querySelectorAll("ytd-playlist-video-renderer");
    if (rows.length >= maxItems || rows.length === previousCount) break;
    previousCount = rows.length;

    rows.at(-1)?.scrollIntoView({ block: "end" });
    await waitForMoreRows(rows.length);
  }

  return () => restoreScrollPositions(positions);
}
```

`window` だけでなく、ページ内要素がスクロール領域になる場合もあるため、候補を複数保持する。終了条件は「最大件数へ達した」または「追加読み込みを待っても件数が増えなかった」とした。

固定の `sleep(500)` だけに頼ると、回線や描画負荷によって取りこぼす。実装では、件数が増えたかを確認しながら次へ進む。

## DOM抽出後にfinallyで位置を戻す

呼び出し側では、動画 ID の抽出が終わるまで復元関数を呼ばない。

```js:refresh-items.js
async function refreshItems() {
  const restoreScroll = await loadPlaylistRows(300);

  try {
    const items = await waitForPlaylistItems();
    return extractVideoIds(items);
  } finally {
    restoreScroll();
  }
}
```

`finally` に置く理由は、抽出処理が例外になったときも利用者の位置を戻すためである。処理成功時だけ復元すると、DOM 変更や一時的な取得失敗が起きたときに画面が末尾へ残る。

この変更で処理順序は次になった。

1. スクロール候補と現在位置を保存する
2. 末尾方向へ進み、追加行を読み込む
3. 追加行が DOM にある状態で動画 ID を抽出する
4. 抽出結果をメモリへ保持する
5. `finally` で元の位置へ戻す

抽出後のソートや投稿日取得は DOM から切り離せる。仮想化 DOM に依存する時間を短くすることも、この順序の利点だった。

## 既存の通常順復元とは別の問題だった

この拡張には、並べ替え前の `originalIndex` を保存し、通常順へ戻す処理もある。しかし、今回の「スクロール位置の復元」と「動画行の通常順復元」は別の責務である。

- スクロール位置の復元: 利用者が見ていた場所へ戻す
- 通常順の復元: 拡張が並べ替えた動画行を元の順番へ戻す

名前が似ているため、同じ復元処理へまとめるとタイミングを誤りやすい。前者は抽出直後、後者は利用者が通常順を選んだときに実行する。

以前の記事「YouTubeプレイリストを投稿日順に並び替えるChrome拡張を作った話」は拡張全体と API キー不要の設計を扱った。今回は、100件を超える一覧でだけ表面化した仮想化 DOM のタイミングに絞っている。

## 確認したこと

修正後は次を確認した。

- 100件を超える一覧で、読み込んだ行から一意な動画 ID を抽出できる
- 現行の公開実装にある最大取得件数 `300` で停止する
- DOM 抽出が終わった後に復元関数が呼ばれる
- 途中で例外が起きても `finally` で位置を戻す
- 通常順の復元処理とは独立して動く

:::message
YouTubeのDOMセレクタや仮想化方式は変更される可能性がある。件数や要素名を公開仕様として断定せず、回帰テストと実機確認を併用する。
:::

## まとめ

- 長いプレイリストでは、上限値を増やすだけでは仮想化 DOM から後半行を取れなかった
- 追加行が DOM にある間に動画 ID を抽出し、その後でスクロール位置を戻した
- 復元関数を返して `finally` で呼ぶと、成功・失敗にかかわらず利用者の位置を戻せる

対応の経緯は [100件超へ対応したコミット](https://github.com/harness17/youtube-playlist-date-sorter/commit/bfe51f34c7bbcfeabd716a171967a695638d77a4) と [スクロール復元を抽出後へ移したコミット](https://github.com/harness17/youtube-playlist-date-sorter/commit/53aef58f413216f721dd0140f2995e10395f6ff3) に残している。

## 参考リンク

- [Element.scrollIntoView()](https://developer.mozilla.org/docs/Web/API/Element/scrollIntoView) - 要素をスクロール領域へ表示するAPI
- [YouTube Playlist Date Sorter](https://github.com/harness17/youtube-playlist-date-sorter) - 記事で扱った拡張
