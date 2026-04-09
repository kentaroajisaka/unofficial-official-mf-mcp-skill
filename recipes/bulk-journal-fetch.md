# 仕訳の一括取得（大量仕訳のページネーション）

## いつ使うか

- 全仕訳のバックアップが必要なとき（タグ一括更新前のバックアップ等）
- 仕訳ベースの集計・分析で全件が必要なとき
- 1期分の仕訳が500件を超える場合

## 制約

- `getJournals` のレスポンスは1件あたり数KB〜100KB（branch数に比例）
- Claude Codeのツール結果サイズ上限を超えるとファイルに自動保存される
- `per_page` の上限は500（APIの制限）

## 手順

### Step 1: 総件数を確認

```
getJournals(start_date="期首日", end_date="期末日", per_page=1, page=1)
```

レスポンスの `metadata.total_count` と `metadata.total_pages` を確認。
per_page=500での必要ページ数 = ceil(total_count / 500)。

### Step 2: 保存先ディレクトリを作成

```
data/{会社名}/tmp/
```

### Step 3: 全ページを取得

per_page=500で1ページずつ取得。レスポンスはClaude Codeが自動でファイルに保存する。
保存されたファイルを `data/{会社名}/tmp/page_XX.txt` にコピーする。

```
getJournals(start_date="期首日", end_date="期末日", per_page=500, page=N)
```

- 通年で一括取得可能（月ごとに分ける必要はない）
- 各ページの結果ファイル（tool-results/内）を `tmp/page_01.txt` 〜 `tmp/page_XX.txt` にコピー

### Step 4: マージスクリプトで結合

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

### Step 5: tmpを削除

```bash
rm -rf data/{会社名}/tmp/
```

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

- あるく株式会社（2025年度）: 7,115件、per_page=500で15回のAPI呼び出し、18MB
