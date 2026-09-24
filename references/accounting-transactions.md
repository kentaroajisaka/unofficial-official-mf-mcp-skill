# 連携口座・取引登録

## 連携口座一覧

### mfc_ca_getConnectedAccounts

MFクラウド会計に登録されている連携サービス（銀行口座・クレジットカード等）の一覧を取得する。

#### パラメータ

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |

#### 用途

- `postTransactions` で明細を登録する際の `connected_account_id` を確認するため

---

## 取引（明細）登録

### mfc_ca_postTransactions

連携サービスに明細を手動登録する。

#### パラメータ

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| connected_account_id | string | Yes | 明細を作成する連携サービスID |
| transactions | array | Yes | 明細の配列 |

#### transactions 配列の各要素

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| content | string | Yes | 取引内容 |
| date | string | Yes | 取引日 |
| side | string | Yes | `INCOME`（収入）/ `EXPENSE`（支出） |
| value | integer | Yes | 取引金額 |
| memo | string | No | メモ（最大200文字。全角の場合は約74文字） |

#### 備考

- これは仕訳ではなく**未仕訳の明細**を登録するもの
- 登録後、MFクラウド会計の画面で仕訳化する必要がある
- MCPでは未仕訳明細の取得・仕訳化はできない

---

---

## 証憑アップロード（スキーマ未定義・API実在）

### POST /api/v3/vouchers

仕訳に証憑ファイルを添付する。MCPツールスキーマには未定義だが、scopeに `voucher.write` が含まれておりAPIは存在する。

#### リクエスト

```json
{
  "journal_id": "仕訳ID（省略可）",
  "voucher_files": [{
    "file_name": "receipt.jpg",
    "file_data": "base64エンコードデータ"
  }]
}
```

#### 正しい手順

1. `postJournals` で仕訳を登録 → `journal.id` を取得
2. `POST /vouchers` で `journal_id` を指定して証憑アップ

#### 証憑に関する重要な制約

- `journal_id` なしでもアップ可能だが、孤立した証憑になる
- **後から仕訳に紐づけるAPIは存在しない**（PATCH/PUT /vouchers は全て404）
- 証憑の**取得（GET）は不可**（GET /vouchers、GET /vouchers/{id} は全て404）
- 証憑の**削除（DELETE）は不可**（DELETE /vouchers/{id} は404）
- 証憑の**一覧取得も不可**

---

## 制約

- データ連携の**未仕訳明細は取得・仕訳化できない**
- 証憑はアップロードのみ。取得・削除・後付け紐づけは全て不可
- 期首残高（開始仕訳）の登録はできない

---

## 明細（取引）の取得

### mfc_ca_getTransactions

連携サービス（銀行・カード・手動の現金出納帳など）に取り込まれた明細を取得する。mf-full では `mfc_ca_getTransactions`。

#### パラメータ（2026-09-24 実測）

| 名前 | 必須 | 説明 |
|------|-----|------|
| start_date / end_date | Yes | YYYY-MM-DD。差は366日以内 |
| journalizing_statuses | No | `none`（未仕訳）/ `excluded`（対象外＝「仕訳しない」にした明細）/ `registered`（仕訳済み）/ `modified` / `new_voucher_attached` |
| per_page | No | **10〜500**。1000 を渡すと 400 エラー（`per_page must be between 10 and 500`） |
| value_min / value_max | No | 金額で絞る。**`side`（INCOME / EXPENSE）とセットでないと 400 エラー**（`side is required when value_min or value_max is provided`） |
| side | No | `INCOME`（入金）/ `EXPENSE`（出金） |
| connected_account_id / connected_sub_account_id | No | 口座で絞る。ID は `getConnectedAccounts` で取る |

#### 月次監査での使い方

- `journalizing_statuses: ["none"]` で対象月の**未仕訳の明細**を出す。0件でなければ仕訳漏れの候補
- `journalizing_statuses: ["excluded"]` で「仕訳しない」にした明細を出し、**同じ日（前後数日）・同じ口座（補助科目）・同じ金額の仕訳があるか**を仕訳データと突き合わせる。自計化の会社は、借入返済・給与・資金移動などの明細を対象外にして、手で仕訳を入れていることが多い
- 明細の `content`（相手名）と仕訳の摘要が食い違うとき（例：口座間の移動なのに相手名が個人名）は、相手側の口座の明細に同じ日・同じ額があるかを `side: INCOME` と金額で絞って確かめる
- 明細の `connected_sub_account_id` と仕訳の補助科目名の対応は、`getConnectedAccounts` の `connected_sub_accounts[].name` と `sub_account_id` で取る
