---
title: 保持期間が違うデータでお気に入り率が過大になった
tags:
  - JavaScript
  - SQLite
  - データ分析
  - Electron
private: false
updated_at: '2026-07-03T20:32:24+09:00'
id: 5ffdf65364e64a8a6108
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

お気に入り（永久保持）と通常レコード（30日削除）で「お気に入り率」を出すと、分母が勝手に縮んで率が膨張する。保持期間が違うデータで率を出すときは、同一ウィンドウで切れるか確認し、切れないなら件数に切り替える。

## 起きたこと

Electron + SQLite の YouTube 管理アプリで、チャンネル別の「お気に入り率」を実装した。

```text
お気に入り率 = お気に入り数 ÷ 全動画数
```

結果、ほぼすべてのチャンネルでお気に入り率が 80〜100% になった。

## 原因

データ保持ポリシーの違いが分母を歪めていた。

| 種類 | 保持期間 |
|------|---------|
| 通常の動画レコード | 30 日で自動削除 |
| お気に入り動画 | 永久保持 |

分子（お気に入り）は蓄積され続けるが、分母（全動画）は 30 日で入れ替わる。時間が経つほど率は 100% に近づく。

```text
1月: 5 / 30 = 17%
2月: 10 / 32 = 31%  ← 1月の非お気に入り25件は削除済み
3月: 15 / 29 = 52%  ← 2月も削除済み
```

## 修正

率ではなく件数にした。知りたいのは「どのチャンネルの配信をよく保存しているか」であり、全配信に対する割合ではなかった。

```sql
SELECT
  v.channel_id,
  COALESCE(c.title, v.channel_title) AS channel_title,
  COALESCE(c.is_pinned, 0) AS is_pinned,
  COUNT(*) AS favorite_count,
  SUM(CASE WHEN v.viewed_at IS NOT NULL THEN 1 ELSE 0 END) AS viewed_count
FROM videos v
LEFT JOIN channels c ON c.id = v.channel_id
WHERE v.is_favorite = 1
  AND v.channel_id IS NOT NULL
  AND v.channel_id != ''
GROUP BY v.channel_id
ORDER BY
  favorite_count DESC,
  viewed_count DESC,
  channel_title COLLATE NOCASE ASC
```

期間フィルタを入れていないのは、お気に入りが永久保持だから。同じアプリの「視聴済み率」は分母と分子が同じ 30 日ウィンドウで切れるので率が成立する。

## 確認ポイント

保持期間が異なるデータで率を出す前に確認すること。

- 分母と分子の保持期間は一致するか
- 同じ期間ウィンドウで切れるか
- そもそも率が必要か（件数で十分ではないか）

## 参考

- [YouTom](https://github.com/harness17/youtom) — YouTube 配信スケジュール管理 Electron アプリ
- 関連 Zenn 記事: [保持期間が違うデータから「お気に入り率」を出すのをやめた](https://zenn.dev/harness/articles/sqlite-retention-bias-favorite-rate)
