# unofficial-official-mf-mcp-skill

マネーフォワードクラウド会計の**公式MCPサーバー**を使うための**非公式スキル**です。

Claude Code / Claude Desktop（チャット・Cowork）の両方で動作します。AIがMFクラウド会計のMCPの使い方・APIのクセ・制約事項を自動で理解して対応してくれます。

## v2.0.0 の変更点

- **alpha版/beta版の使い分けガイド追加** — メリデメ比較表、複数法人同時処理の使い分け
- **仕訳の一括取得機能** — per_page=500のページネーション + merge_journals.pyで結合（Claude Code / Cowork両対応）
- **Claude Code対応** — セットアップ手順を追加
- `.claude.json` の設定例（alpha/beta両方の同時登録）

## 含まれる内容

- alpha版/beta版の使い分けガイド（認証方式・トークン有効期限・複数法人対応の比較）
- 認証フロー（alpha版: 手動コードコピペ / beta版: PKCE自動コールバック）
- 全ツール一覧と使い方
- APIのクセ（PL累計、end_monthの罠、税込/税抜の違い、科目IDなし、開始仕訳、製造原価報告書の混在、部門別データ取得不可 等）
- 仕訳登録の事前準備（マスタ取得、IDのURLエンコード、補助科目なしの扱い）
- 仕訳更新（putJournals）の全置換仕様とバックアップの必要性
- 仕訳の一括取得レシピ + マージスクリプト（`scripts/merge_journals.py`）
- REST API直叩き時のベースURL・IDの%2Fエンコード問題と対策
- 仕訳URLの生成方法
- 複数法人の同時利用
- できること・できないこと一覧

## セットアップ

### 前提: MF公式MCPサーバーの登録

スキルとは別に、MF公式MCPサーバー（リモートMCPコネクタ）の登録が必要です。

#### Claude Desktop の場合

1. 左サイドバーの「コネクタ」→「+」
2. 「カスタム」を選択
3. 以下のURLを入力:
   - **beta版（推奨）**: `https://beta.mcp.developers.biz.moneyforward.com/mcp/ca/v3`
   - **alpha版**: `https://alpha.mcp.developers.biz.moneyforward.com/mcp/ca/v3`
4. 両方登録すると同時利用可能

#### Claude Code の場合

`~/.claude.json` に以下を追加:

```json
{
  "mcpServers": {
    "mf-official-beta": {
      "type": "http",
      "url": "https://beta.mcp.developers.biz.moneyforward.com/mcp/ca/v3"
    },
    "mf-official-alpha": {
      "type": "http",
      "url": "https://alpha.mcp.developers.biz.moneyforward.com/mcp/ca/v3"
    }
  }
}
```

どちらか片方だけでもOK。

### スキルのインストール

#### Claude Desktop の場合

1. [Releases](../../releases) からzipファイルをダウンロード
2. Claude Desktopを開く
3. 左サイドバーの「カスタマイズ」→「スキル」→「+」
4. ダウンロードしたzipを選択してインストール

#### Claude Code の場合

```bash
# スキルフォルダに配置
mkdir -p ~/.claude/skills/unofficial-official-mf-mcp-skill
cd ~/.claude/skills/unofficial-official-mf-mcp-skill

# GitHubからファイルを取得（zipダウンロード → 展開でもOK）
curl -L https://github.com/kentaroajisaka/unofficial-official-mf-mcp-skill/archive/refs/tags/v2.0.0.tar.gz | tar xz --strip-components=1
```

### alpha版 vs beta版

| | alpha版 | beta版 |
|---|---|---|
| 認証方式 | 手動（認証コードをコピペ） | 自動（PKCE+localhostコールバック） |
| トークン有効期限 | 約1時間（頻繁に再認証が必要） | 長時間 |
| 複数法人同時利用 | **可能**（法人ごとに認証して同時保持） | 不可（切替時に再認証） |

- **1社だけ作業する場合** → beta版が楽
- **複数法人を同時処理する場合** → alpha版

## 注意事項

- これは**非公式**のスキルです。マネーフォワード社が提供・サポートするものではありません
- MFクラウド会計の公式MCPサーバー（リモートMCPコネクタ）は別途設定が必要です（上記「セットアップ」参照）

## 作成者

鯵坂健太郎（あじさか けんたろう）

- 税理士 / 鯵坂税理士事務所 代表
- https://office-wing.net/
- X: [@sabaaji0113](https://x.com/sabaaji0113)

## ライセンス

MIT License
