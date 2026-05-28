# Zenn 記事候補と既存記事の対応表

候補リストと公開済み記事・下書きの対応を管理する。新しい記事候補を選ぶ前と、記事公開後の `/article-publish` 相当の作業で更新する。

## 状態の定義

| 状態 | 意味 |
| --- | --- |
| 公開済み | `articles/<slug>.md` が `published: true` で、Zenn 実サイトでも 200 / タイトル一致を確認済み |
| 公開指定済み / Zenn未確認 | ローカルでは `published: true` だが、Zenn 実サイトでは 200 を確認できていない |
| 下書きあり | `drafts/<slug>.md` または `articles/<slug>.md` の `published: false` がある |
| 公開保留 | 一度公開候補になったが、確認事項が残るため `published: false` で止めている |
| 一部カバー | 近い記事はあるが、候補の主題としては未完了 |
| 未着手 | 対応する公開記事・下書きがない |
| 保留 | 方針上、今は書かない |

## 既存記事リスト

`articles/*.md` の `published: true` と Zenn 実サイトの直接アクセス結果を分けて管理する。Zenn 側が 403 を返すものは、ローカル上は公開指定済みでも実公開未確認として扱う。

最終突き合わせ: 2026-05-20

| ローカル公開日 | slug | タイトル | 候補対応 | Zenn実サイト | テーマ系統 |
| --- | --- | --- | --- | --- | --- |
| 2026-05-10 | `devnext-mvc-helper-extensions` | ASP.NET MVCの自作HelperをASP.NET Coreに移植した話 | 派生記事 | 200 / 公開確認 | ASP.NET Core / Razor Helper |
| 2026-05-10 | `fullcalendar-event-color-rendering` | FullCalendarでDTOの色が反映されない時に見たこと | 派生記事 | 200 / 公開確認 | ASP.NET Core / FullCalendar |
| 2026-05-11 | `youtube-data-api-rss-quota-reduction` | YouTube Data API のクォータ枯渇を RSS で99%削減した話 | 候補H | 200 / 公開確認 | YouTube Data API / API クォータ |
| 2026-05-11 | `claude-code-workflow-evolution` | Claude Code運用を数ヶ月で見直してrulesとskillsに分けた話 | 候補N | 200 / 公開確認 | Claude Code / AI協調開発 |
| 2026-05-13 | `electron-smartscreen-oss-distribution` | 未署名Electronアプリを配布するとSmartScreenで止まる問題に向き合った話 | 候補I | 200 / 公開確認 | Electron / Windows 配布 |
| 2026-05-13 | `youtom-introduction` | 推しの配信予定を見逃さないために YouTom を作った | 派生記事 | 200 / 公開確認 | Electron / React / YouTube |
| 2026-05-17 | `codex-claude-skill-graph-worklog` | AIとの設計判断をMy-Skill-Graphに残して再利用する | 候補O | 200 / 公開確認 | AI協調開発 / ナレッジ管理 |
| 2026-05-17 | `cross-agent-harness-introduction` | CodexとClaude Codeの共同作業をcross-agent-harnessに切り出した | 派生記事 | 200 / 公開確認 | AI協調開発 / OSS |
| 2026-05-19 | `cross-agent-harness-automation` | CodexとClaude Codeを相互呼び出しするハーネスを組んだ | 派生記事 | 200 / 公開確認 | AI協調開発 / 自動化 |
| 2026-05-28 | `zenn-article-repo-workflow` | Zenn記事をリポジトリ管理して公開前レビューまで回した実践メモ | 候補Q | 実公開未確認 | Zenn / 記事運用 / AI協調レビュー |
| 2026-05-28 | `ai-agent-session-brief-memory` | AIエージェントの長期記憶を軽く保つためにsession-briefを作った | 候補S | 実公開未確認 | AI協調開発 / ナレッジ管理 / コンテキスト圧縮 |
| 公開ログ未記録 | `aspnet-core-identity-to-commonlibrary` | ASP.NET Core移行でIdentityエンティティを共通化した判断 | 候補M | 200 / 公開確認 | ASP.NET Core / Identity |
| 公開ログ未記録 | `ai-cross-review-handoff-workflow` | AI 2 台クロスレビューで技術記事の盲点を拾う | 派生記事 | 200 / 公開確認 | AI協調開発 / 記事レビュー |

## Qiita 公開記事リスト

Zenn 原文をベースに Qiita 向けへ一部加筆・再構成した記事。`qiita/public/*.md` を Qiita CLI 管理対象とし、`id` / `updated_at` / `published` 状態は Qiita CLI の結果を優先する。

最終突き合わせ: 2026-05-20

| 公開日 | slug | タイトル | 元記事 | Qiita公開状態 | URL |
| --- | --- | --- | --- | --- | --- |
| 2026-05-20 | `youtube-data-api-rss-quota-reduction` | YouTube Data API のクォータ枯渇を RSS で避ける設計にした話 | `articles/youtube-data-api-rss-quota-reduction.md` | 公開確認 | https://qiita.com/harnesswinner/items/e2d5dba192540222d8d5 |
| 2026-05-20 | `youtom-introduction` | YouTubeの配信予定を追うWindowsアプリ YouTom を作った | `articles/youtom-introduction.md` | 公開確認 | https://qiita.com/harnesswinner/items/52c94119fed2aba20f7e |

## 公開保留・下書きリスト

`npx zenn list:articles` には出るが、`published: false` のため公開済み候補からは除外する。

| slug | タイトル | 候補対応 | 状態 | 次の扱い |
| --- | --- | --- | --- | --- |
| `phycock-schedule-entry-consolidation` | ASP.NET Core MVCでScheduleEntryに寄せた設計判断 | 候補J | 公開保留 | リタリコ確認が取れたら公開判断する |
| `youtube-playlist-date-sorter-introduction` | YouTubeプレイリストを投稿日順に見るChrome拡張を作った話 | 候補K 派生 | 下書きあり | 実装判断に絞った構成メモから本文化する |

## 候補対応表

次に構成・執筆対象として選ぶのは、原則として `未着手` / `一部カバー` / `下書きあり（未公開）` の行だけにする。`公開済み` は選定対象外として扱い、追加で書く場合は既存記事との差分が明確な派生テーマだけにする。

| 候補 | 元テーマ | 状態 | 対応記事・下書き | 次の扱い |
| --- | --- | --- | --- | --- |
| H | YouTube Data API のクォータ枯渇と戦った話 | 公開済み | `articles/youtube-data-api-rss-quota-reduction.md` | 選定対象外。追加で書くなら候補Wのように別切り口にする |
| I | 未署名 Electron アプリの SmartScreen 問題と OSS 配布の現実 | 公開済み | `articles/electron-smartscreen-oss-distribution.md` | 選定対象外。公開後運用は候補Rへ分離 |
| J | Phycock で Schedule を削除して ScheduleEntry に集約した設計判断 | 公開保留（下書き） | `articles/phycock-schedule-entry-consolidation.md` | リタリコ確認が取れたら published: true に戻して公開する |
| K | Chrome 拡張 Manifest V3 移行で遭遇した実装課題 | 下書きあり | `drafts/youtube-playlist-date-sorter-introduction.md` | Manifest V3 移行の網羅ではなく、YouTube プレイリスト投稿日順ソート拡張の実装判断に絞って構成中 |
| L | うつ病療養中のエンジニアが Claude Code で個人開発を続ける方法 | 未着手 | なし | 障害情報リスクがあるため慎重に扱う |
| M | DevNet と DevNext で同じ機能を別実装にした設計判断の差分 | 公開済み | `articles/aspnet-core-identity-to-commonlibrary.md` | 選定対象外。事実確認ルールの反省込みで完了扱い |
| N | Claude Code 導入から数ヶ月の運用変遷 | 公開済み | `articles/claude-code-workflow-evolution.md` | 選定対象外。派生は cross-agent / skill graph 側で扱う |
| O | My-Skill-Graph で設計判断を再利用する運用 | 公開済み | `articles/codex-claude-skill-graph-worklog.md` | 選定対象外。軽量化の話は候補Sへ分離 |
| P | ASP.NET Core MVC で入力フォームの責務を ViewModel に寄せた話 | 未着手 | なし | DevNext / Phycock の実コード確認が必要 |
| Q | Zenn 記事をリポジトリ管理して公開前レビューまで自動化した話 | 公開指定済み / Zenn未確認 | `articles/zenn-article-repo-workflow.md` / `drafts/zenn-article-repo-workflow.md` | Zenn実サイトの200確認後に公開済みへ更新 |
| 派生 | Codex / Claude Code 共同作業ハーネスの切り出し | 公開済み | `articles/cross-agent-harness-introduction.md` | 選定対象外。自動呼び出しは別派生で公開済み |
| 派生 | Codex / Claude Code 相互呼び出しハーネス | 公開済み | `articles/cross-agent-harness-automation.md` / `drafts/cross-agent-harness-automation.md` | 選定対象外 |
| R | Electron 個人開発アプリを公開した後に必要だった運用メモ | 一部カバー | `articles/electron-smartscreen-oss-distribution.md` / `articles/youtom-introduction.md` | README / Releases / 署名方針の運用に絞れば別記事化可能 |
| S | AI エージェント用 Skill Graph を軽量化した話 | 公開指定済み / Zenn未確認 | `articles/ai-agent-session-brief-memory.md` | Zenn実サイトの200確認後に公開済みへ更新 |
| T | ASP.NET Core の認証必須ページを Playwright で PDF 化した話 | 未着手 | なし | Phycock の実装確認後、PDF / Chart.js / Cookie 転送の詰まりに絞る |
| U | Phycock で IDOR 対策を Service 層に置いた話 | 未着手 | なし | 個人データを扱うため守秘・医療情報の一般化を前提にする |
| V | ライブ開始通知を状態遷移だけで出すようにした話 | 未着手 | なし | YouTom の軽め記事候補。起動時通知連打の回避に絞る |
| W | YouTube メンバー限定配信を RSS と API の二段構えで扱った話 | 一部カバー | `articles/youtube-data-api-rss-quota-reduction.md` | 候補Hとの差分として、メン限・存在しない API・クォータ上限に絞れば別記事化可能 |
| X | AI 活用証跡をプロジェクト単位で整理して面接説明に使う話 | 未着手 | なし | note「AI使った就活がソシャゲじみてきた。」のZenn派生。就活雑感ではなく、証跡管理・レビュー・記事候補化の運用に絞る |

## 次に選ぶ候補ショートリスト

公開済み・公開保留を除いた、次回の構成作成で優先的に見る候補。新しい記事を選ぶときはまずここを見て、必要なら候補対応表へ戻る。

| 優先 | 候補 | 理由 | 事前確認 |
| --- | --- | --- | --- |
| 1 | Q: Zenn 記事リポジトリ運用 | 既に記事ファイルと構成メモがあり、公開前レビューへ進めやすい | `articles/zenn-article-repo-workflow.md` の公開前チェック |
| 2 | S: Skill Graph 軽量化 | 公開済みの候補Oと近いが、token肥大と起動入口圧縮という別の詰まりで書ける | vault の個人情報・ローカルパスを出さない |
| 3 | T: Playwright PDF 化 | ASP.NET Core / 認証 / Chart.js / PDF で技術深度が出る | Phycock 実コードとテスト、守秘範囲の確認 |
| 4 | U: IDOR 対策を Service 層へ置いた話 | セキュリティ判断として説明価値が高い | 実コード・回帰テスト・個人データ表現の一般化 |
| 5 | V / W / R | 軽めの YouTom 派生。短期で本数を増やす候補 | 既存 H / I / YouTom 紹介記事との差分確認 |

## Skill Graph 由来の追加候補

2026-05-20 に My-Skill-Graph の decisions / strategies から追加抽出した候補。既存公開記事と重複しないよう、公開済みテーマの焼き直しではなく「まだ記事化していない詰まり」と「判断軸」が明確なものだけ残す。

### 候補S: AI エージェント用 Skill Graph を軽量化した話

- **ソース**: `[[SkillGraph起動入口をsession-briefに分けたのはコンテキスト肥大を防ぐため]]` / `[[SkillGraph軽量化はAIエージェント運用記事の題材になる]]`
- **書ける理由**: Codex の token 使用量が膨らんだ実体験から、起動時 orientation、`self/goals.md`、`decisions/index.md`、handoff の分離に至った判断を説明できる
- **想定読者**: AI コーディングエージェントに長期記憶を持たせたいが、コンテキスト肥大に困っている個人開発者
- **想定文字数**: 3000〜4000字 / 想定執筆時間: 4〜5時間
- **障害情報リスク**: 低（vault 内の就活・個人情報・ローカルパスを出さない）
- **OK切り口（これだけ書く）**: 「記憶を増やしたら起動時コンテキストが重くなった → session-brief と archive に分けた → 長期記憶と作業速度を両立した」
- **NG切り口（書かない）**: 「Obsidian の使い方」「AI 記憶術の一般論」

### 候補T: ASP.NET Core の認証必須ページを Playwright で PDF 化した話

- **ソース**: `[[PlaywrightサーバーPDFは認証Cookie転送＋print=1パターンで実装したのは保守性のため]]`
- **書ける理由**: 認証 Cookie 転送、`?print=1`、Chart.js 描画待機、改ページ制御など、実装時に詰まりやすい判断がまとまっている
- **想定読者**: ASP.NET Core MVC でグラフ付き画面を PDF 出力したいエンジニア
- **想定文字数**: 3000〜4000字 / 想定執筆時間: 5〜6時間
- **障害情報リスク**: 低（Phycock の利用者文脈は一般化する）
- **OK切り口（これだけ書く）**: 「HTML をそのまま PDF にしたかったが認証と JS 描画で詰まった → Cookie 転送 + print mode + chartsReady で解決した」
- **NG切り口（書かない）**: 「Playwright 入門」「PDF 出力ライブラリ比較」
- **事前確認**: 個人開発リポジトリの実コードに触れるため、構成前に `article-fact-check.md` のチェックリストを通す

### 候補U: Phycock で IDOR 対策を Service 層に置いた話

- **ソース**: `[[PhycockのIDOR対策をサービス層に置いたのは画面とリポジトリの責務を分離するため]]`
- **書ける理由**: 体調・睡眠・予定のような個人データで、Controller / Service / Repository のどこに所有者チェックを置くかという判断軸を説明できる
- **想定読者**: ASP.NET Core MVC でユーザー別データを扱い、編集・削除時の認可漏れを避けたいエンジニア
- **想定文字数**: 2500〜3500字 / 想定執筆時間: 4〜5時間
- **障害情報リスク**: 中（体調管理・支援文脈は抽象化し、個人情報や施設名を出さない）
- **OK切り口（これだけ書く）**: 「Repository の userId 条件だけでは不安が残った → Service のユースケース境界で所有者と Admin 例外を判定した」
- **NG切り口（書かない）**: 「ASP.NET Core 認可の網羅解説」「医療・支援データ運用の一般論」
- **事前確認**: 認可・セキュリティ記事になるため、実コードとテストの存在確認を先に行う

### 候補V: ライブ開始通知を状態遷移だけで出すようにした話

- **ソース**: `[[ライブ開始通知を遷移時だけ出すのは起動時の通知連打を避けるため]]` / `[[起動時live通知の暴発防止に初回ロード完了フラグを使うのは空配列baselineを避けるため]]`
- **書ける理由**: 起動時に既存 live を通知すると通知連打になる、というユーザー体験の失敗から実装判断を説明できる
- **想定読者**: Electron / React で状態変化に応じた通知を実装している個人開発者
- **想定文字数**: 2000〜3000字 / 想定執筆時間: 3〜4時間
- **障害情報リスク**: なし
- **OK切り口（これだけ書く）**: 「現在状態を通知するとノイズになった → 初回状態を baseline にして、遷移だけ通知した」
- **NG切り口（書かない）**: 「通知 API の使い方」「React hook 入門」

### 候補W: YouTube メンバー限定配信を RSS と API の二段構えで扱った話

- **ソース**: `[[メンバーシップ取得にsearch.listを使いRSSと分離したのはRSSにメンバー限定動画が含まれないため]]`
- **書ける理由**: 既存の RSS クォータ削減記事では通常配信が中心だったため、メンバー限定配信だけを別取得にした判断を独立して説明できる
- **想定読者**: YouTube Data API と RSS を併用して、クォータ上限内で配信予定を取得したい個人開発者
- **想定文字数**: 2500〜3500字 / 想定執筆時間: 4〜5時間
- **障害情報リスク**: なし
- **OK切り口（これだけ書く）**: 「RSS にはメンバー限定動画が出ない → 全件 API 取得はクォータ破綻する → 登録チャンネルだけ search.list に分離した」
- **NG切り口（書かない）**: 「YouTube Data API 入門」「候補Hの焼き直し」

### 候補X: AI 活用証跡をプロジェクト単位で整理して面接説明に使う話

- **ソース**: note 下書き `note/drafts/ai-job-hunting-as-social-game.md` / `[[AI活用証跡をプロジェクト単位で整理するのは就活説明力を上げるため]]` / `[[AI就活のソシャゲ化はnoteで共感を取りZennで技術証跡に分けるべき]]`
- **書ける理由**: AI を使った就活体験の中から、面接で「AIに作らせた」ではなく「自分が設計・判断・検証した」と説明するための証跡整理を技術運用として切り出せる
- **想定読者**: AI コーディングエージェントを使った成果物を、ポートフォリオや面接で説明できる形に整理したい個人開発者
- **想定文字数**: 3000〜4000字 / 想定執筆時間: 4〜5時間
- **障害情報リスク**: 中（就活状況・応募先・個人事情は出さず、公開成果物と運用だけに限定する）
- **OK切り口（これだけ書く）**: 「AI作業ログが散らばる → プロジェクト単位で証跡を束ねる → 記事候補と面接説明に変換できるようにした」
- **NG切り口（書かない）**: 「AI就活の雑感」「媒体論だけの記事」「Lapras / Findy のスコア攻略法」

## 保留候補

候補A〜G の SQL Server チューニング・ASP.NET Core 解説系は、体験記事としての課題と判断軸が弱いため保留する。実務復帰後に一次情報と失敗例が揃ったら見直す。

## 更新ルール

- 新しい構成メモを作ったら、対応候補を `下書きあり` に更新する。
- `articles/<slug>.md` を `published: true` にしたら、公開日・slug・タイトルを `既存記事リスト` に追加し、対応候補を `公開指定済み` に更新する。
- 公開後に `https://zenn.dev/harness/articles/<slug>` へ直接アクセスし、HTTP 200 と記事タイトル一致を確認できたら `Zenn実サイト` を `200 / 公開確認` に更新する。
- 403 / 404 / タイトル不一致の場合は `Zenn実サイト` を `実公開未確認` のまま残し、`drafts/published-log.md` の確認予定にも入れる。
- 候補外の派生記事を公開した場合も、`既存記事リスト` に追加して `候補対応` を `派生記事` にする。
- 既存候補と重複する新規案を出す前に、この表で公開済み・下書き済みを確認する。
