---
title: JSON.stringifyでDateがUTC文字列になりサーバーで日付が1日ズレた
tags:
  - JavaScript
  - JSON
  - DateTime
  - フロントエンド
  - ASP.NET
private: false
updated_at: ''
id: null
organization_url_name: null
slide: false
ignorePublish: false
---

## 何が起きたか

日付ピッカーで選んだ日付を JavaScript の `Date` オブジェクトとして受け取り、`JSON.stringify` でサーバーに送った。クライアント側では `2026-01-15` を選択したのに、サーバー側では `2026-01-14`（前日）として保存された。

```javascript
// 日付ピッカーやライブラリが Date オブジェクトを返すケース
const date = new Date(2026, 0, 15); // ローカル（JST）の 1/15 午前0時
const body = JSON.stringify({ targetDate: date });
console.log(body);
// → {"targetDate":"2026-01-14T15:00:00.000Z"}
//                  ^^^^^^^^^^  ← 前日の15時になっている
```

## 原因

`JSON.stringify` は `Date` オブジェクトに対して `toISOString()` を呼ぶ。`toISOString()` は **常に UTC 文字列** を返す。

JST（UTC+9）で午前 0 時の `2026-01-15` は、UTC では前日の 15:00 になる。

```
JST:  2026-01-15 00:00:00+09:00
UTC:  2026-01-14 15:00:00Z        ← 9時間巻き戻る
```

仕様の流れはこう。

```
JSON.stringify(dateObj)
  → dateObj.toJSON()
    → dateObj.toISOString()
      → "2026-01-14T15:00:00.000Z"  (UTC固定)
```

サーバー側で UTC 文字列をそのままパースすると、UTC の日付部分 `2026-01-14` が使われて 1 日ズレる。

## 再現

ブラウザの DevTools コンソールで確認できる。

```javascript
// ズレるケース: コンストラクタ引数で Date を作る場合
const d = new Date(2026, 0, 15); // ローカル（JST）の 1/15 午前0時
console.log(d.toString());
// → "Thu Jan 15 2026 00:00:00 GMT+0900 (日本標準時)"

console.log(d.toISOString());
// → "2026-01-14T15:00:00.000Z"  ← 前日になる

console.log(JSON.stringify({ date: d }));
// → {"date":"2026-01-14T15:00:00.000Z"}
```

日付ピッカーのライブラリや UI フレームワークが `new Date(year, month, day)` 形式で Date を返す場合、この問題が起きる。

### 紛らわしい点: `new Date("2026-01-15")` はズレない

`input[type="date"]` の `.value` は `"2026-01-15"` という文字列を返す。この文字列を `new Date()` に渡した場合、ES2015+ の仕様では **date-only 文字列は UTC として解釈** される。

```javascript
// ズレないケース: ISO 8601 date-only 文字列
const d = new Date("2026-01-15"); // UTC の 1/15 午前0時として解釈
console.log(d.toISOString());
// → "2026-01-15T00:00:00.000Z"  ← ズレない

console.log(JSON.stringify({ date: d }));
// → {"date":"2026-01-15T00:00:00.000Z"}  ← 偶然ズレない
```

ただし、`new Date("2026-01-15T00:00:00")`（日時文字列にタイムゾーン指定なし）は**ローカル時刻として解釈**される。文字列に時刻部分を付けた瞬間に挙動が変わるので注意。

```javascript
// ズレるケース: 時刻付き・タイムゾーンなし → ローカル時刻
const d = new Date("2026-01-15T00:00:00");
console.log(d.toISOString());
// → "2026-01-14T15:00:00.000Z"  ← 前日になる
```

## 解決方法

### 方法1: 文字列のまま送る（推奨）

`input[type="date"]` の `.value` は文字列 `"2026-01-15"` を返す。Date オブジェクトに変換せず、そのまま送る。

```javascript
const dateStr = document.querySelector('input[type="date"]').value;
// "2026-01-15" — 文字列のまま

const body = JSON.stringify({ targetDate: dateStr });
// {"targetDate":"2026-01-15"} — ズレない
```

サーバー側は文字列をそのまま `DateOnly` や日付型にバインドする。`DateOnly` は .NET 6 で導入されたが、`System.Text.Json` での組み込みシリアライズは .NET 7 以降で対応。.NET 6 ではカスタムコンバーターが必要。

```csharp
// ASP.NET Core
public class RequestDto
{
    public DateOnly TargetDate { get; set; }  // "2026-01-15" → OK
}
```

### 方法2: ローカル日付文字列に変換してから送る

どうしても Date オブジェクトを経由する場合は、`toISOString()` ではなくローカル日付を文字列化する。

```javascript
function toLocalDateString(date) {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
}

const d = new Date(2026, 0, 15);
const body = JSON.stringify({ targetDate: toLocalDateString(d) });
// {"targetDate":"2026-01-15"}
```

### 方法3: サーバー側で UTC を考慮する

サーバー側で受け取った UTC 文字列をローカルタイムゾーンに変換してから日付部分を取る。ただしサーバーのタイムゾーン設定に依存するため、方法1 のほうが安全。

## 注意点

- `new Date("2026-01-15")`（date-only 文字列）は **UTC** として解釈される。`new Date(2026, 0, 15)`（コンストラクタ引数）と `new Date("2026-01-15T00:00:00")`（時刻付き・TZ なし）は **ローカル時刻** として解釈される。この違いがズレの原因
- `Intl.DateTimeFormat` で表示用にフォーマットする場合も、元の Date がローカルか UTC かで結果が変わる
- ASP.NET Core の `[DataType(DataType.Date)]` は表示・バリデーション用のメタデータであり、JSON バインディングの挙動は変えない。JSON で日付だけを受け取るなら `DateOnly` 型（.NET 6 で導入、`System.Text.Json` の組み込み JSON バインディング対応は .NET 7+）を使う
- 「日付だけ」を扱うフィールドでは、`Date` オブジェクトを経由させないのが一番安全

## まとめ

| やり方 | ズレるか | 推奨度 |
|--------|---------|--------|
| `input.value`（文字列）をそのまま送る | ズレない | ◎ |
| `toLocalDateString` で文字列化して送る | ズレない | ○ |
| `JSON.stringify(new Date(...))` で送る | **ズレる** | ✕ |

`JSON.stringify` + `Date` の組み合わせで日付だけを送ると UTC 変換でズレる。日付フィールドは文字列のまま扱うのが最もシンプルな解決策。

## 参考リンク

- [MDN - Date.prototype.toISOString()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/toISOString)
- [MDN - JSON.stringify()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON/stringify)
- [MDN - Date() constructor](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date/Date)
