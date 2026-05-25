---
title: "未署名Electronアプリを配布するとSmartScreenで止まる問題に向き合った話"
emoji: "🪟"
type: "tech"
topics: ["electron", "windows", "githubactions", "oss", "codesigning"]
published: true
---

## はじめに

個人開発の Electron デスクトップアプリ [YouTom](https://github.com/harness17/youtube-schedule) を Windows 向けに配布しようとしたとき、アプリ本体とは別のところで詰まりました。

ビルドして installer を作ることはできます。GitHub Releases に置くこともできます。ただ、未署名の `.exe` をダウンロードして実行すると、Microsoft Defender SmartScreen の警告が出ます。

ユーザーから見ると、これは「危ないアプリ」に見えます。作った機能以前に、初回起動の導線で信頼を失う可能性があります。

この記事では、個人 OSS の Electron アプリを Windows 向けに配布するとき、SmartScreen 警告とコード署名にどう向き合ったかを書きます。SmartScreen を消す裏技ではなく、未署名期間をどう説明し、後から署名へ移れる release workflow にしたかの記録です。

## ビルドできても、そのまま信頼されるわけではない

YouTom は YouTube の登録チャンネルの配信予定やライブ中の動画を一覧表示する Windows デスクトップアプリです。

Electron アプリとしては、`electron-builder` で Windows installer を作っています。

```yaml
appId: io.github.harness17.youtube-schedule
productName: YouTom
win:
  executableName: YouTubeSchedule
nsis:
  artifactName: ${name}-${version}-setup.${ext}
  shortcutName: ${productName}
  uninstallDisplayName: ${productName}
```

この設定で `npm run build:win` を実行すれば、`youtube-schedule-X.X.X-setup.exe` のような installer を作れます。

```json
{
  "scripts": {
    "build": "electron-vite build",
    "build:win": "npm run build && electron-builder --win"
  }
}
```

ここまでは「アプリを作る」側の作業です。問題は、この installer をユーザーがダウンロードして実行する段階で起きました。

未署名の実行ファイルでは、Windows が SmartScreen 警告を出す場合があります。Microsoft の SmartScreen reputation の説明では、ダウンロードされたファイルの評判や発行元の評判を見て警告を出すと説明されています。

参考: [SmartScreen reputation for Windows app developers](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation)

つまり、開発者側で「これは自分が作ったアプリです」と思っていても、OS から見るとまだ信頼できる配布物とは限りません。特に個人開発の初期リリースでは、ダウンロード数も少なく、発行元としての評判もありません。

## 正攻法はコード署名だが、個人 OSS には重い

正攻法はコード署名です。

Electron 公式ドキュメントでも、配布するアプリはコード署名するべきだと説明されています。未署名アプリは、OS 側の警告や追加操作が必要になるためです。

参考: [Electron - Code Signing](https://www.electronjs.org/docs/latest/tutorial/code-signing)

ただ、個人 OSS で最初から商用のコード署名証明書を用意するのは重いです。証明書の費用、審査、更新、CI への組み込み、秘密情報の管理が必要になります。

そこで、YouTom では [SignPath Foundation](https://signpath.io/solutions/open-source-community) の OSS コード署名を検討しました。実際に申請もしましたが、2026 年 5 月時点では、外部の利用実績や第三者による言及などの信頼シグナル不足で未承認です。

ここで判断が必要になりました。

- 署名できるまでリリースを止める
- 未署名のまま出し続ける
- 署名を目標に置きつつ、未署名であることを明示して配布する

今回は 3 つ目を選びました。まだ利用者が少ない段階でリリースを止めると、そもそも利用実績もフィードバックも増えません。一方で、未署名であることを隠して配布するのはよくありません。

なので、README では SmartScreen 警告が出る可能性と、現在の配布版が未署名であることを明記しました。

## README では警告が出ることを先に書いた

YouTom の README では、インストーラー版の手順に SmartScreen の説明を入れています。記事として載せるなら、たとえば次のような案内です。

```markdown
> #### ⚠️ Windows セキュリティの警告が出た場合
>
> インストール時に「**Windows によって PC が保護されました**」と表示されることがあります。
> これはコード署名証明書のないアプリでも表示される警告です。実行前に、配布元とソースコードを確認してください。
>
> **回避手順：**
>
> 1. 「**詳細情報**」をクリック
> 2. 「**実行**」ボタンをクリック
>
> 現在の配布版は未署名です。SignPath Foundation の OSS コード署名は外部の利用実績・言及などの信頼シグナルが増えた段階で再申請する予定です。
```

ここで気をつけたのは、「警告は無視してよい」と書かないことです。

SmartScreen はユーザーを守るための警告です。開発者が「自分のアプリだから安全」と思っていても、ユーザーにとっては初めて見る実行ファイルです。警告を軽く扱う文章にすると、セキュリティ意識の低い配布に見えます。

そのため、README では次の情報をセットにしました。

- 現在の配布版は未署名である
- SmartScreen 警告が表示される場合がある
- 実行する場合の操作は「詳細情報」→「実行」
- OSS コード署名は再申請予定である
- ソースコードと release workflow は GitHub 上で確認できる

未署名配布を正当化するのではなく、ユーザーが判断できる材料を増やす方針です。

## release workflow は未署名 fallback を残した

次に、GitHub Actions の release workflow を見直しました。

目標は、SignPath の設定が揃ったら署名を実行し、まだ揃っていない場合は未署名のまま release artifact を出せる形にすることです。

実際の workflow では、まず未署名 installer を作ります。

```yaml
- name: Build (unsigned)
  run: npm run build:win -- --publish never

- name: Upload unsigned installer as artifact
  id: upload-unsigned
  uses: actions/upload-artifact@v4
  with:
    name: unsigned-installer
    path: dist/*-setup.exe
```

その後、SignPath 用の secret がある場合だけ署名ステップを実行します。

```yaml
- name: Sign with SignPath
  id: signpath
  if: ${{ env.SIGNPATH_API_TOKEN != '' && env.SIGNPATH_ORGANIZATION_ID != '' }}
  uses: SignPath/github-action-submit-signing-request@v1
  with:
    api-token: '${{ secrets.SIGNPATH_API_TOKEN }}'
    organization-id: '${{ secrets.SIGNPATH_ORGANIZATION_ID }}'
    project-slug: 'youtube-schedule'
    signing-policy-slug: 'release-signing'
    artifact-configuration-slug: 'initial'
    github-artifact-id: '${{ steps.upload-unsigned.outputs.artifact-id }}'
    github-token: '${{ secrets.GITHUB_TOKEN }}'
    wait-for-completion: true
    output-artifact-directory: 'dist-signed'
  continue-on-error: true
```

署名が成功した場合だけ、署名済み installer を `dist/` に戻します。

```yaml
- name: Use signed installer
  if: ${{ steps.signpath.outcome == 'success' }}
  run: Copy-Item dist-signed\*.exe dist\ -Force
  shell: pwsh
```

最後に GitHub Release へ upload します。

```yaml
- name: Upload installer to GitHub Release
  if: ${{ github.event_name != 'workflow_dispatch' || !inputs.dry_run }}
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

この形にした理由は、リリースの反復速度と配布の信頼性を両方残したかったからです。

署名情報がないならリリース失敗、という設計にすると、OSS プランが未承認の間はリリースできません。一方で、常に未署名でよいという設計にすると、後から署名基盤を入れる導線が弱くなります。

そのため、workflow 上は署名を組み込む場所を先に作り、secret がない間はスキップする形にしました。

GitHub Actions の secret は、リポジトリや environment に保存した機密情報を workflow から参照する仕組みです。署名用 token や organization id のような値は、記事やリポジトリに直接書かず、secret 経由で渡します。

参考: [GitHub Actions - Secrets](https://docs.github.com/en/actions/concepts/security/secrets)

## SignPath 再申請用のメモもリポジトリに残した

もうひとつやったのは、SignPath が使えるようになった後の手順を `.github/signpath-setup.md` に残したことです。

未承認の段階で細かい設定を全部完了させることはできません。それでも、再申請できる状態になったときに何を見るかは残せます。

メモには次の内容を書きました。

- 再申請前に確認する信頼シグナル
- SignPath の project / artifact configuration / signing policy の作成項目
- GitHub Secrets に登録する値
- workflow 上で署名ステップが動いているかの確認手順
- 署名後も SmartScreen が出る場合があること

:::message alert
特に、署名後も SmartScreen がすぐ消えるとは限らない点は重要です。

Microsoft の説明では、SmartScreen はファイルの評判や発行元の評判を見るため、新しいビルドでは評判が十分でない場合があります。署名は信頼性を上げる重要な手段ですが、「署名すれば初回から必ず警告ゼロ」とは書かない方が正確です。
:::

この点は、配布前に期待値を下げるためではなく、ユーザー向け説明と開発者側の計画を現実に合わせるために必要でした。

## SmartScreen 対応は配布設計だった

今回の対応で分かったのは、SmartScreen 問題はコードだけで解ける問題ではないということです。

アプリの機能が動いていても、OS から見た信頼、ユーザーから見た信頼、リリース手順の透明性は別です。

個人 OSS で最初から十分な署名体制を持てない場合でも、できることはあります。

- 未署名であることを README に明記する
- SmartScreen 警告が出る可能性を事前に説明する
- ソースコードと release workflow を公開して、検証可能性を上げる
- 署名が使えるようになったときの workflow を先に用意する
- secret や証明書の情報はリポジトリに置かない

社内配布なら、組織の証明書や配布基盤を使うのが自然です。一般公開なら、Microsoft Store やコード署名を早めに検討した方がよいです。

個人 OSS では、その中間の期間があります。署名はまだないが、配布して使ってもらわないと信頼シグナルも増えない。その期間をどう扱うかまで含めて、配布設計でした。

## まとめ

Electron アプリは、`electron-builder` で installer を作れた時点ではまだ配布完了ではありませんでした。

- 未署名の Windows installer は SmartScreen 警告で初回導線が止まることがある
- コード署名は正攻法だが、個人 OSS では費用や審査の負担がある
- 未署名期間は README で明示し、ユーザーが判断できる情報を置く
- release workflow は署名あり・署名なしの両方を通せる形にしておく
- 署名用 token や証明書情報は GitHub Secrets で扱い、記事やリポジトリには書かない

自分にとってこの件は、「アプリを作る」と「アプリを配る」は別の設計問題だと気づくきっかけでした。

YouTom の実装と release workflow は [YouTom リポジトリ](https://github.com/harness17/youtube-schedule) にあります。今後 SignPath Foundation を再申請できる状態になったら、この記事の続きとして、署名後の workflow と SmartScreen の見え方も記録する予定です。

## 参考リンク

- [YouTom リポジトリ](https://github.com/harness17/youtube-schedule)
- [SmartScreen reputation for Windows app developers](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/smartscreen-reputation)
- [Code signing options for Windows app developers](https://learn.microsoft.com/en-us/windows/apps/package-and-deploy/code-signing-options)
- [Electron - Code Signing](https://www.electronjs.org/docs/latest/tutorial/code-signing)
- [electron-builder - Code Signing](https://www.electron.build/code-signing.html)
- [GitHub Actions - Secrets](https://docs.github.com/en/actions/concepts/security/secrets)
