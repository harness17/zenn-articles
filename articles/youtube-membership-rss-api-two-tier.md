---
title: "YouTubeメンバー限定配信をRSSと手動登録の二段構えで追跡した話"
emoji: "🔒"
type: "tech"
topics: ["youtube", "electron", "api", "nodejs", "indie"]
published: true
---

## はじめに

[YouTom](https://github.com/harness17/youtube-schedule) は、YouTube の登録チャンネルの配信予定・ライブ中の動画を一覧表示する Windows デスクトップアプリです。配信予定の取得は、もともと YouTube Data API の `search.list` で実装していましたが、クォータ消費が大きすぎたため RSS フィードに切り替えました（[別記事](https://zenn.dev/harness/articles/youtube-data-api-rss-quota-reduction) で書きました）。

ところが RSS に切り替えた後、**メンバー限定（メン限）配信だけが一覧に出てこない** ことに気づきました。この記事は、メン限配信を「自動取得ルートに無理に乗せる」のではなく、**手動登録という別系統に分けた** 判断と、その実装をまとめたものです。

- 対象読者: YouTube Data API と RSS を併用して、クォータ上限内で配信情報を取得したい個人開発者
- 前提: YouTube Data API のクォータは 1 日 10,000 ユニット。`search.list` は 1 回 100 ユニット、`videos.list` は 50 件まで 1 ユニット、RSS フィードはクォータ消費 0
- この記事で分かること: 自動取得できないデータを、無理にAPIで取りに行かず別ルートに切り分ける設計判断

なぜこれが問題になるかというと、推しのメン限配信を見逃さないことがアプリの存在価値だからです。一覧に出ない配信があると、アプリの目的そのものが崩れます。

## メン限配信は自動取得ルートに出てこない

YouTom の自動取得は2つの経路を使っています。

1. 登録チャンネルの列挙: `subscriptions.list`
2. 各チャンネルの新着動画: チャンネルの RSS フィード

```js
// src/main/fetchers/subscriptionsFetcher.js（抜粋）
export function createSubscriptionsFetcher() {
  return {
    async fetch(yt) {
      const channels = []
      let pageToken = undefined
      do {
        const res = await yt.subscriptions.list({
          part: ['snippet'],
          mine: true,
          maxResults: 50,
          pageToken
        })
        for (const item of res.data.items || []) {
          const id = item.snippet?.resourceId?.channelId
          if (!id) continue
          channels.push({ id, title: item.snippet.title ?? null, uploadsPlaylistId: 'UU' + id.slice(2) })
        }
        pageToken = res.data.nextPageToken
      } while (pageToken)
      return channels
    }
  }
}
```

問題は、メン限配信が **どちらの経路にも現れない** ことでした。RSS フィードはチャンネルの公開動画しか含まず、メンバー特典の動画は非メンバーから見えないため出てきません。`subscriptions.list` はチャンネルの列挙であって、メン限動画を返す API でもありません。

つまり「登録チャンネル → 新着動画」という自動取得の枠組みの中には、メン限配信を拾う場所が構造的に存在しませんでした。

## 捨てた選択肢: search.list で全件取得し直す

最初に考えたのは「RSS をやめて `search.list` に戻し、メン限も含めて全部取り直す」案でした。これは却下しました。理由はクォータです。

`search.list` は 1 回 100 ユニット。登録チャンネルが 30 あって 2 時間ごとに自動更新すると、

```
100 ユニット × 30 チャンネル × 12 回/日 = 36,000 ユニット/日
```

1 日の上限 10,000 ユニットを軽く超えます。そもそも `search.list` のクォータ消費を避けるために RSS へ移行したので、メン限のために `search.list` を呼び戻すのは本末転倒でした。

「メン限は登録チャンネル数に対してごく少数なのに、その少数のために全件取得のコストを払う」という構造が間違っていると判断しました。

## 自動検出できないものは手動登録ルートに分ける

そこで方針を変えました。**自動で見つけられないものを自動取得の枠組みに押し込むのをやめ、URL / ID を手動で登録する別系統を用意する** ことにしました。

```js
// src/main/services/schedulerService.js（抜粋）
// URL/ID で指定された動画を手動登録する。メンバー限定配信など
// RSS・購読 API で自動検出できない動画を追跡対象に加えるために使う。
async function addManualVideo(input) {
  const videoId = resolveVideoId(input)
  if (!videoId) return { ok: false, error: 'INVALID_INPUT' }
  if (!authClient) return { ok: false, error: 'NOT_AUTHENTICATED' }

  const yt = ytFactory(authClient)
  let details
  try {
    details = await videoFetcher.fetch(yt, [videoId]) // videos.list（1ユニット/50件）
  } catch (err) {
    logger.error('scheduler.addManualVideo.error', { videoId, error: err })
    return { ok: false, error: 'FETCH_FAILED' }
  }
  const item = details.find((v) => v.id === videoId)
  if (!item) {
    // 動画が存在しない / 非公開 / メンバーでないため取得不可
    return { ok: false, error: 'NOT_FOUND' }
  }
  const record = {
    ...toVideoRecord(item, Date.now()),
    isMembershipOnly: true,
    source: 'manual'
  }
  videoRepo.upsert(record)
  return { ok: true, video: videoRepo.getById(videoId) }
}
```

ポイントは取得手段です。手動登録では `videos.list`（`videoFetcher.fetch`）を使います。これは ID 指定で 50 件まで 1 ユニットなので、`search.list` の 100 ユニットと比べて圧倒的に安く済みます。ユーザーがメン限配信の URL を貼った 1 件だけを取りに行くので、クォータをほとんど消費しません。

レコードには `source: 'manual'` と `isMembershipOnly: true` を持たせます。これで「どの経路で入ってきた動画か」を後から区別できます。

```js
// videoRepository.upsert（抜粋）— source と membership フラグを保持
isMembershipOnly: video.isMembershipOnly ? 1 : 0,
source: video.source ?? 'api'
```

`videos.list` は本人のメンバーシップ権限を持つ認証クライアントで叩くため、メンバーであれば詳細が取れ、非メンバーだと `NOT_FOUND` 相当になります。「取れなかった理由」をユーザーに返せるのも、手動登録ルートに分けた副次的な利点でした。

## 登録後は自動ルートと同じ追跡に乗せる

手動登録は「入口」を分けただけで、登録後の追跡は自動取得の動画と同じ仕組みに合流させます。配信開始直前と配信中の動画は、軽量ポーラーが `videos.list` で再問い合わせして状態遷移を検出します。

```js
// src/main/services/imminentPoller.js（先頭コメント）
// 配信開始直前の動画と現在 live の動画だけを短い間隔で videos.list に再問い合わせて
// upcoming → live → ended の遷移を即時検出する軽量ポーラー。
// クォータ: videos.list は 50 件まで 1 ユニット。対象ゼロのときは API を呼ばない。
```

入口（取得経路）は2系統に分けつつ、出口（状態追跡・通知）は1系統に統一する。これにより、メン限配信もメンバー限定バッジを付けたうえで、通常配信と同じ一覧・同じ通知に乗せられました。

## まとめ

- メン限配信は RSS にも `subscriptions.list` にも出てこない。自動取得の枠組みには構造的に拾う場所がなかった
- `search.list` で全件取り直すとクォータが破綻する。少数のために全件コストを払う設計は間違いと判断した
- 自動検出できないものは、URL/ID の **手動登録ルート**（`videos.list` で 1 件取得・`source: 'manual'`）に分離した。入口は2系統、出口（追跡・通知）は1系統に統一した

「取れないものを無理に自動化の枠に押し込まない」という切り分けは、外部 API のクォータと付き合ううえで何度か効いた判断でした。次は、登録した配信の開始通知を「状態遷移のときだけ」出す実装を別記事で書きます。

## 参考リンク

- リポジトリ: [youtube-schedule (YouTom)](https://github.com/harness17/youtube-schedule)
- 関連記事: [YouTube Data API のクォータ枯渇を RSS で削減した話](https://zenn.dev/harness/articles/youtube-data-api-rss-quota-reduction)
- [YouTube Data API v3 — Quota and Cost](https://developers.google.com/youtube/v3/determine_quota_cost)
