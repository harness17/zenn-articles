---
slug: claude-md-import-split-rules
status: draft
type: qiita
created: 2026-05-24
---

# Qiita構成メモ: Claude CodeのCLAUDE.mdを@importで分割してトークンを節約した

## 中心主張（1文）

単一の `CLAUDE.md` にルールを全部書くとセッション開始時のトークン消費が増えるので、トピックごとに `.claude/rules/*.md` へ分割して `@.claude/rules/xxx.md` で取り込む構成に変えた。

## 想定読者

- Claude Code を導入したばかりで `CLAUDE.md` の分割粒度に迷っている
- ルールが増えてきて毎セッションのコンテキストが重い
- 「グローバルルール」と「プロジェクト固有ルール」の置き場所を整理したい

## 詰まったポイント

- 単一 `CLAUDE.md` にルールを書き続けたら 200 行を超え、毎セッションそのまま読み込まれる
- ルール追加のたびに「他のルールと並ぶ位置」を考えるコストが上がる
- 1 トピックだけ修正したいのに巨大ファイルを編集することになる

## 採用した構成

```
~/.claude/
├── CLAUDE.md              # 38 行（@import のみ）
└── rules/
    ├── advisor-strategy.md         # 58 行
    ├── api-quota-design.md         # 85 行
    ├── git-ops.md                  # 38 行
    ├── security-coding.md          # 74 行
    ├── skill-graph-auto-register.md # 111 行
    ├── handoff-capture.md          # 102 行
    └── ... 計17ファイル / 合計 929 行
```

`CLAUDE.md` の中身は次のように `@` プレフィックス付きの相対パスで列挙する：

```markdown
# グローバルルール
ユーザに同調せず、目的達成を優先する。

@rules/claude-md-generation.md
@rules/git-ops.md
@rules/security-coding.md
@rules/api-quota-design.md
...
```

## 分割の判断軸（実運用で固めたもの）

- 1 ファイル 1 トピック（例: git 操作 / API クォータ / セキュリティ）
- 60〜100 行を超えたら別ファイルへ抽出
- ルールが「いつ適用するか」を冒頭で必ず宣言
- プロジェクト固有ルールは `<repo>/.claude/rules/` に同じ構成で置く

## 落とし穴

- `@` パスは CLAUDE.md ファイルからの相対パス。絶対パスやエイリアスは使わない
- ファイル名にスペースを含めない
- import を増やしすぎても結局トークン全部読まれるので、肥大化を防ぐ仕組みとセットで運用する
- ルール生成時は `@.claude/rules/xxx.md` 形式で参照する命名規則をルール側で固定しておく（後述）

## 副産物：ルール生成ルール

`claude-md-generation.md` というメタルールを 1 つ作り、「CLAUDE.md を生成する時は必ず `.claude/rules/` も同時に作る」「分割は `@import` 形式で参照」を強制している。AI に新規プロジェクトのセットアップを任せる時に効く。

## まとめ（記事末尾用）

- `CLAUDE.md` は @import の目次だけにする
- ルール本体は `.claude/rules/<topic>.md` へトピック別に分割
- 生成ルール側で「分割 + import 参照」を強制すると新規プロジェクトでも一貫する

## 参考リンク（記事内）

- Claude Code 公式: Settings and Permissions（CLAUDE.md の項）
- 個人開発 rules フォルダ例（記事内ではディレクトリ構造の図のみ）

## NG ライン

- 個人ファイル絶対パスを記事に貼らない（`C:/Users/harne/...` は構造図に置き換え）
- 業務固有・案件固有ルールには触れない
- 他のAIツール（Codex等）との優劣比較はしない
