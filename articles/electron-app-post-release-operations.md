---
title: "個人開発のElectronアプリをGitHubに公開してから必要になったもの"
emoji: "📦"
type: "tech"
topics: ["electron", "github", "個人開発", "windows"]
published: true
---

## はじめに

YouTube の配信予定を管理する Electron アプリ [Youtom](https://github.com/harness17/youtube-schedule) を公開したあと、「アプリを作る」と「人に使ってもらえる状態にする」は別の作業だと分かった。

ビルドして installer を作り、GitHub Releases に置けば配布は始められる。ただ、公開後に README、リリースノート、更新通知、バイナリ添付を整えないと、利用者はどこから始めればよいか分からない。

この記事では Electron アプリの作り方ではなく、公開後に足りないと分かった運用を書きます。SmartScreen とコード署名は別記事で扱ったので、参照に留めます。

関連: [未署名Electronアプリを配布するとSmartScreenで止まる問題に向き合った話](https://zenn.dev/harness/articles/electron-smartscreen-oss-distribution)

## 公開後に足りなかったもの

最初に GitHub 公開した時点では、開発者向けの情報は手元にあった。`npm install` して `npm run dev` すれば起動できるし、`npm run build:win` で Windows 向けにビルドできる。

ただ、利用者が見る情報はそれだけでは足りなかった。

- インストーラーをどこからダウンロードするのか
- Node.js が必要なのか
- 初回起動後に何をすればよいのか
- うまくログインできないとき、何を確認すればよいのか
- 新しいバージョンが出たとき、どう気づくのか

GitHub に置いた瞬間、README は「開発メモ」ではなく「利用者の入口」になる。

Youtom では、README を利用者向けに組み直した。Releases から installer を落とす手順、簡易モードでの初回利用、フルモードで使う OAuth クライアントの作成、よくあるトラブルを順に置いた。簡易モードは OAuth なしで起動できるため、まず手動追加したチャンネルを RSS で見る導線を先に書いた。

## README は利用者の最初の画面になる

公開後に README を直した理由は、問い合わせを減らすためだけではない。README の具体性がそのまま信頼につながる。

README では、インストーラー利用の冒頭を次のような流れにした。

```markdown
## インストーラー版を使う（推奨）

### 1. インストーラーをダウンロードする

[Releases](https://github.com/harness17/youtube-schedule/releases) から
最新の `youtube-schedule-X.X.X-setup.exe` をダウンロードして実行します。

> Node.js は不要です。

### 2. まず簡易モードで使う

1. アプリを起動する
2. 右上の設定を開く
3. 手動追加セクションでチャンネル URL または @ハンドルを入力する
4. 更新ボタンを押す
```

この程度の説明でも、開発者向け README とは役割が違う。利用者が最初に迷う点を先に潰す。

FAQ も実装上の都合ではなく利用者の症状から書いた。`credentials.json` の形式不備、OAuth 同意画面のテストユーザー不足、API クォータ超過は別問題だが、利用者から見るとすべて「ログインできない」「表示されない」になる。

## Release は draft で作るようにした

GitHub Releases も、単に `.exe` を置けばよいわけではなかった。

Youtom は `electron-builder` を使って Windows installer を作っている。設定では GitHub Releases を publish 先にしている。

```yaml:electron-builder.yml
appId: io.github.harness17.youtube-schedule
productName: Youtom
win:
  executableName: YouTubeSchedule
nsis:
  artifactName: ${name}-${version}-setup.${ext}
  shortcutName: ${productName}
  uninstallDisplayName: ${productName}
publish:
  provider: github
  owner: harness17
  repo: youtube-schedule
```

リリース時は Git タグを `v1.23.0` のように切り、GitHub Actions が installer を作る。ここで気をつけたのは、Release を最初から公開しないことだった。

```yaml:.github/workflows/release.yml
on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: windows-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: '24'
          cache: 'npm'
      - name: Install dependencies
        run: npm ci
      - name: Build (unsigned)
        run: npm run build:win -- --publish never
```

このあと、draft release を作って installer と `latest.yml` を添付する。

```yaml:.github/workflows/release.yml
- name: Create GitHub Release (draft)
  run: gh release create "${{ github.ref_name }}" --draft --generate-notes --title "${{ github.ref_name }}"
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}

- name: Upload installer to GitHub Release
  run: |
    $exe = Get-ChildItem dist\*-setup.exe | Select-Object -First 1
    gh release upload "${{ github.ref_name }}" $exe.FullName --clobber
    if (Test-Path dist\latest.yml) {
      gh release upload "${{ github.ref_name }}" dist\latest.yml --clobber
    }
  shell: pwsh
```

draft にした理由は、自動更新との相性だった。`electron-updater` は GitHub Releases の `latest.yml` を見に行く。アセットが揃う前に Release を公開すると、利用者側で更新情報の取得に失敗する。

そのため、workflow では draft まで作る。人間がリリースノートと添付ファイルを確認してから、draft を外す運用にした。

## リリースノートは変更内容だけでなく利用者影響を書く

GitHub Releases のリリースノートでは、バージョン番号と変更内容だけを書いても伝わりにくい。自分用なら「設定モーダル修正」で分かる。しかし利用者向けには「何が変わったか」「更新してよいか」「既知の注意点はあるか」を分けた方が読みやすい。

Youtom では、手動確認時の構成を次のようにした。

```text
v1.23.0

## 変更内容
- 設定画面にアップデート確認を追加
- 自動更新の有効 / 無効を保存できるようにした

## 利用者への影響
- 起動時に新しいバージョンがある場合、アプリ内に通知が出ます
- 既存データの移行作業は不要です

## 添付ファイル
- youtube-schedule-1.23.0-setup.exe
- latest.yml
```

ここまで分けると、あとで自分が見返したときにも「このバージョンで何を出したか」が分かる。

## electron-updater を入れるかどうか

更新通知も公開後に考え直した点だった。選択肢は大きく 2 つある。

| 方針 | 利点 | 困る点 |
|------|------|--------|
| README と GitHub Releases だけで案内する | 実装が軽い | 利用者が更新に気づきにくい |
| electron-updater を入れる | アプリ内で更新を知らせられる | Release アセットや `latest.yml` の運用が必要 |

Youtom では `electron-updater` を入れた。アプリ情報画面にアップデート確認と自動更新設定を置き、更新があれば renderer 側へ通知する。

```js:src/main/index.js
function setupAutoUpdater(mainWindow) {
  if (is.dev) return

  autoUpdater.autoDownload = getSetting('autoDownload', true)
  autoUpdater.autoInstallOnAppQuit = true

  autoUpdater.on('update-available', (info) => {
    mainWindow.webContents.send('updater:update-available', info)
  })
  autoUpdater.on('update-downloaded', (info) => {
    mainWindow.webContents.send('updater:update-downloaded', info)
  })
  autoUpdater.on('error', (err) => {
    logger?.error('autoUpdater.error', { error: err })
    mainWindow.webContents.send('updater:error', 'UPDATE_CHECK_FAILED')
  })

  autoUpdater.checkForUpdates()
}
```

ここで失敗したのは、更新通知を入れた時点で Release 運用も一段固くする必要があったことだ。GitHub Releases の公開順序、`latest.yml` の添付、draft の解除タイミングまで含めて設計しないと利用者側のエラーになる。

## 作って終わりではなかった

Electron アプリを GitHub に公開する前は、配布後の作業を少し軽く見ていた。ビルドが通り、installer ができ、Release に置ければ一区切りだと思っていた。

実際には、その後に必要なものが多かった。

- README を利用者の入口として書き直す
- Releases のタグ命名とリリースノートを揃える
- installer と `latest.yml` を漏れなく添付する
- 自動更新を入れるなら draft release の確認手順を作る
- 未署名配布や SmartScreen は別の説明として切り分ける

個人開発では、実装もドキュメントもリリース作業も同じ人が見る。だからこそ、運用の手順を曖昧にしていると、自分が次のリリースで詰まる。アプリを公開した時点で運用が始まる、というのが今回の気づきだった。

## 参考リンク

- [Youtom / youtube-schedule リポジトリ](https://github.com/harness17/youtube-schedule)
- [Youtom Releases](https://github.com/harness17/youtube-schedule/releases)
- [electron-builder: Publishing Artifacts](https://www.electron.build/configuration/publish)
- [electron-updater](https://www.electron.build/auto-update)
- [GitHub Docs: Managing releases in a repository](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
- [関連Zenn記事: 未署名Electronアプリを配布するとSmartScreenで止まる問題に向き合った話](https://zenn.dev/harness/articles/electron-smartscreen-oss-distribution)
