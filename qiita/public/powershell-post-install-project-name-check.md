---
title: PowerShellインストーラーでコピー先のプレースホルダーを検査しないと古い指示が残る
tags:
  - PowerShell
  - テンプレート
  - 自動化
  - AIエージェント
private: false
updated_at: '2026-07-14T15:00:32+09:00'
id: b52a1ef29100426fffba
organization_url_name: null
slide: false
ignorePublish: false
---

## TL;DR

AI エージェント用のハーネス（ルール・スキル・ハンドオフの一式）をプロジェクトへコピーする PowerShell インストーラーを作った。テンプレートの `{{PROJECT_NAME}}` は自動置換されるが、手動で埋めるべき `TODO` や `YYYY-MM-DD` は残る。post-install 検査がないと、エージェントがコピー元の古い指示をそのまま読んでしまう。

```powershell
function Test-HarnessWarnings {
    param([string]$RootPath)
    $warnings = [System.Collections.Generic.List[string]]::new()

    $profilePath = Join-Path $RootPath ".claude\rules\project-collaboration-profile.md"
    if (Test-Path $profilePath) {
        $text = [System.IO.File]::ReadAllText($profilePath, [System.Text.UTF8Encoding]::new($false, $true))
        foreach ($token in @("TODO", "YYYY-MM-DD", "<agent>", "<repo-root>")) {
            if ($text.Contains($token)) {
                $warnings.Add("profile still contains placeholder: $token")
            }
        }
    }
    return $warnings
}
```

対象リポジトリは非公開のため、この記事では実装意図が追えるように必要な抜粋コードを本文内に載せる。

## 起きたこと

Codex と Claude Code の共同作業で使うハーネスを、新しいプロジェクトへ導入するインストーラーを作った。

```powershell
.\install.ps1 -TargetPath C:\Projects\NewProject
```

インストーラーは 2 種類のコピーを行う。

| 種類 | 処理 | 例 |
|------|------|-----|
| 静的コピー | ファイルをそのままコピー | `cross-agent-harness.md`, `handoff-protocol.md` |
| テンプレート展開 | `{{PROJECT_NAME}}` と `{{TARGET_PATH}}` を置換してコピー | `project-collaboration-profile.md`, `CLAUDE_CODE_HANDOFF.md` |

テンプレート展開は正しく動いていた。しかし展開後のファイルには、人間が埋めるべきプレースホルダーが残っている。

```markdown
# NewProject 共同開発プロフィール

- プロジェクト概要: TODO
- verify コマンド: TODO
- 初回ハンドオフ担当: <agent>
- 更新日: YYYY-MM-DD
```

最初はこの残存に気づかず、エージェントが `TODO` という文字列を含むプロフィールをそのまま読んでいた。ハンドオフの `対象リポジトリ` がコピー元パスのまま残っていたケースもあった。

## 原因

テンプレート内の `{{PROJECT_NAME}}` は自動置換できるが、「プロジェクト概要」「verify コマンド」のように人間にしか書けない内容は `TODO` で残るしかない。問題は、その `TODO` が残っているかどうかをインストーラーが確認していなかったこと。

エージェントは指示ファイルの内容を真面目に読むので、`TODO` が残った指示をそのまま解釈しようとする。`対象リポジトリ` のパスが別プロジェクトのままだと、ハンドオフ先を間違える。

## 修正

インストーラーの末尾に post-install 検査を追加した。

```powershell
function Test-HarnessWarnings {
    param([string]$RootPath)
    $warnings = [System.Collections.Generic.List[string]]::new()

    # プロフィールのプレースホルダー残存チェック
    $profilePath = Join-Path $RootPath ".claude\rules\project-collaboration-profile.md"
    if (Test-Path $profilePath) {
        $text = [System.IO.File]::ReadAllText($profilePath, [System.Text.UTF8Encoding]::new($false, $true))
        foreach ($token in @("TODO", "YYYY-MM-DD", "<agent>", "<repo-root>")) {
            if ($text.Contains($token)) {
                $warnings.Add("profile still contains placeholder: $token")
            }
        }
    }

    # ハンドオフのプレースホルダーと対象パス不一致チェック
    $handoffPath = Join-Path $RootPath "CLAUDE_CODE_HANDOFF.md"
    if (Test-Path $handoffPath) {
        $text = [System.IO.File]::ReadAllText($handoffPath, [System.Text.UTF8Encoding]::new($false, $true))
        foreach ($token in @("TODO", "YYYY-MM-DD", "<agent>", "<repo-root>")) {
            if ($text.Contains($token)) {
                $warnings.Add("handoff still contains placeholder: $token")
            }
        }

        $match = [regex]::Match($text, '対象リポジトリ:\s*`([^`]+)`')
        if ($match.Success) {
            $expected = $RootPath.Replace("\", "/")
            if ($match.Groups[1].Value -ne $expected) {
                $warnings.Add("handoff target repo mismatch: expected $expected")
            }
        }
    }

    return $warnings
}

$warnings = Test-HarnessWarnings -RootPath $targetRoot.Path
if ($warnings.Count -gt 0) {
    Write-Host "Warnings:" -ForegroundColor Yellow
    foreach ($w in $warnings) { Write-Host "- $w" -ForegroundColor Yellow }
}
```

エラーではなく警告（Yellow）にしたのは、`TODO` が残っている状態がインストール直後としては正常だから。monorepo で複数ターゲットに入れたとき、false positive でインストール自体を止めるのは過剰だった。

## 確認ポイント

- `Test-HarnessWarnings` がインストール完了後に呼ばれているか
- チェック対象のトークン一覧（`TODO`, `YYYY-MM-DD`, `<agent>`, `<repo-root>`）がテンプレートで使っているプレースホルダーと一致しているか
- ハンドオフの `対象リポジトリ` パスが `$targetRoot.Path` と一致するか
- 警告はエラー（赤）ではなく警告（黄色）で出力しているか

## 参考

- cross-agent-harness（非公開） — 本文内の抜粋コードで post-install 検査の要点を示した
- [PowerShell System.IO.File](https://learn.microsoft.com/ja-jp/dotnet/api/system.io.file)
