# note 公開記事ログ

note 公開済み記事と、ローカル下書き・インポートXMLの対応を管理する。

最終確認: 2026-05-22
確認元: https://note.com/harness_ / note creator contents API

## 公開記事

| 公開日時 | slug | タイトル | URL | ローカル下書き | インポートXML | 状態 |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-05-22 12:57 JST | `ai-job-hunting-as-social-game` | AI使った就活がソシャゲじみてきた。 | https://note.com/harness_/n/n432c467dd3e2 | `note/drafts/ai-job-hunting-as-social-game.md` | `note/import/ai-job-hunting-as-social-game.xml` | 公開確認 |
| 2026-05-21 22:11 JST | `youtom-introduction` | YouTube の配信予定を見逃しやすいので、Youtom というWindowsアプリを作った | https://note.com/harness_/n/n7e280ad6914f | `note/drafts/youtom-introduction.md` | `note/import/youtom-introduction.xml` | 公開確認 |
| 2026-05-21 21:40 JST | `youtube-playlist-date-sorter` | YouTube のプレイリストを投稿日順で追いたくて Chrome 拡張を作った | https://note.com/harness_/n/nc40f8dfc014b | `note/drafts/youtube-playlist-date-sorter.md` | `note/import/youtube-playlist-date-sorter.xml` | 公開確認 |
| 2026-05-21 21:36 JST | `amazon-wishlist-sale-picker` | Amazon の欲しいものリストからセール中の商品だけ見たくて Chrome 拡張を作った | https://note.com/harness_/n/n14df4e9af8cc | `note/drafts/amazon-wishlist-sale-picker.md` | `note/import/amazon-wishlist-sale-picker.xml` | 公開確認 |

## 確認時メモ

- `ai-job-hunting-as-social-game`: note API 上の status は `published`、price は `0`、likeCount は `0`、commentCount は `0`。
- 2026-05-22 時点で note 側の公開記事は上記4件。

## 更新ルール

- note に公開したら、このファイルに公開日時、タイトル、URL、元下書き、インポートXMLを追記する。
- 公開確認は `https://note.com/harness_` または `https://note.com/api/v2/creators/harness_/contents?kind=note&page=1` で行う。
- note の記事本文は `note/drafts/`、インポート用 WXR は `note/import/` に残す。
