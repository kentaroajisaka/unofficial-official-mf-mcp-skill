---
name: unofficial-official-mf-mcp-skill
description: マネーフォワードクラウド会計のMCPサーバーを使用する際の非公式ガイド。認証フロー、仕訳取得・登録、試算表・推移表の取得、科目マスタの扱い、金額計算の注意点など、MF公式MCPの全ツールの使い方とクセを網羅。「MFの仕訳」「マネーフォワードの試算表」「MF認証」「MFで仕訳登録」等のキーワードで発動。
---

# マネーフォワードクラウド会計 公式MCP ガイド

## 認証手順（認証が切れたら以下を実行）

1. `mfc_ca_authorize` ツールを呼び出して認証URLを生成する
2. ユーザーに認証URLを提示し「このURLをブラウザで開いて、事業者を選択 → 許可 → 認証コードをコピーして貼り付けてください」と伝える
3. ユーザーから認証コードを受け取ったら、`mfc_ca_exchange` ツールでアクセストークンに交換する
4. アクセストークンの有効期限は**1時間**。期限切れエラーが出たら上記を再実行する
5. 取得した `access_token` は、以降の**全てのMFツール呼び出し**で `access_token` パラメータに指定すること

## ツール一覧

| カテゴリ | ツール | 用途 |
|---------|--------|------|
| 認証 | `mfc_ca_authorize` / `mfc_ca_exchange` | OAuth認証・トークン交換 |
| 事業者 | `mfc_ca_currentOffice` | 事業者情報・会計期間 |
| 仕訳 | `mfc_ca_getJournals` / `mfc_ca_getJournalById` | 仕訳取得 |
| 仕訳 | `mfc_ca_postJournals` / `mfc_ca_putJournals` | 仕訳登録・更新 |
| 試算表 | `mfc_ca_getReportsTrialBalanceBalanceSheet` / `ProfitLoss` | 試算表（累計） |
| 推移表 | `mfc_ca_getReportsTransitionBalanceSheet` / `ProfitLoss` | 推移表（月別） |
| マスタ | `mfc_ca_getAccounts` / `getSubAccounts` / `getDepartments` / `getTaxes` | 科目・部門・税区分 |
| 取引先 | `mfc_ca_getTradePartners` / `postTradePartners` | 取引先取得・登録 |
| 証憑 | `mfc_ca_postVouchers` | 証憑アップロード |
| 口座 | `mfc_ca_getConnectedAccounts` | 連携口座一覧 |
| 取引 | `mfc_ca_postTransactions` | 取引登録 |
| 辞書 | `mfc_ca_en_ja_dictionary` | 英日辞書 |

## PLの取得ルール

- ユーザーから「試算表を見たい」「PLを見たい」等の指示があった場合、**累計が知りたいのか単月が知りたいのか確認**すること
- **累計** → 試算表API（`getReportsTrialBalance*`）
- **単月** → 推移表API（`getReportsTransition*`）
- 試算表APIのPLは累計で返る。単月は推移表APIを優先

## パラメータの注意点

- `end_month` は**カレンダー月**を指定する（会計期の第N月目ではない）

## 金額の扱い

- **試算表・推移表**: MFでの設定上の経理方式に従う（そのまま使ってOK）
- **仕訳取得時**: `value` は税抜き。税込 = `value` + `tax_value`
- **仕訳登録時**: `value` は**税込金額**を指定する。APIが自動で税抜と消費税に分解する

## 科目の突合

- 試算表・推移表には**科目IDがない**。科目名の文字列一致で突合する

## 開始仕訳の除外

- `entered_by` が `JOURNAL_TYPE_OPENING` の仕訳は期首残高。**集計から除外**すること

## 製造原価報告書

- PLに製造原価報告書の科目が混在する。**二重カウントしないこと**

## 仕訳登録の事前準備

仕訳を登録する前に**必ず以下のマスタを取得**しておくこと:

1. `getAccounts` → `account_id` を確認
2. `getSubAccounts` → `sub_account_id` を確認
3. `getTaxes` → `tax_id` を確認
4. `getDepartments` → `department_id` を確認

- IDは**URLエンコード済みのまま渡す**こと。デコードするとエラーになる
- 補助科目なしの仕訳は `sub_account_id` を省略すればよい

## 仕訳の登録・更新・削除

- **登録・更新前に必ずユーザーに確認を取ること**
- **仕訳削除はAPI経由で可能**（`DELETE /api/v3/journals/{id}` → 204）。ただしMCPツールスキーマには未定義のため、直接APIを叩く必要がある
- 削除前に必ずユーザーに確認を取ること

### putJournalsは全置換API（重要）

`putJournals` はタグだけ・メモだけの部分更新ができない。`branches`, `journal_type`, `transaction_date` が**必須**で、仕訳全体を送り直す必要がある。

- タグだけ追加したい場合でも、既存のbranches（account_id, value, tax_id, department_id, invoice_kind, sub_account_id, remark）を**全て正確に再現**して送る必要がある
- フィールドを省略すると仕訳データが壊れる（科目・金額・部門等が消える）
- **バックアップ推奨**: バッチ更新前にgetJournalsの結果をJSONファイルに保存しておくこと

### タグの仕様

- 1タグ: **半角20文字以内**
- 1仕訳: 500タグ × 20文字 = 10,000文字まで確認済み
- **10,000タグ送信: サイレントに100件に切り捨て**（エラーなし。重大な注意点）
- タグの追加・変更・削除すべてAPI経由で可能
- MF UIでもタグ表示・個別削除可能

## 証憑アップロード

- **証憑アップロードはAPI経由で可能**（`POST /api/v3/vouchers`）。MCPツールスキーマには未定義だが、scopeに `voucher.write` が含まれておりAPIは存在する
- **正しい手順: 仕訳を先に登録 → `journal_id` を指定して証憑アップ**
- `journal_id` なしでもアップ可能だが、孤立した証憑になり**後から仕訳に紐づけるAPIは存在しない**
- 証憑の**取得・一覧・削除のAPIは存在しない**（全て404）

## 仕訳URLの生成

```
https://accounting.moneyforward.com/books?numbers={number}&recognized_at_from={期首日%2Fエスケープ}&recognized_at_to={期末日%2Fエスケープ}
```

## 部門別データ

- 試算表・推移表は**全部門合計**。部門別は仕訳APIから `department_name` で集計する

## 複数法人の同時利用

- 同じMCPコネクタで複数事業者の認証が可能
- **事業者名とトークンを紐づけて管理**すること

## MCPの制約（できないこと）

- データ連携の未仕訳明細は取得・仕訳化できない
- 証憑の取得・ダウンロード・削除はできない（APIが存在しない）。突合にはローカルのスキャンデータを使うこと
- 証憑の後付け紐づけはできない（アップ時にjournal_idを指定する以外の方法がない）
- 勘定科目・補助科目・部門・税区分の登録・編集はできない
- 期首残高（開始仕訳）の登録はできない

## REST APIを直接叩く場合

MCPツールではなくREST APIを直接叩く場合（バッチ処理等）の注意事項。

### ベースURL

```
https://api-accounting.moneyforward.com/api/v3
```

- **APIリファレンス（Redoc）**: https://developers.api-accounting.moneyforward.com/
- **OpenAPI仕様**: APIリファレンスサイトの説明文内にYAMLダウンロードリンクあり

### IDの%2F問題（重要）

journal ID・account ID等のリソースIDはBase64エンコードされており、`%2F`（= `/`）を含むことがある。
このIDをURLパスにそのまま渡すと、サーバー側で `%2F` がスラッシュとしてデコードされ、パスが壊れて **403 forbidden** になる。

**対策**: IDをURLパスに埋め込む前に `quote(id, safe='')` で**全体を再エンコード**すること。

```python
from urllib.parse import quote

journal_id = quote(raw_id, safe='')  # %2F → %252F, %3D → %253D 等
url = f"{BASE_URL}/journals/{journal_id}"
```

- `%2F` だけ二重エンコードする方法は **400エラー** になる（部分的な対処は不可）
- MCPツール経由の場合はMCPサーバーが自動処理するので問題ない
- REST API直叩きの場合のみ発生する

## スキーマ未定義だがAPIで利用可能な操作

以下はMCPツールスキーマに定義されていないが、アクセストークンで直接APIを叩けば利用可能:

| 操作 | エンドポイント | メソッド | 備考 |
|------|--------------|---------|------|
| 仕訳削除 | `/api/v3/journals/{id}` | DELETE | 204で成功。完全削除 |
| 証憑アップロード | `/api/v3/vouchers` | POST | journal_id指定で仕訳紐づけ |
