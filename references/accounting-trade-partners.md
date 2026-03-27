# 取引先（Trade Partners）

## 取引先取得

### mfc_ca_getTradePartners

#### パラメータ

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| available | boolean | No | 利用可能な取引先のみ |

#### レスポンス構造

```typescript
{
  trade_partners: [{
    code: string;                          // 取引先コード
    name: string;                          // 取引先名
    search_key?: string;                   // 検索キー
    invoice_registration_number?: string;  // 適格請求書発行事業者登録番号
    available?: boolean;
  }]
}
```

---

## 取引先登録

### mfc_ca_postTradePartners

#### パラメータ

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |
| trade_partners | array | Yes | 登録する取引先の配列 |

#### trade_partners 配列の各要素

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| name | string | Yes | 取引先名称 |
| search_key | string | No | 検索名称 |
| invoice_registration_number | string | No | 適格請求書発行事業者登録番号 |
| corporate_number | string | No | 法人番号 |
| available | boolean | No | 利用可能フラグ |

#### 備考

- 仕訳の借方/貸方に `trade_partner_code` を指定する際は、ここで取得/登録した `code` を使う
- 一括登録（配列で複数件）が可能
