# 試算表・推移表（Reports）

## 試算表（残高試算表） — 累計

### mfc_ca_getReportsTrialBalanceBalanceSheet — BS試算表
### mfc_ca_getReportsTrialBalanceProfitLoss — PL試算表

#### パラメータ（BS/PL共通）

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| fiscal_year | integer | No | 会計年度。省略で最新 |
| start_month | integer | No | 集計開始月（カレンダー月）。省略で期首月 |
| end_month | integer | No | 集計終了月（カレンダー月）。省略で期末月 |
| start_date | string | No | 対象期間の開始日 |
| end_date | string | No | 対象期間の終了日 |
| with_sub_accounts | boolean | No | 補助科目を含めるか |
| include_tax | boolean | No | 税込表示（税抜(内税)方式の場合のみ有効） |
| journal_types | array | No | 仕訳種別フィルタ: `journal_entry` / `adjusting_entry`。省略で両方 |

**注意**: `journal_types` は試算表のみ。推移表にはない。

#### レスポンスのcolumns（固定）

| カラム | 説明 |
|--------|------|
| opening_balance | 前期残高 |
| debit_amount | 借方金額 |
| credit_amount | 貸方金額 |
| closing_balance | 期末残高 |
| ratio | 構成比（分母が0の場合はnull） |

#### 特記事項

- 金額が全て0の科目・補助科目は返却されない
- 未実現仕訳は含まれない
- 常に**全部門合計**で集計される
- **PLは累計**で返る。単月のPLが必要な場合は推移表APIを使うこと

---

## 推移表 — 月次

### mfc_ca_getReportsTransitionBalanceSheet — BS推移表
### mfc_ca_getReportsTransitionProfitLoss — PL推移表

#### パラメータ（BS/PL共通）

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| type | string | Yes | **`monthly` 固定**（現在は月次のみ） |
| fiscal_year | integer | No | 会計年度。省略で最新 |
| start_month | integer | No | 集計開始月（カレンダー月）。省略で期首月 |
| end_month | integer | No | 集計終了月（カレンダー月）。省略で期末月 |
| with_sub_accounts | boolean | No | 補助科目を含めるか |
| include_tax | boolean | No | 税込表示（税抜(内税)方式の場合のみ有効） |

#### レスポンスのcolumns

指定した期間の各月の値が配列で返却される。

#### 特記事項

- 金額が全て0の科目・補助科目は返却されない
- 未実現仕訳は含まれない
- 常に**全部門合計**で集計される
- **`type` パラメータは必須**（`monthly` を指定）

---

## パラメータの注意点

### end_month はカレンダー月

- `end_month` は**カレンダー月**（1〜12）を指定する
- 会計期の第N月目ではない
- 例: 3月決算法人の10月分まで → `end_month: 10`

### include_tax の挙動

- 事業者の経理方式が「税抜(内税)」の場合のみ有効
- 「税込」「税抜(別記)」方式では**このパラメータは無視される**
- 通常はMFの設定に従えばよい（指定不要）

---

## 科目突合の注意

- 試算表・推移表には**科目IDがない**
- 科目の突合は**科目名の文字列一致**で行う
- getAccountsで取得した科目名と照合すること

---

## 部門別データの取得方法

- 試算表・推移表は**全部門合計のみ**
- 部門別の数値が必要な場合は仕訳API（`getJournals`）から `department_name` で集計する

---

## 製造原価報告書

- PLに製造原価報告書の科目が混在する場合がある
- **二重カウントしないこと**（当期製品製造原価は売上原価の内訳）
