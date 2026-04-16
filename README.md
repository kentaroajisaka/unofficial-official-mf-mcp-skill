# unofficial-official-mf-mcp-skill

マネーフォワードクラウド会計の**公式MCPサーバー**を使うための**非公式スキル**です。

Claude Code / Claude Desktop（チャット・Cowork）の両方で動作します。AIがMFクラウド会計のMCPの使い方・APIのクセ・制約事項を自動で理解して対応してくれます。

## v2.3.0 の変更点

- **`getTermSettings` ツールを追加** — 事業者の**経理方式（税込/税抜）・課税方式（簡易/本則/免税）・都道府県・業種区分・端数処理**を1回のAPI呼び出しで取得可能。**試算表APIを `include_tax` で2回叩いて比較する必要はなくなった**
- **`complete_authentication` ツールを追加** — beta版認証でlocalhostリダイレクトが失敗した時のフォールバック（URLを手動で貼り付けて認証完了）
- **`available` パラメータの実測仕様を追加** — `getAccounts` / `getSubAccounts` / `getDepartments` の `available` クエリは、**`false` 指定で「全件（有効+無効）」**を返す仕様（直感と逆）。`true` / 省略は有効な科目のみ。実測で確定
- **`deleteVouchers` の正体が判明** — 「証憑本体の削除」ではなく **「仕訳と証憑の関連付け解除」** のAPI。証憑自体は孤立した状態で残る
- **OpenAPIローカルコピーを2026-04最新版に差し替え** — 従来のローカルコピーは2025-01時点で古かった

## v2.2.0 の変更点

- **`per_page` 上限を500→10,000に修正** — 実測で `per_page=10000` がAPIに受け付けられることを確認。10,001以上はエラー。v2.1.0以前の「上限500」は誤りでした
- **大半の法人は1回のAPI呼び出しで全仕訳取得可能に** — ページネーション + merge_journals.py が不要になるケースがほとんど
- **データ整合性を検証済み** — per_page=500 と per_page=10000 で同一仕訳をJSON完全比較し、欠落・劣化がないことを確認

### v2.1.0

- **alpha版の認証フローを明確化** — `mfc_ca_authorize` → `mfc_ca_exchange` の2ステップを明記（exchangeを飛ばすと接続失敗する問題を修正）
- **比較表にヘッドレス対応を追加** — alpha版はTelegramボット等ブラウザのない環境でも認証可能であることを明記

### v2.0.0

- **alpha版/beta版の使い分けガイド追加** — メリデメ比較表、複数法人同時処理の使い分け
- **仕訳の一括取得機能** — per_page=10000で一括取得 + merge_journals.pyで結合（10,000件超の場合のみ）
- **Claude Code対応** — セットアップ手順を追加
- `.claude.json` の設定例（alpha/beta両方の同時登録）

## 含まれる内容

- alpha版/beta版の使い分けガイド（認証方式・トークン有効期限・複数法人対応の比較）
- 認証フロー（alpha版: 手動コードコピペ / beta版: PKCE自動コールバック）
- 全ツール一覧と使い方
- APIのクセ（PL累計、end_monthの罠、税込/税抜の違い、科目IDなし、開始仕訳、製造原価報告書の混在、部門別データ取得不可 等）
- 仕訳登録の事前準備（マスタ取得、IDのURLエンコード、補助科目なしの扱い）
- 仕訳更新（putJournals）の全置換仕様とバックアップの必要性
- 仕訳の一括取得レシピ（per_page=10000で大半の法人は1回で完了）+ マージスクリプト（`scripts/merge_journals.py`）
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
curl -L https://github.com/kentaroajisaka/unofficial-official-mf-mcp-skill/archive/refs/tags/v2.3.0.tar.gz | tar xz --strip-components=1
```

### alpha版 vs beta版

| | alpha版 | beta版 |
|---|---|---|
| 認証方式 | 手動（認証コードをコピペ） | 自動（PKCE+localhostコールバック） |
| トークン有効期限 | 約1時間（頻繁に再認証が必要） | 長時間 |
| 複数法人同時利用 | **可能**（法人ごとに認証して同時保持） | 不可（切替時に再認証） |
| ヘッドレス環境 | **対応**（コードをチャット等で渡せばOK） | 不可（localhostへのリダイレクトが必要） |

- **1社だけ作業する場合** → beta版が楽
- **複数法人を同時処理する場合** → alpha版
- **Telegramボット等ブラウザのない環境** → alpha版（認証コードをチャットで送るだけで認証可能）

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
