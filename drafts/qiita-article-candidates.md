# Qiita 独立記事候補

Zenn 記事の再投稿ではなく、Qiita 向けに独立して書ける「1記事1トラブル」候補を管理する。

## 方針

- Zenn: 体験全体、設計判断、作ったものの背景、学び
- Qiita: 詰まった1点、原因、再現条件、解決コード、注意点
- 既存 Zenn と同じ題材でも、Qiita では検索される具体トラブルへ切り出す
- 単なる網羅解説ではなく、自分が詰まった実装・運用上の問題を起点にする
- 実コードに触れる候補は、執筆前に該当リポジトリの事実確認を行う

## 既存 Qiita 公開記事

| 公開日 | slug | タイトル | 元記事 | URL |
| --- | --- | --- | --- | --- |
| 2026-05-20 | `youtube-data-api-rss-quota-reduction` | YouTube Data API のクォータ枯渇を RSS で避ける設計にした話 | `articles/youtube-data-api-rss-quota-reduction.md` | https://qiita.com/harnesswinner/items/e2d5dba192540222d8d5 |
| 2026-05-20 | `youtom-introduction` | YouTubeの配信予定を追うWindowsアプリ Youtom を作った | `articles/youtom-introduction.md` | https://qiita.com/harnesswinner/items/52c94119fed2aba20f7e |
| 2026-05-24 | `youtube-playlist-restore-dom-order` | YouTubeプレイリストのDOM順を一度保存して通常順に戻す実装 | （独立記事） | https://qiita.com/harnesswinner/items/fa3a124e5fa50229a887 |
| 2026-05-24 | `youtube-spa-content-script-matches` | Chrome拡張でYouTubeのSPA遷移後にcontent scriptが効かない問題を直した | （独立記事） | https://qiita.com/harnesswinner/items/3bac40961a0b5ff20dee |
| 2026-05-24 | `chrome-extension-mutationobserver-rerender-loop` | Chrome拡張でDOMを並び替えた後にMutationObserverが再発火する問題への対処 | （独立記事） | https://qiita.com/harnesswinner/items/5429f56b3a8e23675703 |

## 最優先候補

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| A | Chrome拡張でYouTubeのSPA遷移後にcontent scriptが効かない問題を直した | 拡張紹介ではなく、`matches` と SPA 遷移の1点解決 | `youtube-spa-content-script-matches` | 最初に構成化する候補 |
| A | PlaywrightでChart.jsの描画完了を待ってからPDF化する | ASP.NET Core PDF 化全体ではなく、JSグラフ待機に絞る | `playwright-wait-chartjs-before-pdf` | Phycock 実コード確認後 |
| A | ASP.NET CoreのログインCookieをサーバー側Playwrightに渡す実装 | PDF出力の認証問題だけを切り出す | `aspnet-core-playwright-auth-cookie-pdf` | Phycock 実コード確認後 |
| A | Chrome拡張でDOMを並び替えた後にMutationObserverが再発火する問題への対処 | 投稿日順ソート拡張の中から監視ループ回避だけ扱う | `chrome-extension-mutationobserver-rerender-loop` | YouTube Sorter 実装確認後 |
| A | YouTubeプレイリストのDOM順を一度保存して通常順に戻す実装 | 拡張紹介ではなく、DOM順復元の実装に絞る | `youtube-playlist-restore-dom-order` | YouTube Sorter 実装確認後 |
| A | ElectronアプリでSmartScreen警告が出たときに確認したこと | SmartScreen記事の再投稿ではなく、確認手順と判断材料に絞る | `electron-smartscreen-checklist` | 既存記事との差分を整理 |
| A | AIエージェントの長期記憶を軽くするためにsession-briefを作った | Skill Graph体験記事ではなく、起動時コンテキスト圧縮の運用メモ | `ai-agent-session-brief-memory` | ローカルパス・個人情報を伏せて構成化 |

## Chrome拡張 / YouTube 系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| A | Chrome拡張でYouTubeのSPA遷移後にcontent scriptが効かない問題を直した | `matches` と SPA 遷移元での注入問題に絞る | `youtube-spa-content-script-matches` | 最優先 |
| A | Manifest V3でYouTubeページのURL変更を検知する実装メモ | MV3一般論ではなく、YouTubeのSPAでのURL監視に絞る | `manifest-v3-youtube-url-change-detection` | 実装確認後 |
| A | YouTubeプレイリストのDOM順を一度保存して通常順に戻す実装 | 並び替え復元だけを扱う | `youtube-playlist-restore-dom-order` | 実装確認後 |
| A | Chrome拡張でDOMを並び替えた後にMutationObserverが再発火する問題への対処 | バッジ差分更新・監視ループ回避に絞る | `chrome-extension-mutationobserver-rerender-loop` | 実装確認後 |
| A | YouTubeの動画カードに投稿日バッジを後付けするときに見たDOM構造 | DOM解析・セレクタ設計のメモ | `youtube-video-card-date-badge-dom` | 実装確認後 |
| A | YouTube Data APIを使わずに投稿日順ソートした理由と限界 | APIキー不要設計の技術メモ | `youtube-sort-without-data-api` | Zenn下書きとの差分整理 |
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
| A | ElectronアプリでSmartScreen警告が出たときに確認したこと | 配布の現実ではなく、確認手順に絞る | `electron-smartscreen-checklist` | 既存記事との差分整理 |
| A | Windows向けElectronアプリにコード署名する前に整理した判断軸 | 署名方式・費用・OSS配布の判断材料に絞る | `electron-windows-code-signing-decision` | 追加調査後 |
| B | electron-builderでWindows配布物を作るときに詰まった設定 | 具体設定メモとして扱う | `electron-builder-windows-distribution-settings` | 実装確認後 |
| B | GitHub Releasesで個人開発アプリを配布するときのREADME導線 | 技術寄りの運用メモ | `github-releases-app-readme-flow` | README確認後 |
| B | 未署名アプリの配布でユーザーに説明すべきこと | SmartScreen記事の補足 | `unsigned-electron-app-user-notice` | 文章設計候補 |
| C | Electronアプリの自動更新を入れる前に決めること | 実装済みでなければ候補止まり | `electron-auto-update-before-implementation` | 保留 |

## YouTube API / RSS 系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| A | YouTube RSSで取得できる情報とData APIが必要になる情報を分ける | 既存Qiitaと近いため、比較表特化なら可 | `youtube-rss-vs-data-api-fields` | 重複注意 |
| A | YouTube Data APIのクォータ消費をざっくり見積もる方法 | 既存記事の補助線 | `youtube-data-api-quota-estimation` | 重複注意 |
| B | YouTubeのメンバー限定配信がRSSに出ない前提で取得経路を分ける | 候補WをQiita向けに切る | `youtube-membership-rss-data-api-split` | 実装確認後 |
| B | RSS取得を通常ルート、API取得を例外ルートに分けた実装判断 | quota / 取得漏れ / 更新頻度に絞る | `youtube-rss-normal-api-exception-route` | 実装確認後 |
| B | YouTube配信予定の取得でキャッシュを入れる前に考えたこと | quota / 更新頻度 / 手動更新の切り分け | `youtube-schedule-cache-quota-design` | 実装確認後 |
| C | YouTube APIのエラー時にユーザーへ何を表示するか | エラー表示設計の小記事 | `youtube-api-error-message-design` | 実装確認後 |

## ASP.NET Core / Phycock 系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| A | ASP.NET Core MVCで認証必須ページをPlaywrightでPDF化した | 候補Tより、Cookie転送手順に絞る | `aspnet-core-playwright-auth-cookie-pdf` | 実コード確認必須 |
| A | PlaywrightでChart.jsの描画完了を待ってからPDF化する | JS描画待機に絞る | `playwright-wait-chartjs-before-pdf` | 実コード確認必須 |
| A | ASP.NET CoreのログインCookieをサーバー側Playwrightに渡す実装 | 認証付きPDF出力の実装メモ | `aspnet-core-playwright-auth-cookie-pdf` | 実コード確認必須 |
| B | PDF出力用に`?print=1`を用意して画面表示と分けた | 画面表示と印刷表示の分離判断 | `aspnet-core-print-mode-pdf` | 実コード確認必須 |
| B | FullCalendarでDTOの色が反映されないときに確認したこと | 既存ZennのQiita切り出し候補 | `fullcalendar-event-color-dto-check` | 既存記事との差分整理 |
| B | ASP.NET Core MVCでViewModelに入力責務を寄せると何が楽になるか | 候補Pの一部 | `aspnet-core-mvc-viewmodel-input-responsibility` | 実コード確認必須 |
| B | ユーザー別データのIDOR対策をService層で見るようにした | 候補Uより、認可漏れ防止の実装メモ | `aspnet-core-idor-service-layer` | 実コード・守秘確認必須 |
| C | ScheduleとScheduleEntryを統合した後にControllerがどう単純化したか | コード差分が明確なら可 | `aspnet-core-scheduleentry-controller-simplify` | 下書きとの差分確認 |

## AIエージェント / 執筆運用系

| 優先 | 候補 | Zenn との差分 | 想定 slug | 次の扱い |
| --- | --- | --- | --- | --- |
| A | Codex用AGENTS.mdとClaude用CLAUDE.mdを分けて運用したメモ | 体験記事ではなく、設定ファイル構成のメモ | `codex-agents-claude-md-split` | 既存記事との差分整理 |
| A | AIエージェントの長期記憶を軽くするためにsession-briefを作った | 起動時コンテキスト圧縮の運用メモ | `ai-agent-session-brief-memory` | 個人情報を伏せて構成化 |
| B | 巨大なhandoffやgoalsをAIに毎回読ませないための整理方法 | Skill Graph軽量化の実務メモ | `ai-agent-handoff-goals-compaction` | 個人情報を伏せて構成化 |
| B | Zenn記事をGit管理して公開前レビューを回す構成 | 候補Qをリポジトリ構成とhook寄りに切る | `zenn-git-review-workflow` | 既存下書き確認後 |
| B | 記事レビュー用の文体チェックhookをCodex/Claudeで共有する | 執筆環境の自動化に絞る | `codex-claude-article-style-hook` | hook確認後 |
| C | AI 2台レビューで記事の事実誤認を減らすためにやったこと | 運用手順ならQiita可 | `ai-cross-review-fact-check-workflow` | Zennとの差分整理 |

## 執筆順の案

1. `youtube-spa-content-script-matches`
2. `chrome-extension-mutationobserver-rerender-loop`
3. `youtube-playlist-restore-dom-order`
4. `playwright-wait-chartjs-before-pdf`
5. `aspnet-core-playwright-auth-cookie-pdf`
6. `electron-smartscreen-checklist`
7. `ai-agent-session-brief-memory`

## 更新ルール

- Qiita 用に構成メモを作ったら、このファイルの該当候補の `次の扱い` を更新する
- `qiita/public/*.md` に記事を作成したら、既存 Qiita 公開記事または下書き管理欄を追加する
- Zenn 記事からの再構成の場合も、Qiita 独立記事としての差分を必ず残す
- 実コードに触れる候補は、執筆前に対象ファイル・依存関係・中心主張の事実確認を行う
