# 試算表・推移表の取得・分析

## PLの累計 vs 単月

ユーザーから「試算表を見たい」「PLを見たい」と言われたら、**まず確認する**:

- **累計**が知りたい → 試算表API（`getReportsTrialBalance*`）
- **単月**が知りたい → 推移表API（`getReportsTransition*`）

試算表APIのPLは**期首からの累計**で返る。単月PLが必要なら推移表を使うこと。

---

## 試算表の取得

### BS試算表

```
mfc_ca_getReportsTrialBalanceBalanceSheet
  access_token: "..."
  fiscal_year: 2025        # 省略で最新年度
  end_month: 12            # カレンダー月（12月まで）
```

### PL試算表（累計）

```
mfc_ca_getReportsTrialBalanceProfitLoss
  access_token: "..."
  fiscal_year: 2025
  end_month: 12
```

### 決算整理仕訳を除外する場合

```
journal_types: ["journal_entry"]   # 通常仕訳のみ
```

---

## 推移表の取得（単月PL）

### PL推移表

```
mfc_ca_getReportsTransitionProfitLoss
  access_token: "..."
  type: "monthly"          # ★ 必須
  fiscal_year: 2025
  start_month: 4           # 4月から
  end_month: 12            # 12月まで
```

各月の値が配列で返る。

### BS推移表

```
mfc_ca_getReportsTransitionBalanceSheet
  access_token: "..."
  type: "monthly"          # ★ 必須
  fiscal_year: 2025
```

---

## 補助科目付きで取得

```
with_sub_accounts: true
```

勘定科目の下に補助科目ごとの内訳が返る。

---

## 前年同月比較

1. 当期: `fiscal_year: 2025` で推移表取得
2. 前期: `fiscal_year: 2024` で推移表取得
3. 同じ科目名で突合して比較

**注意**: 科目IDは返らないので、**科目名の文字列一致**で突合する。

---

## 部門別分析

試算表・推移表は全部門合計のみ。部門別が必要な場合:

1. `mfc_ca_getJournals` で対象期間の全仕訳を取得
2. `department_name` でグループ化して集計

---

## 製造原価報告書がある場合

PLに製造原価の科目が混在する。以下に注意:

- `fs_type: 'cr'` の科目は製造原価報告書の科目
- 「当期製品製造原価」は売上原価の内訳として計上される
- 売上原価と製造原価を**二重カウントしない**こと

---

## 月次推移の表示例

ユーザーに見せる際の推奨フォーマット:

```
| 科目名     | 4月      | 5月      | 6月      | 累計      |
|-----------|---------|---------|---------|----------|
| 売上高     | 1,000   | 1,200   | 980     | 3,180    |
| 売上原価   | 600     | 720     | 590     | 1,910    |
| 売上総利益 | 400     | 480     | 390     | 1,270    |
```

金額はカンマ区切りで見やすく。千円単位・万円単位はユーザーの指示に従う。
