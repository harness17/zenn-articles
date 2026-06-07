---
title: "Chrome拡張をFirefoxにも出すためにmanifestをファイル分離した話"
emoji: "🔀"
type: "tech"
topics: ["chrome拡張", "firefox", "manifestv3", "webextension", "個人開発"]
published: true
---

## はじめに

Chrome 拡張を作って公開したあと、「Firefox にも出したい」と思うことがある。Manifest V3 同士なら大部分のコードは共通で動くが、`manifest.json` だけはブラウザ固有の差分がある。

最初は Chrome 用の `manifest.json` をコピーして Firefox 向けに手で書き換えていた。しかし拡張の機能が増えるにつれ、片方だけ更新してもう片方を直し忘れる事故が起きた。

この記事では、個人開発の Chrome / Firefox 両対応拡張で manifest をファイル分離して管理するパターンを紹介する。実際に [YouTube Playlist Date Sorter](https://github.com/harness17/youtube-playlist-date-sorter) と [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) の 2 つの拡張で採用している構成で、ビルドスクリプト 1 本で両ブラウザの zip を出せるようになった。

**対象読者**: Chrome 拡張を作った経験があり、Firefox にも出したい個人開発者。Manifest V3 の基本構造は知っている前提で書く。

## 1つの manifest.json では何が起きるか

Chrome と Firefox は同じ Manifest V3 仕様に基づいているが、細かい差分がある。

| 項目 | Chrome | Firefox |
|------|--------|---------|
| サイドパネル | `side_panel` | `sidebar_action` |
| バックグラウンド | `service_worker`（1ファイル） | `scripts`（配列） |
| オフスクリーン | `offscreen` 権限あり | 存在しない |
| アドオンID | 不要 | `browser_specific_settings.gecko.id` が必要 |
| データ収集宣言 | 不要 | `gecko.data_collection_permissions` が必須（2025年11月以降の新規申請） |

たとえば Kindle Series Sale Tracker では、Chrome 版で `side_panel` と `offscreen` 権限を使っている。この manifest をそのまま Firefox に読み込ませると、`side_panel` キーは無視され、`offscreen` 権限は未知の権限として審査で指摘される。

逆に Firefox 向けに `browser_specific_settings.gecko` を追加した manifest を Chrome にそのまま出すと、Chrome は `browser_specific_settings` を無視するため動くには動くが、不要なキーが残った状態になる。

問題は「動かない」ことより「片方だけ更新してもう片方を直し忘れる」ことだった。差分が manifest.json の中に暗黙的に混在すると、変更のたびに「これは Chrome だけ？ Firefox も？」と考えなければならず、レビューで追えなくなる。

## manifests/ に Chrome / Firefox を明示ファイルで分離する

採用した構造はこうなっている。

```
拡張プロジェクト/
├── extension/           # 共通コード（content script, popup, icons, _locales）
│   ├── _locales/
│   │   ├── ja/messages.json
│   │   └── en/messages.json
│   ├── content/
│   ├── popup/
│   ├── shared/
│   └── icons/
├── manifests/           # ブラウザ別 manifest
│   ├── chrome.json
│   └── firefox.json
├── scripts/
│   └── package-release.ps1
└── dist/                # ビルド出力
    ├── chrome/
    └── firefox/
```

`extension/` 配下にはブラウザに依存しないコードだけを置く。`manifest.json` は `extension/` には存在しない。代わりに `manifests/chrome.json` と `manifests/firefox.json` を用意する。

### 差分が小さい拡張の例

YouTube Playlist Date Sorter は Chrome / Firefox の差分が少ない。Firefox 版は `browser_specific_settings.gecko` を追加しただけ。

```json
// manifests/chrome.json
{
  "manifest_version": 3,
  "name": "__MSG_extName__",
  "version": "0.2.0",
  "description": "__MSG_extDescription__",
  "default_locale": "ja",
  "permissions": ["storage"],
  "action": {
    "default_title": "__MSG_actionTitle__",
    "default_popup": "popup/popup.html"
  },
  "host_permissions": ["https://www.youtube.com/*"],
  "icons": {
    "16": "icons/icon16.png",
    "48": "icons/icon48.png",
    "128": "icons/icon128.png"
  },
  "content_scripts": [{
    "matches": ["https://www.youtube.com/*"],
    "js": ["shared/date-sorter.js", "shared/i18n.js", "content/content.js"],
    "css": ["content/content.css"],
    "run_at": "document_idle"
  }]
}
```

Firefox 版は `browser_specific_settings.gecko` を追加しただけ。それ以外のフィールドは Chrome 版と完全に同一。

```json
// manifests/firefox.json（差分部分のみ抜粋）
{
  // ...chrome.json と同じフィールド...
  "browser_specific_settings": {
    "gecko": {
      "id": "youtube-playlist-date-sorter@harness",
      "data_collection_permissions": {
        "required": ["none"]
      }
    }
  }
}
```

### 差分が大きい拡張の例

Kindle Series Sale Tracker は Chrome / Firefox の差分が大きい。サイドパネル、バックグラウンドスクリプト、権限がすべて異なる。

```json
// manifests/chrome.json（差分部分を抜粋）
{
  "permissions": ["activeTab", "storage", "sidePanel", "alarms", "offscreen"],
  "action": { "default_title": "__MSG_actionTitle__" },
  "side_panel": { "default_path": "popup/popup.html" },
  "background": { "service_worker": "background/background.js" }
}
```

```json
// manifests/firefox.json（差分部分を抜粋）
{
  "permissions": ["activeTab", "storage", "alarms"],
  "action": { "default_title": "__MSG_actionTitle__" },
  "sidebar_action": {
    "default_panel": "popup/popup.html",
    "default_title": "__MSG_actionTitle__"
  },
  "background": {
    "scripts": [
      "shared/kindle-library.js",
      "shared/catalog-probe.js",
      "shared/series-card.js",
      "background/background.js"
    ],
    "persistent": false
  },
  "browser_specific_settings": {
    "gecko": {
      "id": "kindle-series-sale-tracker@harness",
      "data_collection_permissions": { "required": ["none"] }
    }
  }
}
```

ファイルを分けたことで、Chrome の `side_panel` / `sidePanel` 権限と Firefox の `sidebar_action` が同じファイルに混在しなくなった。片方を変更するとき、もう片方のファイルも diff に出るかどうかで「対応漏れ」が分かる。

## ビルドスクリプトで target 別に zip を出す

`manifests/` に分離した manifest を、ビルド時に `manifest.json` としてコピーする。PowerShell スクリプト 1 本でやっている。

```powershell
# scripts/package-release.ps1
param(
    [ValidateSet("chrome", "firefox", "all")]
    [string]$Target = "all"
)

$ErrorActionPreference = "Stop"
$ProjectRoot  = Resolve-Path (Join-Path $PSScriptRoot "..")
$ExtensionRoot = Join-Path $ProjectRoot "extension"
$ManifestRoot  = Join-Path $ProjectRoot "manifests"
$DistRoot      = Join-Path $ProjectRoot "dist"
$PackageSlug   = Split-Path $ProjectRoot -Leaf

function New-ReleasePackage {
    param([string]$TargetName)

    $ManifestPath = Join-Path $ManifestRoot "$TargetName.json"
    $Manifest = Get-Content -Raw -Path $ManifestPath | ConvertFrom-Json -AsHashtable
    $Version  = $Manifest["version"]

    $TargetDistRoot = Join-Path $DistRoot $TargetName
    $StageRoot = Join-Path $TargetDistRoot "$PackageSlug-$TargetName-v$Version"
    $ZipPath   = Join-Path $TargetDistRoot "$PackageSlug-$TargetName-v$Version.zip"

    # 前回の出力をクリーンアップ
    if (Test-Path $StageRoot) { Remove-Item -LiteralPath $StageRoot -Recurse -Force }
    if (Test-Path $ZipPath)   { Remove-Item -LiteralPath $ZipPath -Force }

    New-Item -ItemType Directory -Force -Path $StageRoot | Out-Null
    # extension/ を丸ごとコピー
    Copy-Item -Path (Join-Path $ExtensionRoot "*") -Destination $StageRoot -Recurse -Force
    # manifest を manifest.json としてコピー
    Copy-Item -LiteralPath $ManifestPath -Destination (Join-Path $StageRoot "manifest.json") -Force
    # zip 化
    Compress-Archive -Path (Join-Path $StageRoot "*") -DestinationPath $ZipPath -Force
    Write-Host "Created $ZipPath"
}

if ($Target -eq "all") {
    New-ReleasePackage -TargetName "chrome"
    New-ReleasePackage -TargetName "firefox"
} else {
    New-ReleasePackage -TargetName $Target
}
```

使い方はこう。

```powershell
# 両方ビルド
./scripts/package-release.ps1 -Target all

# Chrome だけ
./scripts/package-release.ps1 -Target chrome
```

出力は `dist/chrome/拡張名-chrome-v0.2.0.zip` と `dist/firefox/拡張名-firefox-v0.2.0.zip` になる。そのまま Chrome Web Store と Firefox Add-ons にアップロードできる。

## i18n の共有で両 manifest をつなぐ

manifest の `name` や `description` はハードコードせず、`__MSG_extName__` のように i18n キーで参照している。`_locales/` は `extension/` 配下にあるため、Chrome / Firefox 両方のビルドで同じ `messages.json` が使われる。

```json
// extension/_locales/ja/messages.json
{
  "extName": {
    "message": "YouTube Playlist Date Sorter",
    "description": "拡張管理画面に表示する拡張名"
  },
  "extDescription": {
    "message": "YouTube のプレイリストを投稿日順・タイトル順・再生時間順に並び替えます。",
    "description": "ストアに表示する短い説明"
  }
}
```

両方の manifest で `"name": "__MSG_extName__"` と書くことで、拡張名を変えたいときは `messages.json` だけ直せばよい。manifest ファイルの差分は「ブラウザ固有の構造だけ」に絞り込める。

ただし注意点がある。`_locales/en/messages.json` にキーを追加し忘れると、英語環境では `default_locale`（この場合 ja）のテキストにフォールバックする。拡張名が日本語のままでも動きはするが、英語ユーザーには読めない名前が表示される。`default_locale` のロケールにもキーがなければ空表示になる。manifest と locale のキー整合チェックは自動化されないため、新しいキーを追加したら全 locale に追加する運用ルールを決めておく必要がある。

## まとめ

- **manifest の差分はファイル分離で明示する**。1 つの `manifest.json` にブラウザ固有の記述を混在させると、片方の更新漏れに気づけない
- **拡張コード（`extension/`）は共通にして、manifest だけ target 別に持つ**。差分が大きい拡張（サイドパネル、バックグラウンド構造が異なる場合）ほど効果がある
- **ビルドスクリプト 1 本で Chrome / Firefox 両方の zip を出せる**。manifest のコピーと zip 化だけなので、Webpack や Rollup のような重いツールは不要

この構成は「Chrome 拡張をとりあえず Firefox にも出す」という小規模な個人開発にちょうどよい。拡張の数が増えたり、manifest の差分が複雑になったりした場合は、バンドラーベースのビルド（Webpack / Vite プラグインで target 別に manifest を生成する方式）を検討する段階だと思う。なお [webextension-polyfill](https://github.com/nicolo-ribaudo/webextension-polyfill) は Chrome / Firefox 間の Promise API 差分を吸収するライブラリであり、manifest の構造差分を解消するものではない。

## 参考リンク

- [YouTube Playlist Date Sorter](https://github.com/harness17/youtube-playlist-date-sorter) - 差分が小さい例
- [Kindle Series Sale Tracker](https://github.com/harness17/kindle-series-sale-tracker) - 差分が大きい例
- [MDN - browser_specific_settings](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/browser_specific_settings)
- [Chrome Extensions Manifest V3](https://developer.chrome.com/docs/extensions/reference/manifest)
