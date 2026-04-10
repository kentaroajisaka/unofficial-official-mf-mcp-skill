---
name: unofficial-official-mf-mcp-skill
description: マネーフォワードクラウド会計の公式MCP（mf-official）を使用する際のガイド。認証フロー、仕訳取得・登録、試算表・推移表の取得、科目マスタの扱い、金額計算の注意点など、MF公式MCPの全ツールの使い方とクセを網羅。「MFの仕訳」「マネーフォワードの試算表」「MF認証」「MFで仕訳登録」等のキーワードで発動。
---

# マネーフォワードクラウド会計 公式MCP ガイド

## alpha版とbeta版の使い分け

MF公式MCPにはalpha版とbeta版の2つのエンドポイントがある。**両方同時に`.claude.json`に登録可能**。

| | alpha版 | beta版 |
|---|---|---|
| URL | `https://alpha.mcp.developers.biz.moneyforward.com/mcp/ca/v3` | `https://beta.mcp.developers.biz.moneyforward.com/mcp/ca/v3` |
| 認証方式 | 手動（認証コードをコピペ） | 自動（PKCE+localhostコールバック） |
| トークン有効期限 | **約1時間**（頻繁に再認証が必要） | 長時間（詳細不明） |
| 複数法人同時利用 | **✅ 可能**（法人ごとに認証して同時保持） | ❌ 1法人ずつ（切替時に再認証） |
| 手間 | 毎回コードコピペが面倒 | 認証はほぼワンクリック |

**使い分けの目安**:
- **1社だけ作業する場合** → beta版が楽（認証が簡単、長持ち）
- **複数法人を同時に処理する場合** → alpha版（複数法人の認証を同時保持できる）

### `.claude.json` の設定例

```json
{
  "mcpServers": {
    "mf-official-beta": {
      "type": "http",
      "url": "https://beta.mcp.developers.biz.moneyforward.com/mcp/ca/v3"
    },
    "mf-official-alpha": {
      "type": "http",
      "url": "https://alpha.mcp.developers.biz.moneyforward.com/mcp/ca/v3"
    }
  }
}
```

### ツール名について

ツール名は `.claude.json` のサーバー名に依存する。上記設定例の場合:
- beta版: `mcp__mf-official-beta__authenticate`, `mcp__mf-official-beta__mfc_ca_getJournals` 等
- alpha版: `mcp__mf-official-alpha__authenticate`, `mcp__mf-official-alpha__mfc_ca_getJournals` 等

本ガイドでは便宜上 `mfc_ca_*` とツール名のサフィックス部分のみで記載する。

## 認証手順

### beta版
1. `authenticate` ツールを呼び出す
2. 認証URLが生成されるので、ユーザーに「このURLをブラウザで開いて、事業者を選択 → 許可してください」と伝える
3. ブラウザでの認証完了後、ローカルコールバック（localhost）経由で自動的にトークンが取得される。**トークンの手動コピペは不要**
4. 認証完了後は `mfc_ca_*` ツールが自動的に使えるようになる。**access_tokenパラメータの手動指定も不要**（サーバー側で自動管理）
5. 認証切れ時は再度 `authenticate` を実行する

### alpha版
1. `mfc_ca_authorize` を呼び出す → 認証URLが生成される
2. ユーザーにブラウザで認証URLを開いてもらい、事業者を選択→許可
3. ブラウザに表示される**認証コードをコピー**してもらい、ユーザーがチャットに貼り付ける
4. **`mfc_ca_exchange` で認可コードをアクセストークンに交換する**（⚠️ この手順を飛ばすとAPI呼び出しが全て失敗する）
5. 交換成功後、`mfc_ca_currentOffice` 等のAPIが利用可能になる
6. **約1時間で期限切れ**。切れたら再度 手順1から実行する
7. 複数法人を扱う場合は、法人ごとに認証を行えば**同時に保持**できる

## ツール一覧

| カテゴリ | ツール | 用途 |
|---------|--------|------|
| 認証 | `authenticate` | OAuth認証（beta版はこれだけでOK） |
| 認証 | `mfc_ca_authorize` | 認証URL生成（alpha版ステップ1） |
| 認証 | `mfc_ca_exchange` | 認可コード→アクセストークン交換（alpha版ステップ2、**必須**） |
| 事業者 | `currentOffice` | 事業者情報・会計期間 |
| 仕訳 | `getJournals` / `getJournalById` | 仕訳取得 |
| 仕訳 | `postJournals` / `putJournals` | 仕訳登録・更新 |
| 試算表 | `getReportsTrialBalanceBalanceSheet` / `ProfitLoss` | 試算表（累計） |
| 推移表 | `getReportsTransitionBalanceSheet` / `ProfitLoss` | 推移表（月別） |
| マスタ | `getAccounts` / `getSubAccounts` / `getDepartments` / `getTaxes` | 科目・部門・税区分 |
| 取引先 | `getTradePartners` / `postTradePartners` | 取引先取得・登録 |
| 証憑 | `postVouchers` | 証憑アップロード |
| 口座 | `getConnectedAccounts` | 連携口座一覧 |
| 取引 | `postTransactions` | 取引登録 |
| 辞書 | `en_ja_dictionary` | 英日辞書 |

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

- beta版では認証時に選択した事業者に自動的に紐づく
- 事業者を切り替える場合は `authenticate` で再認証し、別の事業者を選択する（beta版の場合）
- alpha版は複数法人の認証を同時保持できるため、切り替え不要

## MCPの制約（できないこと）

- データ連携の未仕訳明細は取得・仕訳化できない
- 証憑の取得・ダウンロード・削除はできない（APIが存在しない）。突合にはローカルのスキャンデータを使うこと
- 証憑の後付け紐づけはできない（アップ時にjournal_idを指定する以外の方法がない）
- 勘定科目・補助科目・部門・税区分の登録・編集はできない
- 期首残高（開始仕訳）の登録はできない

## 仕訳の一括取得（大量ページネーション）

全仕訳のバックアップや一括集計が必要な場合は、`recipes/bulk-journal-fetch.md` の手順に従う。

- per_page=500で通年一括取得（月ごとに分ける必要なし）
- 結果ファイルを `data/{会社名}/tmp/page_XX.txt` に保存
- スキル同梱の `scripts/merge_journals.py` で結合（パスは `find / -name merge_journals.py` で確認）
- 重複排除・日付順ソート済みの `journals-backup.json` を出力

## REST APIを直接叩く場合

MCPツールではなくREST APIを直接叩く場合（バッチ処理等）の注意事項。

### ベースURL

```
https://api-accounting.moneyforward.com/api/v3
```

- **APIリファレンス（Redoc）**: https://developers.api-accounting.moneyforward.com/
- **OpenAPI仕様（ローカルコピー）**: `~/claude/customer-dashboard/openapi.yaml`

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
