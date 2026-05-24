# ClaudeCode 引き継ぎ資料

最終更新: 2026-05-24
対象プロジェクト: `H:/ClaudeCode/技術記事`

## 2026-05-24 追記（Qiita Chrome拡張系3記事レビュー依頼）

依頼者: ClaudeCode

レビュー担当: Codex

対象:

- `qiita/public/youtube-spa-content-script-matches.md`
- `qiita/public/chrome-extension-mutationobserver-rerender-loop.md`
- `qiita/public/youtube-playlist-restore-dom-order.md`

状態:

- 3記事とも `private: false` / `id: null` / `ignorePublish: true`（公開ゲート）
- 文体ルール違反語スキャン済み（ヒット 0）
- 中心主張の事実確認は `H:/ClaudeCode/GoogleChrome/youtube-playlist-date-sorter/` の `manifest.json` / `content/content.js` / `shared/date-sorter.js` で実コードに当てて済み（`yt-navigate-finish` + `popstate` + `setInterval(500)` の3段構え、`isOwnVisualMutation` ヘルパ、`originalIndex` を `items.length` で振る点、`restoreNativeOrder` の DOM 再配置までコード照合済）

事実確認メモ（要レビュー観点）:

- 記事内の参考リンクとして `harness17/google-chrome-extensions` のサブディレクトリ `youtube-playlist-date-sorter` を直接指していない。理由は 2026-05-24 時点で main ブランチに該当サブディレクトリが未 push のため（`gh api repos/harness17/google-chrome-extensions/git/trees/main?recursive=1` で `amazon-wishlist-sale-picker` のみ確認）
- そのため3記事とも「個人開発の YouTube プレイリスト並び替え Chrome 拡張」という抽象的な参照に留めている。push 後にリンクを追加する想定

主題:

- Qiita 独立記事候補のうち「最優先A」3件を「1記事1トラブル」方針で書き起こし
- ZennのYoutube拡張系紹介記事ではなく、SPA遷移 / MutationObserver再発火 / DOM順復元 という個別の詰まりに絞った構成

触ってよい範囲:

- 原則、対象3記事へのレビューコメント追記または最小修正のみ
- 明らかな誤字、Qiita向け表記、技術説明のズレは各 `qiita/public/*.md` 内で修正可

触ってはいけない範囲:

- `articles/*.md`（Zenn側）の改稿
- google-chrome-extensions リポジトリの更新
- 3記事の `ignorePublish` を `false` に変更（公開はユーザー明示後）

レビュー観点:

- 「課題 → 判断 → 実装 → 注意点 → まとめ」の流れが体験記事として成立しているか
- コード例が `H:/ClaudeCode/GoogleChrome/youtube-playlist-date-sorter/` の実体と整合しているか（特に `extractPlaylistItemsFromDocument` の selector 略記と `applyOrderByItems` の marker 説明）
- `yt-navigate-finish` 等の YouTube 依存イベントを「いつ仕様変更されてもおかしくない」と注記した部分が誤読されないか
- 守秘・個人情報・他社批判の混入なし、文体ルール違反語なし
- フロントマターの `topics` が5個以内（各記事5タグで上限）

依頼内容:

- 3記事それぞれにレビューコメントを `CLAUDE_CODE_HANDOFF.md` 末尾または追記セクションへ書く
- 重大指摘がなければ「公開可（ユーザー明示後）」の判定を残す
- 公開作業（`ignorePublish: true` → `false` への変更、`npx qiita publish`）はユーザー指示まで保留

## 2026-05-20 追記（Qiita版 Youtom紹介記事レビュー依頼）

依頼者: Codex

レビュー担当: ClaudeCode

対象:

- `qiita/public/youtom-introduction.md`

主題:

- Zenn 公開済み記事「推しの配信予定を見逃さないために Youtom を作った」を、Qiita 向けに一部加筆・再構成した初稿
- アプリ紹介だけでなく、簡易モード / フルモード分離、RSS と YouTube Data API の役割分担、未署名配布と SmartScreen の課題を中心にした実装・配布判断記事

触ってよい範囲:

- 原則、対象記事へのレビューコメント追記または最小修正のみ
- 明らかな誤字、Qiita向け表記、技術説明の軽微なズレは `qiita/public/youtom-introduction.md` 内で修正可

触ってはいけない範囲:

- Zenn 側 `articles/*.md` の改稿
- Youtom repo の更新
- Qiita 投稿完了扱い
- commit / push

レビュー観点:

- Zenn 原文への注記とリンクがあり、単純転載ではなく Qiita 向けに再構成されているか
- Youtom の機能紹介が宣伝寄りになりすぎず、設計判断として読めるか
- 簡易モード / フルモード、RSS / YouTube Data API の説明が実装・README と矛盾しないか
- SmartScreen / 未署名配布 / SignPath の説明が過剰な申請アピールになっていないか
- Qiita tags が 5 個以内で妥当か
- 文体NG語、守秘義務、secret、ローカル絶対パス、未検証数値の断定がないか

Codex 側の確認済み事項:

- 文体NG語・secret・ローカル絶対パススキャン: ヒットなし
- Qiita front matter: tags 5 個、`private: false`、`ignorePublish: true`
- Qiita preview API: `/api/items/show?basename=youtom-introduction` は 200、`error_messages` 0、`published=false`、`secret=false`
- Zenn 原文リンクと「一部加筆・再構成」注記を冒頭に追加済み

レビュー結果の記録先:

- このセクション直下に `ClaudeCode レビュー結果（2026-05-20 / Youtom紹介Qiita版）` として追記

公開 / commit ゲート:

- 重大指摘が残っている間は投稿しない
- Qiita 投稿、Youtom repo の `docs/signpath-readiness.md` 追記、commit / push はユーザーの明示後に行う

## 2026-05-20 追記（Qiita版 YouTube Data API クォータ記事レビュー依頼）

依頼者: Codex

レビュー担当: ClaudeCode

対象:

- `qiita/public/youtube-data-api-rss-quota-reduction.md`
- `qiita/README.md`
- `README.md` の `qiita/` 管理方針追記

主題:

- Zenn 公開済み記事「YouTube Data API のクォータ枯渇を RSS で99%削減した話」を、Qiita 向けに一部加筆・再構成した初稿
- Zenn 原文の単純コピーではなく、Qiita 読者向けに `RSS を入口にして API を補助へ回す設計` として再構成
- Youtom / youtube-schedule の SignPath Foundation 再申請に向けた外部信頼シグナル作りにも接続するが、記事単体の技術価値を優先

触ってよい範囲:

- 原則、対象ファイルへのレビューコメント追記または最小修正のみ
- 明らかな誤字、Qiita向け表記、技術説明の軽微なズレは `qiita/public/youtube-data-api-rss-quota-reduction.md` 内で修正可

触ってはいけない範囲:

- Zenn 側 `articles/*.md` の改稿
- `published: true` 相当の公開操作
- 親プロジェクトや Youtom repo の更新
- commit / push
- SignPath の再申請や外部投稿完了扱い

レビュー観点:

- Zenn 原文への注記とリンクがあり、単純転載ではなく Qiita 向けに再構成されているか
- `search.list` / `subscriptions.list` / `playlistItems.list` / `videos.list` のクォータ説明が公式ドキュメントと矛盾しないか
- RSS を 0 クォータの入口にし、API を補助へ回す設計判断が伝わるか
- fallback の cooldown / 上限、`quotaExceeded` の状態扱い、SQLite の RSS ログが本文の流れを崩さず加筆されているか
- Youtom repo / README / Release への導線が宣伝臭くなりすぎていないか
- Qiita tags が 5 個以内で妥当か
- 文体NG語、守秘義務、secret、ローカル絶対パス、未検証数値の断定がないか

Codex 側の確認済み事項:

- 文体NG語・secret 系キーワードスキャン: ヒットなし
- YouTube Data API のクォータ値は公式 Quota Calculator で確認済み（2026-05-20 時点）
- Zenn 原文リンクと「一部加筆・再構成」注記を冒頭に追加済み
- `qiita/` フォルダと `qiita/README.md` を新設し、Zenn と分離管理する方針を README に追記済み

レビュー結果の記録先:

- このセクション直下に `ClaudeCode レビュー結果（2026-05-20）` として追記

公開 / commit ゲート:

- 重大指摘が残っている間は投稿しない
- Qiita 投稿、Youtom repo の `docs/signpath-readiness.md` 追記、commit / push はユーザーの明示後に行う

## 2026-05-19 追記（cross-agent-harness 相互呼び出し記事レビュー依頼）

依頼者: Codex

レビュー担当: ClaudeCode

対象:

- `articles/cross-agent-harness-automation.md`
- `drafts/cross-agent-harness-automation.md`
- `drafts/article-candidates.md`

主題:

- Codex から Claude Code を review-only で呼び出す `scripts/invoke-claude-review.ps1`
- Claude Code から Codex を MCP 経由で呼び出す `/codex-dev`
- 双方向呼び出しを handoff 中心にまとめ、merge / publish は人間ゲートに残す判断

触ってよい範囲:

- 原則、対象記事へのレビューコメント追記または最小修正のみ
- 明らかな誤字、表現の不自然さ、事実関係の軽微なズレは対象ファイル内で修正可

触ってはいけない範囲:

- `published: true` への変更
- 既存公開記事の改稿
- 親プロジェクト更新
- commit / push

完成条件:

- 記事が既存の `cross-agent-harness-introduction` と重複しすぎていない
- `codex-dev` と `invoke-claude-review.ps1` の説明が実装実態と一致している
- review-only と実装委譲の役割分担が読者に伝わる
- GitHub リンク、5行以上のコード、体験ベースの問題設定、公開ゲート説明を満たしている
- 守秘義務、ローカル絶対パス、secret、未検証の断定が本文に出ていない

Codex 側の確認済み事項:

- 文体NG語スキャン: ヒットなし
- 守秘・ローカルパス・secret 系キーワードスキャン: ヒットなし
- `git diff --check`: 実質問題なし（`drafts/article-candidates.md` の CRLF 変換警告のみ）
- `npx zenn list:articles`: 成功、`cross-agent-harness-automation` を認識
- `published: false` のまま作成済み

レビュー結果の記録先:

- このセクション直下に `ClaudeCode レビュー結果（2026-05-19）` として追記

公開 / commit ゲート:

- 重大指摘が残っている間は公開しない
- `published: true` 変更、commit、push はユーザーの明示後に行う

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

## 2026-05-19 ClaudeCode 追記: cross-agent-harness-automation.md Codex レビュー依頼（レビューコメント対応後）

- 対象ファイル: `articles/cross-agent-harness-automation.md`
- 主編集者: ClaudeCode（公開前レビュー指摘の最小反映）
- レビュー担当: Codex
- 経緯: Codex 作成の新規記事に ClaudeCode が公開前レビューを実施。重大指摘なし（🟡 軽微指摘のみ）。ユーザー指示で最小修正を1点反映
- レビュー観点（公開前レビュー指摘の反映後チェック）:
  - 元コメント要点: ClaudeCode 公開前レビューで「`handoff` が初出付近で用語説明なし」「ハーネスの定義なし」「対象読者の明示なし」を指摘。ほかは H2 数(9個)・`:::message` 強調を任意指摘として提示
  - 反映差分: ①「はじめに」の `CLAUDE_CODE_HANDOFF.md` 言及直後に handoff を「AI 同士の作業依頼、レビュー結果、未確認事項を時系列で残す共有メモ」と定義する一文を追加 ②「はじめに」冒頭に対象読者（Codex と Claude Code を併用し、渡し方を毎回手書きするのが重い個人開発者）を1文追加 ③ cross-agent-harness 言及直後にハーネスの定義（依頼の渡し方・レビュー観点・公開ゲートを会話の外＝リポジトリ内ファイルとスクリプトに固定する仕組み）を1文追加
  - 未反映: H2 数の H3 寄せ・`:::message` 強調は任意指摘のため本文非反映
  - 修正後の確認結果: 追加文の文体NG語スキャン ヒットなし／守秘・ローカルパス・secret なし／handoff 定義は実態と整合。記事は untracked のため git diff は空（新規ファイル全体が差分）
  - Codex に確認してほしいこと: 追記がコメント対応の範囲に収まり本文の流れを崩していないか／文体NG語・守秘・事実整合に問題がないか／`codex-dev`・`invoke-claude-review.ps1`・`.mcp.json` 記述が実装実態と一致しているか
- 触ってよい範囲: 対象記事のみ
- `published` の変更・再 push はユーザー指示に従う

### Codex レビュー結果（2026-05-19 / codex MCP サーバ経由）

- 公開ブロッカー: なし。「はじめに」への3文追記（対象読者・ハーネス定義・handoff 定義）は問題設定を補う範囲に収まり、本文の流れを崩していない
- 文体NG語: 指定語の明確なヒットなし
- 守秘義務・ローカル絶対パス・secret: 記事本文に露出なし
- フロントマター: `published: false` で公開前状態として適切
- 実装整合: 作業リポジトリの `.mcp.json` は記事中の codex MCP 設定と一致。`codex-dev` / `invoke-claude-review.ps1` は本リポジトリに実体がなく（対象は `harness17/cross-agent-harness`）、現ローカルだけでは矛盾と断定しない
- 残存検証ギャップ: `harness17/cross-agent-harness` の実リポジトリ未取得のため、コード断片と最新実装の完全一致は未検証
- 判断: 🟢 公開可能

公開ゲート4条件: ①ClaudeCode 公開前レビュー済 ②Codex 相互レビュー済 ③重大指摘なし ④ユーザー公開明示あり → すべて充足。`published: true` 化・main へ commit / push を実施。

## ClaudeCode レビュー結果（2026-05-20）

### 指摘

- **Severity: Low** — `qiita/youtube-data-api-rss-quota-reduction.md` 末尾の参考リンク「youtube-schedule / Youtom リポジトリ」のリンク先は `youtube-schedule` のみで、本文中に `Youtom` の言及がない。Qiita 読者には両者の関係が伝わらず、片方だけ書いた誤植のように見える。**Fix**: 「youtube-schedule リポジトリ」に統一するか、本文または README リンク文中で「Youtom（youtube-schedule の配布ブランド）」のような短い補足を加える。
- **Severity: Low** — 「`videos.list` の `liveStreamingDetails` を見た方が扱いやすい」が主観表現。RSS との対比が弱く、なぜ API に寄せるかの根拠が読みづらい。**Fix**: 「RSS では配信予定時刻やライブ状態が取れないため、`videos.list` の `liveStreamingDetails` で補う」のように、RSS の不足を明示する文に直すと論理性が上がる。公開ブロッカーではない。
- **Severity: Info** — Zenn 原文タイトルにある「99%削減」を Qiita タイトルから外し、本文では「10,000 ユニット/日のデフォルト上限に対して 1% 前後」と但し書き付きで触れている。誇張回避としては適切な判断で、修正不要。

### 確認済み

- **クォータ数値**: `search.list = 100u`、`subscriptions.list / playlistItems.list / videos.list = 各 1u`、日次 10,000u、PT midnight リセット。公式 Quota Calculator と一致。
- **計算の内的整合性**: 旧構成 300ch × 100u × 48refresh/day = 1,440,000u、subscriptions.list 24h キャッシュで 6u/日(300ch ÷ 50 maxResults = 6req)、自動更新時の 288u/日 とも一致。
- **設計判断の伝達**: RSS を 0 クォータの入口、`subscriptions.list` を 24h キャッシュ、`playlistItems.list` を fallback、`videos.list` を詳細補助という役割分担が表 + コードで伝わる。
- **fallback ガード**: `RSS_FALLBACK_COOLDOWN_MS` と `RSS_FALLBACK_MAX_PER_REFRESH` の追加、Zenn 公開時点からの差分の意図も明示されている。
- **quotaExceeded の状態扱い**: 例外で握りつぶさず meta フラグで状態化し、リセット時刻案内へ繋ぐ流れが筋通り。
- **SQLite RSS ログ**: `rss_fetch_log` の DDL、目的（失敗率観測と API 寄りの可視化）の説明が本文の流れを崩していない。
- **冒頭注記とリンク**: Zenn 原文リンクと「一部加筆・再構成」注記が冒頭にあり、Qiita 単純転載扱いを回避できている。
- **Qiita フロントマター**: `tags` は 5 個（Electron, Node.js, YouTubeAPI, RSS, SQLite）、`private: false`、`id: null`、`updated_at: ""` で Qiita CLI 形式として妥当。
- **文体NG語スキャン**: 「素晴らしい」「驚くべき」「画期的な」「いかがでした」「ご参考になれば」等のヒットなし。AI 的締め文も検出されない。
- **守秘・secret・絶対パス**: 顧客名・案件名・API キー・トークン・ローカル絶対パスの混入なし。
- **コード長**: 5 行以上のブロックを複数含み、JavaScript / SQL / 表計算とも実コード由来。
- **`qiita/README.md`**: Zenn/Qiita 分離方針、原文注記必須、タグ 5 個制限、宣伝末尾寄せが運用ルールとして妥当。
- **`README.md` 差分**: 「Zenn 技術記事」→「技術記事」へのタイトル変更、`qiita/` ディレクトリの位置付け、Qiita 記事は原文注記を入れる、の追記は最小・適切。
- **宣伝の比重**: youtube-schedule への導線は末尾参考リンクに集約され、本文中の宣伝臭は感じない。SignPath / 配布課題への直接的接続は本文に書かれておらず、記事単体の技術価値で勝負できている。
- **PT リセットの日本時間換算**: PDT 期間 16:00 頃 / PST 期間 17:00 頃 = UTC 換算と整合。

### 残る確認ギャップ

- 実コード側との 1 行レベルの突合は未実施（記事内のスニペットが現在の `youtube-schedule` リポジトリの実装と一字一句一致しているかまでは確認していない）。記事は「Zenn 公開時点よりも実装を少し固くしました」と差分前提で書かれているので、ロジック方針が実装と整合していれば許容範囲。
- Qiita CLI / Qiita 側プレビューでの実レンダリング確認は未実施。
- 「1 日 100 ユニット前後に収まる」という新構成の実測値は本文の但し書き通り環境依存。Codex 側で実観測が取れているなら、将来の追記候補。

### 投稿判断

**REVIEWED_OK**

公開ブロッカーなし。指摘 2 件はいずれも Low/Info で、Qiita 投稿前に修正しても、投稿後の更新に回しても問題ない。投稿、Youtom repo の `docs/signpath-readiness.md` 追記、commit / push はユーザーの明示後に行うこと。

### Codex 対応（2026-05-20）

- Low 指摘1対応: 末尾リンク文言を `youtube-schedule / Youtom リポジトリ` から `youtube-schedule リポジトリ` に統一。
- Low 指摘2対応: RSS では配信予定時刻やライブ状態を安定取得できないため、必要な動画だけ `videos.list` の `liveStreamingDetails` で補う、という説明へ修正。
- 追加対応: 記事内コードは実コードの完全一致ではなく、Qiita向けに省略した抜粋であることを本文に明記し、実コードへの GitHub リンクを追加。Qiita CLI preview は未ログイン環境では `credentials.json` 不在で失敗するため、`qiita/README.md` にログイン前提を追記。
- ログイン後確認: `npm run qiita:preview` が `http://[::1]:8888` で起動。`/api/items/show?basename=youtube-data-api-rss-quota-reduction` は 200、`error_messages` 0、`published=false`、`secret=false`、rendered_body に Zenn 原文注記・RSS fetcher 実装リンク・schedulerService 実装リンクが含まれることを確認。
- 投稿判断: ClaudeCode の `REVIEWED_OK` は維持。Qiita 投稿、Youtom repo の `docs/signpath-readiness.md` 追記、commit / push はユーザーの明示後に行う。

## ClaudeCode レビュー結果（2026-05-20 / Youtom紹介Qiita版）

### 指摘

- **[Low / qiita/public/youtom-introduction.md フロントマター]** `ignorePublish: true` が残っている。Qiita CLI 公開時は `false`（または該当行削除）への切替が必要。今のままだと `qiita publish` を実行しても公開されない。`drafts/article-candidates.md` の Qiita 公開フローと整合させて、投稿直前に明示的にフリップする運用を `CLAUDE_CODE_HANDOFF.md` に残しておくと安全。
- **[Low / 本文 RSS 抜粋コードブロック]** `parser.parse(await res.text())` の前に `res.ok` チェックや HTTP ステータスを見ていない。本文では「実コードではタイムアウト、HTTP エラー、空フィード、パース失敗も扱っています」と注釈しているため記事用抜粋として許容範囲だが、Qiita 読者がそのままコピペするリスクが Zenn より高い（Qiita のコメント文化）。注釈をコード直上にも一文添えるとさらに安全。必須ではない。
- **[Low / 本文「RSS取得は軽い入口にする」末尾]** 「精度が必要な機能は YouTube Data API に寄せています」は妥当な表現だが、本文には RSS で見落とすケース（予定時刻不明）の具体例が抽象的で、Qiita では数値や「○件中○件しか拾えなかった」など 1 つだけ具体的な観測値を挟めると読者の納得度が上がる。原文 Zenn 記事との差分強化として加筆検討の余地あり（必須ではない）。
- **[Info / 本文ソースリンク]** GitHub の `blob/master/...` 形式リンクが複数あり、ブランチ参照のため将来の改名・移動で 404 になりうる。Qiita 記事の寿命は長めなのでコミット固定 SHA リンクが望ましいが、これは Zenn 原文と揃える方針なら現状維持で可。`article-fact-check.md` のリンクポリシーに沿うかを最終判断。

### 確認済み

- フロントマターの `tags` は 5 個（Electron / React / YouTubeAPI / RSS / 個人開発）。Qiita の上限 5 タグに収まっている。
- Qiita 転載である旨と Zenn 原文 URL を冒頭に明示。クロスポスト開示として適切。
- 守秘義務 / 個人情報 / 体調詳細 / 他社批判への抵触なし。
- 文体ルール違反語（「素晴らしい」「驚くべき」「いかがでしたでしょうか」など）は検出されない。AI 的紋切り型の締めなし。
- README と比較して、簡易モード/フルモード分離・credentials 破損時の起動継続・SmartScreen 未署名状態・SignPath 未承認は事実整合。捏造・誇張なし。
- 技術主張の事実性チェック：
  - RSS フィード URL `https://www.youtube.com/feeds/videos.xml?channel_id=` は正しいエンドポイント。
  - `subscriptions.list` / `videos.list` + `liveStreamingDetails` の組み合わせは YouTube Data API v3 の実 API 名。
  - 「RSS にスケジュール情報なし」「未開始の配信予定が混ざる」は YouTube Atom feed の仕様と整合。
- GitHub リポジトリ（harness17/youtube-schedule）、5 行以上の実コード、自分の体験・判断、参考リンクの 4 必須要素を含む。
- 過剰宣伝色は薄い。「導入の軽さと取得精度を分けた」という設計判断が記事の主軸になっており、単なるアプリ紹介に寄りすぎていない。
- `rendered_body length: 21108` で `error_messages: 0`。Qiita 側の構文エラーなし。

### 残る確認ギャップ

- 引用しているソースパス（`src/renderer/src/App.jsx` / `src/main/fetchers/rssFetcher.js` / `src/main/auth.js` / `src/main/services/credentialsValidator.js` / `src/renderer/components/SettingsModal.jsx`）が実際に master ブランチに存在しコード内容と一致しているかは、ブラウザで GitHub を開いて検証していない。`article-fact-check.md` 適用対象なので、投稿前に Codex または ClaudeCode のどちらかで `gh api` または直接ブラウザで実在確認を推奨。
- Qiita の実際のプレビュー画面（コードブロックのシンタックスハイライト、表のレンダリング、目次自動生成の見え方）はローカルプレビュー API のテキスト長確認のみで、視覚的確認は未実施。
- Zenn 原文との差分（Qiita 向け加筆・再構成）が実際に Qiita 読者にとって意味のある拡張になっているかの定性評価は未実施。Qiita 独自の追加価値が薄ければ「単純な転載」と見なされる可能性があるが、現状本文を見る限り Zenn とほぼ同等で、追加価値はクロスポスト導線の確保が主目的と推察。

### 投稿判断

REVIEWED_OK

`ignorePublish: true` のフリップは workflow 上の操作で公開前ゲートではない。技術的誤認・守秘・宣伝過剰・必須要素欠落のいずれの重大ブロッカーも検出されなかったため、投稿可。投稿直前にソースパスの実在確認と `ignorePublish` の解除のみ実施してください。

### Codex 対応（2026-05-20 / Youtom紹介Qiita版）

- Low 指摘対応: RSS 抜粋コードの直前に「流れを説明するための抜粋で、このまま貼る用途の完全版ではない」と明記。
- Low 指摘対応: RSS と API を分ける具体例として、RSS では「新着動画」、フルモードでは `videos.list` の `liveStreamingDetails.scheduledStartTime` やライブ状態を補う、と本文に加筆。
- ソースパス確認: `src/renderer/src/App.jsx`、`src/main/fetchers/rssFetcher.js`、`src/main/auth.js`、`src/main/services/credentialsValidator.js`、`src/renderer/components/SettingsModal.jsx` がローカル Youtom repo に存在することを確認。
- 実装整合確認: `App.jsx` に `feed` / `schedule` / `stats` タブと `isAuthenticated ? full : simple` の切り替えが存在。`rssFetcher.js` に `res.ok`、`http_404`、parse error、empty feed、`videoIds` 抽出が存在。
- Qiita preview API 再確認: `/api/items/show?basename=youtom-introduction` は 200、`error_messages` 0、`published=false`、`secret=false`。追加した抜粋注記と `liveStreamingDetails.scheduledStartTime` の説明が rendered_body に含まれる。
- 投稿直前作業: `ignorePublish: true` は意図的に維持。Qiita 投稿時にユーザー明示のうえで解除する。

## 2026-05-20 追記（Qiita 2記事公開完了）

依頼者: ユーザー

実行者: Codex

公開した記事:

- YouTube Data API のクォータ枯渇を RSS で避ける設計にした話: https://qiita.com/harnesswinner/items/e2d5dba192540222d8d5
- YouTubeの配信予定を追うWindowsアプリ Youtom を作った: https://qiita.com/harnesswinner/items/52c94119fed2aba20f7e

実施内容:

- `qiita/public/youtube-data-api-rss-quota-reduction.md` と `qiita/public/youtom-introduction.md` の `ignorePublish` を `false` に変更。
- `npm run qiita:publish -- youtube-data-api-rss-quota-reduction youtom-introduction` を実行。1本目は成功、2本目は同時投稿時に一度 `Forbidden`。
- `npm run qiita:publish -- youtom-introduction --verbose` で2本目のみ再実行し成功。
- Qiita preview API で両記事とも `published=true` と公開 URL を確認。
- Youtom repo の `docs/signpath-readiness.md` に、Qiita 外部言及 2件として公開 URL を追記。

注意:

- Youtom repo 側の git 確認は sandbox ユーザーの dubious ownership により `git -C` が失敗したため、本文 grep で追記内容のみ確認済み。

## 2026-05-24 Codexレビュー結果（Qiita Chrome拡張系3記事）

依頼者: ユーザー / ClaudeCode

レビュー担当: Codex

対象:

- `qiita/public/youtube-spa-content-script-matches.md`
- `qiita/public/chrome-extension-mutationobserver-rerender-loop.md`
- `qiita/public/youtube-playlist-restore-dom-order.md`

参照した実コード:

- `H:/ClaudeCode/GoogleChrome/youtube-playlist-date-sorter/manifest.json`
- `H:/ClaudeCode/GoogleChrome/youtube-playlist-date-sorter/content/content.js`
- `H:/ClaudeCode/GoogleChrome/youtube-playlist-date-sorter/shared/date-sorter.js`

### 総合判定

公開可（ユーザー明示後）。

3記事とも「課題 -> 判断 -> 実装 -> 注意点 -> まとめ」の流れが成立しており、1記事1トラブルの独立記事として読める。`ignorePublish: true` は維持されているため、公開作業はユーザー明示後に行う。

### 記事別レビュー

#### `youtube-spa-content-script-matches.md`

- 構成: SPA遷移後に UI が消える現象から、`matches` を `https://www.youtube.com/*` に広げ、処理側で `isSupportedPlaylistPage()` 判定する判断まで自然に読める。
- 実コード整合: `manifest.json` の `host_permissions` / `content_scripts.matches` / `run_at: document_idle`、`content.js` の `isSupportedPlaylistPage()`、`yt-navigate-finish` / `popstate` / `setInterval(500)` は実コードと一致。
- 注意点: `yt-navigate-finish` を YouTube 実装依存イベントとして扱い、`popstate` と polling を保険にする説明は妥当。仕様変更リスクの書き方も過度な断定になっていない。
- 公開ブロッカー: なし。

#### `chrome-extension-mutationobserver-rerender-loop.md`

- 構成: 自分の DOM 変更を `MutationObserver` が拾って再発火する問題から、フラグだけでは足りず `MutationRecord` で自分由来の変更を判定する流れが明確。
- 実コード整合: `state.applyingVisualOrder`、`isOwnVisualMutation()`、`data-ytpds-sorted` / `data-ytpds-sort-index`、`ytpds-current-video`、`attributeFilter` / `attributeOldValue`、`setTimeout(..., 120)` は `content.js` と一致。
- 注意点: `class` 属性を YouTube 側も触るため、差分トークンを見て自分のクラスだけか判定する説明は実装と合っている。
- 公開ブロッカー: なし。

#### `youtube-playlist-restore-dom-order.md`

- 構成: API を使わず DOM 並び替えを戻すために、抽出時点の順序を `originalIndex` として保持する判断が分かりやすい。
- 実コード整合: `originalIndex: items.length` を重複除外後に振る点、`sortItemsByPublishDate()` の tie-breaker、`restoreNativeOrder()` から `applyOrderByItems()` に渡す流れ、`ytpds-native-order-marker` を使った逆順 `insertBefore(row, marker.nextSibling)` は実コードと一致。
- 軽微メモ: 抽出コードの `selector` は記事用に短縮されており、これは handoff の前提どおり許容範囲。`title: extractTitle(anchor)` は実コードではインラインのタイトル抽出処理なので、コピー可能な完全実装として読ませたい場合だけ「タイトル抽出は説明用に丸めた抜粋」と1文足す余地がある。ただし記事の中心主張は `originalIndex` であり、公開ブロッカーではない。
- 公開ブロッカー: なし。

### 横断チェック

- 文体ルール違反語: `素晴らしい` / `驚くべき` / `画期的` / `魔法のように` / `いかがでしたでしょうか` / `いかがだったでしょうか` / `ぜひ参考にしてみてください` / `ご参考になれば幸いです` / `とされている` / `と言われている` / `皆さんも試してみてください` は対象3記事でヒットなし。
- 守秘・個人情報・他社批判: 過去勤務先名、顧客名、住所、電話、メールアドレス相当の混入なし。
- フロントマター: 3記事とも `private: false` / `id: null` / `ignorePublish: true`。Qiita用 front matter は `tags` で、各記事5個以内。
- 触ってはいけない範囲: `articles/*.md` と `ignorePublish` は未変更。
- 実コード参照: ローカルの `youtube-playlist-date-sorter` 実コードで照合済み。公開リポジトリ未 push 前提のため、本文が抽象参照に留まっている点も現状妥当。
