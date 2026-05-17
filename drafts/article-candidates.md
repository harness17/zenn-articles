# Zenn 記事候補と既存記事の対応表

候補リストと公開済み記事・下書きの対応を管理する。新しい記事候補を選ぶ前と、記事公開後の `/article-publish` 相当の作業で更新する。

## 状態の定義

| 状態 | 意味 |
| --- | --- |
| 公開済み | `articles/<slug>.md` が `published: true` で、Zenn 実サイトでも 200 / タイトル一致を確認済み |
| 公開指定済み / Zenn未確認 | ローカルでは `published: true` だが、Zenn 実サイトでは 200 を確認できていない |
| 下書きあり | `drafts/<slug>.md` または `articles/<slug>.md` の `published: false` がある |
| 一部カバー | 近い記事はあるが、候補の主題としては未完了 |
| 未着手 | 対応する公開記事・下書きがない |
| 保留 | 方針上、今は書かない |

## 既存記事リスト

`articles/*.md` の `published: true` と Zenn 実サイトの直接アクセス結果を分けて管理する。Zenn 側が 403 を返すものは、ローカル上は公開指定済みでも実公開未確認として扱う。

最終突き合わせ: 2026-05-17

| ローカル公開日 | slug | タイトル | 候補対応 | Zenn実サイト | テーマ系統 |
| --- | --- | --- | --- | --- | --- |
| 2026-05-10 | `devnext-mvc-helper-extensions` | ASP.NET MVCの自作HelperをASP.NET Coreに移植した話 | 派生記事 | 200 / 公開確認 | ASP.NET Core / Razor Helper |
| 2026-05-10 | `fullcalendar-event-color-rendering` | FullCalendarでDTOの色が反映されない時に見たこと | 派生記事 | 200 / 公開確認 | ASP.NET Core / FullCalendar |
| 2026-05-11 | `youtube-data-api-rss-quota-reduction` | YouTube Data API のクォータ枯渇を RSS で99%削減した話 | 候補H | 200 / 公開確認 | YouTube Data API / API クォータ |
| 2026-05-11 | `claude-code-workflow-evolution` | Claude Code運用を数ヶ月で見直してrulesとskillsに分けた話 | 候補N | 200 / 公開確認 | Claude Code / AI協調開発 |
| 2026-05-13 | `electron-smartscreen-oss-distribution` | 未署名Electronアプリを配布するとSmartScreenで止まる問題に向き合った話 | 候補I | 200 / 公開確認 | Electron / Windows 配布 |
| 2026-05-13 | `youtom-introduction` | 推しの配信予定を見逃さないために Youtom を作った | 派生記事 | 200 / 公開確認 | Electron / React / YouTube |
| 2026-05-16 → 保留 | `phycock-schedule-entry-consolidation` | ASP.NET Core MVCでScheduleEntryに寄せた設計判断 | 候補J | 下書き / 公開保留 | ASP.NET Core / データモデル設計 |
| 2026-05-16 | `codex-claude-skill-graph-worklog` | AIとの設計判断をMy-Skill-Graphに残して再利用する | 候補O | 403 / 実公開未確認 | AI協調開発 / ナレッジ管理 |
| 2026-05-17 | `cross-agent-harness-introduction` | CodexとClaude Codeの共同作業をcross-agent-harnessに切り出した | 派生記事 | 403 / 実公開未確認 | AI協調開発 / OSS |
| 公開ログ未記録 | `aspnet-core-identity-to-commonlibrary` | ASP.NET Core移行でIdentityエンティティを共通化した判断 | 候補M | 200 / 公開確認 | ASP.NET Core / Identity |
| 公開ログ未記録 | `ai-cross-review-handoff-workflow` | AI 2 台クロスレビューで技術記事の盲点を拾う | 派生記事 | 200 / 公開確認 | AI協調開発 / 記事レビュー |

## 候補対応表

| 候補 | 元テーマ | 状態 | 対応記事・下書き | 次の扱い |
| --- | --- | --- | --- | --- |
| H | YouTube Data API のクォータ枯渇と戦った話 | 公開済み | `articles/youtube-data-api-rss-quota-reduction.md` | 追加で書くなら別切り口にする |
| I | 未署名 Electron アプリの SmartScreen 問題と OSS 配布の現実 | 公開済み | `articles/electron-smartscreen-oss-distribution.md` | 公開後運用は候補Rへ分離 |
| J | Phycock で Schedule を削除して ScheduleEntry に集約した設計判断 | 公開保留（下書き） | `articles/phycock-schedule-entry-consolidation.md` | リタリコ確認が取れたら published: true に戻して公開する |
| K | Chrome 拡張 Manifest V3 移行で遭遇した実装課題 | 未着手 | なし | 実装記憶の掘り起こしが必要 |
| L | うつ病療養中のエンジニアが Claude Code で個人開発を続ける方法 | 未着手 | なし | 障害情報リスクがあるため慎重に扱う |
| M | DevNet と DevNext で同じ機能を別実装にした設計判断の差分 | 公開済み | `articles/aspnet-core-identity-to-commonlibrary.md` | 事実確認ルールの反省込みで完了扱い |
| N | Claude Code 導入から数ヶ月の運用変遷 | 公開済み | `articles/claude-code-workflow-evolution.md` | 派生は cross-agent / skill graph 側で扱う |
| O | My-Skill-Graph で設計判断を再利用する運用 | 公開指定済み / Zenn未確認 | `articles/codex-claude-skill-graph-worklog.md` | Zenn実サイトで 200 になるか確認する |
| P | ASP.NET Core MVC で入力フォームの責務を ViewModel に寄せた話 | 未着手 | なし | DevNext / Phycock の実コード確認が必要 |
| Q | Zenn 記事をリポジトリ管理して公開前レビューまで自動化した話 | 下書きあり | `drafts/zenn-article-repo-workflow.md` | 次に本文化する候補 |
| R | Electron 個人開発アプリを公開した後に必要だった運用メモ | 一部カバー | `articles/electron-smartscreen-oss-distribution.md` / `articles/youtom-introduction.md` | README / Releases / 署名方針の運用に絞れば別記事化可能 |

## 保留候補

候補A〜G の SQL Server チューニング・ASP.NET Core 解説系は、体験記事としての課題と判断軸が弱いため保留する。実務復帰後に一次情報と失敗例が揃ったら見直す。

## 更新ルール

- 新しい構成メモを作ったら、対応候補を `下書きあり` に更新する。
- `articles/<slug>.md` を `published: true` にしたら、公開日・slug・タイトルを `既存記事リスト` に追加し、対応候補を `公開指定済み` に更新する。
- 公開後に `https://zenn.dev/harness/articles/<slug>` へ直接アクセスし、HTTP 200 と記事タイトル一致を確認できたら `Zenn実サイト` を `200 / 公開確認` に更新する。
- 403 / 404 / タイトル不一致の場合は `Zenn実サイト` を `実公開未確認` のまま残し、`drafts/published-log.md` の確認予定にも入れる。
- 候補外の派生記事を公開した場合も、`既存記事リスト` に追加して `候補対応` を `派生記事` にする。
- 既存候補と重複する新規案を出す前に、この表で公開済み・下書き済みを確認する。
