# 仕訳の取得・登録・更新

## 仕訳を取得する

### 手順

1. `mfc_ca_authorize` → 認証URL生成 → ユーザーに認証させる
2. `mfc_ca_exchange` → 認証コードをトークンに交換
3. `mfc_ca_currentOffice` → 会計期間（期首日・期末日）を確認
4. `mfc_ca_getJournals` → `start_date` / `end_date` を指定して取得

### ページネーション

- レスポンスの `pagination.total_count` で総件数を確認
- `page` / `per_page` で制御
- 全件取得が必要な場合は、`total_count` に達するまでページを繰り返す

### 開始仕訳の除外

期中の取引集計を行う場合、以下を除外すること:

```
entered_by === 'JOURNAL_TYPE_OPENING'
```

これは期首残高であり、期中の取引ではない。

### 税込金額の算出

```
税込金額 = value + tax_value
```

取得した `value` は税抜。必ず `tax_value` を加算すること。

---

## 仕訳を登録する

### 事前準備（必須）

登録前に以下のマスタを全て取得しておく:

1. `mfc_ca_getAccounts` → `account_id`
2. `mfc_ca_getSubAccounts` → `sub_account_id`
3. `mfc_ca_getTaxes` → `tax_id`
4. `mfc_ca_getDepartments` → `department_id`

### 手順

1. マスタを取得して正しいIDを確認
2. ユーザーに登録内容を提示して**確認を取る**
3. `mfc_ca_postJournals` で登録
4. レスポンスの仕訳番号を使ってMF画面のURLを生成し、ユーザーに提示

### 注意点

- `value` には**税込金額**を指定する（取得時と逆）
- IDは**URLエンコード済みのまま**渡す
- 補助科目なしの場合は `sub_account_id` を省略
- **削除はできない**。誤登録は逆仕訳で対応

### 仕訳登録の確認テンプレート

ユーザーへの確認時は以下の形式で提示:

```
日付: 2026/03/31
種別: 通常仕訳
借方: 旅費交通費 11,000円（課仕 10%）
貸方: 普通預金 11,000円（対象外）
摘要: 東京出張 新幹線代

この仕訳を登録してよろしいですか？
```

---

## 仕訳を更新する

### 手順

1. `mfc_ca_getJournalById` で現在の仕訳を取得
2. 変更内容をユーザーに確認
3. `mfc_ca_putJournals` で更新（仕訳全体を再送信）

### 注意

- 部分更新ではなく**全体置換**。変更しないフィールドも含めて送信すること
- 更新前に必ず最新の仕訳を取得して確認すること

---

## 特定科目の仕訳を検索する

`mfc_ca_getJournals` の `account_id` パラメータで、特定の勘定科目を含む仕訳だけを絞り込める。

```
account_id: "取得したaccount_id"
start_date: "2026-04-01"
end_date: "2026-04-30"
```

これにより、借方または貸方のいずれかにその科目を含む仕訳のみが返る。
