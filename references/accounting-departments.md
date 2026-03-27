# 部門（Departments）

## mfc_ca_getDepartments

#### パラメータ

| 名前 | 型 | 必須 | 説明 |
|------|-----|------|------|
| access_token | string | Yes | アクセストークン |

#### レスポンス構造

```typescript
{
  departments: [{
    id: string;            // 部門ID
    name: string;          // 部門名
    code?: string;         // 部門コード
    parent_id: string | null; // 親部門ID
    search_key?: string;   // 検索キー
  }]
}
```

#### 用途

- 仕訳登録時に `department_id` を指定するための事前取得
- 部門に親子関係がある場合は `parent_id` で階層を把握できる

#### 制約

- 部門の**登録・編集はMCPではできない**
- 試算表・推移表は常に全部門合計。部門別は仕訳APIから集計する
