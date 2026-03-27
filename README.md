# unofficial-official-mf-mcp-skill

マネーフォワードクラウド会計の**公式MCPサーバー**を使うための**非公式スキル**です。

Claude Desktop（チャット・Cowork）にインストールすると、AIがMFクラウド会計のMCPの使い方・APIのクセ・制約事項を自動で理解して対応してくれます。

## 含まれる内容

- 認証フロー（authorize → exchange → access_token管理）
- 全ツール一覧と使い方
- APIのクセ（PL累計、end_monthの罠、税込/税抜の違い、科目IDなし、開始仕訳、製造原価報告書の混在、部門別データ取得不可 等）
- 仕訳登録の事前準備（マスタ取得、IDのURLエンコード、補助科目なしの扱い）
- 仕訳URLの生成方法
- 複数法人の同時利用
- できること・できないこと一覧

## インストール方法

1. [Releases](../../releases) からzipファイルをダウンロード
2. Claude Desktopを開く
3. 左サイドバーの「カスタマイズ」→「スキル」
4. 「プラグインを参照」をクリック
5. ダウンロードしたzipを選択してインストール

## 注意事項

- これは**非公式**のスキルです。マネーフォワード社が提供・サポートするものではありません
- MFクラウド会計の公式MCPサーバー（リモートMCPコネクタ）は別途設定が必要です
- 公式MCPサーバーのURL: `https://alpha.mcp.developers.biz.moneyforward.com/mcp/ca/v3`

## 作成者

鯵坂健太郎（あじさか けんたろう）

- 税理士 / 鯵坂税理士事務所 代表
- https://office-wing.net/
- X: [@sabaaji0113](https://x.com/sabaaji0113)

## ライセンス

MIT License
