---
title: "YouTubeプレイリストを投稿日順に並び替えるChrome拡張を作った話"
emoji: "📅"
type: "tech"
topics: ["chrome拡張", "manifestv3", "javascript", "youtube", "個人開発"]
published: true
---

## はじめに

YouTube で「このプレイリストを古い順に見ていきたい」と思ったことはないだろうか。YouTube の公式 UI にも並び順の設定はあるが、それは自分が作ったプレイリストを保存順で変えるもので、「見るときだけ投稿日順にしたい」という用途とは少し違う。

そこで、表示中のプレイリストを投稿日順に並び替えて次の動画に移動できる Chrome 拡張 [YouTube Playlist Date Sorter](https://github.com/harness17/google-chrome-extensions/tree/main/youtube-playlist-date-sorter) を作った。この記事では、**API キーなしで投稿日を取る設計判断**と、**YouTube の SPA 遷移で詰まった問題**を中心に書く。

対象読者：YouTube の UI を自分の用途に合わせたい人、API キーを使わず content script 中心で小さな拡張を作りたい人。

## 何を作ったか

`/playlist` ページと `/watch?v=...&list=...` ページで動作する拡張で、右下に操作パネルが現れる。できること：

- 表示中のプレイリストを投稿日の昇順 / 降順 / 通常順に並び替え
- 「次へ」ボタンで並び替え後の順序に従って次の動画を開く
- 自動送り（1 動画が終わると次を自動で開く）
- 表示言語の切替（日本語 / 英語）
- パネルの最小化

プレイリスト本体のデータは変更しない。あくまで「見るときの表示順と次に開く URL」だけを拡張側で制御している。

## YouTube Data API ではなく DOM と動画 HTML を使った

投稿日を取る方法は 2 種類考えた。

| 方法 | API キー | クォータ消費 | 対応範囲 |
|------|----------|------------|---------|
| YouTube Data API v3 | 必要 | あり（playlistItems.list = 1ユニット/回） | 公式データ |
| DOM + 動画ページ HTML | 不要 | なし | 表示中の最大 120 件 |

今回は「インストールして API キー設定なしで使える」ことを優先したため、DOM + HTML の方法を選んだ。代わりに受け入れたデメリットは「YouTube の DOM 構造変更に弱い」「表示中の件数しか見られない」の 2 点。

### manifest.json の権限設計

```json
{
  "manifest_version": 3,
  "permissions": ["storage"],
  "host_permissions": ["https://www.youtube.com/*"],
  "content_scripts": [
    {
      "matches": ["https://www.youtube.com/*"],
      "js": ["shared/date-sorter.js", "shared/i18n.js", "content/content.js"],
      "run_at": "document_idle"
    }
  ]
}
```

`"background"` キーがない。Service Worker は使っていない。`"storage"` は `chrome.storage.local` でソート設定を保存するためだけに使う。

### 投稿日の抽出

各動画の投稿日は、動画ページ（`https://www.youtube.com/watch?v=...`）の HTML を fetch して JSON-LD や `<meta>` タグから取る。

```javascript
function extractPublishDateFromHtml(html) {
  const normalized = normalizeHtmlForDateSearch(html);

  // JSON-LD の publishDate / uploadDate / datePublished を優先
  const exactDateCandidates = [
    /"publishDate"\s*:\s*"([^"]+)"/,
    /"uploadDate"\s*:\s*"([^"]+)"/,
    /"datePublished"\s*:\s*"([^"]+)"/,
    /<meta[^>]+itemprop=["']datePublished["'][^>]+content=["']([^"']+)["']/i,
    // ...
  ];
  for (const pattern of exactDateCandidates) {
    const match = normalized.match(pattern);
    const date = normalizeDateText(match && match[1]);
    if (date) return date;
  }

  // YouTube の dateText / publishDateText にフォールバック
  const textDateCandidates = [
    /"dateText"\s*:\s*\{\s*"simpleText"\s*:\s*"([^"]+)"/,
    /"publishDateText"\s*:\s*\{\s*"simpleText"\s*:\s*"([^"]+)"/,
  ];
  // ...
}
```

日付テキストは ISO 8601 / スラッシュ区切り / 日本語表記（「2024年3月1日」など）の 3 形式に対応している。また、HTML 中のエスケープシーケンス（`"` 等）を正規化してからマッチしている。

## 並び替えは DOM 操作と次動画 URL 制御で実現した

### プレイリスト行の取得

```javascript
function extractPlaylistItemsFromDocument(documentRef) {
  const isPlaylistPage = documentRef.location.pathname === '/playlist';
  const selector = isPlaylistPage
    ? 'ytd-playlist-video-renderer a[href*="/watch"][href*="v="]'
    : 'ytd-playlist-panel-video-renderer a[href*="/watch"][href*="v="]';
  const anchors = Array.from(documentRef.querySelectorAll(selector));

  const items = [];
  for (const anchor of anchors) {
    const videoId = getVideoIdFromUrl(anchor.href);
    if (!videoId || seen.has(videoId)) continue;
    items.push({ videoId, title, originalIndex: items.length });
  }
  return items;
}
```

`/playlist` ページと `/watch` ページでは表示されるコンポーネントが異なるため、セレクタを切り替えている。

### ソートと次動画の決定

```javascript
function sortItemsByPublishDate(items, dateByVideoId, order) {
  const multiplier = order === 'desc' ? -1 : 1;
  return [...items].sort((a, b) => {
    const aDate = toDateMs(dateByVideoId[a.videoId]);
    const bDate = toDateMs(dateByVideoId[b.videoId]);
    const aUnknown = !Number.isFinite(aDate);
    const bUnknown = !Number.isFinite(bDate);
    if (aUnknown !== bUnknown) return aUnknown ? 1 : -1; // 日付不明は末尾
    if (aDate !== bDate) return (aDate - bDate) * multiplier;
    return a.originalIndex - b.originalIndex; // 同日は元の順序を維持
  });
}

function findNextVideoId(sortedItems, currentVideoId) {
  const index = sortedItems.findIndex((item) => item.videoId === currentVideoId);
  if (index < 0 || index >= sortedItems.length - 1) return '';
  return sortedItems[index + 1].videoId;
}
```

日付が取れなかった動画は末尾に回し、同日・不明の場合は元の表示順（`originalIndex`）で安定ソートしている。

次の動画を開くときは `findNextVideoId` で videoId を決めてから `buildWatchUrl(videoId, playlistId)` で URL を組み立てる。YouTube 本体のキューは書き換えない。

## YouTube の SPA 遷移と再描画で詰まった

ここが一番悩んだところ。

### 問題: ページ遷移でパネルが消える

`/playlist` から動画リンクをクリックして `/watch?v=...&list=...` に遷移すると、YouTube は SPA として動作するためページ全体の再読み込みが起きない。つまり content script は再実行されない。初期化処理だけに頼っていたパネルは、遷移後に DOM から消えたまま戻ってこなかった。

### 対処: ナビゲーション検知を 3 層で組み合わせた

```javascript
document.addEventListener('yt-navigate-finish', onNavigationMaybeChanged);
window.addEventListener('popstate', onNavigationMaybeChanged);
setInterval(onNavigationMaybeChanged, 500);
```

`yt-navigate-finish` は YouTube が発火するカスタムイベントで、SPA 遷移完了後に呼ばれる。ただし発火しないケースや、発火したときにまだ DOM が整っていないケースがある。`popstate` はブラウザ標準の URL 変化検知。500ms の `setInterval` はフォールバックで、3 層重ねることで取りこぼしを減らした。

`onNavigationMaybeChanged` の中では、URL やパスが変化したかどうかを前回と比較して、変化があった場合だけ再初期化する。

```javascript
function onNavigationMaybeChanged() {
  const urlChanged = state.lastUrl !== location.href;
  const pathChanged = state.lastPathname !== location.pathname;
  // URL が変わった場合はパネルを再生成し、ソート済みアイテムがあれば表示に再適用
  if (pathChanged && state.sortedItems.length > 0) {
    applySavedOrderWithoutBadges();
    scheduleSavedOrderApply(250);
    scheduleSavedOrderApply(1000);
    scheduleSavedOrderApply(2500);
  }
}
```

遷移後は YouTube の描画タイミングにばらつきがあるため、250ms / 1000ms / 2500ms の 3 回に分けて「ソート済み表示の再適用」を試みている。

### 問題: MutationObserver が自分の DOM 変更で再発火する

バッジ（動画行に投稿日を表示する小さなラベル）を DOM に追加すると、その変更を MutationObserver が検知して「何か変化した → ソート処理を走らせる」というループに入り、バッジが点滅した。

対処として `isOwnVisualMutation` 関数を作り、「自分の変更だけで構成された mutation は無視する」という判定を入れた。

```javascript
function isOwnVisualMutation(mutation) {
  if (mutation.type === 'attributes') {
    if (mutation.target.closest('.ytpds-date-badge')) return true;
    if (
      mutation.attributeName === 'data-ytpds-sorted' ||
      mutation.attributeName === 'data-ytpds-sort-index'
    ) return true;
  }
  // ...
}

// Observer コールバック内
if (mutations.length > 0 && mutations.every(isOwnVisualMutation)) return;
```

`data-ytpds-*` という独自属性を使って「拡張が書いた変更」を識別し、その変更だけで構成されている場合はスキップする。

## まとめ

3 点を整理する。

- **API キーなしで使える設計のために DOM と動画ページ HTML を選んだ**。API を使えばより安定するが、ユーザーに設定作業を求めない方を優先した。DOM 依存のもろさは受け入れたトレードオフ。
- **プレイリスト本体は変更せず、表示順と次動画 URL だけを拡張側で制御した**。元の順序に戻すためのアンドゥも、保存した `originalIndex` を使えば実現できた。
- **YouTube の SPA 遷移には `yt-navigate-finish` + `popstate` + interval の 3 層が必要だった**。content script を書くときに「ページ遷移後の再初期化」は必ず考慮が必要だと体感した。

拡張は [google-chrome-extensions リポジトリ](https://github.com/harness17/google-chrome-extensions/tree/main/youtube-playlist-date-sorter) に置いてある。Chrome Web Store と Firefox Add-ons でも公開している。

## 参考リンク

- [google-chrome-extensions リポジトリ](https://github.com/harness17/google-chrome-extensions)
- [YouTube Playlist Date Sorter — Chrome Web Store](https://chromewebstore.google.com/detail/youtube-playlist-date-sor/hobigboofokgcnjfobilijbknbmemlbd)
- [YouTube Playlist Date Sorter — Firefox Add-ons](https://addons.mozilla.org/ja/firefox/addon/youtube-playlist-date-sorter/)
- [Chrome Extensions Manifest V3（公式）](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3)
- [MutationObserver — MDN](https://developer.mozilla.org/docs/Web/API/MutationObserver)
