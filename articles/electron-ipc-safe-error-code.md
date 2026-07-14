---
title: "ElectronのIPC越しにraw例外を渡すのをやめて汎用エラーコードにした"
emoji: "⚡"
type: "tech"
topics: ["electron", "javascript", "react", "ipc"]
published: true
---

## はじめに

Electron + React で YouTube 配信スケジュール管理アプリを作っている。自動更新やプレイリスト同期のように、メインプロセスで非同期処理を行い結果を renderer に返す場面が多い。

最初は `catch` した例外の `err.message` をそのまま renderer に送っていた。動いているうちは問題なかったが、ネットワーク障害やAPIエラーが起きると、内部URLやスタックトレースの断片がUI上に表示されることがあった。さらに、エラー時に loading 状態が解除されずUIが固まるケースもあった。

この記事では、IPC越しのエラーを汎用コードに丸めた設計と、renderer 側でコードを日本語メッセージに変換する仕組みを書く。

**対象読者**: Electron の IPC でエラーハンドリングを設計している開発者。

**リポジトリ**: [YouTom](https://github.com/harness17/youtom)

## 問題: raw 例外がUI に漏れる

autoUpdater のエラーハンドラを例にする。

```js
// 修正前: err.message をそのまま送っていた
autoUpdater.on('error', (err) => {
  mainWindow.webContents.send('updater:error', err.message)
})
```

`err.message` には GitHub Releases の内部URL、プロキシ設定、ネットワークエラーの詳細が含まれることがある。ユーザーにとっては意味がないし、アプリの内部構造を漏らすセキュリティリスクにもなる。

プレイリスト同期でも同じ問題があった。YouTube API がクォータ超過を返したとき、`err.message` に内部URLやリクエスト詳細が含まれる可能性がある。

## 修正: 汎用エラーコードに丸める

### メインプロセス側

autoUpdater のエラーは汎用コード `UPDATE_CHECK_FAILED` に丸める。

```js
function setupAutoUpdater(mainWindow) {
  if (is.dev) return

  autoUpdater.on('update-available', (info) => {
    mainWindow.webContents.send('updater:update-available', info)
  })
  autoUpdater.on('update-downloaded', (info) => {
    mainWindow.webContents.send('updater:update-downloaded', info)
  })
  autoUpdater.on('error', (err) => {
    // err.message には内部URLやネットワーク詳細が混ざる可能性があるため汎用コードに丸める
    logger?.error('autoUpdater.error', { error: err })
    mainWindow.webContents.send('updater:error', 'UPDATE_CHECK_FAILED')
  })

  autoUpdater.checkForUpdates()
}
```

`logger` にはフルのエラー情報を残し、renderer には定数文字列だけを送る。

IPC ハンドラでも同じパターンを使う。`errorCode()` ユーティリティで `err.code` があればそれを使い、なければフォールバックの定数を返す。

```js
function errorCode(err, fallback) {
  return err?.code ?? fallback
}

ipcMain.handle('playlist:refresh', async () => {
  try {
    const result = await service.refresh()
    if (result.skipped) {
      return {
        error: result.reason === 'not-authenticated'
          ? 'NOT_AUTHENTICATED'
          : 'PLAYLIST_NOT_CONFIGURED'
      }
    }
    return result
  } catch (err) {
    return { error: errorCode(err, 'REFRESH_FAILED') }
  }
})
```

非同期で完了する処理（`setConfig` 後のバックグラウンド同期など）はイベントでエラーを通知する。

```js
service.refresh()
  .then((result) => {
    if (!result?.skipped) mainWindow.webContents.send('playlist:updated', result)
  })
  .catch((err) => {
    mainWindow.webContents.send('playlist:error', {
      message: errorCode(err, 'REFRESH_FAILED')
    })
  })
```

### Renderer 側: コードを日本語メッセージに変換

エラーコードとユーザー向けメッセージの対応表を renderer 側に持つ。

```js
// updaterMessages.js
const UPDATER_ERROR_MESSAGES = {
  UPDATE_CHECK_FAILED: '更新の確認に失敗しました。時間をおいて再試行してください。'
}

export function updaterErrorMessage(codeOrText) {
  return UPDATER_ERROR_MESSAGES[codeOrText] ?? codeOrText
}
```

プレイリスト系はコードが多いので辞書も大きい。

```js
// usePlaylist.js
export const PLAYLIST_ERROR_MESSAGES = {
  NOT_AUTHENTICATED: 'ログインしてください',
  PLAYLIST_NOT_CONFIGURED: '設定からプレイリストを選択してください',
  QUOTA_EXCEEDED: 'YouTube API クォータ上限に達しました。翌日 17:00 (JST) 頃にリセットされます',
  PLAYLIST_NOT_FOUND:
    'プレイリストが削除/非公開化されている可能性があります。設定で再選択してください'
}

export function playlistErrorMessage(payload) {
  const code = playlistErrorCode(payload)
  if (!code) return null
  if (PLAYLIST_ERROR_MESSAGES[code]) return PLAYLIST_ERROR_MESSAGES[code]
  return `同期に失敗しました（${code}）`
}
```

未知のコードが来たら `同期に失敗しました（CODE）` のように表示する。内部情報は出さないが、コードだけは出すのでログ調査時に対応づけできる。

### loading 状態の解除

エラー時に loading が残らないよう、`finally` または catch 内で必ず解除する。

```js
const refresh = useCallback(async () => {
  setLoading(true)
  setError(null)
  try {
    const result = await window.api.refreshSchedule()
    if (result?.error) {
      setError(result.error)
      setLoading(false)
      return result
    }
    await load()
    return result
  } catch (e) {
    setError(e.message ?? 'FETCH_FAILED')
    setLoading(false)
  }
}, [load])
```

`window.api` は preload の `contextBridge` 経由で公開している。IPC チャネル名だけが renderer に見え、メインプロセスの内部モジュールは見えない。

## 判断の整理

| 層 | 扱う情報 | やること |
|----|---------|---------|
| メインプロセス | フルの例外（message, stack, code） | logger に記録し、renderer には汎用コードだけ送る |
| preload | IPC チャネル名 | `contextBridge` で安全な API だけ公開 |
| renderer | 汎用コード | コード→日本語メッセージの辞書で変換。未知コードは `失敗しました（CODE）` |

raw 例外を renderer に渡さない理由は 3 つ。

1. **情報漏洩**: 内部 URL、リクエスト詳細、ファイルパスがユーザーに見える
2. **UI 破壊**: 長大なスタックトレースがレイアウトを壊す
3. **多言語対応**: 例外メッセージは英語。ユーザー向けには日本語で出したい

## まとめ

- メインプロセスで catch した例外は `err.message` をそのまま renderer に送らない
- 汎用エラーコード（`REFRESH_FAILED` 等）に丸め、renderer 側でユーザー向けメッセージに変換する
- エラー時の loading 解除を忘れると UI が固まる。`finally` または `catch` 内で必ず解除する

## 参考リンク

- [YouTom](https://github.com/harness17/youtom) — YouTube 配信スケジュール管理 Electron アプリ
- [Electron contextBridge](https://www.electronjs.org/docs/latest/api/context-bridge)
- [electron-updater](https://www.electron.build/auto-update.html)
