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
- 仕訳化は対応するMCPまたは会計画面から別途行う。

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

- 証憑はアップロードのみ。取得・削除・後付け紐づけは全て不可
- 期首残高（開始仕訳）の登録はできない

---

## 明細（取引）の取得

### mfc_ca_getTransactions

連携サービス（銀行・カード・手動の現金出納帳など）に取り込まれた明細を取得する。

#### パラメータ

| 名前 | 必須 | 説明 |
|------|-----|------|
| start_date / end_date | 期間検索時 | YYYY-MM-DD。差は366日以内 |
| ids | ID検索時 | API明細IDを1〜50件。両日付を省略。対応版のみ |
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

## 明細のID指定取得と状態更新

2026年11月24日のAPI V3更新で、ID指定検索と明細の対象外・解除が追加された。[公式リリースノート](https://developers.api-accounting.moneyforward.com/release-notes#2026-11-24)と[公式OpenAPI（YAML）](https://developers.api-accounting.moneyforward.com/v3/openapi.yaml)を参照。

### MCPの対応版と認証

利用中の接続のツール一覧で、`mfc_ca_getTransactions` が `ids` を受け取ること、`mfc_ca_putTransactionStatuses` が公開されていることを操作ごとに確認する。該当するツールと入力定義が配備された環境で使える。

| MCP | 確認した対応 | 認証 |
|---|---|---|
| 非公式 `mf-api` | [公開ソースの対応コミット](https://github.com/kentaroajisaka/mf-api-mcp/commit/351d8538ad9fea2e449b9a7a17d078d9f9786182)（パッケージ表記 `0.1.0`）。旧ビルドは期間検索のみの場合がある | APIキーをBearerトークンに交換。対象事業者の `office_code` を明示 |
| 公式 alpha | 両ツールの入力定義を確認済み | OAuth 2.0。対象事業者を認可した `access_token` を指定 |
| 公式 beta・非公式 `mf-full` | この更新の対応は利用中のツール定義を確認 | OAuth 2.0。接続先の事業者を確認 |

APIキー認証では発行者に対象事業者の「自動で仕訳 > 連携サービスから入力」の権限が必要。取得には閲覧、状態更新には編集を使う。OAuth 2.0 では取得に `mfc/accounting/transaction.read`、更新に `mfc/accounting/transaction.write` が必要。OAuth 2.0 の対象事業者は認可で決まり、`office_code` は無視される。

### ID指定取得と更新

1. `GET /api/v3/transactions`（`getTransactions`）の `ids` にAPIが返した明細の `id` を1〜50件指定する。HTTPのクエリでは `ids` をIDごとに繰り返す。返されたIDを二重にURLエンコードしない。ID検索では `start_date` と `end_date` を省略し、期間検索では両方指定する。期間検索のみのMCPで照合する場合は、状態で絞らず対象期間の全ページを確認し、API明細IDで完全一致させる。
2. 認証先の事業者、API明細ID、口座、日付、入出金、金額、取引内容、現在と変更後の状態を照合し、承認された範囲で更新する。明細に紐づく仕訳がある場合、APIでは事前に仕訳の削除が必要。この手順では該当明細を保留し、既存仕訳を保持する。
3. `PUT /api/v3/transactions/statuses`（`putTransactionStatuses`）のクエリ `to` に、対象外にする場合は `excluded`、対象外を解除する場合は `none` を渡す。JSON本文の `transaction_ids` は重複なしで1〜1,000件。対象外と未仕訳の間で更新できる。すでに指定先と同じ状態の明細は更新せず成功を返す。MCPを使う場合は配備先のツール定義に従う。
4. HTTP 200の `transaction_ids` はリクエストと同じ順序で返る。対象IDを同じ事業者で読み戻し、全件の `journalizing_status` と明細内容を確認する。タイムアウトなどで結果が不明な場合も再送前に読み戻す。更新ツールが未配備の場合は会計画面で操作できる。

検証用事業者の明細1件を使い、APIキー認証の公式REST APIでID指定取得と「対象外 → 未仕訳 → 対象外」の往復を確認した。復元後は取得した明細の全項目が操作前と一致した。検証にはテスト用明細のみを使用した。
