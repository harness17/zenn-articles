# 構成メモ: 未署名 Electron アプリを配布すると SmartScreen で止まる問題に向き合った話

## メタ情報

- **slug 案**: `electron-smartscreen-oss-distribution`
- **type**: tech
- **emoji**: 🪟 または 🧾
- **topics**: `electron` / `windows` / `githubactions` / `oss` / `codesigning`
- **想定文字数**: 3000〜4000字
- **想定執筆時間**: 4〜5時間
- **ステータス**: 構成中

## タイトル案

| 案 | タイトル | 強み |
|----|---------|------|
| **A**（推奨） | 未署名Electronアプリを配布するとSmartScreenで止まる問題に向き合った話 | 失敗体験と対象読者が明確 |
| B | 個人開発のElectronアプリ配布でSmartScreen警告に詰まった話 | 個人開発文脈が前に出る |
| C | ElectronアプリをOSSとして配布する前に見ておきたいコード署名の現実 | 読者の事前チェック記事として読まれやすい |

→ **A 推奨**。この記事は「作る」ではなく「配る」で詰まった体験を書くので、SmartScreen をタイトルに入れる。

---

## 想定読者

Electron で Windows 向けの個人開発アプリや OSS ツールを作り、GitHub Releases などで配布しようとしているエンジニア。

---

## 詰まったこと

Electron アプリはビルドして `.exe` や installer を作るだけなら難しくない。

ただ、Windows で未署名の実行ファイルを配布すると、初回起動時に Microsoft Defender SmartScreen の警告が出る。ユーザーから見ると「危ないアプリ」に見えやすく、アプリ本体の機能以前に配布導線で信頼を失う。

個人開発 OSS では商用コード署名証明書の費用が重く、かといって警告を無視してもらうだけでは導入体験が悪い。そこで、コード署名を前提にしつつ、署名できない状態でもリリース自体は止めない方針にした。

---

## 判断軸

- 配布物の安全性を、README と release notes だけで説明しきれるか
- コード署名が失敗したとき、リリースを止めるべきか、未署名として出すべきか
- OSS 向けの署名支援（例: SignPath Foundation）を使えるまでの暫定導線をどうするか
- ユーザーに SmartScreen 回避手順を案内するとき、危険な操作として誤解されない説明になっているか
- GitHub Actions の release workflow が、署名あり・署名なしの両方で追える形になっているか

---

## 記事の核

**「Electron アプリは作って終わりではなく、Windows で信頼される形で配布するところまで設計が必要だった」** という体験を書く。

実装レイヤーは3段階で説明する。

1. **失敗体験**: 未署名ビルドを配布すると SmartScreen 警告で導入が止まる
2. **暫定対応**: README に回避手順を書き、未署名であることを明示する
3. **継続対応**: GitHub Actions に任意署名フローを入れ、署名できる環境では署名済み、できない環境では未署名 fallback にする

---

## 構成

### はじめに（250〜350字）

- 個人開発の Electron アプリを Windows 向けに配布しようとした話として始める
- ビルドや GitHub Releases へのアップロードより、SmartScreen 警告が配布上の問題になったことを書く
- この記事で扱う範囲:
  - SmartScreen 警告が起きる理由の概要
  - 個人 OSS でコード署名コストが重いこと
  - README と release workflow でどこまで現実的に対応したか
- 扱わない範囲:
  - EV 証明書の詳細な比較
  - SmartScreen 評判システムの内部仕様推測

### セクション1: Electron アプリはビルドできても、そのまま信頼されるわけではない（600〜800字）

- 伝えること: Windows 向け配布では、実行ファイルの署名と SmartScreen の見え方がユーザー体験に直結する
- 具体例:
  - GitHub Releases から installer をダウンロードする
  - 初回実行で SmartScreen 警告が出る
  - 「詳細情報」→「実行」という操作が必要になる
- 書き方:
  - SmartScreen を解除する裏技記事にはしない
  - ユーザーから見た不安と、開発者として説明責任が発生する点を書く
- 図候補:
  - `build -> release -> download -> SmartScreen -> first run` の流れを簡単な図にする

### セクション2: 商用コード署名証明書は個人 OSS には重い（600〜800字）

- 伝えること: 正攻法はコード署名だが、個人 OSS では費用・審査・継続運用が負担になる
- 具体例:
  - 商用コード署名証明書を購入する
  - OSS 向け支援プログラムを検討する
  - 署名できるまでは未署名配布を前提に導線を整える
- 注意点:
  - 「証明書を買わなくてよい」とは書かない
  - 署名は信頼性を上げるための正攻法として扱う
  - SignPath Foundation などの申請状況は、執筆時点の事実だけを書く

### セクション3: README では SmartScreen 回避手順を明示した（500〜700字）

- 伝えること: 未署名で配布するなら、警告が出ることを隠さず、ユーザーが判断できる情報を置く
- 具体例:
  - README に「未署名ビルドでは SmartScreen 警告が出る場合がある」と明記
  - 回避手順は「詳細情報」→「実行」の最小限にする
  - ソースコード、ビルド workflow、release artifact を確認できる導線を置く
- コード・文章例候補:

```markdown
### Windows SmartScreen について

現在の Windows ビルドは未署名のため、初回起動時に SmartScreen の警告が表示される場合があります。
内容を確認したうえで実行する場合は、「詳細情報」→「実行」を選択してください。
```

- 注意点:
  - ユーザーに無条件実行を促さない
  - 「警告は無視してよい」と書かない
  - OSS として検証可能な情報に誘導する

### セクション4: release workflow は署名あり・署名なしの両方を通す（800〜1000字）★メイン

- 伝えること: 署名できない環境でもリリース作業を止めず、署名設定が揃ったら同じ workflow で署名済み artifact を出せるようにする
- 具体例:
  - GitHub Actions で Windows build を実行
  - 署名に必要な secret がある場合だけ署名ステップを実行
  - secret がない場合は unsigned artifact として upload
  - release notes や artifact 名で署名状態が分かるようにする
- コード候補:
  - `.github/workflows/release.yml` の署名分岐
  - `electron-builder` の publish / artifact 設定
- 擬似コード例:

```yaml
- name: Build Windows installer
  run: npm run build:win

- name: Sign artifact
  if: ${{ secrets.SIGNING_TOKEN != '' }}
  run: npm run sign:win

- name: Upload release artifact
  uses: actions/upload-artifact@v4
  with:
    name: windows-installer
    path: dist/*.exe
```

- 判断:
  - 「署名がないならリリース不可」にすると、OSS としての反復速度が落ちる
  - 「常に未署名でよい」にすると、配布の信頼性課題を放置する
  - そのため、署名を目標に置きつつ、未署名 fallback を明示する

### セクション5: SmartScreen 対応は技術というより配布設計だった（500〜700字）

- 伝えること: この問題はコードだけで解ける問題ではなく、配布・説明・検証可能性を含む設計だった
- 具体例:
  - アプリ本体の品質と、OS から見た信頼は別
  - README、release notes、署名、ソース公開、CI の透明性を組み合わせる
  - 最初から完璧な署名体制がなくても、ユーザーに見える情報を増やせる
- 読者への判断軸:
  - 社内配布なら組織の証明書や配布基盤を使う
  - 一般公開ならコード署名を早めに設計に入れる
  - 個人 OSS なら、未署名期間の説明導線を先に作る

### まとめ（200〜300字）

- 要点3つ:
  1. Electron アプリはビルドできても、Windows では SmartScreen で配布が止まることがある
  2. 個人 OSS ではコード署名コストが重いので、署名を目標にしつつ未署名時の説明導線を作る
  3. release workflow は署名あり・署名なしの両方を追える形にしておくと、後から署名基盤を足しやすい
- 最後は「作ったアプリをどう信頼してもらうかまで含めて配布設計だった」と締める

---

## コード例の準備状況

| セクション | コード言語 | 出典 | 準備状況 |
|------------|------------|------|----------|
| SmartScreen 回避手順 | markdown | README の SmartScreen 案内 | 要確認 |
| release workflow の署名分岐 | yaml | `.github/workflows/release.yml` | 要確認 |
| electron-builder 設定 | json / yaml | `package.json` または builder config | 要確認 |
| artifact 名・release notes | markdown / yaml | GitHub Release 設定 | 要確認 |

---

## 参考リンク候補

### 公式・一次情報

- Microsoft Learn: Microsoft Defender SmartScreen
- Microsoft Learn: Code signing
- Electron: Code Signing
- electron-builder: Code Signing
- GitHub Actions: Encrypted secrets

### 自分のリポジトリ

- youtube-schedule または Youtom の該当リポジトリ
- README の SmartScreen 案内
- release workflow の署名・upload フロー

---

## 守秘義務・セキュリティ上の注意

- 署名用 secret 名、トークン、証明書ファイル名、内部パスは記事に書かない
- SignPath など外部サービスの審査状況は、公開して問題ない事実だけを書く
- SmartScreen の警告を「無視してよい」と表現しない
- ユーザーが実行判断できるよう、ソースコード・release artifact・workflow への導線を置く

---

## 残タスク（執筆前に確認すること）

- [ ] 対象リポジトリを youtube-schedule / Youtom のどちらにするか確定する
- [ ] README の SmartScreen 案内を確認し、記事に引用する範囲を決める
- [ ] `.github/workflows/release.yml` の署名分岐を確認する
- [ ] SignPath Foundation などの申請状況を、公開可能な事実として書けるか確認する
- [ ] 参考リンクを公式ドキュメント中心に差し替える
- [ ] 本文化後に `/article-review` で文体・必須要素・守秘義務を確認する

---

## 執筆順序（推奨）

1. はじめにと §1 で「配布で詰まった」状況を書く
2. §2 でコード署名の正攻法と個人 OSS の制約を書く
3. §3 で README の案内を具体化する
4. §4 で release workflow の署名分岐をコード例つきで説明する
5. §5 とまとめで「配布設計」という判断軸に戻す
