---
title: Claude Code運用ハーネスを「小さく分けて直せる形」にした3つの理由
tags:
  - ClaudeCode
  - Codex
  - AI
  - 個人開発
  - 開発環境
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

## 結論: 3つの設計原則

Claude Code / Codex の運用ハーネス（rules・skills・hooks・agent分担の総体）を数ヶ月運用して残った設計原則は3つです。

| 原則 | 一言 | 守らないと何が起きたか |
|------|------|----------------------|
| 編集半径を小さくする | 1ファイル1トピック | テスト方針の1行修正で隣のセキュリティ節が崩れた |
| 発火条件で層を分ける | rules/skills/hooks/advisorを混ぜない | 記事チェックがコード実装セッションでも毎回走った |
| 捨てられる単位で持つ | ルール間の順序依存を作らない | 片方を直したらもう片方が壊れた |

以下、各原則の根拠を書きます。

## 編集半径を小さくする

最初は `CLAUDE.md` 1枚に全ルールを書いていました。Git操作、テスト方針、セキュリティ観点が1ファイルに混在する状態です。

テスト方針の文言を直したとき、隣のセキュリティ節でインデントが崩れ、エージェントがセキュリティルールを読み飛ばしました。1行の修正が関係ないルールに波及した。

`rules/` に分割して `CLAUDE.md` を目次にしたら、編集半径が1ファイルに収まりました。`git diff` で変更が1ファイルに閉じていることを確認でき、隣接ルールへの波及が消えました。

```markdown
# グローバルルール
ユーザに同調せず、目的達成を優先する。

@rules/git-ops.md
@rules/test-strategy.md
@rules/security-coding.md
```

分割しすぎると「どのファイルに何があるか」を探すコストが増えます。グローバル18本、プロジェクト固有8本あたりが上限でした。

## 発火条件で層を分ける

次に起きた問題は、全部をルール（rules）に書いてしまうことでした。

記事の公開前チェックをルールに書いていたら、コード実装のセッションでも毎回読み込まれました。スキル（skill）に移したらタスクに応じて起動するようになり、保存時の文体チェックはフック（hook）にしたら呼び忘れもなくなりました。

| 種類 | 発火条件 | 使いどころ |
|------|----------|-----------|
| rules | 常時適用 | 毎タスクで守る制約（Git操作、セキュリティ） |
| skills | タスクに応じて起動 | 定型作業（レビュー、リリース前チェック） |
| hooks | ツール実行時に自動 | 保存時の文体チェック |
| advisor | 難所だけ相談 | アーキテクチャ・セキュリティ判断 |

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "bash .claude/hooks/check-article-style.sh 2>/dev/null || true", "timeout": 10 }
        ]
      }
    ]
  }
}
```

発火条件が違うものを1箇所に混ぜると、常時走るべきものが呼び忘れで抜けたり、必要なときだけでよいものが毎回ノイズになります。

## 捨てられる単位で持つ

ハーネスの部品は足すだけでなく外すこともあります。使っていないルールを残すと、エージェントが読み込む量が増えて判断が鈍ります。

大事なのは、1つのルールを外しても他のルールが壊れないことです。実際に、リリース前チェックのスキルが「`sprint-contract.md` の完成条件リストを参照して検証する」と書いてあった時期がありました。`sprint-contract.md` の書き方を変えたら、リリース前チェックも壊れた。

ルール間の参照は「関連として存在を知っている」程度にとどめ、実行順序の依存は作らないようにしました。**ルールを読んでも作業の質が変わらなくなったら**、それは間引く合図です。

## まとめ

- **編集半径を小さくする**: 1ファイルの修正が他に波及しない構造
- **発火条件で層を分ける**: rules/skills/hooks/advisorを混ぜない
- **捨てられる単位で持つ**: ルール間の順序依存を作らない

シリーズとして、組み上がった全体像は [5層の地図](https://zenn.dev/harness/articles/claude-code-harness-layer-map)、ゼロからの組み方は [ビルド順](https://zenn.dev/harness/articles/claude-code-harness-build-order) にまとめています。

## 参考リンク

- [harness17/zenn-articles](https://github.com/harness17/zenn-articles) — rules / skills / hooks の実例
- [Claude Code運用ハーネスの現在地（Zenn）](https://zenn.dev/harness/articles/claude-code-harness-layer-map) — ①組み上がった全体像
