# ClaudeCode 引き継ぎ資料

最終更新: 2026-05-10  
対象プロジェクト: `H:/ClaudeCode/技術記事`

## 2026-05-10 追記（候補Nの記事作成・ClaudeCodeレビュー依頼）

Codex が候補N「Claude Code 導入から数ヶ月の運用変遷」を記事化しました。

- 対象記事: `articles/claude-code-workflow-evolution.md`
- 状態: `published: false`
- 作成者: Codex
- 主題: Claude Code 運用を、単一 `CLAUDE.md` から `rules/`・project rules・skills・handoff・Skill Graph へ分けていった変遷
- レビュー担当: ClaudeCode
- 触ってよい範囲: 原則 `articles/claude-code-workflow-evolution.md` のみ
- `published: true` はユーザーが明示するまで変更しないこと

レビュー観点:

- 「導入直後 → 詰まり → 分割/skill化 → Codex併用 → handoff/Skill Graph」の時系列が自然か
- 公式ドキュメント焼き直しではなく、体験ベースの記事として成立しているか
- Claude Code / Codex / Opus の記述が宣伝調または断定過剰になっていないか
- `.claude` や `settings.json` 由来の機密・個人情報・ローカル事情が出すぎていないか
- GitHubリンク、5行以上のコード例、文体ルール、topics、`published: false` を満たしているか

## 2026-05-10 追記（ClaudeCode による相互レビュー実施）

ClaudeCode が `articles/` 配下の4記事に対して `/article-review` 相当の公開前レビューを実施しました。

対象記事と作成者（ユーザー確認済み）:

- `articles/youtube-data-api-rss-quota-reduction.md` — Codex 作成
- `articles/fullcalendar-event-color-rendering.md` — Codex 作成
- `articles/youtom-introduction.md` — Codex 作成
- `articles/devnext-mvc-helper-extensions.md` — Codex 作成

レビュー結果と修正対応:

- **fullcalendar-event-color-rendering.md**: 福祉ドメイン用語（`ActivityType.IndividualTraining` / `ProgramType.ApplicationInterview` 等）が透けるリスクを ClaudeCode が指摘。汎用業務カレンダー名（`EventCategory.Work` / `EventCategory.Meeting` / `EventCategory.Training` / `WorkType.Conference` / `WorkType.Focused` / `WorkType.Other` 等）に置換済み。`isAtHome` → `isRemote` も合わせて変更。
- **youtom-introduction.md**: `topics` の日本語タグ `個人開発` を `indie` に変更。簡易/フルモードのファーストタッチ所要時間の比較を1行追加（検証証跡の補強）。
- **youtube-data-api-rss-quota-reduction.md**: 末尾の締め文を「クォータ削減のヒントになれば。」から、自分の手癖が変わった体験ベースの締めに修正。
- **devnext-mvc-helper-extensions.md**: 文体・必須要素・守秘義務の重大指摘なし。

公開ゲート4条件（`.claude/rules/cross-agent-review.md`）の状態:

| 記事 | ①セルフ | ②相互レビュー記録 | ③重大指摘 | ④ユーザー指示 |
|------|--------|----------------|-----------|--------------|
| youtube-data-api-rss-quota-reduction | ✅ | ✅（本書） | 🟢 残なし | ❌ 未指示 |
| fullcalendar-event-color-rendering | ✅ | ✅（本書） | 🟢 残なし | ❌ 未指示 |
| youtom-introduction | ✅ | ✅（本書） | 🟢 残なし | ❌ 未指示 |
| devnext-mvc-helper-extensions | ✅ | ✅（本書） | 🟢 残なし | ❌ 未指示 |

次アクション:

- ユーザーの公開順決定を待つ（推奨順は `ops/handoffs/2026-05-10-zenn-article-candidates-codex.md` の Article Draft Progress を参照）
- ユーザーの明示後に `published: true` へ変更してコミット&push
- 公開後は `/article-publish` を実行

## 2026-05-10 追記

Codex が記事作成後の相互レビュー運用をハーネス化しました。

- 追加ルール: `.claude/rules/cross-agent-review.md`
- 更新箇所:
  - `AGENTS.md`
  - `CLAUDE.md`
  - `.claude/rules/zenn-workflow.md`
  - `.claude/rules/writing-process.md`
  - `.agents/skills/article-review/SKILL.md`
  - `.claude/skills/article-review/SKILL.md`
- 今後の標準運用:
  - Codex が記事を作成したら、ClaudeCode へのレビュー依頼を handoff に残す
  - ClaudeCode が記事を作成したら、Codex へのレビュー依頼を handoff に残す
  - `/article-review` では相互レビュー記録の有無も確認する
  - `published: true` は、相互レビュー記録・重大指摘なし・ユーザーの公開指示が揃うまで変更しない

Codex が FullCalendar 系候補を記事化しました。

- 記事: `articles/fullcalendar-event-color-rendering.md`
- 状態: `published: false`
- 次: `/article-review` 相当で文体・必須要素・守秘義務を確認し、必要ならタイトルと導入を調整する

Codex が Youtom 紹介記事も作成しました。

- 記事: `articles/youtom-introduction.md`
- 状態: `published: false`
- 次: ClaudeCode で公開前レビューに回す
- レビュー観点:
  - 紹介記事として宣伝寄りになりすぎていないか
  - 「課題 → 判断 → 実装 → 使いどころ」の流れが自然か
  - 簡易モード（RSS）とフルモード（YouTube Data API）の説明に誤解がないか
  - 実コード例・GitHub リンク・体験/判断軸・参考リンクが Zenn 記事要件を満たしているか
  - `published: true` はユーザーが明示するまで変更しない

## 目的

このリポジトリは、細川 良（GitHub: `harness17`）の Zenn 技術記事プロジェクトです。

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
