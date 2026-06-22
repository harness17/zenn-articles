# YouTube Playlist Date Sorter 宣伝用原稿

## 推奨媒体

- 第一候補: note / 個人ブログ
- 補助: X / Bluesky の短文告知
- 技術寄りに再構成する場合: Zenn / Qiita
- インストール導線: Chrome Web Store を主リンクにする

## 長文版（note / 個人ブログ向け）

YouTube のプレイリストを「投稿日順」で見たい場面がありました。

たとえば、シリーズものの動画、配信アーカイブ、古い順に追いたい学習用プレイリストです。YouTube のプレイリストは便利ですが、表示順はプレイリスト側の順序に依存します。自分が見たい順番と一致しないことがあります。

そこで、YouTube のプレイリストを投稿日順に並び替えて、その順番で次の動画へ移動できる Chrome 拡張を作りました。

## できること

- YouTube のプレイリストページで、表示中の動画を投稿日順に並び替える
- 古い順 / 新しい順を切り替える
- 並び替えた順番で「次の動画へ」移動する
- 自動 ON にすると、動画終了後に投稿日順で次の動画へ移動する
- YouTube の通常順に戻せる
- 日本語 / English を切り替えられる
- 右下パネルを最小化できる

対象は次のような URL です。

- `https://www.youtube.com/playlist?list=...`
- `https://www.youtube.com/watch?...&list=...`

## API キーは不要です

この拡張では YouTube Data API を使っていません。API キーの作成や Google Cloud Console の設定は不要です。

表示中のプレイリスト DOM から動画 ID を取り、各動画ページの HTML から投稿日を読み取って並び替えます。プレイリストそのものの順序や所有者データは変更しません。あくまで、ブラウザ上の表示順と次に開く動画を拡張側で制御します。

## こんな人向けです

- プレイリストを古い動画から順番に見たい
- シリーズものや配信アーカイブを時系列で追いたい
- YouTube の標準 UI だけだと並び順が足りない
- API キーなしで使える小さな拡張がほしい

## 注意点

YouTube のページ構造に依存しているため、YouTube 側の DOM 変更で動かなくなる可能性があります。また、対象はページ上に読み込まれている動画です。長いプレイリストでは、まず表示されている範囲から処理します。

それでも、自分の用途では「プレイリストを投稿日順に追える」だけでかなり見やすくなりました。

## リンク

- Chrome Web Store: https://chromewebstore.google.com/detail/youtube-playlist-date-sor/hobigboofokgcnjfobilijbknbmemlbd
- Firefox Add-ons: https://addons.mozilla.org/ja/firefox/addon/youtube-playlist-date-sorter/
- GitHub: https://github.com/harness17/google-chrome-extensions/tree/main/youtube-playlist-date-sorter

## 短文版（X / Bluesky 向け）

YouTube のプレイリストを投稿日順に並び替える Chrome / Firefox 拡張を作りました。

- 古い順 / 新しい順
- 並び替え順で次の動画へ移動
- 自動再生にも対応
- YouTube Data API キー不要

シリーズものや配信アーカイブを時系列で追う用途向けです。

Chrome Web Store:
https://chromewebstore.google.com/detail/youtube-playlist-date-sor/hobigboofokgcnjfobilijbknbmemlbd

Firefox Add-ons:
https://addons.mozilla.org/ja/firefox/addon/youtube-playlist-date-sorter/

GitHub:
https://github.com/harness17/google-chrome-extensions/tree/main/youtube-playlist-date-sorter

## Chrome Web Store 説明文案

### 短い説明

YouTube のプレイリストを動画投稿日順に並び替え、その順序で次の動画へ移動します。

### 詳細説明

YouTube Playlist Date Sorter は、YouTube のプレイリストページとプレイリスト再生ページで、表示中の動画を投稿日順に並び替える Chrome 拡張です。

古い順 / 新しい順を切り替え、並び替えた順番で次の動画へ移動できます。自動 ON にすると、動画終了後に投稿日順で次の動画へ移動します。

YouTube Data API は使わないため、API キーの設定は不要です。プレイリスト自体の順序や所有者データは変更せず、ブラウザ上の表示と拡張側の次動画制御だけで動作します。

主な機能:

- プレイリストを投稿日順に並び替え
- 古い順 / 新しい順 / 通常順の切り替え
- 並び替え順で次の動画へ移動
- 動画終了後の自動移動
- 日本語 / English 切り替え
- 右下パネルの最小化

注意:

- YouTube のページ構造変更により、動作しなくなる場合があります。
- ページ上に読み込まれている動画を対象にします。
