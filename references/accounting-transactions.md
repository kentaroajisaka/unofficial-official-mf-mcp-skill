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
