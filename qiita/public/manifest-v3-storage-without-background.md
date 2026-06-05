---
title: Manifest V3のChrome拡張でService Workerなしにchrome.storage.localを使う
tags:
  - JavaScript
  - Chrome
  - ChromeExtension
  - ManifestV3
  - 個人開発
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

## 何に詰まったか

YouTube プレイリストを投稿日順に並び替える Chrome 拡張を作っていたとき、Manifest V3 のドキュメントや入門記事を読むと「バックグラウンド処理には Service Worker が必要」という説明が多い。しかし、実際に作りたかったのは「content script だけで完結し、設定を保存したい」という単純な拡張だった。

**Service Worker が本当に必要かどうかを調べたら、必要なかった。**

## 結論から

`chrome.storage.local` は content script から直接使える。`"background"` キーが manifest.json にない拡張でも動作する。

```json
{
  "manifest_version": 3,
  "permissions": ["storage"],
  "host_permissions": ["https://www.youtube.com/*"],
  "content_scripts": [
    {
      "matches": ["https://www.youtube.com/*"],
      "js": ["shared/date-sorter.js", "content/content.js"],
      "run_at": "document_idle"
    }
  ]
}
```

`"background"` が存在しない。これで `chrome.storage.local` が使えている。

## なぜ「Service Worker が必要」と思い込みやすいか

Manifest V3 では Manifest V2 の `"background": { "scripts": [...] }` が廃止され、代わりに `"background": { "service_worker": "..." }` になった。この変更が「MV3 はバックグラウンド処理を Service Worker に書く」という印象を与える。

しかし Service Worker が必要なのは：

- **クロスオリジン fetch** をバックグラウンドから行いたい
- **定期処理**（`chrome.alarms` など）を使いたい
- **他のコンポーネント（popup, content script）から呼び出せるメッセージハンドラ**を置きたい

content script の中だけで完結し、storage の読み書きだけが必要な拡張なら Service Worker は不要。

## content script から直接読み書きする

```javascript
const SETTINGS_KEY = 'ytpds:settings';

async function storageGet(key) {
  if (
    !chrome.storage ||
    !chrome.storage.local ||
    !chrome.storage.local.get
  ) return undefined;
  return new Promise((resolve) => {
    chrome.storage.local.get(key, (result) => resolve(result[key]));
  });
}

async function storageSet(key, value) {
  if (!chrome.storage || !chrome.storage.local) return;
  return new Promise((resolve) => {
    chrome.storage.local.set({ [key]: value }, () => resolve());
  });
}

// 設定の読み込み
const saved = await storageGet(SETTINGS_KEY);
if (saved) {
  state.order = saved.order ?? 'asc';
  state.language = saved.language ?? 'ja';
  state.autoAdvance = saved.autoAdvance ?? false;
}

// 設定の保存
await storageSet(SETTINGS_KEY, {
  order: state.order,
  language: state.language,
  autoAdvance: state.autoAdvance,
});
```

`chrome.storage` が存在するかを確認してから使うのは、テスト環境（jsdom など）でも同じコードを動かすため。

## storage の変更を他タブから検知する

`chrome.storage.onChanged` も content script から使える。

```javascript
if (chrome.storage && chrome.storage.onChanged) {
  chrome.storage.onChanged.addListener((changes, areaName) => {
    if (areaName !== 'local') return;
    const changed = changes[SETTINGS_KEY];
    if (!changed) return;
    const newVal = changed.newValue;
    if (newVal) {
      state.order = newVal.order ?? state.order;
      // ...
    }
  });
}
```

同じ設定で開いている複数のタブで設定変更を同期したい場合に使える。

## 制約

- `chrome.storage.local` は 1 拡張あたり 10MB が上限（`QUOTA_BYTES` 定数で確認できる）
- storage の読み書きは非同期（Manifest V2 の `localStorage` のような同期 API はない）
- Service Worker なしでも機能するが、popup → content script へのメッセージパッシングが必要な場合は Service Worker （または `chrome.tabs.sendMessage` 経由）を検討する

## まとめ

Service Worker なしの manifest.json で `chrome.storage.local` は使える。content script だけで完結する拡張なら `"background"` を書く必要はない。

実装は [google-chrome-extensions リポジトリ（youtube-playlist-date-sorter）](https://github.com/harness17/google-chrome-extensions/tree/main/youtube-playlist-date-sorter) で確認できる。

## 参考リンク

- [chrome.storage API リファレンス（公式）](https://developer.chrome.com/docs/extensions/reference/api/storage)
- [Manifest V3 migration guide（公式）](https://developer.chrome.com/docs/extensions/develop/migrate/what-is-mv3)
- [Content scripts の概要（公式）](https://developer.chrome.com/docs/extensions/develop/concepts/content-scripts)
