---
title: SQLite FTS5で日本語の部分一致がヒットしないためLIKEへ戻した
tags:
  - JavaScript
  - SQLite
  - 全文検索
  - Electron
  - 個人開発
private: false
updated_at: '2026-06-14T19:57:17+09:00'
id: bdf56392d081ceed99b9
organization_url_name: null
slide: false
ignorePublish: false
---

## 何に詰まったか

Electron アプリの動画アーカイブ検索へ SQLite FTS5 を導入した。英単語の検索は動いたが、日本語タイトルに対する短い検索語が期待どおりヒットしなかった。

たとえば「ホロライブ配信」というタイトルに対し、通常の `MATCH 'ホロ'` はヒットしなかった。`MATCH 'ホロ*'` なら先頭一致にできるが、「ライブ」のような任意位置の部分一致はできなかった。

## 結論

検索対象が数百から数千件で、要件が「タイトルやチャンネル名の素直な部分一致」なら、FTS5 を維持するより `LIKE` の方が単純だった。

```sql
WHERE title LIKE '%' || @query || '%' ESCAPE '!'
```

ただし、利用者の入力に含まれる `%` と `_` はワイルドカードになるため、事前にエスケープする。

## FTS5で起きたこと

最初は次の仮想テーブルを作った。

```sql
CREATE VIRTUAL TABLE videos_fts USING fts5(
  title,
  description,
  tokenize = 'unicode61'
);
```

FTS5 はトークン単位で検索する。`unicode61` は Unicode の空白や句読点などを境界として扱うが、日本語の任意位置を自動的に部分文字列へ分割する tokenizer ではない。

最小構成では次の結果になった。

```sql
-- どちらもヒットしない
SELECT * FROM videos_fts WHERE videos_fts MATCH 'ホロ';
SELECT * FROM videos_fts WHERE videos_fts MATCH 'ライブ*';

-- トークン先頭へのprefix queryなのでヒットする
SELECT * FROM videos_fts WHERE videos_fts MATCH 'ホロ*';
```

そのため、次の要件とは相性が悪かった。

- 「地獄の果てまで」を「地獄」で検索する
- 「ホロライブ配信」を「ホロ」で検索する
- タイトル、チャンネル名、説明文の対象を切り替える

prefix query はトークン先頭の検索には使える。しかし、今回必要だった任意位置の部分一致は、期待する分割単位が tokenizer から得られなければ解決しない。

## LIKEへ切り替えた

検索 SQL は対象カラムをフラグで切り替える形にした。

```sql
SELECT *
FROM videos
WHERE status = 'ended'
  AND (
    (@searchTitle
      AND title LIKE '%' || @query || '%' ESCAPE '!')
    OR
    (@searchChannel
      AND channel_title LIKE '%' || @query || '%' ESCAPE '!')
    OR
    (@searchDescription
      AND description LIKE '%' || @query || '%' ESCAPE '!')
  )
ORDER BY scheduled_start_at DESC
LIMIT @limit;
```

アプリ側では `!` を escape 文字にした。

```js
function escapeLikeQuery(raw) {
  const trimmed = String(raw ?? '').trim();
  if (!trimmed) return '';

  return trimmed.replace(/[!%_]/g, '!$&');
}
```

これで入力値は次のように変換される。

| 入力 | SQLへ渡す値 |
| --- | --- |
| `ホロ` | `ホロ` |
| `100%` | `100!%` |
| `a_b` | `a!_b` |
| `!` | `!!` |

値は文字列連結で SQL 文へ埋め込まず、プレースホルダーへ渡す。

## テストしたケース

最低限、次を回帰テストにした。

```js
expect(searchByText('地獄').map((video) => video.id)).toEqual(['v1']);
expect(searchByText('ホロ').map((video) => video.id)).toEqual(['v2']);
expect(searchByText('100%').map((video) => video.id)).toEqual(['v3']);
expect(searchByText('_')).toEqual([]);
expect(searchByText('   ')).toEqual([]);
```

特に `%` と `_` のテストを入れないと、利用者の入力が意図せず全件検索に近い条件になる。

## FTS5を捨てる判断基準

今回は次の条件だったため `LIKE` を選んだ。

- ローカル DB で検索対象が数百から数千件
- 検索は利用者の操作時だけ
- 日本語の任意部分一致が最優先
- tokenizer や検索用インデックスの保守を増やしたくない

件数が増えて `LIKE '%query%'` の全走査が問題になったら、FTS5 の trigram tokenizer を候補にする。SQLite の公式ドキュメントでは、trigram tokenizer は一般的な部分文字列一致と、条件を満たす `LIKE` / `GLOB` のインデックス利用を支援する。

最初から高機能な全文検索を維持するのではなく、現在の件数と検索要件に合わせて選び直した。

## 参考

- [SQLite FTS5 Extension](https://www.sqlite.org/fts5.html)
- [LIKEへ切り替えたコミット](https://github.com/harness17/youtube-schedule/commit/692233e969d22865c17d0cdf8bb0734eb0b0830f)
