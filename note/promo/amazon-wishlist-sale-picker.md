# Amazon Wishlist Sale Picker 宣伝用原稿

## 推奨媒体

- 第一候補: note / 個人ブログ
- 補助: X / Bluesky の短文告知
- 技術寄りに再構成する場合: Zenn / Qiita
- インストール導線: Chrome Web Store を主リンクにする

## 長文版（note / 個人ブログ向け）

Amazon の欲しいものリストを見ていて、「セール中の商品だけ見たい」と思うことがありました。

欲しいものリストに商品が増えると、どれが値下がりしているのかを1つずつ見るのが面倒になります。タイムセール、打ち消し価格、価格下落表示など、セールらしき情報は画面上に出ていますが、リスト全体からまとめて拾うには手間がかかります。

そこで、Amazon.co.jp の欲しいものリストからセール中の商品だけを抽出する Chrome 拡張を作りました。

## できること

- Amazon.co.jp の欲しいものリストに「セールのみ表示」ボタンを追加
- ボタンを押すと、リストをスキャンしてセール中の商品だけに絞り込み
- タイムセールバッジ、打ち消し価格、価格下落表示、セール系キーワードを見て判定
- 割引率フィルターで「○% 以上の割引だけ」に絞り込み
- lazy load のリストを自動スクロールで読み込み
- 外部サーバーへの送信なし

対象は Amazon.co.jp の欲しいものリストです。

- `https://www.amazon.co.jp/hz/wishlist/ls/*`
- `https://www.amazon.co.jp/hz/wishlist/genericItemsPage/*`
- `https://www.amazon.co.jp/gp/registry/wishlist/*`

## 外部サーバーには送信しません

この拡張は、欲しいものリストの画面上で動きます。セール判定もブラウザ内で行います。

権限は `storage` を使い、割引率フィルターなどの設定を保存します。欲しいものリストの内容を外部サーバーへ送る設計にはしていません。

## こんな人向けです

- Amazon の欲しいものリストに商品をたくさん入れている
- セール中の商品だけをまとめて見たい
- 値下がりしているものから優先して買いたい
- リストを1件ずつ確認するのが面倒

## 注意点

Amazon のページ構造や表示文言に依存しているため、Amazon 側の DOM 変更で検出できなくなる可能性があります。また、現時点では Amazon.co.jp を対象にしています。海外 Amazon は対象外です。

セール判定は画面上の表示から行うため、Amazon 側の正式な価格履歴を保証するものではありません。購入前には、商品ページの価格と条件を確認してください。

## リンク

- Chrome Web Store: https://chromewebstore.google.com/detail/amazon-wishlist-sale-pick/hbjnpfdjifnmofkgadigphfamcnpgbaj
- GitHub: https://github.com/harness17/google-chrome-extensions/tree/main/amazon-wishlist-sale-picker

## 短文版（X / Bluesky 向け）

Amazon.co.jp の欲しいものリストから、セール中の商品だけを抽出する Chrome 拡張を作りました。

- セールのみ表示
- 割引率フィルター
- lazy load の全件読み込み
- 外部サーバー送信なし

欲しいものリストが増えて、値下がり商品を探すのが面倒な人向けです。

Chrome Web Store:
https://chromewebstore.google.com/detail/amazon-wishlist-sale-pick/hbjnpfdjifnmofkgadigphfamcnpgbaj

GitHub:
https://github.com/harness17/google-chrome-extensions/tree/main/amazon-wishlist-sale-picker

## Chrome Web Store 説明文案

### 短い説明

Amazon.co.jp の欲しいものリストから、セール中の商品だけを抽出します。

### 詳細説明

Amazon Wishlist Sale Picker は、Amazon.co.jp の欲しいものリストでセール中の商品を見つけやすくする Chrome 拡張です。

欲しいものリストに「セールのみ表示」ボタンを追加し、ボタンを押すとリスト内の商品をスキャンして、セール中の商品だけに絞り込みます。

主な機能:

- セール中商品の抽出
- タイムセールバッジ、打ち消し価格、価格下落表示、セール系キーワードによる判定
- 割引率フィルター
- lazy load の自動読み込み
- ブラウザ内での判定

この拡張は Amazon.co.jp の欲しいものリストを対象にしています。海外 Amazon は対象外です。

注意:

- セール判定はページ上の表示に基づきます。
- Amazon 側のページ構造変更により、検出できなくなる場合があります。
- 購入前には商品ページの価格と条件を確認してください。
