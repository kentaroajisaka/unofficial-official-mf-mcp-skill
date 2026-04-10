# 仕訳の一括取得

## いつ使うか

- 全仕訳のバックアップが必要なとき（タグ一括更新前のバックアップ等）
- 仕訳ベースの集計・分析で全件が必要なとき

## API制約

- **`per_page` の上限は10,000**（2026-04-10 実測確認済み。10,001以上は `invalid_query_parameter_value` エラー）
- `getJournals` のレスポンスは1件あたり数KB〜100KB（branch数に比例）
- Claude Codeのツール結果サイズ上限を超えるとファイルに自動保存される

> **v2.1.0以前では `per_page` 上限を500と記載していましたが、実際にはAPIは10,000まで受け付けます。**
> 複数法人で per_page=500 と per_page=10000 の結果をJSON完全比較し、データの欠落・劣化がないことを確認済みです。

## 手順

### Step 1: 総件数を確認

```
getJournals(start_date="期首日", end_date="期末日", per_page=1, page=1)
```

レスポンスの `metadata.total_count` を確認。

### Step 2: 取得

**10,000件以下（大半の法人）→ 1回で完了:**

```
getJournals(start_date="期首日", end_date="期末日", per_page=10000, page=1)
```

レスポンスはClaude Codeが自動でファイルに保存する。そのファイルパスがそのまま使える。

**10,000件超の場合 → 2回に分けて取得:**

```
getJournals(start_date="期首日", end_date="期末日", per_page=10000, page=1)
getJournals(start_date="期首日", end_date="期末日", per_page=10000, page=2)
```

- 通年で一括取得可能（月ごとに分ける必要はない）
- 各ページの結果ファイルを `data/{会社名}/tmp/page_01.txt`, `page_02.txt` に保存

### Step 3: マージ（複数ページの場合のみ）

1ページで全件取得できた場合はこのステップ不要。

merge_journals.pyはスキルのscripts/フォルダに同梱されている。パスは環境によって異なる:
- **Claude Code**: `~/.claude/skills/{スキル名}/scripts/merge_journals.py`
- **Claude Desktop (Cowork)**: `/sessions/{セッション名}/mnt/.claude/skills/{スキル名}/scripts/merge_journals.py`

スクリプトの場所が不明な場合は `find / -name merge_journals.py 2>/dev/null` で探す。

```bash
python3 /path/to/merge_journals.py data/{会社名}
```

出力:
- `data/{会社名}/journals-backup.json` — 全仕訳（重複排除・日付順ソート済み）
- 月別件数サマリー

マージ後: `rm -rf data/{会社名}/tmp/`

## merge_journals.py の仕様

- 入力: `data_dir/tmp/page_*.txt`（MCP tool-result形式 or 生JSON）
- 出力: `data_dir/journals-backup.json`
- 重複排除: 仕訳IDベース（ページ境界での重複を防止）
- ソート: transaction_date → number の昇順
- MCP tool-result形式（`[{type: "text", text: "..."}]`）と生JSON形式の両方に対応

## journals-backup.json のスキーマ

```json
{
  "fetched_at": "2026-04-09T...",
  "total_count": 7115,
  "actual_count": 7115,
  "journals": [
    {
      "id": "...",
      "number": 1,
      "transaction_date": "2025-04-01",
      "entered_by": "JOURNAL_TYPE_OPENING",
      "journal_type": "journal_entry",
      "tags": ["CF:D1:X", ...],
      "memo": "",
      "create_time": "...",
      "update_time": "...",
      "is_realized": true,
      "term_period": 2025,
      "voucher_file_ids": [],
      "branches": [
        {
          "debitor": {
            "account_id": "...",
            "account_name": "普通預金",
            "sub_account_id": "...",
            "sub_account_name": "みずほ銀行",
            "department_id": "...",
            "department_name": "本部",
            "tax_id": "...",
            "tax_name": "対象外",
            "tax_long_name": "対象外",
            "value": 49500,
            "tax_value": 0,
            "invoice_kind": "INVOICE_KIND_NOT_TARGET",
            "trade_partner_code": null,
            "trade_partner_name": null
          },
          "creditor": { ... },
          "remark": "摘要テキスト"
        }
      ]
    }
  ]
}
```

## 実績

- A社（約4,300件）: per_page=10000で1回、約10MB
- B社（約18,600件）: per_page=10000で2回、約15MB+α
- C社（約7,100件）: per_page=10000で1回

## データ整合性の検証結果（2026-04-10）

per_page=500 と per_page=10000 で同一仕訳500件を完全比較:
- ID・tags・branches・全フィールドが**JSONレベルで完全一致**
- per_page増加によるデータ欠落・劣化は一切なし
