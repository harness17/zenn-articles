---
title: Chrome拡張を__MSG_key__で多言語化したら英語環境で日本語が出た
tags:
  - Firefox
  - I18n
  - Chrome拡張
  - WebExtension
  - ManifestV3
private: false
updated_at: '2026-06-07T00:11:18+09:00'
id: d02fa6e00ed86a9f243c
organization_url_name: null
slide: false
ignorePublish: false
---

## 何が起きたか

Chrome 拡張の manifest.json を多言語対応するため、`name` と `description` を `__MSG_key__` 形式の i18n キーに書き換えた。`_locales/ja/messages.json` にはキーを追加したが、`_locales/en/messages.json` への追加を忘れていた。

結果、英語環境の Chrome で拡張を読み込むと、**拡張の説明文が日本語のまま表示された**。`chrome://extensions/` の拡張管理画面で description 欄に日本語が出ていた。英語ユーザーにとっては読めない説明文になるし、Chrome Web Store の審査でも印象が悪い。

## 原因：default_locale へのフォールバック

Chrome / Firefox の i18n 仕様では、`__MSG_key__` の解決順序はこうなっている。

```
1. 現在のブラウザ言語の messages.json にキーがあるか
   → あれば、その値を使う
2. なければ、default_locale の messages.json にキーがあるか
   → あれば、その値を使う（フォールバック）
3. どちらにもなければ、空文字になる
```

自分のケースでは `default_locale: "ja"` で、`ja/messages.json` にはキーがあった。英語環境で `en/messages.json` に `extDescription` キーがないため、**ステップ2で日本語テキストにフォールバック**した。

```
default_locale: "ja" の場合
├── _locales/ja/messages.json  → extDescription あり ✅（日本語テキスト）
└── _locales/en/messages.json  → extDescription なし ❌
                                 → ja にフォールバック → 日本語の説明文が出る
```

`extName`（拡張名）は日英とも同じ英語テキストだったので気づかなかった。`extDescription`（説明文）は日本語と英語で別テキストにしていたため、フォールバックで目に見えるズレが起きた。エラーにならないのがやっかいで、開発中は日本語環境で確認していたため見逃していた。

## 再現条件

1. `manifest.json` で `"default_locale": "ja"` を設定
2. `"description": "__MSG_extDescription__"` に書き換え
3. `_locales/ja/messages.json` にのみキーを追加し、`en` への追加を忘れる

```json
// _locales/ja/messages.json ✅
{
  "extName": {
    "message": "YouTube Playlist Date Sorter",
    "description": "拡張管理画面に表示する拡張名"
  },
  "extDescription": {
    "message": "YouTube のプレイリスト再生を投稿日順・タイトル順・再生時間順に並び替えて、次の動画へ移動します。",
    "description": "ストアに表示する短い説明"
  }
}
```

```json
// _locales/en/messages.json ❌ extDescription キーなし
{
  "extName": {
    "message": "YouTube Playlist Date Sorter",
    "description": "Extension name"
  }
}
```

4. Chrome の言語を英語に切り替えるか、`--lang=en` フラグで起動
5. `chrome://extensions/` で拡張の説明文が **日本語** で表示される（空ではなく、ja のメッセージがフォールバックで出る）

DevTools のコンソールでも確認できる。

```javascript
// background / popup のコンソールで実行
chrome.i18n.getMessage("extDescription")
// → "YouTube のプレイリスト再生を投稿日順・..." （ja のメッセージが返る）
```

英語環境なのに日本語テキストが返っている。`extName` は ja/en とも同じ英語テキストなのでフォールバックしても見た目が変わらず、`extDescription` で初めて問題に気づいた。

なお、`default_locale` の `messages.json` にもキーがない場合は**空文字**になる。こちらはさらに深刻で、説明文が完全に消える。

## 解決

全 locale の `messages.json` に同じキーセットを揃える。

```json
// _locales/en/messages.json ✅ 修正後（extDescription を追加）
{
  "extName": {
    "message": "YouTube Playlist Date Sorter",
    "description": "Extension name shown in the Chrome Web Store and extension manager"
  },
  "extDescription": {
    "message": "Sort visible YouTube playlist playback by publish date, title, or duration, and jump to the next video in that order.",
    "description": "Short description shown in the Chrome Web Store and extension manager"
  },
  "actionTitle": {
    "message": "Playlist Date Sorter",
    "description": "Toolbar icon tooltip"
  }
}
```

### キー漏れを防ぐ確認方法

manifest 内の `__MSG_*__` キーと各 locale ファイルのキーを突き合わせるワンライナーを使っている。

```powershell
# manifest 内の __MSG_xxx__ キーを抽出して、各 locale に存在するか確認
$keys = (Get-Content manifests/chrome.json -Raw) |
  Select-String '__MSG_(\w+)__' -AllMatches |
  ForEach-Object { $_.Matches } |
  ForEach-Object { $_.Groups[1].Value } | Sort-Object -Unique

Get-ChildItem extension/_locales -Directory | ForEach-Object {
    $locale = $_.Name
    $msgs = (Get-Content "$($_.FullName)/messages.json" -Raw | ConvertFrom-Json)
    foreach ($key in $keys) {
        if (-not $msgs.PSObject.Properties[$key]) {
            Write-Warning "MISSING: $locale/$key"
        }
    }
}
```

出力例（en に `extDescription` と `actionTitle` が欠けている場合）：

```
WARNING: MISSING: en/extDescription
WARNING: MISSING: en/actionTitle
```

新しい i18n キーを追加したタイミングで、このスクリプトを実行する運用にした。

## 注意点

- `browser_specific_settings.gecko.id` など Firefox 固有のフィールドには `__MSG_*__` は使えない。リテラル文字列で書く必要がある
- `default_locale` を設定したら、`_locales/` フォルダが必須になる。`default_locale` を指定しつつ `_locales/` がないと拡張の読み込み自体が失敗する
- フォールバックが効くのは `default_locale` のロケールまで。`default_locale` 自体にキーがなければ空文字になる
- 新しい i18n キーを追加するときは、全 locale に同時追加する運用ルールを決めておく。1 locale だけ追加して PR を出すと、他言語でフォールバックが起きる

## 参考リンク

- [MDN - Internationalization](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/Internationalization)
- [Chrome i18n API](https://developer.chrome.com/docs/extensions/reference/api/i18n)
- [YouTube Playlist Date Sorter](https://github.com/harness17/youtube-playlist-date-sorter) - 実装例
