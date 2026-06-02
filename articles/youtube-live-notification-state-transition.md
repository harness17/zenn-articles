---
title: "YouTubeライブ開始通知を状態遷移のときだけ出す実装にした"
emoji: "🔔"
type: "tech"
topics: ["youtube", "react", "electron", "notification", "indie"]
published: true
---

## はじめに

[YouTom](https://github.com/harness17/youtube-schedule) は、YouTube の配信予定とライブ中の動画を追う Windows デスクトップアプリです。配信予定の5分前と、配信が live に変わったときにデスクトップ通知を出します。

最初に詰まったのは、**アプリ起動時に既に live の動画まで「いま始まった」と扱ってしまう** ことでした。DB から復元された live 動画が複数あると、起動直後に通知が連続で出ます。ユーザーから見ると「新規の開始通知」ではなく、過去状態の読み込みノイズです。

この記事では、現在状態をそのまま通知するのではなく、初回読み込み時に baseline を作り、その後に known 集合へ入っていない ID だけ通知する実装をまとめます。

- 対象読者: React / Electron で状態変化に応じた通知を出している個人開発者
- 前提: YouTube の動画状態は `upcoming` / `live` / `ended` のように変わる。DB 復元直後の live は新規開始とは限らない
- この記事で分かること: 「現在 live か」ではなく「今回 live へ遷移したか」で通知を出す判断

## 課題: 現在状態をそのまま通知すると起動時に暴発する

通知条件を素直に書くと、`live` 配列に入っている動画へ通知を出したくなります。

```js
for (const item of live) {
  if (!item.isNotify) continue
  window.api?.showNotification?.(
    '配信が始まりました',
    `${item.channelTitle}「${item.title}」がライブ配信を開始しました`
  )
}
```

しかし、この書き方だと「今 live である」ことと「たった今 live へ変わった」ことを区別できません。

YouTom はアプリ起動後に DB から動画一覧を復元します。前回終了時点で live だった動画や、バックグラウンド中に live へ変わっていた動画も、起動直後の `live` 配列に入ります。ここでそのまま通知すると、ユーザーはアプリを開いただけなのに「配信が始まりました」が連続で出ます。

最初はこの「現在状態を通知する」寄りの考え方で実装していました。実際に使うと、起動時の通知連打がノイズになり、通知の信頼度が落ちました。必要だったのは live 一覧の通知ではなく、**live へ入った差分だけの通知**でした。

## 判断: 初回 live 集合を baseline として扱う

そこで、通知判定を次の3段階に分けました。

1. `initialLoaded` が `false` の間は baseline を確立しない
2. 初回ロード後の live 集合を `liveBaselineSyncedRef` で baseline として保存し、通知しない
3. それ以降は `knownLiveIdsRef` に入っていない ID だけ通知する

実コードは `src/renderer/hooks/useNotificationCheck.js` に置いています。

```js
const notifiedRef = useRef(new Set())
const knownLiveIdsRef = useRef(new Set())
const liveNotifiedRef = useRef(new Set())
const liveBaselineSyncedRef = useRef(false)

useEffect(() => {
  if (!isAuthenticated) {
    knownLiveIdsRef.current = new Set()
    liveBaselineSyncedRef.current = false
    return
  }

  // 初回ロードが完了するまでは baseline を確立しない。
  // 空配列の初期状態を baseline にしてしまうと、その直後に DB から
  // 復元された live が「新規開始」と誤判定され通知が暴発する。
  if (!initialLoaded) return

  const currentLiveIds = new Set(live.map((item) => item.id))
  if (!liveBaselineSyncedRef.current) {
    knownLiveIdsRef.current = currentLiveIds
    liveBaselineSyncedRef.current = true
    return
  }

  for (const item of live) {
    if (!item.isNotify) continue
    if (knownLiveIdsRef.current.has(item.id)) continue
    if (liveNotifiedRef.current.has(item.id)) continue
    liveNotifiedRef.current.add(item.id)
    window.api?.showNotification?.(
      '配信が始まりました',
      `${item.channelTitle}「${item.title}」がライブ配信を開始しました`
    )
  }

  knownLiveIdsRef.current = currentLiveIds
}, [live, isAuthenticated, initialLoaded])
```

ここで重要なのは、空配列を baseline にしないことです。

React の初期レンダー時点では、まだ DB から live 一覧が復元されていないことがあります。この時点の `live = []` を baseline として保存すると、その直後に復元された live は全て「known に無い ID」と見なされます。結果として、DB 復元データが新規開始扱いになります。

そのため、`initialLoaded` が `false` の間は何もしません。初回ロードが終わってから最初に見えた live 集合を baseline として保存し、その回は通知せずに返します。

## 実装のポイント

通知対象は `item.isNotify` が `true` の動画だけにしています。ユーザーが通知を切った動画は、live へ遷移しても通知しません。

また、`liveNotifiedRef` で同じ live に対する二重通知を止めています。`knownLiveIdsRef` は「既に live 集合にいたか」を表す集合で、`liveNotifiedRef` は「通知済みか」を表す集合です。役割を分けておくと、再レンダーや一覧更新があっても同じ ID へ何度も通知しません。

`isAuthenticated` が `false` になったときは `knownLiveIdsRef` と `liveBaselineSyncedRef` を初期化します。認証状態が変わると、取得できる動画の前提も変わるためです。前のセッションの baseline を持ち越すと、次の認証後に通知漏れや誤通知の原因になります。

## 5分前リマインダーは別の useEffect に分ける

ライブ開始通知とは別に、配信開始前のリマインダーもあります。こちらは「状態遷移」ではなく、現在時刻と `scheduledStartTime` の差分で判定します。

同じ通知でも条件が違うため、別の `useEffect` に分けています。

```js
useEffect(() => {
  if (!isAuthenticated) return
  const id = setInterval(() => {
    const now = Date.now()
    const threshold = reminderMinutesRef.current * 60 * 1000
    for (const item of upcomingRef.current) {
      if (!item.isNotify) continue
      if (notifiedRef.current.has(item.id)) continue
      const start = new Date(item.scheduledStartTime).getTime()
      const remaining = start - now
      if (remaining > 0 && remaining <= threshold) {
        notifiedRef.current.add(item.id)
        window.api?.showNotification?.(
          'もうすぐ配信開始',
          `${item.channelTitle}「${item.title}」が${reminderMinutesRef.current}分後に始まります`
        )
      }
    }
  }, 60 * 1000)
  return () => clearInterval(id)
}, [isAuthenticated])
```

ここでは `setInterval(60 * 1000)` で1分ごとに確認し、`scheduledStartTime` と現在時刻を比較します。`upcomingRef` を使っているのは stale closure 対策です。interval のコールバックは初回マウント時の値を持ち続けるため、最新の `upcoming` は ref 経由で読むようにしています。

ライブ開始通知と5分前リマインダーを同じ条件に混ぜると、baseline の話と時刻比較の話が絡みます。片方は「状態集合の差分」、もう片方は「時刻のしきい値」です。判定軸が違うものは別 effect に分けた方が読みやすくなりました。

## 検証と使いどころ

確認したい挙動は次の4つです。

- アプリ起動直後、DB から復元された既存 live には通知しない
- 初回ロード後に新しく live へ入った動画だけ通知する
- `item.isNotify` が `false` の動画は通知しない
- 同じ live に対して再レンダーや一覧更新で二重通知しない

この考え方は、YouTube に限らず「現在状態」と「状態遷移」を区別したい通知に使えます。

たとえば、サービス監視で「現在 down のサービス」を起動時に全部通知すると、既知の down 状態まで新規アラートになります。チャット通知でも、未読一覧の読み込みと新着メッセージ通知を混ぜると、起動時に過去メッセージが通知されます。

状態通知では、最初に見えた状態を baseline として扱い、以降の差分だけ通知するかを先に決める必要があります。

## まとめ

- 現在 live の動画をそのまま通知すると、DB 復元済みの既存 live まで新規開始扱いになり、起動時に通知が連続で出る
- `initialLoaded` が終わるまで baseline を作らず、初回 live 集合は `liveBaselineSyncedRef` で baseline として保存して通知しない
- 以降は `knownLiveIdsRef` に無い ID だけ通知し、`item.isNotify` と `liveNotifiedRef` で通知対象と二重通知を制御する
- 5分前リマインダーは別 `useEffect` で、`scheduledStartTime` と現在時刻の差分から判定する

通知で大事なのは「その状態か」ではなく「その状態に変わったか」でした。起動時の状態復元と新規イベントを分けるだけで、通知のノイズを大きく減らせました。

## 参考リンク

- リポジトリ: [youtube-schedule (YouTom)](https://github.com/harness17/youtube-schedule)
- 関連記事: [YouTubeメンバー限定配信をRSSと手動登録の二段構えで追跡した話](https://zenn.dev/harness/articles/youtube-membership-rss-api-two-tier)
- [React Docs - Referencing Values with Refs](https://react.dev/learn/referencing-values-with-refs)
- [MDN - setInterval()](https://developer.mozilla.org/docs/Web/API/Window/setInterval)
