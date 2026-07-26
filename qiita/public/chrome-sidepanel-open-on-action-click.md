---
title: Chrome拡張のsidePanelを開く2つのAPIからsetPanelBehaviorを選んだ
tags:
  - Chrome拡張
  - JavaScript
  - ManifestV3
  - sidePanel
private: false
updated_at: '2026-07-26T13:16:54+09:00'
id: 6d36324d2f1157584322
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

Manifest V3 で拡張アイコンから sidePanel を開く方法は2つある。全タブで同じパネルを出すだけなら `setPanelBehavior()` の設定1回で済む。タブや条件で出し分けるなら `sidePanel.open()` が必要になるが、ユーザージェスチャー必須・`tabId` か `windowId` の指定必須・Chrome 116 以降という制約が付く。

[Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) では前者を選んだ。この記事はその比較の記録である。

## 前提

`side_panel.default_path` を書いただけではアイコンクリックでパネルは開かない、という詰まり自体と `setPanelBehavior()` の実装手順は、公開済みの記事「[Chrome拡張のpopupがリンクを開くたび閉じるのでsidePanelへ移した](https://qiita.com/harnesswinner/items/9e3eb0c313afb6ba67f0)」で扱った。ここでは重複を避け、**2つのAPIのどちらを採るか**だけを書く。

拡張側の manifest は `default_popup` を持たない `action` と `side_panel` を並べた形になっている。

```json:manifests/chrome.json
  "permissions": ["activeTab", "storage", "sidePanel", "alarms", "offscreen"],
  "action": {
    "default_title": "__MSG_actionTitle__"
  },
  "side_panel": {
    "default_path": "popup/popup.html"
  },
```

この状態から、アイコンクリックでパネルを開く経路を足す。

## 2つのAPIの違い

| | `setPanelBehavior()` | `sidePanel.open()` |
| --- | --- | --- |
| 種類 | 挙動の設定（1回呼ぶ） | 命令的に開く（都度呼ぶ） |
| 導入バージョン | Chrome 114 | Chrome 116 |
| ユーザージェスチャー | 不要（起動時に設定できる） | 必要 |
| 対象の指定 | 不要（アイコンクリック全体に適用） | `tabId` か `windowId` のどちらかが必須 |
| クリックイベントの管理 | ブラウザ側 | `chrome.action.onClicked` などを自前で持つ |

`openPanelOnActionClick` の既定値は `false` である。つまり `side_panel.default_path` を書いてもアイコンクリックには何も紐づかない。

## 採用しなかった案

`sidePanel.open()` を使うなら、クリックイベントを受けて対象タブを渡す形になる。

```js
chrome.action.onClicked.addListener(async (tab) => {
  if (!tab.id) {
    return
  }
  await chrome.sidePanel.setOptions({
    tabId: tab.id,
    path: 'popup/popup.html',
    enabled: true
  })
  await chrome.sidePanel.open({ tabId: tab.id })
})
```

この書き方だと、タブごとに別のパネルを出したり、特定ドメインでだけ開いたりできる。Amazon の商品ページでだけパネルを出す、といった制御も可能になる。

しかし今回の拡張では、蔵書一覧とセール状態をどのタブからでも同じように見たい。タブ単位の出し分けは要件になかった。それなら `open()` を選ぶ理由は、次の3つのコストに見合わない。

- クリックイベントのハンドラを自前で保守する
- `tabId` の取得失敗（`tab.id` が `undefined` になるケース）を自分で扱う
- 対応下限が Chrome 116 に上がる

## 採用した案

起動時に `setPanelBehavior({ openPanelOnActionClick: true })` を1回呼ぶだけにした。クリックの受け取りと開閉はブラウザに任せ、background 側にはイベントハンドラを持たない。

Firefox 版は `sidebar_action.default_panel` を使うため、この設定自体が不要になる。同じ background を両ブラウザで読み込む都合上、API とメソッドの存在確認を挟んでから呼んでいる（実装は前掲の公開済み記事にある）。

## 確認ポイント

- Chrome でアイコンを押すとパネルが開閉する
- `chrome.action.onClicked` を登録していない（登録するなら `setPanelBehavior` と役割が重複しないか確認する）
- Firefox で background を読み込んでも未定義 API の例外が出ない
- タブ単位の出し分けが要件に入った時点で `open()` へ移す判断をやり直す

要件が「全タブで同じパネルを開く」に収まるうちは、設定1回で済む方を選んだ。出し分けが必要になったら `open()` へ移るが、そのときはクリックイベントの管理を引き受けることになる。

### 参考

- [kindle-series-sale-tracker](https://github.com/harness17/kindle-series-sale-tracker) — 記事で扱った manifest と background の実装
- [chrome.sidePanel API](https://developer.chrome.com/docs/extensions/reference/api/sidePanel) — `setPanelBehavior` / `open` / `setOptions` の公式仕様
- [公開済みQiita記事](https://qiita.com/harnesswinner/items/9e3eb0c313afb6ba67f0) — popup から sidePanel へ移した経緯と `setPanelBehavior` の実装手順
