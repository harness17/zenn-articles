---
title: Chrome拡張でDOMを並び替えた後にMutationObserverが再発火する問題への対処
tags:
  - JavaScript
  - Chrome
  - dom
  - ChromeExtension
  - MutationObserver
private: false
updated_at: '2026-05-24T10:22:45+09:00'
id: 5429f56b3a8e23675703
organization_url_name: null
slide: false
ignorePublish: false
---

## 何に詰まったか

YouTube プレイリストを投稿日順に並び替える Chrome 拡張を作っていたとき、並び替えた直後にバッジが点滅し、CPU 使用率が跳ね上がる現象に遭遇しました。

構成はこうです。

1. プレイリストの DOM 行を取得する
2. 各動画の投稿日を取って sort する
3. sort 結果に従って DOM 行を `parent.insertBefore()` で並び替える
4. 各行に投稿日バッジを `appendChild` で付ける
5. YouTube 側が DOM を差し戻すことがあるため、`MutationObserver` で監視しておき、差し戻されたら再度並び替える

3 と 4 は自分の DOM 操作です。これを 5 の `MutationObserver` が拾い、「変更があった」と判定して再度並び替えを走らせる、という無限ループになっていました。

## 単純な解決とその限界

最初に試したのは「自分が DOM 操作している間はフラグを立てて、observer の callback を無視する」です。

```js
state.applyingVisualOrder = true;
try {
  // parent.insertBefore(...) でまとめて並び替え
  for (let i = desiredOrder.length - 1; i >= 0; i -= 1) {
    const row = rowByVideoId.get(desiredOrder[i]);
    if (row && row.parentElement === parent) {
      parent.insertBefore(row, marker.nextSibling);
    }
  }
} finally {
  setTimeout(() => {
    state.applyingVisualOrder = false;
  }, 300);
}
```

callback 側：

```js
const observer = new MutationObserver((mutations) => {
  if (state.applyingVisualOrder) return;
  if (state.sortedItems.length === 0) return;
  scheduleApply();
});
```

これで「ループ内の即時再発火」は止まりました。ところがフラグ解除後にもう一度再発火する現象が残りました。

原因は、自分が追加したバッジ要素が、その後に YouTube 側のサムネイル差し替えや属性変更を受けて、`MutationObserver` 経由で「変更検知」されることでした。

## 自分の変更を判定するヘルパで対処

`MutationObserver` の callback には変更内容（`MutationRecord`）が渡ってきます。これを使って「全部自分の変更だったらスキップ」する判定関数を作りました。

```js
function isOwnVisualMutation(mutation) {
  if (mutation.type === 'attributes') {
    // 自分が付けたバッジ要素の中の変更は自分由来
    if (mutation.target.closest && mutation.target.closest('.ytpds-date-badge')) return true;
    // 自分が制御する data 属性の変更は自分由来
    if (
      mutation.attributeName === 'data-ytpds-sorted' ||
      mutation.attributeName === 'data-ytpds-sort-index'
    ) {
      return true;
    }
    // 自分が制御するクラスだけが入れ替わったケースは自分由来
    if (mutation.attributeName === 'class') {
      return onlyClassTokenChanged(
        mutation.oldValue || '',
        mutation.target.getAttribute('class') || '',
        ['ytpds-current-video']
      );
    }
  }
  if (mutation.type === 'childList') {
    const nodes = Array.from(mutation.addedNodes).concat(Array.from(mutation.removedNodes));
    return nodes.length > 0 && nodes.every(isYtpdsArtifactNode);
  }
  return false;
}
```

callback 側はこうなります。

```js
const observer = new MutationObserver((mutations) => {
  if (state.applyingVisualOrder || state.sortedItems.length === 0) return;
  if (mutations.length > 0 && mutations.every(isOwnVisualMutation)) return;
  clearTimeout(state.visualApplyTimer);
  state.visualApplyTimer = setTimeout(() => applyVisualOrder(), 120);
});
```

ポイントは 3 つです。

- 自分由来の属性変更は、属性名（`data-ytpds-sorted` 等）と要素種別（`.ytpds-date-badge`）で判定できる
- `class` 属性は YouTube 側も触るので、入れ替わったトークンが「自分が管理するクラスだけか」で判定する
- `addedNodes` / `removedNodes` は、自分が付けたバッジ要素かどうかで判定する

## observer の対象を絞る

もう 1 つ効いたのが、`observer.observe()` の対象を必要なだけに絞ったことです。

```js
observer.observe(root, {
  attributes: true,
  attributeOldValue: true,
  attributeFilter: ['class', 'data-ytpds-sorted', 'data-ytpds-sort-index'],
  childList: true,
  subtree: true,
});
```

`attributeFilter` を指定すると、関心のある属性以外の変更で callback が呼ばれなくなります。`attributeOldValue: true` は、上の `onlyClassTokenChanged` で `oldValue` と `newValue` を比較するために必要でした。

これだけで callback の発火回数は体感で 1/10 以下になりました。

## まとめ

- 自分が DOM を変更しながら同じ DOM を `MutationObserver` で監視する場合、フラグだけでは再発火を止められない
- `MutationRecord` の内容を見て「全部自分由来か」を判定するヘルパで callback 側を絞ると、ループも点滅も止まる
- `attributeFilter` と `attributeOldValue` を使って observer の対象を最初から絞ると、callback 自体の回数が減って判定コストも下がる
- 「再描画ループに巻き込まれない」ためには、自分の変更に印（独自 data 属性、独自クラス名）を付けておくと、後から判定が楽になる

## 参考リンク

- [MutationObserver - MDN](https://developer.mozilla.org/docs/Web/API/MutationObserver)
- [MutationObserverInit.attributeFilter - MDN](https://developer.mozilla.org/docs/Web/API/MutationObserver/observe#attributefilter)
- [MutationRecord - MDN](https://developer.mozilla.org/docs/Web/API/MutationRecord)
