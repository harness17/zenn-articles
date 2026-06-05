---
title: ElectronアプリをGitHub Releasesで配布するまでに整えたもの
tags:
  - Electron
  - GitHub
  - 個人開発
  - Windows
  - electron-builder
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

## 何に詰まったか

Electron アプリ [Youtom](https://github.com/harness17/youtube-schedule) を GitHub Releases で配布するとき、「installer を作って release に置く」だけでは足りなかった。

利用者に渡すには、タグ名、release note、installer の添付、`latest.yml` の添付、自動更新から見える release の状態を揃える必要があった。

この記事では Electron の作り方ではなく、GitHub Releases で配布するために整えた部分だけを書く。Windows の SmartScreen やコード署名は別記事で扱ったので、ここでは触れない。

## 結論の設定

`electron-builder.yml` では GitHub Releases を publish 先にする。

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

`artifactName` を固定しておくと、Release に添付される installer 名が読みやすくなる。Youtom では `youtube-schedule-1.23.0-setup.exe` のような名前になる。

## タグ名は v 始まりにした

Release workflow は `v*` タグで起動する。

```yaml:.github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'
```

`v1.23.0` のように npm の `version` と対応させると、GitHub Releases の一覧でもアプリ内のバージョン表示でも追いやすい。タグ名と package version がずれると、あとで「どの installer がどのコードから作られたか」を確認しにくくなる。

## Release は draft で作る

自動更新を使う場合、Release を即公開しないようにした。理由は、アセットが揃う前に公開すると、アプリ側が `latest.yml` を取りに行って失敗する可能性があるから。

```yaml:.github/workflows/release.yml
- name: Build (unsigned)
  run: npm run build:win -- --publish never

- name: Create GitHub Release (draft)
  run: gh release create "${{ github.ref_name }}" --draft --generate-notes --title "${{ github.ref_name }}"
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

workflow では draft release まで作る。人間が release note と添付ファイルを確認してから draft を解除する。

## installer と latest.yml を添付する

Youtom では installer だけでなく、`latest.yml` も添付する。`electron-updater` が更新確認に使うため。

```yaml:.github/workflows/release.yml
- name: Upload installer to GitHub Release
  run: |
    $exe = Get-ChildItem dist\*-setup.exe | Select-Object -First 1
    gh release upload "${{ github.ref_name }}" $exe.FullName --clobber
    if (Test-Path dist\latest.yml) {
      gh release upload "${{ github.ref_name }}" dist\latest.yml --clobber
    }
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  shell: pwsh
```

ここでの失敗例は、installer だけを見て「release できた」と判断しそうになったこと。自動更新を入れているなら、利用者が直接ダウンロードする `.exe` と、アプリが参照する `latest.yml` の両方が release asset として必要になる。

## release note は利用者向けに分ける

`--generate-notes` で下書きは作れるが、そのまま公開せず、次のように確認する。

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

開発者向けの変更一覧だけだと、利用者は更新してよいか判断しにくい。データ移行の有無、既知の注意点、添付ファイル名を明示すると、あとで見返すときも楽になる。

## 参考リンク

- [Youtom / youtube-schedule リポジトリ](https://github.com/harness17/youtube-schedule)
- [Youtom Releases](https://github.com/harness17/youtube-schedule/releases)
- [electron-builder: Publishing Artifacts](https://www.electron.build/configuration/publish)
- [electron-updater](https://www.electron.build/auto-update)
- [GitHub Docs: Managing releases in a repository](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository)
