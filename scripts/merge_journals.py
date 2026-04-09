#!/usr/bin/env python3
"""
仕訳マージ: MCP getJournalsの結果ファイル（ページ分割）を結合

MCPのgetJournalsはレスポンスが大きいとファイルに保存される。
このスクリプトはそれらのファイルを読み込み、1つのjournals-backup.jsonに結合する。

入力: data_dir/tmp/page_*.txt（MCP tool-result形式 or 生JSON）
出力: data_dir/journals-backup.json

Usage:
    python3 merge_journals.py <data_dir>
"""

import json
import sys
import os
import glob
from datetime import datetime


def parse_tool_result(filepath):
    """MCP tool-resultファイルまたは生JSONからjournalsリストを抽出"""
    with open(filepath, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    # MCP tool-result形式: [{type: "text", text: "..."}]
    if isinstance(raw, list) and len(raw) > 0 and 'text' in raw[0]:
        parsed = json.loads(raw[0]['text'])
    # 生JSON形式: {journals: [...], metadata: {...}}
    elif isinstance(raw, dict):
        parsed = raw
    else:
        print(f"WARNING: 不明な形式: {filepath}")
        return [], {}

    journals = parsed.get('journals', [])
    metadata = parsed.get('metadata', {})
    return journals, metadata


def merge(data_dir):
    tmp_dir = os.path.join(data_dir, 'tmp')
    if not os.path.exists(tmp_dir):
        print(f"ERROR: {tmp_dir} が見つかりません")
        sys.exit(1)

    # page_*.txt を番号順にソート
    files = sorted(glob.glob(os.path.join(tmp_dir, 'page_*.txt')))
    if not files:
        print(f"ERROR: {tmp_dir}/page_*.txt が見つかりません")
        sys.exit(1)

    all_journals = []
    seen_ids = set()
    total_count = 0

    for f in files:
        journals, metadata = parse_tool_result(f)
        if metadata.get('total_count'):
            total_count = metadata['total_count']

        # 重複排除（ページ境界で重複する可能性）
        new = 0
        for j in journals:
            jid = j.get('id', '')
            if jid not in seen_ids:
                seen_ids.add(jid)
                all_journals.append(j)
                new += 1

        print(f"  {os.path.basename(f)}: {len(journals)}件取得, {new}件追加 (累計: {len(all_journals)}件)")

    # 日付順ソート
    all_journals.sort(key=lambda j: (j.get('transaction_date', ''), j.get('number', 0)))

    # 保存
    output = {
        'fetched_at': datetime.now().isoformat(),
        'total_count': total_count,
        'actual_count': len(all_journals),
        'journals': all_journals,
    }

    output_path = os.path.join(data_dir, 'journals-backup.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # サマリー
    months = {}
    for j in all_journals:
        m = j.get('transaction_date', '')[:7]
        months[m] = months.get(m, 0) + 1

    print(f"\n=== マージ完了 ===")
    print(f"ファイル数: {len(files)}")
    print(f"API報告件数: {total_count}")
    print(f"実取得件数: {len(all_journals)} (重複除去後)")
    print(f"\n月別:")
    for m in sorted(months.keys()):
        print(f"  {m}: {months[m]}件")
    print(f"\n保存先: {output_path}")
    return output


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 merge_journals.py <data_dir>")
        sys.exit(1)
    merge(sys.argv[1])
