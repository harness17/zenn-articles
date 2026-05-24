# Qiita 独立記事候補

Zenn 記事の再投稿ではなく、Qiita 向けに独立して書ける「1記事1トラブル」候補を管理する。

## 方針

- Zenn: 体験全体、設計判断、作ったものの背景、学び
- Qiita: 詰まった1点、原因、再現条件、解決コード、注意点
- 既存 Zenn と同じ題材でも、Qiita では検索される具体トラブルへ切り出す
- 単なる網羅解説ではなく、自分が詰まった実装・運用上の問題を起点にする
- 実コードに触れる候補は、執筆前に該当リポジトリの事実確認を行う

## 優先度基準（A / B / C）

候補を追加するときは以下の基準で振り分ける。判断に迷ったら 1 段下げる。

| 優先 | 意味 | 満たすべき条件 | 想定執筆コスト |
| --- | --- | --- | --- |
| A | ソースが手元にあり、書く価値も明確 | 次のすべてを満たす：(1) 実体験のソース（実コード・設定ファイル・自作ルール・handoff・コミット履歴のいずれか）が手元にある／(2) 中心主張が一文で言える／(3) 守秘義務リスクが軽微（顧客名・案件名・体調詳細を出さずに書ける） | 0.5〜2日（執筆前の実コード確認1ステップを含む） |
| B | ソースの所在または主題の独立性が要確認 | 次のいずれかに該当：(1) ソースはあるが対象ファイル・依存・バージョンの特定が未了／(2) ルール文や下書きを読み直して構成を組み直す必要がある／(3) 既存 Qiita / Zenn 記事との差分整理が未完 | 2〜3日 |
| C | 保留・補助・判断待ち | 次のいずれかに該当：(1) 実装が未完了・運用ログが浅い／(2) 主題が小さく単独記事化が弱い／(3) 守秘義務・障害情報など **書き方の判断自体が必要**／(4) 公開後の運用結果待ち | 判断待ち（書かない可能性あり） |

**A と B の境界:**
- 「○○実コード確認後」「○○実装確認後」「○○ルール文確認後」などの 1 ステップ確認は **A の通常プロセスに含まれる**（A から外す理由にはならない）
- 「○○との差分整理」「○○の追加調査」など、**書き始める前に方向性判断が要る**ものは B
- 「実装が未完了」「公開後に整理」「守秘判断が必要」は C

**運用ルール:**
- 守秘義務リスク（顧客名・案件名・体調詳細）の **書き方判断が残る** ものは C で扱う（軽微な伏字で済むものは A 可）
- 既存記事との重複が疑われ、差分の見通しが立たないものは B 以下で扱う
- 1 つの記事を書き終えたら、参照した実コード・ルールから派生する候補を A に昇格できないか見直す
- 新規候補追加時、既存候補の振り分けが基準とズレていないか **追加と同じセッションで** 見直す

## 既存 Qiita 公開記事

| 公開日 | slug | タイトル | 元記事 | URL |
| --- | --- | --- | --- | --- |
| 2026-05-20 | `youtube-data-api-rss-quota-reduction` | YouTube Data API のクォータ枯渇を RSS で避ける設計にした話 | `articles/youtube-data-api-rss-quota-reduction.md` | https://qiita.com/harnesswinner/items/e2d5dba192540222d8d5 |
| 2026-05-20 | `youtom-introduction` | YouTubeの配信予定を追うWindowsアプリ Youtom を作った | `articles/youtom-introduction.md` | https://qiita.com/harnesswinner/items/52c94119fed2aba20f7e |
| 2026-05-24 | `youtube-playlist-restore-dom-order` | YouTubeプレイリストのDOM順を一度保存して通常順に戻す実装 | （独立記事） | https://qiita.com/harnesswinner/items/fa3a124e5fa50229a887 |
| 2026-05-24 | `youtube-spa-content-script-matches` | Chrome拡張でYouTubeのSPA遷移後にcontent scriptが効かない問題を直した | （独立記事） | https://qiita.com/harnesswinner/items/3bac40961a0b5ff20dee |
| 2026-05-24 | `chrome-extension-mutationobserver-rerender-loop` | Chrome拡張でDOMを並び替えた後にMutationObserverが再発火する問題への対処 | （独立記事） | https://qiita.com/harnesswinner/items/5429f56b3a8e23675703 |
| 2026-05-24 | `claude-md-import-split-rules` | Claude CodeのCLAUDE.mdを@importで分割してトピック別ルールに整理した | （独立記事） | https://qiita.com/harnesswinner/items/6678320489deec25113a |
| 2026-05-24 | `ai-edit-surgical-changes-rule` | AIに「修正して」と頼むと無関係コードまで触られる問題をSurgical Changesルールで抑えた | （独立記事） | レート制限により公開保留中（記事1公開後すぐ再試行→失敗）|

## 最優先候補

> **Phycock 関連候補は、ユーザーからの公開許可が下りるまで C（保留）扱い。** 該当 slug: `playwright-wait-chartjs-before-pdf` / `aspnet-core-playwright-auth-cookie-pdf` / `aspnet-core-print-mode-pdf` / `aspnet-core-mvc-viewmodel-input-responsibility` / `aspnet-core-idor-service-layer` / `aspnet-core-scheduleentry-controller-simplify` / `aspnet-core-tempdata-not-persisted`

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| C | PlaywrightでChart.jsの描画完了を待ってからPDF化する | ASP.NET Core PDF 化全体ではなく、JSグラフ待機に絞る | `playwright-wait-chartjs-before-pdf` | Phycock 公開許可待ち |
| C | ASP.NET CoreのログインCookieをサーバー側Playwrightに渡す実装 | PDF出力の認証問題だけを切り出す | `aspnet-core-playwright-auth-cookie-pdf` | Phycock 公開許可待ち |
| B | ElectronアプリでSmartScreen警告が出たときに確認したこと | SmartScreen記事の再投稿ではなく、確認手順と判断材料に絞る | `electron-smartscreen-checklist` | 既存記事との差分整理が必要 |
| C | AIエージェントの長期記憶を軽くするためにsession-briefを作った | Skill Graph体験記事ではなく、起動時コンテキスト圧縮の運用メモ | `ai-agent-session-brief-memory` | 個人情報・ローカルパスの伏せ方判断が必要 |

## Chrome拡張 / YouTube 系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| A | Manifest V3でYouTubeページのURL変更を検知する実装メモ | MV3一般論ではなく、YouTubeのSPAでのURL監視に絞る | `manifest-v3-youtube-url-change-detection` | 実装確認後 |
| A | YouTubeの動画カードに投稿日バッジを後付けするときに見たDOM構造 | DOM解析・セレクタ設計のメモ | `youtube-video-card-date-badge-dom` | 実装確認後 |
| B | YouTube Data APIを使わずに投稿日順ソートした理由と限界 | APIキー不要設計の技術メモ | `youtube-sort-without-data-api` | Zenn下書きとの差分整理が必要 |
| A | Chrome拡張のcontent scriptを広く注入して処理側でURL判定する | 権限変更の注意点とガード条件に絞る | `chrome-extension-wide-matches-url-guard` | 実装確認後 |
| B | YouTubeのplaylistページでDOM順と取得データを照合してからUIを出す | 誤ソート防止の照合処理だけ扱う | `youtube-playlist-dom-data-validation` | 実装確認後 |
| B | YouTubeのSPAでpopupの設定変更をcontent scriptへ反映する | popup / content script / storage の連携メモ | `chrome-extension-popup-content-settings` | 実装確認後 |
| B | Chrome拡張で保存済み設定を即時反映する最小構成 | `chrome.storage` 周辺に絞る | `chrome-extension-storage-settings-apply` | 実装確認後 |
| B | Chrome拡張のパネルを最小化できるようにした理由と実装 | UI改善の小ネタとして独立 | `chrome-extension-page-panel-minimize` | 実装確認後 |
| B | YouTubeページ上に追加UIを置くときに邪魔にならない位置を考えた | 技術とUXの小記事 | `youtube-extension-overlay-ui-position` | 実装確認後 |
| C | Chrome Web Store提出前にzipへ含めるもの・含めないものを確認した | 公開作業メモ | `chrome-web-store-zip-checklist` | 公開後に整理 |
| C | Manifestのmatches変更でChrome Web Store審査時に確認したこと | 権限変更と審査確認の運用メモ | `chrome-web-store-matches-permission-review` | 審査提出後 |

## Electron / Windows 配布系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| B | ElectronアプリでSmartScreen警告が出たときに確認したこと | 配布の現実ではなく、確認手順に絞る | `electron-smartscreen-checklist` | 既存記事との差分整理が必要 |
| B | Windows向けElectronアプリにコード署名する前に整理した判断軸 | 署名方式・費用・OSS配布の判断材料に絞る | `electron-windows-code-signing-decision` | 追加調査（署名方式・費用比較）が必要 |
| B | electron-builderでWindows配布物を作るときに詰まった設定 | 具体設定メモとして扱う | `electron-builder-windows-distribution-settings` | 実装確認後 |
| B | GitHub Releasesで個人開発アプリを配布するときのREADME導線 | 技術寄りの運用メモ | `github-releases-app-readme-flow` | README確認後 |
| B | 未署名アプリの配布でユーザーに説明すべきこと | SmartScreen記事の補足 | `unsigned-electron-app-user-notice` | 文章設計候補 |
| C | Electronアプリの自動更新を入れる前に決めること | 実装済みでなければ候補止まり | `electron-auto-update-before-implementation` | 保留 |

## YouTube API / RSS 系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| B | YouTube RSSで取得できる情報とData APIが必要になる情報を分ける | 既存Qiitaと近いため、比較表特化なら可 | `youtube-rss-vs-data-api-fields` | 既存Qiitaとの差分整理が必要 |
| B | YouTube Data APIのクォータ消費をざっくり見積もる方法 | 既存記事の補助線 | `youtube-data-api-quota-estimation` | 既存Qiitaとの差分整理が必要 |
| B | YouTubeのメンバー限定配信がRSSに出ない前提で取得経路を分ける | 候補WをQiita向けに切る | `youtube-membership-rss-data-api-split` | 実装確認後 |
| B | RSS取得を通常ルート、API取得を例外ルートに分けた実装判断 | quota / 取得漏れ / 更新頻度に絞る | `youtube-rss-normal-api-exception-route` | 実装確認後 |
| B | YouTube配信予定の取得でキャッシュを入れる前に考えたこと | quota / 更新頻度 / 手動更新の切り分け | `youtube-schedule-cache-quota-design` | 実装確認後 |
| C | YouTube APIのエラー時にユーザーへ何を表示するか | エラー表示設計の小記事 | `youtube-api-error-message-design` | 実装確認後 |

## ASP.NET Core / Phycock 系

> **このセクション全件は Phycock 公開許可待ちのため C 扱い。** ユーザー許可が下りた時点で個別に再判定する。

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| C | ASP.NET Core MVCで認証必須ページをPlaywrightでPDF化した | 候補Tより、Cookie転送手順に絞る | `aspnet-core-playwright-auth-cookie-pdf` | Phycock 公開許可待ち |
| C | PlaywrightでChart.jsの描画完了を待ってからPDF化する | JS描画待機に絞る | `playwright-wait-chartjs-before-pdf` | Phycock 公開許可待ち |
| C | ASP.NET CoreのログインCookieをサーバー側Playwrightに渡す実装 | 認証付きPDF出力の実装メモ | `aspnet-core-playwright-auth-cookie-pdf` | Phycock 公開許可待ち |
| C | PDF出力用に`?print=1`を用意して画面表示と分けた | 画面表示と印刷表示の分離判断 | `aspnet-core-print-mode-pdf` | Phycock 公開許可待ち |
| C | FullCalendarでDTOの色が反映されないときに確認したこと | 既存ZennのQiita切り出し候補 | `fullcalendar-event-color-dto-check` | Phycock 公開許可待ち＋既存記事との差分整理 |
| C | ASP.NET Core MVCでViewModelに入力責務を寄せると何が楽になるか | 候補Pの一部 | `aspnet-core-mvc-viewmodel-input-responsibility` | Phycock 公開許可待ち |
| C | ユーザー別データのIDOR対策をService層で見るようにした | 候補Uより、認可漏れ防止の実装メモ | `aspnet-core-idor-service-layer` | Phycock 公開許可待ち＋守秘判断必要 |
| C | ScheduleとScheduleEntryを統合した後にControllerがどう単純化したか | コード差分が明確なら可 | `aspnet-core-scheduleentry-controller-simplify` | Phycock 公開許可待ち |

## C# / ASP.NET Core 実装系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| C | ASP.NET Core MVCで`TempData`が次のリクエストに残らないときに見たこと | Session設定とCookie要件の最小確認手順 | `aspnet-core-tempdata-not-persisted` | Phycock 公開許可待ち |
| A | Razor部分ビューに別ViewModelを渡すときの`@model`型不一致エラー | `PartialAsync`の引数型ミスマッチ事例 | `razor-partial-view-model-type-mismatch` | 実装確認後 |
| A | EF Coreで`Include`を忘れてN+1になっていたのをログで気づいた | ロギング設定とSQL確認手順に絞る | `efcore-include-forget-n-plus-1-detect` | 実コード確認後 |
| A | ASP.NET Core IdentityのRoleを初回起動時にseedする最小コード | `RoleManager`/`UserManager`の取得タイミングに絞る | `aspnet-core-identity-role-seed-on-startup` | 実コード確認後 |
| A | `DateTime`をUTCで保存しビュー側でJSTに変換する設計に統一した | `DateTimeKind.Unspecified`混入を防ぐ実装メモ | `aspnet-core-datetime-utc-to-jst-policy` | 実コード確認後 |
| B | Ajax POSTで`__RequestVerificationToken`が落ちて403になる | antiforgeryトークンの送り方3パターン | `aspnet-core-ajax-antiforgery-token` | 実装確認後 |
| B | `DbContext`をシングルトン化してハマったので`Scoped`に戻した | DIライフタイムの選び方メモ | `efcore-dbcontext-lifetime-scoped` | 実装確認後 |
| B | ASP.NET Coreで`appsettings.Development.json`を本番に混ぜないための設定分離 | 環境別設定の最小ルール | `aspnet-core-appsettings-env-separation` | 設定確認後 |
| B | サーバー側バリデーションをクライアント検証と二重化したときの実装パターン | `[Required]`属性 + ModelState確認 | `aspnet-core-server-validation-double-check` | 実装確認後 |
| B | Razorで静的ファイルがブラウザキャッシュされ更新されない問題への対処 | `asp-append-version`とビルドハッシュの選択 | `aspnet-core-static-file-cache-bust` | 実装確認後 |
| C | カスタムModelBinderを書く前に標準バインダで足りるか確認した話 | バインダ拡張の判断軸 | `aspnet-core-modelbinder-before-custom` | 保留 |

## SQL Server / EF Core 実装系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| A | `IDENT_CURRENT`と`SCOPE_IDENTITY`を間違えて他セッションのIDを取った話 | 関数の違いと再現条件に絞る | `sqlserver-ident-current-vs-scope-identity` | 体験整理後 |
| A | インデックスを貼ったのにスキャンされていたsargableでないクエリ | `WHERE`句の関数化が原因のパターン | `sqlserver-non-sargable-where-clause` | 体験整理後 |
| A | `NVARCHAR`と`VARCHAR`の暗黙変換でindexが無効になった | 列型と引数型の不一致を見つける手順 | `sqlserver-implicit-conversion-index-bypass` | 体験整理後 |
| B | EF Coreで生成されたSQLを見て手書きSQLに切り替えた判断 | LINQ表現の限界と切替基準 | `efcore-generated-sql-switch-raw` | 体験整理後 |
| B | 一時テーブルとテーブル変数を使い分けた基準 | 件数・統計情報・スコープの判断軸 | `sqlserver-temp-table-vs-table-variable` | 体験整理後 |
| C | パラメータスニッフィング対策で`OPTION (RECOMPILE)`を入れた基準 | 副作用とコストの整理 | `sqlserver-parameter-sniffing-recompile` | 保留 |

## JavaScript / フロント実装系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| A | Chart.jsのcanvasがコンテナリサイズで再描画されない | `responsive` / `maintainAspectRatio`の組み合わせ | `chartjs-canvas-resize-not-redraw` | 実装確認後 |
| A | `fetch`が302を自動追跡してCORSで死ぬ問題 | `redirect: "manual"`に切り替えた判断 | `fetch-302-redirect-cors-manual` | 実装確認後 |
| A | `JSON.stringify`で`Date`がUTC文字列になりサーバーで日付ズレ | クライアント送信前にローカル文字列化する判断 | `json-stringify-date-utc-shift` | 実装確認後 |
| B | `await`を1箇所忘れてエラーが握り潰される事故 | `no-floating-promises`相当の検知方法 | `js-missing-await-silent-failure` | 体験整理後 |
| B | `localStorage`の5MB制限に気づかず書き込みエラーになった | 容量計測と退避戦略 | `localstorage-5mb-quota-overflow` | 実装確認後 |
| B | FullCalendarの`eventColor`がDTO経由で反映されない条件 | プロパティ名のキャメル/パスカル不一致 | `fullcalendar-eventcolor-dto-naming` | 既存記事と差分整理 |
| C | `Intl.DateTimeFormat`でJST固定にしてサーバー/クライアント差を消した | フォーマット統一の判断 | `intl-datetimeformat-jst-fixed` | 実装確認後 |

## Node / Windows 開発環境系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| A | `npm install`がWindowsで`EPERM`になるときに最初に確認すること | ファイルロック元プロセスの特定手順 | `npm-install-eperm-windows-lockcheck` | 体験整理後 |
| A | ESM / CJS混在プロジェクトで`require is not defined`になった | `package.json`の`type`と拡張子の対応表 | `node-esm-cjs-mixed-require-error` | 実装確認後 |
| A | Windowsのロングパス制限で`npm`が落ちたときに有効化した設定 | レジストリ / git config / Node側の3点 | `windows-long-path-npm-fail` | 体験整理後 |
| B | `.gitignore`に追加したのに既に追跡済みで除外されないファイル | `git rm --cached`の最小手順 | `gitignore-already-tracked-file-remove` | 体験整理後 |
| B | PowerShellで日本語ログが文字化けしたときに直した設定 | `chcp 65001`と`$OutputEncoding`の関係 | `powershell-japanese-mojibake-utf8` | 体験整理後 |
| B | VSCodeで複数フォーマッタが衝突して保存ごとに差分が出る | `editor.defaultFormatter`の優先順位 | `vscode-formatter-conflict-on-save` | 体験整理後 |
| C | `nvm-windows`で複数Nodeバージョンを切り替えるときに踏んだ罠 | グローバルパッケージのバージョン跨ぎ | `nvm-windows-global-package-trap` | 保留 |

## AIエージェント / 執筆運用系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| A | Codex用AGENTS.mdとClaude用CLAUDE.mdを分けて運用したメモ | 体験記事ではなく、設定ファイル構成のメモ | `codex-agents-claude-md-split` | 既存記事との差分整理 |
| A | AIエージェントの長期記憶を軽くするためにsession-briefを作った | 起動時コンテキスト圧縮の運用メモ | `ai-agent-session-brief-memory` | 個人情報を伏せて構成化 |
| A | Claude Codeの`CLAUDE.md`を`@import`で分割してトークンを節約した | フラット巨大ファイル→トピック別ルール分割の構成メモ | `claude-md-import-split-rules` | `.claude/rules/` 実物確認後 |
| A | Claude Codeのhooksで保存時に文体NG語を警告する仕組みを入れた | PostToolUse hookの最小実装と落とし穴 | `claude-code-posttool-style-warning-hook` | `.claude/settings.json` 確認後 |
| A | Claude Sonnetを実行係、Opusを助言係に分けるadvisor戦略 | model指定でAgent呼び出しを切り替えるパターン | `claude-sonnet-opus-advisor-pattern` | rules整理後 |
| A | Codex MCPサーバを`.mcp.json`に登録してClaude Codeから叩いた | 設定ファイル例とハマりどころに絞る | `codex-mcp-server-claude-code-setup` | 設定実物確認後 |
| B | Claude Codeの自作Skillを`.claude/skills/`に置いて`/コマンド`化する最小手順 | Skill定義ファイルのフロントマターと配置 | `claude-code-custom-skill-minimum-setup` | 既存skill確認後 |
| B | Claude Codeのworktreeで並列セッションを走らせるときに気をつけたこと | git worktreeとAIセッション分離の運用メモ | `claude-code-worktree-parallel-session` | 運用ログ確認後 |
| B | 設計判断をObsidianに命題文ファイルとして自動登録するルールを書いた | Skill Graphの構造ではなく登録ルール側に絞る | `ai-agent-decision-auto-register-rule` | ルール文確認後 |
| B | AIに毎回読ませる`goals.md`を「アクティブだけ」に圧縮した運用 | 履歴は別ファイル退避、入口は軽量化の判断 | `ai-agent-goals-active-only-compaction` | 既存ファイル確認後 |
| B | 巨大なhandoffやgoalsをAIに毎回読ませないための整理方法 | Skill Graph軽量化の実務メモ | `ai-agent-handoff-goals-compaction` | 個人情報を伏せて構成化 |
| B | Zenn記事をGit管理して公開前レビューを回す構成 | 候補Qをリポジトリ構成とhook寄りに切る | `zenn-git-review-workflow` | 既存下書き確認後 |
| B | 記事レビュー用の文体チェックhookをCodex/Claudeで共有する | 執筆環境の自動化に絞る | `codex-claude-article-style-hook` | hook確認後 |
| B | プロンプトを別エージェントにブラインド実行させて改善する手順 | Empirical Prompt Tuningの最小実践メモ | `prompt-blind-eval-iteration` | スキル本体との差分整理 |
| C | AI 2台レビューで記事の事実誤認を減らすためにやったこと | 運用手順ならQiita可 | `ai-cross-review-fact-check-workflow` | Zennとの差分整理 |
| C | Claude CodeにTaskCreateで作業を分割させて完了状態を追わせる | TodoWrite運用の最小ルール | `claude-code-taskcreate-todo-workflow` | 運用ログ確認後 |

## AIエージェント駆動開発（AI実装委譲）系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| C | Claude Codeに認可付きControllerを書かせたら所有権チェックが抜けた | IDORを毎回踏むので「認可観点」を先渡しする運用 | `claude-code-controller-authz-missing` | Phycock 由来の体験のため公開許可待ち |
| A | AIに「修正して」と頼むと無関係な隣接コードまで整形される問題 | surgical changesルールを先に渡して防いだ手順 | `ai-edit-surgical-changes-rule` | ルール文確認後 |
| A | Codexに大規模リファクタを任せる前に「触る範囲」を明示した | スコープ宣言テンプレと禁止事項リスト | `codex-refactor-scope-declaration` | 体験整理後 |
| A | Claude Codeに「テスト書いて」と頼むとハッピーパスしか作らない | テスト観点リストを先に渡して網羅性を上げた手順 | `ai-test-perspective-prefeed` | ルール文確認後 |
| C | AIにEF Coreのクエリ最適化を任せる前にSQLログを見せた | 推測実装を防ぐための「観測データ先渡し」運用 | `ai-efcore-optimization-with-logs` | Phycock 由来の体験のため公開許可待ち |
| A | Claude Codeにマイグレーションを書かせる前に決めた4項目 | 削除方式・ID型・TZ・Null許容のレビューゲート | `ai-migration-pre-decision-gate` | ルール文確認後 |
| B | AIが事実誤認したコードを書いた回数を減らすために導入した確認ルール | 中心主張のファイル全体確認・反証クエリ運用 | `ai-implementation-fact-check-rule` | ルール文確認後 |
| B | AIに新しいライブラリを使わせるときに公式docを先に貼る運用 | 推測実装を防ぐ「一次情報先渡し」パターン | `ai-new-library-doc-prefeed` | 体験整理後 |
| B | git worktreeで2つのAIセッションに同時実装させてマージ衝突した | 並列分担の境界設計と統合タイミング | `ai-parallel-worktree-merge-conflict` | 体験整理後 |
| B | 「既存の○○を参考に」と類似ファイルを渡してAIに実装させる運用 | テンプレ参照プロンプトの最小パターン | `ai-reference-file-template-prompt` | 体験整理後 |
| B | Claude Codeにエラーログから原因仮説を3つ立てさせる手順 | 修正前の仮説分岐で誤修正を減らした運用 | `ai-error-log-hypothesis-three` | 体験整理後 |
| B | AIにcommit messageを書かせるときの統一フォーマット指示 | プレフィックス・行数・co-authorの指定 | `ai-commit-message-format-rule` | ルール文確認後 |
| B | AIが生成したコードのテストを同じAIに書かせると検出力が落ちる | 役割分離（実装AIと検証AIを分ける）の運用 | `ai-impl-test-role-separation` | 体験整理後 |
| C | AIにUIコンポーネントを作らせるときの「画面構成だけ先に決める」運用 | デザイン指示の粒度メモ | `ai-ui-component-layout-first` | 体験整理後 |
| C | AIに自動テストの失敗を直させると「テストの方を緩める」問題 | 修正方向を固定するプロンプトの最小例 | `ai-test-failure-fix-direction-lock` | 体験整理後 |

## 開発運用 / Git・リリース系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| A | `git add .`をやめて個別ファイル指定に統一した理由 | `.env`混入事故の再現条件と回避ルール | `git-add-explicit-file-rule` | ルール文確認後 |
| A | pre-commit hookが落ちたときに`--no-verify`せず直す運用 | 原因分類と対処パターンに絞る | `pre-commit-hook-no-skip-policy` | 体験整理後 |
| A | リリース前チェックリストをスキル化して毎回回す運用 | チェック項目ではなく仕組み化に絞る | `pre-release-checklist-as-skill` | 既存skill確認後 |
| A | 実装前に「完成条件」を宣言するSprint Contract運用 | 観点別の具体化ガイド付きの最小テンプレ | `sprint-contract-before-implementation` | ルール文確認後 |
| B | 外部APIの上限件数を1つの計算式で決めた話 | 安全係数とバッファの考え方に絞る | `external-api-quota-formula` | 既存Qiita記事と差分整理 |
| B | ログイン済みチェックと所有権チェックを分けてIDORを防いだ | 失敗パターンと最小コード例 | `aspnet-core-auth-vs-ownership-idor` | 実コード確認後 |
| B | 個人開発OAuthで`refresh_token`だけ保存して再ログインを最小化した | トークン保存の判断軸とファイル設計 | `oauth-refresh-token-only-storage` | 実装確認後 |
| B | Electronで`electron-store`を選んだ理由（CJS互換） | ライブラリ選定の判断軸メモ | `electron-store-cjs-compat-choice` | 実装確認後 |
| B | エラーレスポンスにスタックトレースを返さないための最小ハンドラ | 情報漏洩防止の実装パターン | `aspnet-core-error-response-no-stacktrace` | 実コード確認後 |
| B | データ設計を変更コスト順に並べて先に決めた項目リスト | 削除方式・ID型・TZの判断軸 | `data-design-decide-first-list` | ルール文確認後 |
| C | handoffファイルが肥大化したときのアーカイブ閾値運用 | quarterly切り出しと判定基準 | `handoff-archive-threshold-policy` | ルール文確認後 |
| C | テスト観点を実装前にリスト化してAIに渡す運用 | ハッピーパスだけにしないための観点表 | `test-perspective-list-before-impl` | ルール文確認後 |
| C | フロントの`/perf-review`スキルでReactフックの肥大化を検出する運用 | 自動適用しない原則と実行タイミング | `react-hook-perf-review-policy` | スキル確認後 |

## 執筆順の案

> **2026-05-24 更新:** Phycock 関連は公開許可待ちのため執筆順から除外。AIエージェント運用系 / AI駆動開発系 / 開発運用系 / SQL Server 系 / Node 系を優先する。

1. `claude-md-import-split-rules`（AIエージェント運用系・今回着手）
2. `ai-edit-surgical-changes-rule`（AI駆動開発系・今回着手）
3. `git-add-explicit-file-rule`
4. `sqlserver-non-sargable-where-clause`
5. `npm-install-eperm-windows-lockcheck`
6. `codex-agents-claude-md-split`
7. `claude-code-posttool-style-warning-hook`
8. `codex-refactor-scope-declaration`
9. `ai-test-perspective-prefeed`
10. `pre-commit-hook-no-skip-policy`

**保留（Phycock 公開許可が下りたら最優先）:**
- `playwright-wait-chartjs-before-pdf`
- `aspnet-core-playwright-auth-cookie-pdf`
- `claude-code-controller-authz-missing`
- `ai-efcore-optimization-with-logs`

（2026-05-24 に Chrome拡張系 3 件 `youtube-spa-content-script-matches` / `chrome-extension-mutationobserver-rerender-loop` / `youtube-playlist-restore-dom-order` を公開済み。既存 Qiita 公開記事テーブル参照）

## 更新ルール

- Qiita 用に構成メモを作ったら、このファイルの該当候補の `次の扱い` を更新する
- `qiita/public/*.md` に記事を作成したら、既存 Qiita 公開記事または下書き管理欄を追加する
- Zenn 記事からの再構成の場合も、Qiita 独立記事としての差分を必ず残す
- 実コードに触れる候補は、執筆前に対象ファイル・依存関係・中心主張の事実確認を行う
