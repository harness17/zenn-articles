---
name: note-import
description: note向け記事本文やnoteインポートへ直接アップロードできるWXRファイルを作成・整形するスキル。noteに投稿する宣伝記事、読み物記事、noteインポート仕様に合わせた本文チェック、MarkdownからWXRへの変換、画像・iframe・日付・文字コードの注意点を反映した原稿作成を求められたときに使う。
---

# note-import

note 向けの記事本文を作成・整形し、必要なら note インポートへ直接アップロードできる WXR XML を生成する。Zenn / Qiita の技術記事とは分け、読者の利用シーン、悩み、作った理由、使いどころを先に出す。

## 基本方針

- 宣伝主目的の記事は note / 個人ブログ向けにする。
- 技術深掘りより、読者が「自分にも関係ある」と判断できる利用シーンを先に書く。
- 過度な売り文句ではなく、何に困って作ったか、何ができるか、注意点を正直に書く。
- GitHub や Chrome Web Store への導線は末尾に置く。
- Zenn / Qiita へ転用する場合は、技術判断や実装の詰まりを主題に組み替える。

## note本文の推奨構成

```markdown
# <読者の困りごとが分かるタイトル>

<困った場面を1〜3段落で書く>

## 作ったもの

<名前と一言説明>

- できること
- 対象URLや対象環境
- 使うと何が楽になるか

## こういうときに使いたい / こういう人向け

<自分の利用シーンと読者像>

## 少しだけ技術的な話

<APIキー不要、外部送信なし、ブラウザ内処理など、読者の安心材料になる範囲だけ>

## 注意点

<制約、対象外、壊れうる点、購入・利用前の確認事項>

## リンク

<GitHub / Chrome Web Store / 関連ページ>
```

## インポート仕様チェック

note のインポート機能を使う原稿・変換作業では、必要に応じて `references/note-import-spec.md` を読む。

最低限チェックすること:

- WXR / MT 形式のどちらにするか決める。
- 文字コードは UTF-8 にする。
- 1ファイル 20MB まで、1回 1000記事までに収める。
- インポート後は記事一覧にテキスト記事として下書き追加される前提で、公開状態を期待しない。
- iframe / 一部文字装飾は再設定が必要になりうる。
- 画像は `http://` または `https://` で始まる JPEG / PNG / GIF の img src を使う。ローカル画像や相対パスは手動再設定前提にする。
- 未来日付や 2014-04-07 12:00 以前の日付は note 側で補正される可能性を明記する。

## WXRファイル生成

Markdown から note インポート用 WXR を作る場合は、`scripts/markdown_to_wxr.py` を使う。note は1回のインポートで複数記事を含む WXR を受け取れるため、複数記事を note 用に生成するときは1つの XML にまとめる。

```powershell
& '<python.exe>' .agents\skills\note-import\scripts\markdown_to_wxr.py `
  note\drafts\note-example.md `
  -o note\import\note-example.xml `
  --slug note-example `
  --date 2026-05-21T21:30:00
```

複数記事を1ファイルにまとめる例:

```powershell
& '<python.exe>' .agents\skills\note-import\scripts\markdown_to_wxr.py `
  note\drafts\article-a.md `
  note\drafts\article-b.md `
  -o note\import\articles.xml `
  --slug article-a `
  --slug article-b `
  --date 2026-05-21T21:30:00
```

実行後に確認すること:

- 出力ファイルの拡張子は `.xml` にする。
- XML 先頭が `<?xml version="1.0" encoding="UTF-8"?>` であること。
- `<content:encoded><![CDATA[...]]></content:encoded>` に本文が入っていること。
- 複数記事の場合は、記事数ぶんの `<item>` があること。
- note インポート後は下書きになる前提で、公開作業は note 側で行うこと。
- Markdown の細かい装飾は完全再現しない。見出し、詰めた段落、箇条書き、太字、インラインコード、裸 URL を基本変換対象にする。
- note 上で段落間の空白が広がりやすいため、通常段落は `<p>` ではなく `<br />` ベースで出力する。

## note向けに避けること

- Zenn の frontmatter を残さない。
- コードブロック中心の構成にしない。必要な場合だけ短く入れる。
- 「ぜひ」「ご参考になれば」などの定型的な締めにしない。
- Chrome / Amazon / YouTube の公式機能であるように見える表現を避ける。
- 読者の個人データや購入判断に関わる機能では、外部送信の有無と注意点を明記する。

## 出力場所

- note 向け単体本文は `note/drafts/<slug>.md` に置く。
- 宣伝素材セットは `note/promo/<slug>.md` に置く。
- note インポートへアップロードする WXR XML は `note/import/<slug>.xml` に置く。
- 複数記事をまとめる WXR XML は `note/import/<batch-name>.xml` に置く。
- Zenn 技術記事とは別管理にし、`articles/` や `drafts/` 直下には置かない。
