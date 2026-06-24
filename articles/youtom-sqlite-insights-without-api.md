---
title: "Electron個人開発アプリで既存SQLiteだけの分析機能を追加した話"
emoji: "📊"
type: "tech"
topics: ["electron", "sqlite", "javascript", "react"]
published: true
---

## はじめに

YouTube 配信スケジュール管理の Electron アプリを個人開発している。v1.24 で「視聴傾向の分析タブ」を追加した。新しい API 呼び出しも、OAuth スコープの追加も、DB マイグレーションも使わずに、既にローカル SQLite に貯まっていたデータだけで 4 種類のインサイトを出せた。

この記事では、既存テーブルから分析を引き出す設計と、「追加コストゼロ」で機能追加するための判断を書く。

**対象読者**: Electron + SQLite で個人開発しており、既存データの活用を考えている開発者。

**リポジトリ**: [YouTom](https://github.com/harness17/youtom)

## 背景: ローカルに貯まっていたデータ

このアプリは YouTube Data API を使って、登録チャンネルの配信スケジュールを取得・表示している。取得したデータはローカルの SQLite に保存される。

| テーブル | 主な内容 |
|---------|---------|
| `channels` | チャンネル名、ピン留め状態（`is_pinned`） |
| `videos` | 配信情報、視聴済みフラグ（`viewed_at`）、お気に入りフラグ（`is_favorite`） |

v1.23 までは「今日の配信」「予定一覧」の表示が主な用途だった。ここに「このチャンネルどのくらい見てる？」「お気に入りに偏りはある？」のようなインサイトを追加したかった。

### なぜ API を増やさなかったか

YouTube Data API にはクォータ上限がある（10,000ユニット/日）。分析のために追加の API 呼び出しをすると、日常の配信取得と競合してクォータ枯渇のリスクが上がる。既に手元の SQLite にデータがあるなら、ローカルで集計するほうが安全で速い。

OAuth スコープの追加も避けたかった。現状 `youtube.readonly` だけで動いており、スコープを増やすと再認証が必要になる。

## 実装した 4 つのインサイト

すべて `statsRepository.js` の SQL で完結する。IPC ハンドラ `stats:channelActivity` 1つで 4 つのクエリ結果をまとめて返す。

### 1. よく見る推し（視聴済み率）

ピン留めしたチャンネルについて、過去 30 日の配信のうち何割を視聴済みにしたかを計算する。

```sql
SELECT
  c.name AS channelName,
  COUNT(*) AS totalCount,
  SUM(CASE WHEN v.viewed_at IS NOT NULL THEN 1 ELSE 0 END) AS viewedCount,
  ROUND(
    SUM(CASE WHEN v.viewed_at IS NOT NULL THEN 1 ELSE 0 END) * 100.0 / COUNT(*),
    1
  ) AS viewedRate
FROM videos v
JOIN channels c ON c.channel_id = v.channel_id
WHERE c.is_pinned = 1
  AND v.status = 'ended'
  AND v.scheduled_at >= ?   -- now - 30日
GROUP BY v.channel_id
ORDER BY viewedRate ASC
```

視聴率が低い順に並べるのは、「意外と見てないチャンネル」を発見しやすくするため。

### 2. 未視聴蓄積

過去 30 日で `viewed_at IS NULL` の配信が多いチャンネルを表示する。

```sql
SELECT
  c.name AS channelName,
  COUNT(*) AS unviewedCount,
  MIN(v.scheduled_at) AS oldestActivity
FROM videos v
JOIN channels c ON c.channel_id = v.channel_id
WHERE v.viewed_at IS NULL
  AND v.status = 'ended'
  AND v.scheduled_at >= ?
GROUP BY v.channel_id
ORDER BY unviewedCount DESC
```

「未視聴が溜まっている」ことに気づけるだけで、ピン留め整理のきっかけになる。

### 3. 頻度 x 視聴済み率（2x2 マトリクス）

配信頻度と視聴率を 2 軸で分類する。

| | 視聴率 ≥ 50% | 視聴率 < 50% |
|---|---|---|
| **配信 ≥ 4件/月** | よく見るアクティブ | 配信多いが見てない |
| **配信 < 4件/月** | たまに見る | 低頻度・低視聴 |

閾値はハードコードしている。

```jsx
const isFrequent = ch.totalCount >= 4
const isWatched = ch.viewedRate >= 50
```

4 件と 50% は実データで試して「体感と一致した」値を採用した。個人ツールなので、設定画面で変えられるようにするより、まず固定値で使い勝手を確かめるほうが早かった。

### 4. お気に入り傾向

お気に入りに登録した配信のチャンネル分布を出す。

```sql
SELECT
  c.name AS channelName,
  COUNT(*) AS favoriteCount
FROM videos v
LEFT JOIN channels c ON c.channel_id = v.channel_id
WHERE v.is_favorite = 1
GROUP BY v.channel_id
ORDER BY favoriteCount DESC
```

このクエリだけ 30 日の期間フィルタがない。お気に入りは永久保持する設計にしているため、全期間で集計する。非お気に入りの配信は 30 日でクリーンアップされるが、お気に入りはクリーンアップ対象外になっている。

この非対称性については別の記事（[SQLiteの保持期間バイアスがお気に入り率の分母を狂わせた話](https://zenn.dev/harness/articles/sqlite-retention-bias-favorite-rate)）で詳しく書いた。

## 追加コストゼロの内訳

v1.24 で増えたもの・増えなかったものを整理する。

| 項目 | 増えた？ | 理由 |
|------|---------|------|
| API 呼び出し | ❌ | SQLite のローカルクエリだけで完結 |
| OAuth スコープ | ❌ | `youtube.readonly` のまま |
| DB マイグレーション | ❌ | 既存の `videos` / `channels` テーブルをそのまま使用 |
| IPC チャネル | ✅ 1つ | `stats:channelActivity` ハンドラを追加 |
| renderer コンポーネント | ✅ | `StatsTab.jsx` + `useStats` hook |

マイグレーションなしは偶然ではなく、v1.0 の時点で `viewed_at`、`is_favorite`、`is_pinned` を入れていたから。当時は分析のためではなく、視聴管理とお気に入り機能のために追加したカラムだった。

## IPC の設計

分析タブを開いたときに 1 回だけ呼ぶ。4 つのクエリをメインプロセスで同期的に実行し、まとめて返す。

```js
// statsHandlers.js
ipcMain.handle('stats:channelActivity', () => {
  const repo = getStatsRepo()
  if (!repo) return { dbBroken: true }
  return repo.getChannelActivity()
})
```

`getChannelActivity()` は 4 つの SQL を順に実行して結果をまとめたオブジェクトを返す。SQLite の同期アクセスなので、4 クエリ合計でも数十ミリ秒で終わる（登録チャンネル数十件の規模）。

renderer 側は `useStats` フックで呼び出し、ローディング中は既存の loading 表示パターンを使う。DB が壊れている場合は `dbBroken: true` を返し、UI で「データベースに問題があります」と表示する。

## 判断の一般化

既存データから機能を追加するとき、3つの判断基準を使った。

**1. スキーマに手を入れないで済むか**

既存カラムの組み合わせで必要な集計が出せるなら、マイグレーションは不要。マイグレーションを追加するとアップデート時の互換性リスクが増える。

**2. 外部 API を叩かないで済むか**

ローカルデータで完結するなら、クォータ・レート制限・ネットワーク障害の心配がない。分析機能がメインの配信取得を邪魔しない。

**3. 閾値はハードコードで始める**

個人ツールでは、設定 UI を作るコストより「固定値で試して合わなかったら直す」ほうが早い。設定が必要になるのは、利用者が複数いるか、自分の使い方が頻繁に変わるときだけ。

## まとめ

- 既存 SQLite のデータだけで 4 種類の視聴傾向分析を実装した
- API 呼び出し、OAuth スコープ、DB マイグレーションの追加はゼロ
- 個人ツールの閾値はハードコードから始め、実データで確認してから設定化を検討する

## 参考リンク

- [YouTom](https://github.com/harness17/youtom) — YouTube 配信スケジュール管理 Electron アプリ
- [SQLiteの保持期間バイアスがお気に入り率の分母を狂わせた話](https://zenn.dev/harness/articles/sqlite-retention-bias-favorite-rate) — 関連する設計判断の記事
- [better-sqlite3](https://github.com/WiseLibs/better-sqlite3) — Node.js 用 SQLite バインディング
