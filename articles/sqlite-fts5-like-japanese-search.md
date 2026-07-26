---
title: "SQLite FTS5を残しつつ日本語検索はLIKEに戻した話"
emoji: "🔎"
type: "tech"
topics: ["sqlite", "electron", "javascript", "fts5", "個人開発"]
published: true
---

## はじめに

YouTube 配信スケジュール管理アプリ YouTom には、終了済み配信を検索するアーカイブ画面がある。SQLite には FTS5 仮想テーブルも作っていたので、最初は全文検索をそこへ寄せるつもりだった。

しかし、日本語の部分一致では FTS5 の `unicode61` トークナイザーが期待と合わなかった。たとえば「ホロ」で「ホロライブ」を見つけたいような検索は、単語境界が明確な英語検索とは違う。個人ツールの件数規模では、FTS5 の高度さより `LIKE` の素直な部分一致のほうが使い勝手に合っていた。

この記事では、FTS5 テーブルを残しつつ、実際の検索処理は `LIKE` に戻した判断を書く。

**対象読者**: SQLite で日本語検索を実装していて、FTS5 と `LIKE` のどちらに寄せるか迷っている開発者。

**リポジトリ**: [YouTom](https://github.com/harness17/youtom)

## FTS5は用意していた

YouTom の migration 003 では、終了済み配信の検索に使う前提で `videos_fts` を作っている。

```js
CREATE VIRTUAL TABLE IF NOT EXISTS videos_fts USING fts5(
  title,
  description,
  content='videos',
  content_rowid='rowid',
  tokenize='unicode61'
);

INSERT INTO videos_fts(rowid, title, description)
  SELECT rowid, title, description FROM videos;
```

INSERT / UPDATE / DELETE に合わせて FTS テーブルを同期するトリガーもある。

```js
CREATE TRIGGER IF NOT EXISTS videos_ai AFTER INSERT ON videos BEGIN
  INSERT INTO videos_fts(rowid, title, description)
    VALUES (new.rowid, new.title, new.description);
END;

CREATE TRIGGER IF NOT EXISTS videos_au AFTER UPDATE ON videos BEGIN
  INSERT INTO videos_fts(videos_fts, rowid, title, description)
    VALUES ('delete', old.rowid, old.title, old.description);
  INSERT INTO videos_fts(rowid, title, description)
    VALUES (new.rowid, new.title, new.description);
END;
```

ここまで用意しているなら、そのまま FTS5 を使いたくなる。ただ、実際のアーカイブ検索で欲しかったのは「検索エンジン的な全文検索」ではなく、「動画タイトルやチャンネル名にこの文字列を含むか」だった。

## 日本語部分一致で困った

FTS5 の `unicode61` は、英数字や空白区切りのテキストには扱いやすい。一方、日本語タイトルでは単語境界が分かりにくい。ユーザーとしては「ホロ」と入力して「ホロライブ」の配信を見つけたいが、トークン単位の検索では直感とずれることがある。

このアプリの検索対象は、数百万件の文書ではない。個人のローカル SQLite にある終了済み配信で、画面にもページングを入れている。性能より、「入力した文字列がそのまま含まれていれば出る」ことを優先した。

## 実検索はLIKEにした

現在の検索は `videoQueries.js` に寄せている。`searchByText()` も、アーカイブ画面の複合フィルタも `LIKE` を使う。

```js
const searchStmt = db.prepare(`
  SELECT * FROM videos
  WHERE status = 'ended'
    AND (
      (@searchTitle   AND title        LIKE '%' || @query || '%' ESCAPE '!')
      OR (@searchChannel AND channel_title LIKE '%' || @query || '%' ESCAPE '!')
      OR (@searchDesc    AND description  LIKE '%' || @query || '%' ESCAPE '!')
    )
  ORDER BY COALESCE(actual_start_time, scheduled_start_time, last_checked_at) DESC
  LIMIT @limit
`)
```

アーカイブ一覧では、チャンネル・期間・テキスト検索を同じ SQL にまとめている。

```js
where.push(`(
  @query = ''
  OR (
    (@searchTitle AND title LIKE '%' || @query || '%' ESCAPE '!')
    OR (@searchChannel AND channel_title LIKE '%' || @query || '%' ESCAPE '!')
    OR (@searchDesc AND description LIKE '%' || @query || '%' ESCAPE '!')
  )
)`)
```

`LIKE` にしたことで、タイトル・チャンネル名・説明文のどこを検索対象にするかもフラグで分けやすくなった。

## ワイルドカードは必ずエスケープする

`LIKE` に戻すと、`%` と `_` がワイルドカードとして解釈される。検索ボックスに `%` を入れただけで全件ヒットするのは困るので、入力値は `!` でエスケープしている。

```js
function escapeLikeQuery(raw) {
  const trimmed = String(raw ?? '').trim()
  if (!trimmed) return ''
  // LIKE のワイルドカード文字（! % _）をエスケープ
  return trimmed.replace(/[!%_]/g, '!$&')
}
```

`ESCAPE '!'` を SQL 側にも入れて、ユーザー入力の `%` と `_` を文字として扱う。

この挙動はテストで固定した。

```js
it('searchByText escapes LIKE wildcard characters', () => {
  videos.upsert(sampleVideo({ id: 'literal-percent', title: '100% endurance' }))
  videos.upsert(sampleVideo({ id: 'plain', title: '100 percent endurance' }))

  expect(queries.searchByText('%').map((video) => video.id)).toEqual(['literal-percent'])
  expect(queries.searchByText('_').map((video) => video.id)).toEqual([])
})
```

`%` を検索したときに「100% endurance」だけが出る。ワイルドカードとして全件に広がらないことを確認している。

## FTS5テーブルをすぐ消さなかった理由

「使わないなら FTS5 テーブルも migration から消せばいい」と考えたくなるが、既に配布済みのローカル DB には `videos_fts` とトリガーが存在する。ここで無理に削除 migration を入れると、検索方式の変更より DB 互換性リスクのほうが大きくなる。

今回は、検索クエリだけを `LIKE` に寄せ、既存の FTS5 テーブルはそのまま残した。

| 選択肢 | 判断 |
|---|---|
| FTS5を使い続ける | 日本語部分一致の直感と合わない |
| FTS5を削除するmigrationを入れる | 既存DBへの影響が検索改善に対して大きい |
| FTS5は残し、検索だけLIKEにする | 互換性を保ちながら検索体験を直せる |

将来、検索対象が増えて `LIKE` では重くなったら、その時点で trigram 方式や別の tokenizer を検討すればよい。今の規模では、先に複雑な検索基盤へ寄せる必要はなかった。

## まとめ

- SQLite FTS5 は migration で用意していたが、日本語部分一致では期待とずれた
- 現行検索は `LIKE '%query%' ESCAPE '!'` に寄せ、タイトル・チャンネル・説明文を対象にした
- `%` と `_` は検索文字として扱えるようにエスケープし、テストで固定した
- 既存DB互換性を優先し、FTS5テーブルは残したまま検索経路だけを変えた

## 参考リンク

- [YouTom](https://github.com/harness17/youtom)
- [SQLite FTS5 Extension](https://www.sqlite.org/fts5.html)
- [SQLite LIKE operator](https://www.sqlite.org/lang_expr.html#the_like_glob_regexp_match_and_extract_operators)
