---
title: Claude CodeからCodexをMCP経由で呼ぶ最小設定で詰まったこと
tags:
  - AI
  - ClaudeCode
  - codex
  - MCP
  - 開発環境
private: false
updated_at: '2026-06-02T22:00:05+09:00'
id: 996fec8e78a219b5159b
organization_url_name: null
slide: false
ignorePublish: false
---

## 詰まったこと

Claude Code で設計を詰めたあと、実装だけ Codex に委譲したい場面がありました。毎回別ターミナルで Codex を起動して、作業範囲や禁止事項を手で貼ると漏れます。

そこで Claude Code から Codex を MCP サーバとして呼ぶ設定を入れました。詰まったのは、MCP の JSON そのものよりも、**Codex CLI の実体、作業ディレクトリ、sandbox / approval policy の前提が曖昧なまま呼び出してしまう** 点でした。

この記事では、1記事1トラブルとして「Claude Code から Codex を叩く最小設定」に絞ります。Codex 側にどんな仕事をさせるか、レビューをどう返すかの設計論は別記事に分けます。

## 結論: .mcp.json は最小でよい

このリポジトリでは、プロジェクトルートに次の `.mcp.json` を置いています。

```json
{
  "mcpServers": {
    "codex": {
      "command": "codex",
      "args": ["mcp-server"]
    }
  }
}
```

設定自体はこれだけです。Claude Code はこの定義から `codex` という MCP サーバを見つけ、`codex mcp-server` を起動します。

ポイントは、ここに作業ルールを詰め込まないことです。`.mcp.json` は「どのコマンドで MCP サーバを起動するか」だけを持たせます。実装範囲、禁止事項、検証コマンドは、呼び出す側の skill や依頼文で固定します。

## 呼び出す前に見るチェックリスト

自分の運用では、Codex を呼ぶ前に次を確認します。

```text
Codex MCP 呼び出し前チェック:
- codex CLI が PATH から起動できる
- Claude Code を対象リポジトリのルートで起動している
- Codex に渡す依頼文に cwd / 対象ファイル / 触らない範囲を書いている
- sandbox は workspace-write を基本にする
- 追加権限が必要なら approval policy で止める前提にする
- git add / commit / push は Codex にさせない
```

MCP サーバ登録だけだと、Codex は「呼べる」状態になります。ただ、呼べることと、狙った作業だけを任せられることは別です。

特に `cwd` は明示します。Claude Code をプロジェクトルートで起動していないと、Codex 側が別のディレクトリを前提に動くことがあります。依頼文には次のように書いています。

```text
対象リポジトリのルートを cwd として作業してください。
作業範囲は次のファイルに限定してください。
- src/main/services/exampleService.js
- src/main/services/exampleService.test.js

実装後に npm test を実行し、結果を報告してください。
git add / git commit / git push は実行しないでください。
```

## ハマりどころ1: codex CLI が PATH に無い

最初の失敗は、Claude Code 側から見た `codex` コマンドが見つからないことでした。自分のターミナルでは動いていても、Claude Code が起動する環境では PATH が違うことがあります。

この場合、`command` に絶対パスを書きたくなりますが、公開リポジトリにローカル絶対パスを置くと環境依存になります。まずはインストール先と PATH を直し、公開設定は次のように保つ方針にしました。

```json
{
  "mcpServers": {
    "codex": {
      "command": "codex",
      "args": ["mcp-server"]
    }
  }
}
```

もう1つの落とし穴は、PATH には `codex` があるのに、実体が壊れているケースです。ローカル確認で `codex --help` を実行したところ、Node の shim が参照先を見つけられず失敗する状態がありました。この場合も `.mcp.json` の問題ではなく、Codex CLI のインストール状態の問題として切り分けます。

## ハマりどころ2: sandbox と approval policy を曖昧にする

Codex に実装を任せるとき、最初から広い権限を渡すと事故が起きます。一方で、権限が足りないと必要なコマンドで止まります。

自分の運用では、基本は次の考え方にしました。

```text
sandbox:
- 通常の編集: workspace-write
- 調査のみ: read-only 相当
- 外部サービスや危険なファイル操作が必要: いったん停止

approval policy:
- 追加権限が必要なコマンドは理由を出して止める
- ネットワーク、外部サービス、danger-full-access は自動で進めない
```

MCP サーバ登録の JSON には、この判断を全部書きません。代わりに、Codex に渡す依頼文で「追加権限が必要なら止めて理由を報告する」と明記します。

```text
ネットワーク、外部サービス、追加権限、danger-full-access が必要になった場合は作業を止め、
必要な理由と未完了範囲を報告してください。
```

これで、Codex が勝手に権限を広げるのではなく、ユーザー判断に戻せます。

## ハマりどころ3: 実装委譲とレビュー委譲を混ぜる

Claude Code から Codex を呼ぶ用途は、実装委譲に絞りました。

逆に、Codex から Claude Code を呼ぶときは review-only にします。両方が同じ worktree で実装し始めると、差分の所有者が分からなくなります。

そのため、Codex に渡す依頼は次の形に寄せています。

```text
あなたは実装担当です。
設計済みの計画に沿って、チェックボックス順に実装してください。
作業範囲は計画ファイルに書かれたファイルと責務に限定してください。
実装後に可能な範囲で verify を実行し、結果を報告してください。
git add / git commit / git push は実行しないでください。
```

MCP サーバはただの接続口です。作業契約を持たせないと、便利な呼び出し口が「広く触れる入口」になります。

## 検証: JSONより先にコマンド単体を見る

問題が起きたときは、Claude Code 側の MCP 設定を疑う前に、まず `codex` コマンド単体で切り分けます。

```powershell
codex --help
codex mcp-server --help
```

ここで失敗するなら、MCP の JSON ではなく CLI のインストールや PATH の問題です。逆に単体コマンドが通るなら、次は Claude Code を起動した場所、`.mcp.json` を置いた場所、依頼文で指定した cwd を確認します。

この順番にすると、「MCP が悪いのか」「Codex CLI が悪いのか」「作業ディレクトリが違うのか」を混ぜずに済みます。

## まとめ

- Claude Code から Codex を呼ぶ最小設定は `.mcp.json` の `command: "codex"` と `args: ["mcp-server"]` で足りる
- 実際に詰まるのは、Codex CLI が Claude Code 側の PATH から起動できるか、作業ディレクトリが合っているか、権限方針が明確か
- `.mcp.json` には起動方法だけを書き、作業範囲・cwd・禁止事項・verify は依頼文や skill で固定する
- 実装委譲とレビュー委譲を混ぜず、Codex には限定実装を任せ、commit / push はさせない

Codex MCP サーバ登録は入口にすぎません。入口を作ったあと、何をさせて、どこで止めるかを決めるところが本題でした。

## 参考リンク

- [harness17/zenn-articles](https://github.com/harness17/zenn-articles) - 本記事で扱った記事リポジトリ
- [OpenAI Codex CLI](https://github.com/openai/codex) - Codex CLI の公開リポジトリ
- [CodexとClaude Codeを相互呼び出しするハーネスを組んだ](https://zenn.dev/harness/articles/cross-agent-harness-automation) - 相互呼び出し全体の設計メモ
