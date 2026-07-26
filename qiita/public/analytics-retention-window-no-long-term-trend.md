---
title: SQLiteの30日ウィンドウ集計から月次トレンドを出すのを止めた話
tags:
  - SQLite
  - Electron
  - データ分析
  - JavaScript
private: false
updated_at: '2026-07-26T13:16:48+09:00'
id: 2d93763423640c4d89e3
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

直近30日のローリング集計は「現在の傾向」には使えるが、その値を月次トレンドとして並べると集計対象期間がずれる。YouTomでは、視聴済み率と未視聴蓄積を30日集計のまま表示し、長期推移は作らなかった。

```js:statsRepository.js
const viewedRates = viewedRateStmt
  .all({ since: now - 30 * DAY_MS, now })
  .map(rowToViewedRate)
const unviewedBacklog = unviewedBacklogStmt
  .all({ since: now - 30 * DAY_MS, now })
  .map(rowToUnviewedBacklog)
```

## 再現条件

Electron + SQLite のYouTube配信管理アプリ [YouTom](https://github.com/harness17/youtom) v1.24.0で、次の2分析を追加した。

- **視聴済み率**: 直近30日に終了した配信のうち、視聴済みにした割合
- **未視聴蓄積**: 直近30日に終了した、ピン留めチャンネルの未視聴配信数

どちらも `getChannelActivity(now)` の `now` を基準に、`now - 30 * DAY_MS` 以降をSQLへ渡す。ここから「先月より視聴率が上がったか」という月次推移も出そうとした。

## 原因

30日ウィンドウは、カレンダー月ではなく実行日から遡るローリング期間である。

| 集計日 | 対象期間 | 月次比較で欠ける部分 |
| --- | --- | --- |
| 7月15日 | 6月15日〜7月15日 | 6月前半 |
| 8月15日 | 7月16日〜8月15日 | 7月前半 |

同じ「7月」の値を作るつもりでも、7月末に集計するか8月中旬に集計するかで、残っている対象期間が変わる。これはSQLのウィンドウ関数の問題ではなく、集計へ渡す `since` の設計によるものだった。

また、YouTomのすべてのインサイトが30日集計ではない。`favoriteChannelsStmt` は期間制限なし、配信頻度ランキングは90日で集計する。保持・集計範囲が異なる値を一律に「月次」として並べないよう、この記事の対象を30日の2分析に限定した。

## 見送った判断

| 選択肢 | 判断 |
| --- | --- |
| 30日集計をそのまま日次保存する | 数字は残るが、「その日から遡った30日」という意味を失いやすい |
| カレンダー月ごとの集計テーブルを追加する | 比較可能になるが、保持期間・マイグレーション・既存データ不足を先に決める必要がある |
| 30日集計を現在の傾向だけに使う | 採用。現在あるデータで説明できる範囲に限定する |

お気に入り数と通常動画数のように保持期間が違うデータから率を出さない判断は、Zenn記事「[保持期間が違うデータから『お気に入り率』を出すのをやめた](https://zenn.dev/harness/articles/sqlite-retention-bias-favorite-rate)」へ分けた。この記事では、ローリング期間と月次期間の違いだけを扱う。

## 確認方法

境界は `statsRepository.test.js` で固定時刻を使って確認した。

- 29日前と30日前の配信は視聴済み率・未視聴蓄積へ含まれる
- 31日前の配信は含まれない
- 期間制限なしのお気に入り集計は、30日分析と別のテストで確認する

このテストにより「30日」の境界は再現できる。ただし月次スナップショットを保存していない以上、長期推移を後から復元できるとは扱わない。

### 参考

- [YouTom](https://github.com/harness17/youtom) — 30日境界のRepository実装とテスト
- [SQLite Date And Time Functions](https://www.sqlite.org/lang_datefunc.html) — SQLiteの日付・時刻処理の公式資料
