---
title: "CodexとClaude Codeの共同作業をcross-agent-harnessに切り出した"
emoji: "🧩"
type: "tech"
topics: ["ai", "codex", "claude", "workflow", "oss"]
published: false
---

## はじめに

Claude Code と Codex を同じリポジトリで使っていると、モデルの性能とは別のところで詰まります。

どちらが何を触ってよいのか。レビュー結果をどこに残すのか。merge や publish の前に何を確認するのか。片方の AI が作った変更を、もう片方が知らずに巻き戻さないためにはどうするのか。

これまでは、プロジェクトごとの `AGENTS.md`、`CLAUDE.md`、`CLAUDE_CODE_HANDOFF.md` にその場でルールを書き足していました。Zenn でも、その運用をいくつか記事にしています。

- Claude Code の運用を `rules` と `skills` に分けた話
- Codex と Claude Code をクロスレビューさせた話
- AI との設計判断を My-Skill-Graph に残して再利用した話

ただ、複数プロジェクトで同じことを繰り返しているうちに、これは各リポジトリに手作業で書き散らすより、移植できるキットにした方がよいと感じました。

そこで作ったのが [harness17/cross-agent-harness](https://github.com/harness17/cross-agent-harness) です。

`cross-agent-harness` は、Codex と Claude Code を同じリポジトリで運用するための軽量な共同開発ハーネスです。アプリ本体ではなく、ルール、handoff テンプレート、skills、導入スクリプトをまとめたキットです。

## 何を解決するためのリポジトリか

AI エージェントを複数使うと、便利な一方で境界が曖昧になります。

たとえば、自分の運用では次のような問題が出ました。

- Claude Code が設計した内容を Codex がどこまで実装してよいか分からない
- Codex が実装後に実行した verify 結果が、次のレビュー担当に伝わらない
- レビュー担当が、依頼外のファイルまでついでに直してしまう
- merge / publish してよい条件が会話の流れで揺れる
- プロジェクトごとに同じ handoff 形式を作り直している

これは「AI にもっと詳しく説明する」だけでは安定しませんでした。必要だったのは、作業前、作業中、作業後に見る場所を固定することです。

`cross-agent-harness` では、その固定部分を次のように分けています。

- 共通ルール: `.claude/rules/cross-agent-harness.md`
- handoff の書式: `.claude/rules/handoff-protocol.md`
- プロジェクト固有設定: `.claude/rules/project-collaboration-profile.md`
- Claude Code 側 skill: `codex-handoff` / `cross-review`
- Codex 側 skill: `implement-task`
- 共有ログ: `CLAUDE_CODE_HANDOFF.md`

共通ルールとプロジェクト固有設定を分けたのがポイントです。どのプロジェクトでも守る作業契約は共通ルールへ置き、verify コマンド、注意領域、重大指摘はプロジェクトごとの profile に置きます。

## インストールスクリプトで対象プロジェクトへ移植する

導入は PowerShell スクリプトで行います。

```powershell
.\install.ps1 -TargetPath C:\Projects\MyApp -ProjectName MyApp
```

PowerShell 7 があれば、macOS / Linux でも同じスクリプトを使えます。

```powershell
pwsh ./install.ps1 -TargetPath /path/to/my-app -ProjectName MyApp
```

既存の `project-collaboration-profile.md` と `CLAUDE_CODE_HANDOFF.md` は、`-Force` を付けない限り上書きしません。ここは意図的に保守的にしています。共同作業ログやプロジェクト固有 profile は、上書き事故の影響が大きいからです。

実際にコピーするファイルは次の通りです。

```text
.claude/rules/cross-agent-harness.md
.claude/rules/handoff-protocol.md
.claude/rules/project-collaboration-profile.md
.claude/skills/codex-handoff/SKILL.md
.claude/skills/cross-review/SKILL.md
.agents/skills/implement-task/SKILL.md
CLAUDE_CODE_HANDOFF.md
```

`install.ps1` の中心は、テンプレート内の `{{PROJECT_NAME}}` と `{{TARGET_PATH}}` を置換して対象プロジェクトへ配置する処理です。

```powershell:install.ps1
$content = [System.IO.File]::ReadAllText($template, [System.Text.UTF8Encoding]::new($false, $true))
$content = $content.Replace("{{PROJECT_NAME}}", $ProjectName)
$content = $content.Replace("{{TARGET_PATH}}", $targetRoot.Path.Replace("\", "/"))

[System.IO.File]::WriteAllText($target, $content, [System.Text.UTF8Encoding]::new($false))
Write-Host "created: $TargetRelative"
```

小さい処理ですが、毎回手でファイルを作るより事故が減ります。特に、`CLAUDE_CODE_HANDOFF.md` と profile の初期形が揃うのが効きました。

## project-collaboration-profile にプロジェクト固有の判断を置く

ハーネスを共通化するときに気をつけたのは、全部を共通ルールへ押し込まないことです。

ASP.NET Core MVC、Electron + React、Chrome 拡張、Zenn 記事リポジトリでは、見るべきリスクが違います。

たとえば ASP.NET Core MVC なら、認可、所有者チェック、Identity、migration、`appsettings.Development.json`、Sample 間依存が重要です。一方、Electron アプリなら、lint、test、build、署名、配布導線、SmartScreen まわりの確認が中心になります。

そこで、プロジェクトごとの差分は `project-collaboration-profile.md` に寄せました。

```markdown:project-collaboration-profile.template.md
## 担当境界

| 条件 | 振り先 |
|------|--------|
| 仕様が明確で、触るファイルが限定される | Codex |
| 複数モジュール・永続化・外部契約をまたぐ設計判断 | Claude Code |
| 実動確認が必要な UI / デスクトップ / ブラウザ変更 | TODO |
| リリース・公開・配布判断 | TODO |
```

この表があると、「今回は Codex に任せるべきか、Claude Code で設計を詰めるべきか」を毎回会話で決めなくて済みます。

もちろん、表だけで判断が完全に自動化されるわけではありません。ただ、迷ったときに戻る場所ができます。

## handoff を共有ログにする

`CLAUDE_CODE_HANDOFF.md` は、Codex と Claude Code の共有作業ログです。

ここには、作業依頼、触ってよい範囲、完成条件、verify 結果、レビュー観点、次アクションを残します。

```markdown:CLAUDE_CODE_HANDOFF.template.md
### 完成条件（スプリントコントラクト）

- Claude Code が Codex へ実装依頼を作れる。
- Codex が handoff から実装・verify・handoff 更新へ進める。
- 反対側エージェントがレビュー結果を同じ handoff に残せる。
- Merge 前にセルフ verify・相互レビュー・重大指摘なし・ユーザー指示の 4 条件を確認できる。
```

以前の記事「AI 2 台クロスレビューで技術記事の盲点を拾う」では、作成者とレビュアーを分ける運用を書きました。`cross-agent-harness` では、その考え方を記事執筆だけでなく、実装、レビュー、検証にも広げています。

特に大事にしているのは、merge / publish の条件です。

```text
1. セルフ verify 済み
2. 反対側レビュー済み
3. 重大指摘なし
4. user が merge / publish を明示
```

AI エージェントが「よさそうなので公開します」と進めないように、最後の判断はユーザーの明示に寄せています。これは Zenn 記事の `published: true` ゲートで効いた考え方を、そのまま共同開発に持ち込んだものです。

## Claude Code 側と Codex 側の skill を分ける

このハーネスでは、Claude Code 側と Codex 側で skill の役割も分けています。

Claude Code 側には、Codex へ渡すための `codex-handoff` と、反対側の変更をレビューする `cross-review` を置きます。

Codex 側には、handoff から限定タスクを実装する `implement-task` を置きます。

```markdown:.agents/skills/implement-task/SKILL.md
## 開始時

1. `CLAUDE_CODE_HANDOFF.md` の最新セクションを読む。
2. `.claude/rules/project-collaboration-profile.md` を読む。
3. `git status --short --branch` で未コミット変更を確認する。
4. 完成条件、触ってよい範囲、verify コマンドを短く宣言する。
```

ここでやりたいのは、万能な自動化ではありません。作業開始時に読むべきものを固定することです。

Codex がいきなり実装へ入るのではなく、handoff、profile、未コミット変更を確認してから限定範囲を触る。Claude Code は設計やレビューの観点を handoff に残す。この分担にすると、同じリポジトリで作業しても衝突しにくくなります。

## 既に導入したプロジェクト

README には、現時点の導入実績も置いています。

| プロジェクト | 種別 | 確認した verify |
|---|---|---|
| DevNext | ASP.NET Core MVC template | `dotnet build DevNext.slnx` / `dotnet test .\Tests\Tests.csproj` |
| Phycock | ASP.NET Core MVC health management app | 既存 profile / handoff 運用を確認 |
| YouTom | Electron + React desktop app | `npm run lint` / `npm run test` / `npm run build` |
| GoogleChromeExtensions | Manifest V3 Chrome extensions container | `node .\verify-detect.mjs` |

この一覧は、単なる実績メモではありません。

自分がどの種類のプロジェクトでこのハーネスを試したかを残すことで、profile の例を増やせます。ASP.NET Core MVC 向けには `examples/aspnetcore-mvc-profile.md` も置いています。

今後、別の種類のリポジトリへ入れるときは、共通ルールを増やすより先に profile の例を増やす方針です。共通ルールを肥大化させると、どのプロジェクトでも読まれる前提が重くなるからです。

## これまでの記事とのつながり

`cross-agent-harness` は、これまでの記事のまとめ直しでもあります。

「Claude Code運用を数ヶ月で見直してrulesとskillsに分けた話」では、巨大な `CLAUDE.md` を分割し、作業領域ごとのルールと skill に分ける方針を書きました。今回のハーネスでは、その分割をプロジェクト横断の形にしました。

「AI 2 台クロスレビューで技術記事の盲点を拾う」では、作成者とレビュアーを分けることで、事実誤認や守秘リスクを拾った話を書きました。今回のハーネスでは、その役割分担を記事だけでなく実装タスクにも広げています。

「AIとの設計判断をMy-Skill-Graphに残して再利用する」では、会話ログではなく判断を残す話を書きました。今回のハーネスでは、handoff に作業結果と次アクションを残し、必要な判断は Skill Graph へ送れるようにしています。

つまり、`cross-agent-harness` は新しい発想というより、手元で効いた運用を移植可能な形へ畳み直したものです。

## まとめ

`cross-agent-harness` は、Codex と Claude Code を同じリポジトリで使うための共同開発キットです。

中心にあるのは、AI を自動で賢くする仕組みではなく、作業境界、handoff、verify、レビュー、merge / publish ゲートを明文化することです。

今のところ、自分の運用で効いているのは次の3点です。

- 共通ルールとプロジェクト固有 profile を分ける
- `CLAUDE_CODE_HANDOFF.md` に依頼、実装、verify、レビューを集約する
- merge / publish はセルフ verify、反対側レビュー、重大指摘なし、ユーザー明示の 4 条件で止める

AI エージェントを複数使うと、会話だけで運用を保つのは難しくなります。作業契約をリポジトリに置き、差分で育てる。そのための小さなキットとして、`cross-agent-harness` を作りました。

## 参考リンク

- [harness17/cross-agent-harness](https://github.com/harness17/cross-agent-harness)
- [Claude Code運用を数ヶ月で見直してrulesとskillsに分けた話](https://zenn.dev/harness/articles/claude-code-workflow-evolution)
- [AI 2 台クロスレビューで技術記事の盲点を拾う](https://zenn.dev/harness/articles/ai-cross-review-handoff-workflow)
- [AIとの設計判断をMy-Skill-Graphに残して再利用する](https://zenn.dev/harness/articles/codex-claude-skill-graph-worklog)
- [harness17/zenn-articles](https://github.com/harness17/zenn-articles)
