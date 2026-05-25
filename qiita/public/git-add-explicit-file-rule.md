---
title: git add .で余計なファイルを混ぜないために個別ファイル指定へ寄せた
tags:
  - Git
  - 開発環境
  - Security
  - AI
private: false
updated_at: '2026-05-25T18:18:28+09:00'
id: 871470b50d10ccbbeac9
organization_url_name: null
slide: false
ignorePublish: false
---

## はじめに

作業後に `git add .` でまとめて staging すると、意図していないファイルまでコミット候補に入ることがあります。

自分のリポジトリでは、記事原稿、Qiita CLI の管理ファイル、生成物、ローカル設定が同じ作業ツリーに並ぶことがあります。その状態で `git add .` を使うと、「今回の変更」と「たまたま存在していた変更」が混ざります。

この記事では、`git add .` をやめて個別ファイル指定に寄せた運用をまとめます。

## 詰まったポイント

問題は、`git status` を見ていても staging の粒度が粗いことでした。

たとえば記事を 1 本直しただけのつもりでも、作業ツリーには次のような変更が同時に残ることがあります。

```text
 M README.md
 M drafts/article-ideas.md
?? articles/new-post.md
?? qiita/public/.remote/example.md
?? .env.local
```

この状態で `git add .` を実行すると、現在のディレクトリ以下の変更がまとめて staging されます。

記事本文だけをコミットしたいのに、候補表、Qiita CLI の remote キャッシュ、ローカル設定まで混ざる可能性があります。

## 原因

`git add .` は「今回の意図」を知りません。

Git から見ると、変更済みファイルも未追跡ファイルも、現在のディレクトリ配下にある変更です。人間にとっては「今触った記事」と「前から残っていたローカルファイル」が別でも、コマンドは区別しません。

特に危ないのは次のファイルです。

- `.env`、`.env.local` のような秘密情報を含み得るファイル
- CLI が生成した `.remote` やキャッシュ
- ローカル環境だけで使う設定
- 別タスクで途中まで触っていたファイル
- 生成された lockfile や画像など、今回の変更理由を説明しにくいファイル

`.gitignore` があっても、まだ ignore に入れていないファイルや、すでに追跡済みのファイルは防げません。

## 採用したルール

自分の運用では、`git add .` と `git add -A` を原則使わず、コミットに含めるファイルを明示するようにしました。

```powershell
git status --short
git diff -- qiita/public/example.md
git diff -- drafts/qiita-article-candidates.md

git add qiita/public/example.md drafts/qiita-article-candidates.md
git status --short
git diff --cached
```

ポイントは、`git add` の前後で見るものを分けることです。

- `git status --short`: 変更全体を見る
- `git diff -- <file>`: staging 前に対象ファイルの中身を見る
- `git add <file>`: 含めるファイルだけ staging する
- `git diff --cached`: staging 済みの差分だけ見る

`git diff --cached` に今回説明できない差分があれば、commit 前に止まれます。

## 複数ファイルをまとめたいとき

複数ファイルを staged にしたいときも、対象を列挙します。

```powershell
git add `
  qiita/public/example.md `
  drafts/qiita-article-candidates.md `
  README.md
```

PowerShell では行末のバッククォートで折り返せます。ただし、貼り付けミスが怖い場合は 1 行で書く方が安全です。

```powershell
git add qiita/public/example.md drafts/qiita-article-candidates.md README.md
```

ディレクトリ単位で staging する場合も、対象ディレクトリが狭いときだけにしています。

```powershell
git add qiita/public/
```

この場合でも、先に `git status --short qiita/public/` で中身を確認します。

## すでに追跡済みのファイルは .gitignore だけでは外れない

よくある落とし穴は、`.gitignore` に追加したのにまだ staging されるケースです。

一度 Git に追跡されたファイルは、`.gitignore` に書いても自動では追跡解除されません。追跡だけ外したい場合は、ファイルを残したまま index から外します。

```powershell
git rm --cached path/to/local-file
```

複数人で使うリポジトリなら、この操作自体も commit に含まれるため、なぜ追跡解除するのかを説明できる状態で実行します。

## AIエージェントに依頼するときの書き方

AI にコミット準備を頼む場合も、「staging して」だけだと範囲が曖昧になります。

自分は次のように対象ファイルを明示します。

```text
以下のファイルだけ staging してください。
- qiita/public/example.md
- drafts/qiita-article-candidates.md

git add . / git add -A は使わないでください。
staging 後に git diff --cached の要約を返してください。
```

AI は作業ツリー全体を見て「関連しそう」と判断することがあります。対象ファイルを明示すると、別タスクの変更を巻き込みにくくなります。

## 注意点

個別ファイル指定にしても、対象ファイルの中に秘密情報が入っていれば防げません。

そのため、最低限次は commit 前に確認します。

```powershell
git diff --cached
```

必要なら、秘密情報らしい文字列も検索します。

```powershell
git diff --cached | Select-String -Pattern "token|secret|password|api_key|connectionString" -CaseSensitive:$false
```

この検索は完全ではありません。最後は diff を読む必要があります。

## まとめ

`git add .` は速いですが、作業ツリーに複数タスクの変更やローカルファイルがあると、意図しない差分を混ぜます。

自分の運用では次の順に固定しました。

1. `git status --short` で全体を見る
2. `git diff -- <file>` で対象だけ確認する
3. `git add <file>` で個別に staging する
4. `git diff --cached` で commit に入る差分だけ確認する

commit は履歴に残るため、少し遅くても「なぜこのファイルが入っているか」を説明できる staging に寄せた方が扱いやすくなりました。

## 参考リンク

- [Git - git-add Documentation](https://git-scm.com/docs/git-add)
- [Git - git-rm Documentation](https://git-scm.com/docs/git-rm)
