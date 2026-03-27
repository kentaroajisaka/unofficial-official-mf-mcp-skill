# 仕訳（Journals）

## 仕訳取得

### mfc_ca_getJournals — 仕訳一覧取得

#### パラメータ

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| start_date | string | No | 対象期間の開始日（取引日基準）|
| end_date | string | No | 対象期間の終了日（取引日基準）|
| account_id | string | No | 勘定科目ID。借方貸方のいずれかに持つ仕訳のみ返却 |
| is_realized | boolean | No | 未実現仕訳フラグ。省略で全件 |
| page | integer | No | ページ番号 |
| per_page | integer | No | 1ページあたり件数 |

**注意**: `start_date` または `end_date` のいずれかを指定する必要がある。指定された日付が含まれる会計期間の仕訳のみ返却される。

#### レスポンス構造

```typescript
{
  journals: [{
    id: string;              // 仕訳ID
    number: number;          // 仕訳番号
    transaction_date: string; // 取引日
    is_realized: boolean;
    journal_type: 'journal_entry' | 'adjusting_entry';
    entered_by?: string;     // ★ 'JOURNAL_TYPE_OPENING' = 期首残高
    memo?: string;
    tags: string[];
    branches: [{
      remark?: string;       // 摘要
      creditor?: {           // 貸方
        value: number;       // ★ 税抜金額
        tax_value?: number;  // ★ 消費税額（税込 = value + tax_value）
        account_id: string;
        account_name: string;
        sub_account_id?: string;
        sub_account_name?: string;
        tax_id?: string;
        tax_name?: string;        // 税区分略称（例: '課仕 10%'）
        tax_long_name?: string;   // 税区分名称
        department_id?: string;
        department_name?: string;
        trade_partner_code?: string;
        trade_partner_name?: string;
        invoice_kind?: string;    // インボイス種別
      };
      debitor?: { /* 借方: 同構造 */ };
    }];
  }];
  pagination: {
    total_count: number;
    page: number;
    per_page: number;
  };
}
```

### mfc_ca_getJournalById — 仕訳ID指定取得

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| id | string | Yes | 仕訳ID |

#### 金額の重要ルール（取得時）

- `value` は**税抜金額**
- `tax_value` は消費税額
- **税込金額 = value + tax_value**

#### 開始仕訳の識別

- `entered_by` が `JOURNAL_TYPE_OPENING` の仕訳は**期首残高**
- 集計時は**必ず除外**すること

---

## 仕訳登録

### mfc_ca_postJournals — 仕訳作成

#### パラメータ

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| journal | object | Yes | 仕訳データ（下記参照） |

#### journal オブジェクト

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| transaction_date | string | Yes | 取引日 |
| journal_type | string | Yes | `journal_entry`（通常）/ `adjusting_entry`（決算整理）|
| branches | array | Yes | 仕訳行の配列（最大300行）|
| memo | string | No | メモ |
| tags | string[] | No | タグ配列 |

#### branch（仕訳行）

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| remark | string | No | 摘要 |
| debitor | object | No | 借方 |
| creditor | object | No | 貸方 |

#### debitor / creditor（借方/貸方）

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| account_id | string | Yes | 勘定科目ID |
| value | integer | Yes | **税込金額** ★登録時は税込！ |
| tax_id | string | No | 税区分ID |
| sub_account_id | string | No | 補助科目ID |
| department_id | string | No | 部門ID |
| trade_partner_code | string | No | 取引先コード |
| invoice_kind | string | No | `INVOICE_KIND_NOT_TARGET` / `INVOICE_KIND_QUALIFIED` / `INVOICE_KIND_UNQUALIFIED_80` |

#### 金額の重要ルール（登録時）

- `value` には**税込金額**を指定する
- APIが自動で税抜と消費税に分解する
- 取得時（tax抜）と登録時（税込）で**意味が逆**なので注意

---

## 仕訳更新

### mfc_ca_putJournals — 仕訳更新

パラメータは `postJournals` と同じ構造に加え、`id`（仕訳ID）が必須。

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| id | string | Yes | 更新対象の仕訳ID |
| journal | object | Yes | 仕訳データ（postJournalsと同構造） |

---

## 仕訳URLの生成

MFクラウド会計の画面で仕訳を表示するURL:

```
https://accounting.moneyforward.com/books?numbers={number}&recognized_at_from={期首日}&recognized_at_to={期末日}
```

- `number`: 仕訳番号（`journal.number`）
- 日付は `%2F` でエスケープ（例: `2026%2F04%2F01`）

## 仕訳削除（スキーマ未定義・API実在）

`DELETE /api/v3/journals/{id}` で仕訳を完全削除できる。MCPツールスキーマには未定義だが、APIは存在する（204で成功）。

```
DELETE https://api-accounting.moneyforward.com/api/v3/journals/{journal_id}
Authorization: Bearer {access_token}
```

- 削除前に**必ずユーザーに確認**を取ること
- 登録前にも**必ずユーザーに確認**を取ること
