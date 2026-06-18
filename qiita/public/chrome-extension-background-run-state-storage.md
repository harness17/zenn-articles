---
title: Chrome拡張のバックグラウンド処理が動いたか分からないのでstorageに状態を保存してバッジで見せた
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

## 何が起きたか

[Kindle Series Sale Tracker](https://github.com/harness17/google-chrome-extensions) という Chrome 拡張を作っている。Kindle の蔵書一覧ページを開いたときに、バックグラウンドで続刊・セール情報を自動取得する機能がある。

問題は、この自動スキャンが **ページ訪問のタイミングでしか発火しない** こと。alarm のように定期実行されるわけではないので、利用者から見ると「動いたのか」「動かなかったのか」「なぜ動かなかったのか」が分からない。

開発中はコンソールログで確認していたが、通常利用で DevTools を開く人はいない。

## 解決: 状態を storage に保存して UI に反映する

発火判定・実行・完了・失敗の各段階を `chrome.storage.local` に保存し、options ページとサイドパネルに表示する設計にした。

### 状態の定義

```javascript
// 自動スキャンの実行状態
const RUN_STATES = {
  CHECKING: 'checking',           // 発火判定中
  SKIPPED_NOT_DUE: 'skipped-not-due',     // 間隔未到来でスキップ
  SKIPPED_NO_BASELINE: 'skipped-no-baseline', // 基準データなしでスキップ
  RUNNING: 'running',             // 実行中
  COMPLETED: 'completed',         // 完了
  FAILED: 'failed'                // 失敗
};
```

スキップにも理由が2種類ある。「まだ時間じゃない」と「そもそも基準データがない」は利用者にとって意味が違うので分けた。

### 保存する情報

```javascript
// storage に保存する実行状態の例
const runState = {
  state: 'completed',
  firedAt: '2026-06-15T10:30:00Z',   // 発火時刻
  nextDueAt: '2026-06-16T10:30:00Z', // 次回期限
  totalItems: 42,                     // 総冊数
  addedItems: 3,                      // 追加冊数
  completedAt: '2026-06-15T10:31:15Z' // 完了時刻
};

await chrome.storage.local.set({ kstAutoScanRunState: runState });
```

失敗時は失敗時刻だけを保存し、エラー詳細は保存しない。利用者に内部エラーを見せてもアクション不能なため。

### UI 側の購読

options ページやサイドパネルは `storage.onChanged` を購読して、開いたまま状態遷移を反映する。

```javascript
chrome.storage.onChanged.addListener((changes, area) => {
  if (area === 'local' && changes.kstAutoScanRunState) {
    const newState = changes.kstAutoScanRunState.newValue;
    updateAutoScanDisplay(newState);
  }
});
```

`running` → `completed` や `running` → `failed` への遷移が、ページをリロードせずにリアルタイムで反映される。

## なぜ alarm の前回実行時刻だけでは足りないか

alarm 駆動のバックグラウンド処理なら、「前回: 12:00 / 次回: 翌12:00」で十分かもしれない。

しかしページ訪問依存の処理には以下の問題がある。

| 状況 | 前回時刻だけで分かるか |
|------|---------------------|
| ページを開いたが間隔未到来でスキップした | 分からない（発火自体を記録していない） |
| 基準データがなくてスキップした | 分からない（スキップ理由が不明） |
| 実行中にタブを閉じた | 分からない（`running` のまま残る） |
| 実行して0件追加で完了した | 分からない（前回時刻は更新されるが結果が不明） |

状態を保存することで「ページを開いたが動かなかった理由」まで表示できるようになった。

## 注意点

- 次回期限は「ページを開いた際に期限判定が通る時刻」であり、実行保証時刻ではない。ページを開かなければ発火しない
- タブ終了や拡張更新で `running` が残ることがある。次回ページ訪問時の `checking` で上書きされるため、手動リカバリは不要
- 自動スキャンがOFFの場合は状態保存自体を行わない

## 参考

- [chrome.storage API（公式）](https://developer.chrome.com/docs/extensions/reference/api/storage)
- [Kindle Series Sale Tracker](https://github.com/harness17/google-chrome-extensions)
