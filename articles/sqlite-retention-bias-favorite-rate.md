---
title: "保持期間が違うデータから「お気に入り率」を出すのをやめた"
emoji: "📊"
type: "tech"
topics: ["sqlite", "electron", "analytics", "javascript"]
published: true
---

## はじめに

Electron + SQLite で YouTube の視聴管理アプリを作っている。v1.24 で「チャンネル別お気に入り傾向」を追加するとき、最初は「お気に入り率」を出そうとした。お気に入り数 ÷ 全動画数で、どのチャンネルの配信をよく保存しているかが分かるはず——だった。

実装してすぐ、お気に入り率がほぼ 100% のチャンネルだらけになった。原因は単純で、非お気に入りの動画は 30 日で自動削除されるのに、お気に入りは永久保持される。分母が勝手に縮むので、率は時間とともに膨らむ一方だった。

この記事では、保持期間が異なるデータで率を計算するとどう壊れるかと、率ではなく件数に切り替えた判断を書く。

**対象読者**: ローカル DB で分析機能を作っている開発者。保持ポリシーの違いが集計を壊す落とし穴を知りたい人。

**リポジトリ**: [YouTom](https://github.com/harness17/youtom)

## 問題：分母が勝手に縮む

アプリのデータ保持ポリシーは以下のとおりだった。

| 種類 | 保持期間 | 根拠 |
|------|---------|------|
| 通常の動画レコード | 30 日 | YouTube Data API のクォータを節約するため、古い配信は定期削除する |
| お気に入り動画 | 永久 | ユーザーが明示的に保存した動画は消さない |

ここで「お気に入り率 = お気に入り数 ÷ 全動画数」を計算すると、こうなる。

```text
1月: お気に入り 5件 / 全30件 = 17%
2月: お気に入り 10件 / 全32件 = 31%  ← 1月の非お気に入り25件は削除済み
3月: お気に入り 15件 / 全29件 = 52%  ← 2月の非お気に入り22件も削除済み
```

実際には毎月同じペースでお気に入りしているのに、率だけ見ると「最近お気に入りが急増した」ように見える。分子（お気に入り）は蓄積される一方、分母（全動画）は 30 日で入れ替わるため、率は必ず上がり続ける。

## 検討した代替案

### 案 1: お気に入りも 30 日で消す

保持期間を揃えれば率は安定する。しかし、お気に入りタブは「後で見返すために保存した動画」の置き場でもあり、30 日で消えるのはユーザー体験として受け入れられない。既存のお気に入りタブもチャンネル削除後に動画を残す契約で動いている。保持ポリシーを分析のために変えるのは本末転倒だった。

### 案 2: 同一 30 日ウィンドウ内で率を計算する

`viewedRate`（視聴済み率）では実際にこの方法を採用している。

```js
const viewedRateStmt = db.prepare(`
  SELECT
    v.channel_id,
    COALESCE(c.title, v.channel_title) AS channel_title,
    COUNT(*) AS total_count,
    SUM(CASE WHEN v.viewed_at IS NOT NULL THEN 1 ELSE 0 END) AS viewed_count,
    MAX(${LIVE_ACTIVITY_AT}) AS last_activity_at
  FROM videos v
  JOIN channels c ON c.id = v.channel_id
  WHERE c.deleted_at IS NULL
    AND c.is_pinned = 1
    AND v.status = 'ended'
    AND ${IS_LIVESTREAM}
    AND ${LIVE_ACTIVITY_AT} >= @since
    AND ${LIVE_ACTIVITY_AT} <= @now
  GROUP BY v.channel_id
  ORDER BY
    CAST(SUM(CASE WHEN v.viewed_at IS NOT NULL THEN 1 ELSE 0 END) AS REAL) / COUNT(*) ASC,
    total_count DESC,
    channel_title COLLATE NOCASE ASC
`)
```

視聴済みフラグは動画と同じ行にあるので、30 日ウィンドウで切れば分母と分子の保持期間が一致する。しかしお気に入りは特定の 30 日間だけで集計しても「傾向」にならない。お気に入りの価値は蓄積量にあるので、期間で切ると一番知りたい情報が落ちる。

### 案 3: 率をやめて件数にする（採用）

お気に入り傾向で知りたいのは「どのチャンネルの配信をよく保存しているか」であって、全配信に対する割合ではない。保存数と視聴済み数の 2 軸で十分だった。

## 実装：期間絞りなし・件数集計

```js
// お気に入りは永久保持され、既存のお気に入りタブもチャンネル削除後に動画を残す。
// その契約に合わせ、期間や channels.deleted_at では絞らず保存中の全件を集計する。
const favoriteChannelsStmt = db.prepare(`
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
`)
```

ポイントは 3 つ。

1. **期間フィルタがない**。`viewedRateStmt` は `@since` で 30 日を切るが、お気に入り集計では使わない。保持期間が永久だから、全件が対象で正しい
2. **`LEFT JOIN channels`** にしている。チャンネルを解除（論理削除）した後もお気に入り動画は残るため、`INNER JOIN` にすると行が消える
3. **率ではなく件数**。`favorite_count` と `viewed_count` を並べて、保存数が多い順に表示する

表示側も率のパーセンテージではなく、件数をそのまま出す。

```js
function rowToFavoriteChannel(row) {
  return {
    channelId: row.channel_id,
    channelTitle: row.channel_title ?? row.channel_id,
    favoriteCount: row.favorite_count,
    viewedCount: row.viewed_count,
    isPinned: row.is_pinned === 1,
    channelUrl: `https://www.youtube.com/channel/${row.channel_id}`
  }
}
```

## 判断の一般化：率を出す前に確認すること

保持期間が異なるデータで率を出そうとしたら、以下を確認する。

| 確認項目 | 問い |
|---------|------|
| 分母の保持期間 | 分母に使うレコードはいつ消えるか |
| 分子の保持期間 | 分子に使うレコードはいつ消えるか |
| 保持期間の一致 | 分母と分子が同じ期間で消えるか |
| 同一ウィンドウ | 両方を同じ期間で切れるか |
| 率の必要性 | そもそも件数ではなく率が必要か |

このアプリでは `viewedRate` は「分母（全配信）と分子（視聴済み）が同じ行にあり、同じ 30 日ウィンドウで切れる」から率が成立する。`favoriteChannels` は「分子（お気に入り）が永久保持、分母（全動画）が 30 日で消える」から率が壊れる。

## まとめ

- 保持期間が異なるデータで率を計算すると、分母の縮小によって率が膨張し続ける
- 同一ウィンドウで切れるなら率は成立する（視聴済み率のケース）。切れないなら件数に切り替える
- 「取れる数字」と「意味のある数字」は違う。率が出せるからといって出すべきとは限らない

## 参考リンク

- [YouTom](https://github.com/harness17/youtom) — YouTube 配信スケジュール管理 Electron アプリ
- [v1.24 視聴傾向インサイト仕様](https://github.com/harness17/youtom/blob/main/docs/superpowers/specs/2026-06-09-v1.24-viewing-insights.md)
