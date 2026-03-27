# 勘定科目・補助科目・税区分

## 勘定科目

### mfc_ca_getAccounts

#### パラメータ

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| available | boolean | No | 利用可能な科目のみ取得するフィルタ |

#### レスポンス構造

```typescript
{
  accounts: [{
    id: string;                    // 勘定科目ID
    name: string;                  // 科目名
    code?: string;                 // 科目コード
    search_key?: string;           // 検索キー
    account_category: string;      // 科目カテゴリ
    account_group?: string;        // 科目グループ
    sub_category?: string;         // サブカテゴリ
    financial_statement_type?: string;
    fs_type: 'bs' | 'pl' | 'cr';  // BS/PL/製造原価
    display_order: number;         // 表示順
    available?: boolean;           // 利用可能フラグ
    tax_id?: string;               // デフォルト税区分ID
    sub_accounts?: [{              // 補助科目（紐づく場合）
      id: string;
      name: string;
      code?: string;
      display_order: number;
    }];
  }]
}
```

---

## 補助科目

### mfc_ca_getSubAccounts

#### パラメータ

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| account_id | string | No | 勘定科目IDで絞り込み |

#### 用途

- 仕訳登録時に `sub_account_id` を指定するために事前取得する
- `account_id` を指定すると、その科目に紐づく補助科目のみ返る
- 補助科目なしの仕訳は `sub_account_id` を省略すればよい

---

## 税区分

### mfc_ca_getTaxes

#### パラメータ

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| available | boolean | No | 利用可能な税区分のみ取得するフィルタ |

#### レスポンス構造

```typescript
{
  taxes: [{
    id: string;              // 税区分ID
    name: string;            // 名称
    abbreviation?: string;   // 略称（例: '課仕 10%'）
    short_name?: string;
    search_key?: string;
    tax_rate?: number;       // 税率
    rate?: number;
    available?: boolean;
  }]
}
```

---

## IDの扱い ★重要

- 全てのID（`account_id`, `sub_account_id`, `tax_id`, `department_id`）は**URLエンコード済みの文字列**
- 仕訳登録・更新時は**エンコード済みのまま渡す**こと
- デコードしてから渡すとエラーになる

---

## 制約

- 勘定科目・補助科目・税区分の**登録・編集はMCPではできない**
- MFクラウド会計の画面から設定する必要がある
