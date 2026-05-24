---
title: Chrome拡張でYouTubeのSPA遷移後にcontent scriptが効かない問題を直した
tags:
  - JavaScript
  - Chrome
  - YouTube
  - ChromeExtension
  - ManifestV3
private: false
updated_at: '2026-05-24T10:22:35+09:00'
id: 3bac40961a0b5ff20dee
organization_url_name: null
slide: false
ignorePublish: false
---

## 何に詰まったか

個人開発で「YouTube プレイリストを動画の投稿日順に並び替える」Chrome 拡張を作っていたとき、`/playlist` ページでは正しく動くのに、そこから動画リンクをクリックして `/watch?...&list=...` に移った瞬間に拡張の UI が消える、という現象に詰まりました。

最初は content script が動いていないと思い、`console.log` を仕込んでみたところ、`/watch` ページでも content script はロードされていました。しかし、`document` を読み込んで UI を差し込む初期化処理は最初の 1 回しか走らず、SPA 遷移後の DOM には反映されていませんでした。

原因は次の 2 点でした。

1. `manifest.json` の `matches` が `/playlist` だけを対象にしていて、`/watch` 側で content script が再注入されていないケースがあった
2. YouTube は SPA なので、URL が変わってもページ全体のロードは発生しない。content script は最初に注入された 1 回だけ実行され、その後の URL 変化を自分で検知しない限り、初期化処理は呼ばれない

## 解決の方針

content script を「特定パスにだけ注入する」のをやめ、`https://www.youtube.com/*` 全体に広く注入したうえで、処理側で URL が対象ページかを判定する構成にしました。

`manifest.json` はこうなりました。

```json
{
  "manifest_version": 3,
  "permissions": ["storage"],
  "host_permissions": ["https://www.youtube.com/*"],
  "content_scripts": [
    {
      "matches": ["https://www.youtube.com/*"],
      "js": ["shared/date-sorter.js", "shared/i18n.js", "content/content.js"],
      "css": ["content/content.css"],
      "run_at": "document_idle"
    }
  ]
}
```

content script 側では、現在の URL が対象ページかを判定する関数を分けます。

```js
function isSupportedPlaylistPage() {
  const playlistId = sorter.getPlaylistIdFromUrl(location.href);
  return Boolean(
    playlistId && (location.pathname === '/watch' || location.pathname === '/playlist')
  );
}
```

`matches` で広く受けて、処理側で `isSupportedPlaylistPage()` を見るようにすると、SPA 遷移で `/playlist` → `/watch` に移ったケースも、`/watch` → 別の動画へ移ったケースも、同じ初期化関数で扱えます。

## SPA 遷移をどう検知するか

content script が再注入されない以上、URL 変化を自分で拾う必要があります。試した中で安定したのは、次の 3 つを併用する構成でした。

```js
document.addEventListener('yt-navigate-finish', onNavigationMaybeChanged);
window.addEventListener('popstate', onNavigationMaybeChanged);
setInterval(onNavigationMaybeChanged, 500);
```

- `yt-navigate-finish` は YouTube が SPA 遷移完了時に発火するカスタムイベント。普段はこれだけで足りる
- `popstate` はブラウザの戻る / 進むに対応する保険
- `setInterval` は上記 2 つが取れなかったケース（広告挿入後の差し込み、長時間滞在後の DOM 入れ替え）を拾うためのフェイルセーフ

`onNavigationMaybeChanged` の中では、前回保存した URL / pathname と比較して変化があれば初期化を走らせます。`setInterval` で 500ms ごとに呼ばれても、差分が無ければ何もしない作りにしておけば負荷は気になりませんでした。

```js
function onNavigationMaybeChanged() {
  const urlChanged = state.lastUrl !== location.href;
  const pathChanged = state.lastPathname !== location.pathname;
  if (urlChanged) state.lastUrl = location.href;
  if (pathChanged) state.lastPathname = location.pathname;

  ensurePanel();
  if (urlChanged) restoreSortState();
}
```

## 詰まった点と注意点

- 最初は `webNavigation` の `onHistoryStateUpdated` を使おうとしましたが、これは background 側の権限で、content script からは扱えません。content script 側で SPA 遷移を取りたい場合は、上記のように DOM イベントと URL 比較を組み合わせるのが手早いです
- `matches` を `https://www.youtube.com/*` に広げると、関係ないページでも content script がロードされます。`isSupportedPlaylistPage()` で早期 return しないと、無関係なページで余計な処理が走り、コンソールに warning が出ることがあります
- `yt-navigate-finish` は YouTube 側の実装に依存するイベントなので、いつ仕様変更されてもおかしくありません。`popstate` と `setInterval` を保険として残しておくと、片方が取れなくなっても拡張が完全に死ぬのは避けられます

## まとめ

- content script を特定パスに限定するより、`https://www.youtube.com/*` に広く注入して処理側で URL 判定するほうが、SPA 遷移に強くなる
- SPA 遷移の検知は `yt-navigate-finish` + `popstate` + `setInterval` の 3 段構えにすると、片方が取れなくなっても拡張が止まらない
- 「content script が動いているか」と「初期化処理が呼ばれているか」は別問題。SPA では初期化を URL 変化に紐づけて再実行する設計が必要

## 参考リンク

- [Chrome Extensions Manifest V3](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3)
- [Content scripts - chrome.scripting](https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts)
- [popstate event - MDN](https://developer.mozilla.org/docs/Web/API/Window/popstate_event)
