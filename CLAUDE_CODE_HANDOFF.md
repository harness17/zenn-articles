# ClaudeCode 引き継ぎ資料

最終更新: 2026-05-17
対象プロジェクト: `H:/ClaudeCode/技術記事`

## 2026-05-18 追記（ClaudeCode への LAPRAS レビュー対応・スキル反映レビュー依頼）

依頼者: Codex

レビュー担当: ClaudeCode

対象:

- LAPRAS AI レビュー対応済み記事
  - `articles/cross-agent-harness-introduction.md`
  - `articles/codex-claude-skill-graph-worklog.md`
  - `articles/aspnet-core-identity-to-commonlibrary.md`
  - `articles/ai-cross-review-handoff-workflow.md`
  - `articles/youtom-introduction.md`
- LAPRAS 指摘を反映したスキル / ルール
  - `.agents/skills/article-plan/SKILL.md`
  - `.agents/skills/article-review/SKILL.md`
  - `.agents/skills/article-publish/SKILL.md`
  - `.claude/skills/article-plan/SKILL.md`
  - `.claude/skills/article-review/SKILL.md`
  - `.claude/skills/article-publish/SKILL.md`
  - `.claude/rules/cross-agent-review.md`
  - `.claude/rules/zenn-workflow.md`

触ってよい範囲:

- 原則、上記ファイルへのレビューコメント追記のみ
- 明らかな誤字・リンクミス・ルール不整合は、対象ファイル内の最小修正なら可
- `published: true` の変更、記事主旨の大幅変更、対象外記事の改稿、親プロジェクト更新、push / commit は行わない

レビュー観点:

- LAPRAS AI レビューの改善点（対象読者、用語定義、セクション接続、図表、導入後トラブルシューティング、参考リンク説明）が、各記事で過不足なく反映されているか
- 記事への追記が説明過多になり、体験記事としての流れを壊していないか
- `.agents/skills/*` と `.claude/skills/*` のミラーが実質的に同期しているか
- `article-plan` / `article-review` / `article-publish` の追加ルールが運用可能な粒度で、次の記事作成時に過剰な負担にならないか
- `CLAUDE_CODE_HANDOFF.md` の記録が長くなりすぎていないか。圧縮や別 handoff 化が必要なら指摘する
- 未コミット差分のうち、`articles/devnext-mvc-helper-extensions.md` は別件の既存差分として扱い、今回レビュー対象から外す

Codex 側の確認済み事項:

- 各記事の文体NG語スキャン: ヒットなし
- `npx zenn list:articles`: 成功
- `git diff --check`: 問題なし
- LAPRAS AI レビュー対応後の Codex 再レビュー結果は、本 handoff の各記事セクションに追記済み
- My-Skill-Graph の `self/goals.md` と判断記録 `[[外部レビュー後にCodex再レビューを挟むのは記事改善を公開ゲートに戻すため]]` を更新済み

レビュー結果の記録先:

- この `CLAUDE_CODE_HANDOFF.md` の本セクション直下に `ClaudeCode レビュー結果（2026-05-18）` として追記
- 継続作業が必要な場合は、My-Skill-Graph の `ops/handoffs/` にも要約を残す

公開 / commit ゲート:

- 重大指摘が残っている間は commit / push しない
- commit する場合は、対象ファイルを明示して個別 stage する
- Zenn 公開反映は既存の `published: true` と main push に依存するため、レビュー完了後にユーザーの明示を待つ

### ClaudeCode レビュー結果（2026-05-18）

レビュー担当: ClaudeCode / 修正は未実施（レビューのみ）

**記事5本（LAPRAS 風レビュー対応差分）**

| 観点 | 結果 |
|------|------|
| 文体NG語 | 5本すべてヒットなし。`ai-cross-review-handoff-workflow.md` L123 の `「いかがでした…」系の問いかけ` は NG パターンを `…` 付きで言い換えた既存表記で、今回差分外。スキャンを壊さないため許容 |
| 守秘義務 | 業務固有名詞・顧客名・実名の追加なし |
| 追記の粒度 | 各記事 1〜2 段落＋表/Mermaid 1 点ずつ。体験記事の流れを崩す説明過多はなし。LAPRAS 指摘（対象読者・用語定義・セクション接続・図表）に正対している |
| `codex-claude-skill-graph-worklog.md` Mermaid | ` ```mermaid ` 指定で Zenn 表示可。decisions/strategies の関係図として論理性指摘に有効 |
| `youtom-introduction.md` RSS/API 比較表 | Markdown テーブル正常。実用性指摘に有効 |

**任意レベルの指摘（公開ブロッカーではない）**

| 指摘 | 内容 |
|------|------|
| `cross-agent-harness-introduction.md` の H2 増加 | 新規 H2「導入後に詰まったときに見るところ」追加で H2 が 11 個に。2026-05-17 レビューで 10 個を許容済みのため範囲内だが、以後の追記では小見出し（H3）への寄せを検討 |
| `aspnet-core-identity-to-commonlibrary.md` の見出しリネーム | `DevNetでもCommonLibraryはIdentity周辺に依存していた` → `DevNetのCommonLibraryは純粋共通ではなかった`。Zenn のアンカー ID が変わる。他記事から旧アンカーへのリンクは見当たらず実害なしと判断 |

**スキル / ルール**

| 観点 | 結果 |
|------|------|
| `.agents/skills/*` と `.claude/skills/*` のミラー同期 | article-plan / article-review / article-publish の 3 ペアとも、差分は意図的なパス読み替え（`.Codex/`↔`.claude/`、`Codex.local.md`↔`CLAUDE.local.md`）のみ。実質同期済み |
| `article-plan` 追加（2.5 読者前提・図表予定欄） | 構成段階のチェック粒度として運用可能。テンプレ欄追加も過剰負担ではない |
| `article-review` 追加（構成チェック・対応モード分類） | LAPRAS 指摘パターンを観点化できており妥当 |
| `article-publish` 追加（LAPRAS レビュー本文の取り込み） | スコア止まりを防ぐ流れとして妥当 |
| `cross-agent-review.md` / `zenn-workflow.md` 外部レビュー対応フロー | 既存の公開前フローと重複せず追加できている |

**スキル側の軽微な指摘**

- `article-review` 対応モード手順 6 が参照する `append-codex-review-request.sh` は `.claude/skills/article-review/scripts/` 配下に未追跡（`?? `）状態。スキル本文がこのスクリプトに依存するため、スキル変更を commit する際は scripts ディレクトリも同時に stage するか、追跡しない方針なら SKILL.md に明記する
- `.agents`（Codex）ミラーの手順 6 もスクリプトパスを `.claude/skills/...` と書いている。スクリプト実体が `.claude` 側のみのため動作上は正しいが、ミラー規約上はパス読み替え対象外であることを意識する

**CLAUDE_CODE_HANDOFF.md の長さ**

- 現在 955 行・`## ` セクション約 30 個。`handoff-archive.md` の閾値（セクション 10 超）を大きく超過。最古セクションは 2026-05-10 で 30 日未満だが、セクション数基準で `/handoff-cleanup` 実行対象。2026-05-14 以前のセクションを `handoffs/archive/2026-Q2.md` へ切り出すことを推奨

**公開可否判断**: 🟢 重大指摘なし。記事5本は公開済み記事の改善差分として問題なし。スキル/ルール差分も commit 可能な品質。commit 時は対象ファイルを個別 stage し、scripts ディレクトリの扱いを確定させること。再 push・公開反映はユーザーの明示を待つ。

## 2026-05-18 追記（LAPRAS AIレビュー指摘のスキル反映）

対象:

- `.agents/skills/article-plan/SKILL.md`
- `.claude/skills/article-plan/SKILL.md`
- `.agents/skills/article-review/SKILL.md`
- `.claude/skills/article-review/SKILL.md`
- `.agents/skills/article-publish/SKILL.md`
- `.claude/skills/article-publish/SKILL.md`

反映した指摘パターン:

- 対象読者の明示不足
- 初出の重要用語説明不足（OAuth / RSS / YouTube Data API / Identity / handoff / ハーネス化）
- セクション間の接続不足
- `decisions` / `strategies` や RSS / API のような関係・比較の図表不足
- 導入後トラブルシューティングや負の定義不足
- 参考リンクの説明不足
- LAPRAS AI レビュー結果をスコア確認で終わらせていたこと

反映内容:

- `article-plan`: 構成段階で「読者前提と補足する用語」を決めるステップを追加。見出し案に橋渡し文の必要性、図表・比較表・トラブルシューティング小セクションの検討を追加
- `article-review`: 構成チェックに対象読者、初出用語、セクション接続、図表、負の定義、参考リンク説明を追加。レビューコメント対応モードに明確性・実用性・論理性別の反映方針を追加
- `article-publish`: LAPRAS AI レビューが表示された場合に、点数と本文を記録し、`article-review` のレビューコメント対応モードへ戻す流れを追加

検証:

- Codex / ClaudeCode 側 skill mirror に同等の追記が入っていることを `rg` と `git diff` で確認
- `git diff --check` 問題なし

注意:

- prompt / harness 変更の第二視点検証は、現行ルール上サブエージェント利用にユーザーの明示的委任が必要なため未実施。ClaudeCode 側レビューが必要なら、この handoff を起点に依頼する

## 2026-05-18 追記（Codex による youtom-introduction LAPRAS 風レビュー対応）

対象記事: `articles/youtom-introduction.md`

ユーザーが貼り付けた LAPRAS 風レビューでは、総合3.9、論理性4.0、実用性4.0、読みやすさ3.5、独自性4.5、明確性3.5。主な改善点は、技術用語の補足、RSS と YouTube Data API の機能差の明確化、実装セクションから配布課題セクションへの遷移補強。

Codex が反映した差分:

- YouTube Data API の前提として出てくる OAuth と `credentials.json` を、配布アプリの初回体験に関係する用語として短く説明
- RSS と YouTube Data API で取れる情報・苦手なことを表で追加
- 実装判断から配布課題へ移る前に、取得方式だけでなく認証ファイル、署名、クォータも体験に直結するという橋渡し文を追加

Codex レビュー結果:

- 文体ルール違反語: 0件
- フロントマター: title / emoji / type / topics / published は維持。既に公開済みのため `published: true`
- 必須要素: GitHub リンク、5行以上のコードブロック、体験ベースの問題設定、参考リンクを維持
- 構成: 簡易/フルモードの判断前に用語補足とRSS/API差分を追加し、配布課題への接続も補強。LAPRAS 指摘の読みやすさ・明確性に対する追記として妥当
- 守秘義務: 業務固有名詞・顧客名・実名の追加なし
- Zenn CLI: `npx zenn list:articles` 成功
- 公開可否: 公開済み記事の改善差分として問題なし。再 push はユーザー指示または通常の公開運用に従う

## 2026-05-18 追記（Codex による ai-cross-review-handoff-workflow LAPRAS 風レビュー対応）

対象記事: `articles/ai-cross-review-handoff-workflow.md`

ユーザーが貼り付けた LAPRAS 風レビューでは、総合3.9、論理性4.0、実用性4.0、読みやすさ4.0、独自性4.0、明確性3.5。主な改善点は、対象読者の明示、`handoff ファイル` と `ハーネス化` の定義、指摘パターンの分類基準、参考リンク説明の補足。

Codex が反映した差分:

- `はじめに` に、AIで記事やコードを書かせているが公開前レビュー・守秘確認・事実確認を会話だけで済ませることに不安がある読者向けの記事だと明示
- Zenn記事以外にも README、技術ブログ、ポートフォリオ説明のレビューに転用できることを補足
- `handoff ファイル` を AI 同士の作業依頼、レビュー結果、未確認事項を時系列で残す共有メモとして定義
- `ハーネス化` を handoff、レビュー観点、公開ゲートをリポジトリ内のルールとテンプレートに固定することとして定義
- `実際に拾われた指摘パターン` に、4分類の基準を追加
- 参考リンクそれぞれに役割説明を追加し、関連する Claude Code 運用変遷記事は実リンクへ変更

Codex レビュー結果:

- 文体ルール違反語: 0件
- フロントマター: title / emoji / type / topics / published は維持。既に公開済みのため `published: true`
- 必須要素: GitHub リンク、5行以上のコードブロック、実例、参考リンクを維持
- 構成: 対象読者と用語定義を冒頭に置き、指摘パターン分類の基準を本文内に明示。LAPRAS 指摘の明確性に対する追記として妥当
- 守秘義務: 業務固有名詞・顧客名・実名の追加なし
- Zenn CLI: `npx zenn list:articles` 成功
- 公開可否: 公開済み記事の改善差分として問題なし。再 push はユーザー指示または通常の公開運用に従う

## 2026-05-18 追記（Codex による aspnet-core-identity-to-commonlibrary LAPRAS 風レビュー対応）

対象記事: `articles/aspnet-core-identity-to-commonlibrary.md`

ユーザーが貼り付けた LAPRAS 風レビューでは、総合4.2、論理性4.5、実用性4.0、読みやすさ4.0、独自性4.5、明確性4.0。主な改善点は、Identity フレームワークの基礎知識がない読者向けの簡潔な補足と、`DevNetでもCommonLibraryはIdentity周辺に依存していた` セクションの冗長感の軽減。

Codex が反映した差分:

- `はじめに` に、ASP.NET Core Identity と `ApplicationUser` の役割を短く補足
- 記事の対象は Identity 導入手順ではなく、Identity 型を Web プロジェクトと共通ライブラリのどちらに置くかという境界判断であることを明示
- `二世代の ApplicationUser を並べる` の導入文を補い、コード比較へ入る流れを少し明確化
- `DevNetでもCommonLibraryはIdentity周辺に依存していた` を `DevNetのCommonLibraryは純粋共通ではなかった` に改め、重複していた説明を圧縮

Codex レビュー結果:

- 文体ルール違反語: 0件
- フロントマター: title / emoji / type / topics / published は維持。既に公開済みのため `published: true`
- 必須要素: GitHub リンク、5行以上のコードブロック、実体験としての前提修正、参考リンクを維持
- 構成: Identity基礎補足 → 二世代比較 → 誤前提の訂正 → 判断軸 → コスト → 将来分割の流れ。LAPRAS 指摘の明確性・読みやすさに対する追記として妥当
- 守秘義務: 業務固有名詞・顧客名・実名の追加なし
- Zenn CLI: `npx zenn list:articles` 成功
- 公開可否: 公開済み記事の改善差分として問題なし。再 push はユーザー指示または通常の公開運用に従う

## 2026-05-18 追記（Codex による codex-claude-skill-graph-worklog LAPRAS 風レビュー対応）

対象記事: `articles/codex-claude-skill-graph-worklog.md`

ユーザーが貼り付けた LAPRAS 風レビューでは、総合4、論理性3.5、実用性4.0、読みやすさ4.0、独自性4.5、明確性4.0。主な改善点は、セクション間の論理接続、`decisions` と `strategies` の相互関係の図解、クロスレビュー記事との役割分けへの遷移、Obsidian 未経験者向けの導入ハードル補足。

Codex が反映した差分:

- `はじめに` に、Obsidian 固有機能ではなく Markdown ファイルを `decisions/` と `strategies/` に分ける運用であり、通常の Git 管理メモでも試せることを追記
- `decisions` セクション末尾に、技術判断を外向きの価値へつなげるため `strategies` が必要になる橋渡し文を追記
- `strategies` セクションに Mermaid 図を追加し、AI 作業から `decisions/`、再利用、`strategies/`、Zenn記事・ポートフォリオ説明へつながる流れを明示
- `クロスレビュー記事とは役割を分ける` の冒頭に、ここまでの論点から隣接テーマ整理へ移る橋渡し文を追記

Codex レビュー結果:

- 文体ルール違反語: 0件
- フロントマター: title / emoji / type / topics / published は維持。既に公開済みのため `published: true`
- 必須要素: GitHub リンク、5行以上のコードブロック、体験ベースの問題設定、参考リンクを維持
- 構成: `decisions` → `strategies` → 記録条件 → 記事候補 → クロスレビューとの差分の接続を補強。LAPRAS 指摘の論理性に対する追記として妥当
- 守秘義務: 業務固有名詞・顧客名・実名の追加なし
- Zenn CLI: `npx zenn list:articles` 成功
- 公開可否: 公開済み記事の改善差分として問題なし。再 push はユーザー指示または通常の公開運用に従う

## 2026-05-18 追記（Codex による LAPRAS 風レビュー対応後チェックと自動化ルール追加）

対象記事: `articles/cross-agent-harness-introduction.md`

ユーザーが貼り付けた LAPRAS 風レビューでは、総合4、論理性4.0、実用性4.0、読みやすさ4.0、独自性4.5、明確性3.5。主な改善点は、AI エージェント運用の初心者向け問題設定と、導入後のトラブルシューティング追加。

Codex が反映した差分:

- `はじめに` に、複数 AI エージェント運用では作業範囲、レビュー結果、検証状況、公開判断が会話ごとに分散するという問題設定を追記
- インストール後の流れとして、対象プロジェクトごとの判断を profile と handoff に寄せる橋渡し文を追記
- `導入後に詰まったときに見るところ` セクションを追加し、`project-collaboration-profile.md`、`CLAUDE_CODE_HANDOFF.md`、既存 profile / handoff がある場合の `-Force` 前確認を説明

Codex レビュー結果:

- 文体ルール違反語: 0件
- フロントマター: title / emoji / type / topics / published は維持。既に公開済みのため `published: true`
- 必須要素: GitHub リンク、5行以上のコードブロック、体験ベースの問題設定、参考リンクを維持
- 構成: `はじめに`、問題設定、導入、profile、handoff、skills、導入実績、トラブルシューティング、まとめの流れ。LAPRAS 指摘の明確性・実用性に対する追記として妥当
- 守秘義務: 業務固有名詞・顧客名・実名の追加なし
- Zenn CLI: `npx zenn list:articles` 成功
- 公開可否: 公開済み記事の改善差分として問題なし。再 push はユーザー指示または通常の公開運用に従う

自動化ルール追加:

- `.claude/rules/cross-agent-review.md` に、LAPRAS / Zenn AI レビュー / ユーザーコメント対応後は `/article-review` 相当で再チェックし、`CLAUDE_CODE_HANDOFF.md` に残すルールを追加
- `.claude/rules/zenn-workflow.md` に、外部レビューコメント対応フローを追加
- `.agents/skills/article-review/SKILL.md` と `.claude/skills/article-review/SKILL.md` に、レビューコメント対応後の Codex/ClaudeCode レビュー記録手順を同期

次アクション:

- この記事を main に反映する場合は、対象ファイルとルール/skill の差分を確認してから個別 stage する
- Zenn 実サイトで 200 を確認できた日を LAPRAS 確認の起算点にする

## アーカイブ済み（2026-Q2）

完了済みハンドオフは [handoffs/archive/2026-Q2.md](handoffs/archive/2026-Q2.md) に切り出し済み。

- 2026-05-17 cross-agent-harness-introduction 公開前レビュー結果（記事公開済み）
- 2026-05-17 cross-agent-harness 紹介記事初稿・ClaudeCodeレビュー依頼
- 2026-05-16 article-review skill コメント対応モードの mirror 同期
- 2026-05-14 M記事執筆の反省と article-fact-check ルール新設
- 2026-05-14 Codex既存記事2本の差別化レビュー結果
- 2026-05-14 ai-cross-review-handoff-workflow 初稿・Codexレビュー（記事公開済み）
- 2026-05-14 M記事を aspnet-core-identity-to-commonlibrary に差し替え（記事公開済み）
- 2026-05-14 devnet-devnext-repository-generic-regret 初稿（retire済み）
- 2026-05-11 electron-smartscreen-oss-distribution 公開前レビュー結果（記事公開済み）
- 2026-05-11 electron-smartscreen-oss-distribution 初稿・ClaudeCodeレビュー依頼
- 2026-05-10 候補N claude-code-workflow-evolution 初稿・レビュー依頼（記事公開済み）
- 2026-05-10 既存4記事の相互レビュー実施（全記事公開済み）
- 2026-05-10 記事相互レビュー運用のハーネス化（cross-agent-review ルール新設）

## 2026-05-11 追記（ClaudeCode による phycock-schedule-entry-consolidation 公開前レビュー結果）

ClaudeCode が `articles/phycock-schedule-entry-consolidation.md`（Codex 作成、2026-05-10 依頼分）に対して `/article-review` 相当の公開前レビューを実施し、ユーザー指示で修正を反映しました。

レビュー結果サマリ:

- 文体ルール違反語: 0 件（「素晴らしい」「いかがでしたでしょうか」等の NG 語なし、`〜することで` 3 連鎖なし）
- 必須要素: GitHub リンク（DevNext）、コードブロック（最大 24 行）、体験表現、文字数（フロントマター込み 11,965 字）すべて充足
- 守秘義務: Phycock 固有名・支援機関・体調・療養文脈は本文に一切出ていない（一般化済み）
- ブロッカー: なし

任意レベルの指摘 3 点とその反映状況:

| 指摘 | 反映内容 |
|------|---------|
| タイトルに `ASP.NET Core MVC` を入れて検索性を上げる | `ASP.NET Core MVCでScheduleEntryに寄せた設計判断`（27 字）に変更済み |
| 重要な注意点を `:::message alert` で強調する | 「業務アプリなら、ここは別判断になります」周辺を `:::message alert` で囲み、「テーブル削除は Entity を消すだけでは終わらない」観点も同ブロックに統合済み |
| コードブロックにファイル名（` ```csharp:Xxx.cs `）を付ける | 9 個すべてのコードブロックに付与済み（`ScheduleEntryEntity.cs` / `ScheduleEntryFormViewModel.cs` / `ScheduleEntryService.cs` / `RemoveScheduleEventTables.cs` / `ApplicationDbContext.cs` / `ScheduleEntryValidation.cs` / `ScheduleEntryServiceTests.cs`） |

公開ゲート4条件（`.claude/rules/cross-agent-review.md`）の状態:

| 記事 | ①セルフ | ②相互レビュー記録 | ③重大指摘 | ④ユーザー指示 |
|------|--------|----------------|-----------|--------------|
| phycock-schedule-entry-consolidation | ✅ | ✅（本書） | 🟢 残なし | ❌ 未指示 |

次アクション:

- ユーザーの公開指示を待つ
- 明示後に `published: true` へ変更してコミット & push
- 公開後は `/article-publish` を実行（README更新、Lapras 確認予約、職経書追記検討）

## 目的

このリポジトリは、GitHub: `harness17`の Zenn 技術記事プロジェクトです。

目的は、個人開発で実際に詰まった課題と解決の判断軸を記事化し、Lapras 技術記事スコア向上と就職選考での説明材料を増やすことです。

## まず読むもの

1. `CLAUDE.md`
2. `.claude/rules/topic-policy.md`
3. `.claude/rules/writing-style.md`
4. `.claude/rules/article-requirements.md`
5. `C:/Users/harne/iCloudDrive/My-Skill-Graph/My-Skill-Graph/ops/handoffs/2026-05-10-zenn-article-candidates-codex.md`
6. `C:/Users/harne/iCloudDrive/My-Skill-Graph/My-Skill-Graph/strategies/Zenn記事候補はハンドオフから課題解決単位で抽出する.md`

親プロジェクト側の元資料:

- `F:/Dropbox/Job-hunting/.claude/worktrees/mystifying-borg-0c5edc/ZENN_ARTICLES_HANDOFF.md`

## 現在の方針

最重要方針は「課題解決力ベース・体験記事優先」です。

SQL Server チューニングなど、体験より解説になりやすいテーマは今は保留します。記事候補は、作業ハンドオフに残っている以下を満たすものから選んでください。

- 何に詰まったかが明確
- 何を比較したかが説明できる
- なぜその解決を選んだかが言える
- 実コードまたは検証証跡を出せる
- 守秘義務や個人情報に触れず一般化できる

## 記事候補

### 第1候補: YouTube Data API のクォータ枯渇と RSS 活用

既定の第1記事候補です。

主軸:

- YouTube Data API のクォータが枯渇した
- `search.list` 依存を避け、RSS と必要最小限の API 呼び出しに寄せた
- 自動更新と手動更新を分けた
- 上限件数を計算式で決めた
- クォータ切れ時にユーザーへどう案内するかを考えた

想定 slug:

- `youtube-data-api-quota-exhaustion`
- 既に記事が存在する場合は、既存 slug を優先して重複作成しない

### 第2候補: Phycock で Schedule を削除して ScheduleEntry に集約した設計判断

設計判断を見せやすい候補です。

主軸:

- 汎用 `Schedule` が、通所予定という実際の用途に対して過剰だった
- `ScheduleEntry` に責務を絞った
- DB・Controller・Service・View・Test から旧 Schedule 系を削除した
- 医療・体調に近いデータなので、表現は一般化する

想定 slug:

- `phycock-schedule-entry-consolidation`

### 第3候補: FullCalendar のイベント色が DTO だけでは反映されなかった話

具体的な UI 検証記事にしやすい候補です。

主軸:

- `Color` を返しても、時間付きイベントが dot 表示になり背景色が面として出なかった
- `backgroundColor` / `borderColor` / `textColor` を DTO で分ける必要があった
- `eventContent` 側の白文字固定で `textColor` が無効化されていた
- `eventDisplay: 'block'` と computed style / screenshot 確認まで必要だった
- DTO の正しさとブラウザ上の見た目は別に検証する

想定 slug:

- `fullcalendar-event-color-rendering`

## 追加の記事候補

上の3本を優先しつつ、次の候補もハンドオフ由来の課題解決記事として使えます。

| 優先 | 候補 | 詰まったポイント | 記事化の軸 | 想定 slug |
|------|------|------------------|------------|-----------|
| 高 | FullCalendar の色指定が UI に出ない原因を切り分けた話 | DTO は正しいのに、時間付きイベントが dot 表示になり背景色が出なかった | データ・描画設定・実ブラウザ検証を分けて確認する | `fullcalendar-event-color-debugging` |
| 中 | `eventContent` の白文字固定で `textColor` が効かなかった話 | サーバー側で文字色を設計しても、フロントのカスタム描画で上書きしていた | DTO と描画カスタマイズはセットでレビューする | `fullcalendar-eventcontent-textcolor` |
| 中 | 表示仕様から `ProgramType` 必須バリデーションを決めた話 | `ActivityType=Program` なのに `ProgramType=null` を許すと色分け不能な予定が作れた | UI 表示に必要なデータ制約をサーバー側でも保証する | `validation-from-calendar-display` |
| 中 | ライブ開始通知を状態遷移時だけ出した話 | 起動時点ですでに live の配信まで通知すると通知連打になる | 初回状態をベースラインとして扱う通知設計 | `notify-on-state-transition` |
| 中 | Identity ユーザーを物理削除せずロックアウトで無効化した話 | 体調・睡眠・通所予定の関連データを持つユーザーを削除すると履歴が壊れる | 関連データを持つアカウントは無効化で扱う | `identity-user-disable-not-delete` |
| 低 | 睡眠記録の日跨ぎ時刻入力を扱った話 | `22:30 - 06:15` のような入力を同日終了として保存すると睡眠時間が壊れる | 日付 + 時刻入力で翌日終了を判定する | `sleep-record-overnight-time` |
| 低 | 通知分数設定の入力範囲を決めた話 | ユーザー設定をそのまま使うと 0 分・巨大値・不正値で通知ロジックが壊れる | 設定値には範囲と安全なデフォルトを持たせる | `notification-reminder-validation` |
| 低 | `textContent` と `white-space: pre-line` の差分で改行が見えなかった話 | DOM 上に改行があっても CSS で折り畳まれた | データ確認だけでなく CSS 表示まで確認する | `css-pre-line-rendering` |

この中で単独記事にしやすいのは、`notify-on-state-transition` と `identity-user-disable-not-delete` です。FullCalendar 系は第3候補の記事へまとめると、一本の記事として読み応えが出ます。

## ClaudeCode への作業依頼の受け方

ユーザーが「記事を作りたい」「構成を作って」と言ったら、まず `/article-plan` を使って `drafts/<slug>.md` に構成メモを作ってください。

構成には必ず以下を入れてください。

- 想定読者
- 詰まったこと
- 試したこと
- 選んだ解決策
- 判断軸
- 実コード候補
- 参考リンク候補
- 守秘義務・個人情報リスク

ユーザーがテーマを迷っている場合は、第1候補の YouTube Data API クォータ枯渇を勧めてください。すでに記事化済み、またはユーザーが Phycock を優先したい場合は、ScheduleEntry 集約か FullCalendar 色表示修正のどちらにするか確認してください。

## 注意点

- `articles/*.md` を公開状態にする前に `/article-review` を実行すること。
- `published: true` への変更は、ユーザーが公開を明示した時だけ行うこと。
- 親プロジェクト `F:/Dropbox/Job-hunting/` は、公開後アクションが必要な時以外は触らないこと。
- Phycock の記事では、支援機関・障害・体調に関する説明を必要以上に具体化しないこと。
- Lapras スコアは結果であり、記事の主目的は読者に役立つ一次体験の共有に置くこと。

## 次の具体アクション

1. `drafts/` と `articles/` に既存記事や構成メモがないか確認する。
2. 第1候補で進めるなら `/article-plan` 相当で `drafts/youtube-data-api-quota-exhaustion.md` を作る。
3. Phycock を先に進めるなら、`phycock-schedule-entry-consolidation` か `fullcalendar-event-color-rendering` のどちらを選ぶかユーザーに確認する。
4. 構成作成後、Skill Graph の `self/goals.md` または handoff に次アクションを残す。

## 2026-05-10 Codex 追記: ScheduleEntry 集約記事の初稿

- 作成ファイル: `articles/phycock-schedule-entry-consolidation.md`
- 状態: `published: false`
- レビュー依頼: ClaudeCode に公開前レビューを依頼したい
- 見てほしい点:
  - `Schedule` / `ScheduleEntry` 集約判断の説明が読み手に伝わるか
  - Phycock 固有のセンシティブな文脈が記事本文に出ていないか
  - 実コード引用が長すぎないか、Zenn 記事として読みやすいか
  - 公開前に `/article-review` 相当の文体・必須要素チェックを通すこと

## 2026-05-11 Codex 追記: ScheduleEntry 集約記事レビュー完了

- 対象: `articles/phycock-schedule-entry-consolidation.md`
- 状態: `published: false`
- レビュー状況: ユーザーより ClaudeCode レビュー終了の連絡あり
- Codex 側確認:
  - フロントマター、文体NG語、守秘義務キーワード、コードブロック言語指定を確認済み
  - Phycock固有のセンシティブな文脈は本文で一般化済み
- レビュー指摘への対応:
  - タイトルに `ASP.NET Core MVC` を追加して検索性を改善
  - テーブル削除時の注意点を `:::message alert` で強調
  - コードブロックへファイル名を付与
  - 見出し統合は任意指摘のため、現状の読みやすさを優先して未実施
- 次: ユーザーが公開を明示したら `published: true` に変更し、公開後に `drafts/published-log.md` を更新する

## 2026-05-18 ClaudeCode 追記: MVC Helper移植記事 LAPRASレビュー対応

- 対象: `articles/devnext-mvc-helper-extensions.md`（`published: true`、公開済み）
- 元コメント: LAPRAS レビュー（総合3.9 / 論理性3.5 / 実用性4.0 / 読みやすさ4.0 / 独自性4.5 / 明確性3.5）
- 元コメント要点:
  - 論理性: 各セクション間の関連性が薄く独立した問題解決として読まれる。統一テーマがほしい
  - 明確性/読みやすさ: TemplateInfo / GetFullHtmlFieldName など内部の仕組みの必要性が簡潔すぎ
  - 実用性: Helperのテスト方法・複雑シナリオの注意点があると良い（任意改善）
- 反映した差分:
  - 「はじめに」に統一テーマ（POST で値が戻る「フォームの契約」を Helper 側で守る）を1段落追加
  - チェックボックス Helper 節に TemplateInfo / GetFullHtmlFieldName の役割補足を1文追加
- 反映しなかった指摘と理由:
  - テスト方法の追記: コード大幅増となり体験記事の軸がぶれるため見送り
  - 独自性・総合の称賛: 講評のため本文非反映
- 修正後チェック: 文体NG語スキャン（ヒットなし）、`git diff` でコメント対応範囲内（4 insertions / 2 deletions、コード変更なし）を確認
- 次: 公開済み記事のため、再 push はユーザーの公開指示を待つ

## 2026-05-18 ClaudeCode 追記: MVC Helper移植記事 Codex レビュー依頼

- 対象ファイル: `articles/devnext-mvc-helper-extensions.md`
- 状態: `published: true`（公開済み・LAPRASレビューコメント対応後、未 push）
- 主編集者: ClaudeCode（LAPRASレビュー対応の本文修正）
- レビュー担当: Codex
- レビュー観点（外部レビューコメント対応後の再レビュー）:
  - 元コメント要点: LAPRAS レビュー（論理性3.5=セクション間の関連性が薄い／明確性3.5=TemplateInfo等の必要性が簡潔すぎ）
  - 反映差分: 「はじめに」に統一テーマ1段落、チェックボックス節に TemplateInfo/GetFullHtmlFieldName 補足1文
  - 未反映: テスト方法の追記（体験記事の軸がぶれるため見送り）
- 確認したいこと: 追記がコメント対応の範囲に収まり本文の流れを崩していないか／統一テーマの説明が各セクションと整合しているか／文体NG語・守秘・事実整合に問題がないか
- 触ってよい範囲: 対象記事のみ
- `published: true` は既に公開済み。再 push はユーザー指示に従う（ClaudeCode 側で勝手に push しない）

## 2026-05-18 Codex 追記: MVC Helper移植記事 ClaudeCode更新レビュー

- 対象: `articles/devnext-mvc-helper-extensions.md`
- レビュー結果:
  - ClaudeCode 追記の「フォームの契約」テーマは、Helper の戻り値、選択部品、`PartialFor`、まとめの流れと整合している
  - `TemplateInfo.GetFullHtmlFieldName` の補足は、LAPRAS コメントの明確性指摘に対して有効。ただし1文が長いため、読みやすさをさらに上げるなら2文に分けてもよい
  - 文体NG語、守秘義務キーワード、コードブロック言語指定、文字数、GitHubリンク、はじめに/まとめを確認し、重大な問題なし
- 軽微な残課題への対応:
  - 参考リンクに、リンク先が何を補う資料かの短い説明を追記済み
- 公開可否判断: 🟢 ClaudeCode のコメント対応差分と Codex の小修正を再 push 可能
- 次: ユーザーが再 push を指示する場合、通常の公開済み記事更新として進める
