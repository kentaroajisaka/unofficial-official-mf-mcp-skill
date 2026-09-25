---
name: unofficial-official-mf-mcp-skill
description: マネーフォワードクラウド会計のMCPを使う際のガイド。公式（alpha/beta）・OAuth版・APIキー版の4方式の使い分けと、認証フロー、仕訳取得・登録、試算表・推移表、科目マスタ、金額計算のクセを網羅。「MFの仕訳」「マネーフォワードの試算表」「MF認証」「MFで仕訳登録」等で発動。
---

# マネーフォワードクラウド会計 MCP ガイド

## まずどれを使うか（4方式）

| | **mf-api**（APIキー） | **mf-full**（OAuth） | 公式 beta | 公式 alpha |
|---|---|---|---|---|
| 実体 | 自作（[mf-api-mcp](https://github.com/kentaroajisaka/mf-api-mcp)） | 自作（[mf-full-mcp](https://github.com/kentaroajisaka/mf-full-mcp)） | MFのリモートMCP | 同左（旧・廃止予定） |
| 認証 | **APIキー1本。ブラウザ不要** | ブラウザで事業者を選んで許可 | ブラウザ | 認証コードをコピペ |
| 事業者の切替 | **呼び出しごとに `office_code`** | `use_office`（プロセス単位） | 再認証が要る | 複数同時保持 |
| 認証情報の寿命 | **期限なし**（JWTだけ1時間） | `refresh_token` が使うたび変わる | 長時間 | 約1時間 |
| **複数環境での併用** | **可** | **不可**（取り合いで `invalid_grant`） | — | — |
| **証憑添付・解除** | **○** | **○** | **×** | **×** |
| **仕訳削除** | **○** | **○** | **×** | **×** |
| 未仕訳明細 | ○ | ○ | × | × |
| **仕訳のメモ欄** | **何も入らない** | **アプリ名が勝手に入る** | アプリ名が入る | アプリ名が入る |

### 選び方

- **原則 `mf-api` を使う。** 証憑添付まで揃っていて、複数環境で同じキーを使え、メモ欄が汚れない
- `mf-full` は OAuth 版。**`mf-api` に移行中**。トークンの取り合いがあるので複数環境で同時に使わない
- **公式（alpha/beta）は予備。** 証憑添付・仕訳削除・未仕訳明細ができないので本番の証憑処理には使えない

### メモ欄にアプリ名が入る件（2026-09-25 実測）

OAuth には「アプリ」が存在する（アプリポータルで名前を付けて登録する）ので、MF がその名前を
記録でき、それが**仕訳のメモ欄に出ていた**（例: `memo: 'customer-dashboard'`）。

**APIキーには「アプリ」が無い。** JWT に入るのは `mfid_uid` と `tenant_user_uid` だけで、
書き込む名前が存在しない。実測でも memo を省略/空文字にすると `''` のままだった。
**メモ欄を自分の用途に使える。**

ただし**文字を入れると末尾に `\n` が付く**（MF が足す）。


## mf-api（APIキー版）の要点

```
APIキー（期限なし） → POST https://api.biz.moneyforward.com/auth/exchange
                    → JWT（ES256・1時間）
                    → https://api-accounting.moneyforward.com/api/v3/...
```

- キーは `MF_API_KEY` か `~/.mf-api-key`（600）
- **`office_code`（XXXX-XXXX）が全ツールで必須。** 無いと `400 missing_required_query_parameter`。
  OAuth では無視されるパラメータ。`MF_OFFICE_CODE` で既定化できる
- 事業者一覧は `list_offices`。**MF から引くので自前の台帳が要らない**
- 交換エンドポイントのレート制限は APIキーごと**毎分100回**。1時間に1回しか叩かないので当たらない。
  429 は `Retry-After` 付き

### キー発行の罠

アプリポータル → APIキー管理 → **「複数事業者」タブ** → 新規登録。

**利用可能事業者の一覧にページ送りがある。全選択はそのページ分しか効かない。**
実際に、全選択したつもりが1ページ分しか入っておらず、普段使っている事業者の大半が
漏れていた（気づいたのは API が「その事業者は使えない」と返したとき）。**全ページ選ぶこと。**

**キーを編集してもキーの値は変わらない。** 顧問先が増えたらチェックを足して保存するだけでよい。


## ⚠️ APIキーは配ってはいけない（2026-09-25 実測）

**APIキー＝発行者そのもの。** JWT に発行者の `mfid_uid` と、事業者ごとの `tenant_user_uid`
が入る。公式ドキュメントも「**発行したユーザーに付与されている権限で**APIを実行する」。

キーを渡した相手は、**自分では入れない顧問先にも発行者の権限で書き込める**。
画面の権限制御を通らない。

**しかも誰がやったか帳簿に残らない。** MF形式CSVで確認した実際の行:

```
MF仕訳タイプ : 外部連携（API）
作成者       : システムユーザー      ← 発行者の名前は出ない
最終更新者   : システムユーザー
```

API のレスポンスにも作成者のフィールドは無い。`entered_by` は
`JOURNAL_TYPE_EXTERNAL` / `JOURNAL_TYPE_IMPORT` 等の**経路**を表すもので、人ではない。

**正しい配り方: 各自が自分の MF アカウントで自分のキーを発行する。**
権限が自動で本人の範囲に絞られ、退職時はそのキーだけ消せる。
MCP の設定は全員同じで、`~/.mf-api-key` の中身だけが人ごとに違う形になる。

**職員向けのボットに持たせるときは要注意。** 職員がボットに頼めば発行者の権限で
実行されるので、実質キーを配ったのと同じになる。


## alpha版とbeta版の使い分け

MF公式MCPにはalpha版とbeta版の2つのエンドポイントがある。**両方同時に`.claude.json`に登録可能**。

| | alpha版 | beta版 |
|---|---|---|
| URL | `https://alpha.mcp.developers.biz.moneyforward.com/mcp/ca/v3` | `https://beta.mcp.developers.biz.moneyforward.com/mcp/ca/v3` |
| 認証方式 | 手動（認証コードをコピペ） | 自動（PKCE+localhostコールバック） |
| トークン有効期限 | **約1時間**（頻繁に再認証が必要） | 長時間（詳細不明） |
| 複数法人同時利用 | **✅ 可能**（法人ごとに認証して同時保持） | ❌ 1法人ずつ（切替時に再認証） |
| 手間 | 毎回コードコピペが面倒 | 認証はほぼワンクリック |
| ヘッドレス環境 | **✅ 対応**（コードをチャット等で渡せばOK） | ❌ 不可（localhostリダイレクトが必要） |

**使い分けの目安**:
- **1社だけ作業する場合** → beta版が楽（認証が簡単、長持ち）
- **複数法人を同時に処理する場合** → alpha版（複数法人の認証を同時保持できる）
- **Telegramボット等ブラウザのない環境** → alpha版（認証コードをチャットで送るだけで認証可能）

### `.claude.json` の設定例

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

### ツール名について

ツール名は `.claude.json` のサーバー名に依存する。上記設定例の場合:
- beta版: `mcp__mf-official-beta__authenticate`, `mcp__mf-official-beta__mfc_ca_getJournals` 等
- alpha版: `mcp__mf-official-alpha__authenticate`, `mcp__mf-official-alpha__mfc_ca_getJournals` 等

本ガイドでは便宜上 `mfc_ca_*` とツール名のサフィックス部分のみで記載する。

## 認証手順

### mf-api（APIキー版）— 認証操作は不要

キーを置いておくだけ。ブラウザも再認証も要らない。

1. `~/.mf-api-key`（600）か環境変数 `MF_API_KEY` にキーを置く
2. `auth_status` で確認（キーの所在・JWT取得可否・使える事業者数が返る。**キーの値は表示されない**）
3. `list_offices` で事業者一覧 → `office_code` を各ツールに渡す

JWTは1時間で切れるがサーバーが自動で取り直す。**利用者側でやることは無い。**

### beta版
1. `authenticate` ツールを呼び出す
2. 認証URLが生成されるので、ユーザーに「このURLをブラウザで開いて、事業者を選択 → 許可してください」と伝える
3. ブラウザでの認証完了後、ローカルコールバック（localhost）経由で自動的にトークンが取得される。**トークンの手動コピペは不要**
4. 認証完了後は `mfc_ca_*` ツールが自動的に使えるようになる。**access_tokenパラメータの手動指定も不要**（サーバー側で自動管理）
5. 認証切れ時は再度 `authenticate` を実行する

### alpha版
1. `mfc_ca_authorize` を呼び出す → 認証URLが生成される
2. ユーザーにブラウザで認証URLを開いてもらい、事業者を選択→許可
3. ブラウザに表示される**認証コードをコピー**してもらい、ユーザーがチャットに貼り付ける
4. **`mfc_ca_exchange` で認可コードをアクセストークンに交換する**（⚠️ この手順を飛ばすとAPI呼び出しが全て失敗する）
5. 交換成功後、`mfc_ca_currentOffice` 等のAPIが利用可能になる
6. **約1時間で期限切れ**。切れたら再度 手順1から実行する
7. 複数法人を扱う場合は、法人ごとに認証を行えば**同時に保持**できる

## ツール一覧

| カテゴリ | ツール | 用途 |
|---------|--------|------|
| 認証 | `authenticate` | OAuth認証（beta版はこれだけでOK） |
| 認証 | `complete_authentication` | beta版認証でlocalhostリダイレクトがエラーになった時のフォールバック（URLを貼り付けて認証完了） |
| 認証 | `mfc_ca_authorize` | 認証URL生成（alpha版ステップ1） |
| 認証 | `mfc_ca_exchange` | 認可コード→アクセストークン交換（alpha版ステップ2、**必須**） |
| 事業者 | `currentOffice` | 事業者情報・会計期間 |
| 事業者 | `getTermSettings` | **会計年度設定**（税込/税抜・簡易課税/本則・都道府県・端数処理） |
| 仕訳 | `getJournals` / `getJournalById` | 仕訳取得 |
| 仕訳 | `postJournals` / `putJournals` | 仕訳登録・更新 |
| 試算表 | `getReportsTrialBalanceBalanceSheet` / `ProfitLoss` | 試算表（累計） |
| 推移表 | `getReportsTransitionBalanceSheet` / `ProfitLoss` | 推移表（月別） |
| マスタ | `getAccounts` / `getSubAccounts` / `getDepartments` / `getTaxes` | 科目・部門・税区分 |
| 取引先 | `getTradePartners` / `postTradePartners` | 取引先取得・登録 |
| 口座 | `getConnectedAccounts` | 連携口座一覧 |
| 取引 | `postTransactions` | 取引登録 |
| 辞書 | `en_ja_dictionary` | 英日辞書 |

> `postVouchers`（証憑アップロード）、`deleteJournals`（仕訳削除）、`deleteVouchers`（証憑の添付解除）はMCPツールスキーマには定義されていないが、アクセストークンで直接APIを叩けば利用可能。詳細は末尾の「スキーマ未定義だがAPIで利用可能な操作」参照。

**getAccounts / getSubAccounts / getDepartments の `available` (boolean) クエリパラメータ（実測で挙動確定）:**

OpenAPI仕様書の description は「nil」で記載がないが、2026-04に無効化済み科目を持つ事業者で3パターン実測した結果、以下の仕様が確定した:

| 指定 | 挙動 |
|---|---|
| 省略 | 有効な科目のみ返却（各レコードは `available:true`） |
| `available=true` | 有効な科目のみ返却（省略時と同一） |
| `available=false` | **全科目（有効+無効）** を返却。無効化された科目は `available:false` で区別 |

**名前と挙動が直感に反する点に注意:**
- `false` = 「無効な科目だけ」ではなく「**全件（有効+無効）**」
- 無効化された科目だけを取得したい場合は `false` で取った後に `available == false` でフィルタする必要がある

実務的な用途:
- MFの設定画面で非表示にしている科目も含めてマスタを網羅的に取得したい場合に `available=false` を使う
- 決算整理等で稀にしか使わない科目（新株予約権・退職給与 等）が無効化されていると、突合時に欠落する可能性があるので注意

## PLの取得ルール

- ユーザーから「試算表を見たい」「PLを見たい」等の指示があった場合、**累計が知りたいのか単月が知りたいのか確認**すること
- **累計** → 試算表API（`getReportsTrialBalance*`）
- **単月** → 推移表API（`getReportsTransition*`）
- 試算表APIのPLは累計で返る。単月は推移表APIを優先
- 補助科目別の残高は `with_sub_accounts: true`。補助科目の付いていない行は「補助科目なし」として出るので、補助科目の付け忘れが見つかる。**会社全体（全部門合計）の残高は、仕訳から積み上げず推移表・試算表で取る**。部門別は下の「部門別データ」のとおり仕訳から集計するしかない
- 明細（銀行・カードの取り込み）の取得は `getTransactions`。`per_page` は10〜500、金額で絞るときは `side` が必須。詳しくは references/accounting-transactions.md

## パラメータの注意点

- **`getTransactions` は `start_date` と `end_date` が必須**（無いと 400）
- **試算表は `from`/`to` ではなく `fiscal_year`**（`from`/`to` だと 400）

- `end_month` は**カレンダー月**を指定する（会計期の第N月目ではない）

## 金額の扱い

- **試算表・推移表**: MFでの設定上の経理方式に従う（そのまま使ってOK）
- **仕訳取得時**: `value` は税抜き。税込 = `value` + `tax_value`
- **仕訳登録時**: `value` は**税込金額**を指定する。APIが自動で税抜と消費税に分解する

## 経理方式・課税方式の取得（`getTermSettings`）

事業者の経理方式（税込/税抜）、課税方式（簡易/本則）、都道府県、端数処理等を一発で取得できる。
**試算表APIを `include_tax` で2回叩いて比較する必要はない。**

レスポンス例:
```json
{
  "term_settings": [
    {
      "accounting_method": "TAX_INCLUDED",    // 税込経理
      "tax_method": "SIMPLE",                 // 簡易課税
      "business_types": ["OTHER"],            // 業種区分
      "prefecture": "鹿児島県",
      "purchases_rounding_method": "ROUND_DOWN",
      "sales_rounding_method": "ROUND_DOWN",
      "fiscal_year": 2025,
      "start_date": "2025-06-06",
      "end_date": "2026-05-31"
    }
  ]
}
```

### accounting_method の値
| 値 | 意味 |
|---|---|
| `TAX_INCLUDED` | 税込経理 |
| `TAX_EXCLUDED` | 税抜経理（内税） |
| `TAX_EXCLUDED_SEPARATE`（推定） | 税抜経理（別記） |

### tax_method の値
| 値 | 意味 |
|---|---|
| `SIMPLE` | 簡易課税 |
| `GENERAL`（推定） | 本則課税（一般課税） |
| `EXEMPT`（推定） | 免税 |

### business_types（簡易課税の業種区分）
簡易課税事業者の場合の業種区分。`OTHER` はその他。複数業種の会社は配列で複数持つ。

### 用途
- 仕訳データの金額補正（税込経理なら `value + tax_value` で帳簿金額）
- 引き継ぎ資料・決算書の「経理方式」「課税方式」欄の自動記載
- 簡易課税なら業種区分から売上高の補助科目設計（三種・四種 等）を確認

## 科目の突合

- 試算表・推移表には**科目IDがない**。科目名の文字列一致で突合する

## 開始仕訳の除外

- `entered_by` が `JOURNAL_TYPE_OPENING` の仕訳は期首残高。**集計から除外**すること

## 製造原価報告書

- PLに製造原価報告書の科目が混在する。**二重カウントしないこと**

## 仕訳登録の事前準備

仕訳を登録する前に**必ず以下のマスタを取得**しておくこと:

1. `getAccounts` → `account_id` を確認
2. `getSubAccounts` → `sub_account_id` を確認
3. `getTaxes` → `tax_id` を確認
4. `getDepartments` → `department_id` を確認

- IDは**URLエンコード済みのまま渡す**こと。デコードするとエラーになる
- 補助科目なしの仕訳は `sub_account_id` を省略すればよい

### 登録時の body の形（2026-09-25 実測。ここで400を3回踏んだ）

```json
{"journal": {
  "journal_type": "journal_entry",          // 必須。無いと 400
  "transaction_date": "2025-06-15",
  "memo": "…",                               // 任意。入れると末尾に \n が付く
  "tags": ["…"],
  "branches": [{
    "debitor":  {"account_id": "…", "tax_id": "…", "value": 1100},
    "creditor": {"account_id": "…", "tax_id": "…", "value": 1100},
    "remark": "摘要"
  }]
}}
```

- 科目は **`account_id`**。`account_item_id` ではない（400 `missing_required_request_body_key`）
- 明細は **`debitor` / `creditor` / `remark`**。`side` / `value` の形ではない
- 取得時のレスポンスも同じ `debitor` / `creditor` / `remark` の形

## 仕訳の登録・更新・削除

- **登録・更新前に必ずユーザーに確認を取ること**
- **仕訳削除はAPI経由で可能**（`DELETE /api/v3/journals/{id}` → 204）。ただしMCPツールスキーマには未定義のため、直接APIを叩く必要がある
- 削除前に必ずユーザーに確認を取ること

### putJournalsは全置換API（重要）

`putJournals` はタグだけ・メモだけの部分更新ができない。`branches`, `journal_type`, `transaction_date` が**必須**で、仕訳全体を送り直す必要がある。

- タグだけ追加したい場合でも、既存のbranches（account_id, value, tax_id, department_id, invoice_kind, sub_account_id, remark）を**全て正確に再現**して送る必要がある
- フィールドを省略すると仕訳データが壊れる（科目・金額・部門等が消える）
- **バックアップ推奨**: バッチ更新前にgetJournalsの結果をJSONファイルに保存しておくこと

## 証憑アップロード

- **証憑アップロードはAPI経由で可能**（`POST /api/v3/vouchers`）。MCPツールスキーマには未定義だが、scopeに `voucher.write` が含まれておりAPIは存在する
- **正しい手順: 仕訳を先に登録 → `journal_id` を指定して証憑アップ**
- `journal_id` なしでもアップ可能だが、孤立した証憑になり**後から仕訳に紐づけるAPIは存在しない**
- 証憑の**取得・一覧・（証憑本体の）削除のAPIは存在しない**（全て404）
- ただし「**仕訳と証憑の関連付け解除**」のAPI（`DELETE /api/v3/vouchers`）は存在する。これは証憑自体を削除するのではなく、仕訳との紐付けを外すだけ（証憑は孤立した状態で残る）

## 仕訳URLの生成

```
https://accounting.moneyforward.com/books?numbers={number}&recognized_at_from={期首日%2Fエスケープ}&recognized_at_to={期末日%2Fエスケープ}
```

## 部門別データ

- 試算表・推移表は**全部門合計**。部門別は仕訳APIから `department_name` で集計する
- 部門別の貸借対照表（残高）を作るときは、**期首仕訳（`entered_by: JOURNAL_TYPE_OPENING`、期首日付の1本）を必ず含めて**集計する。期首仕訳には部門ごとの期首残高が入っていて、部門どうしで打ち消し合う行（例：ある部門に借方、部門なしに同額の貸方）もある。損益は期首仕訳の影響を受けない
- 集計した部門別の数字は、部門を合計すると推移表（全部門合計）と一致するかで検算する

## 複数法人の同時利用

- beta版では認証時に選択した事業者に自動的に紐づく
- 事業者を切り替える場合は `authenticate` で再認証し、別の事業者を選択する（beta版の場合）
- alpha版は複数法人の認証を同時保持できるため、切り替え不要

## 制約（できないこと）

**どのMCPを使うかで変わる。** 2026-09-25 に検証用の事業者で実測し直した。

| | 公式（alpha/beta） | mf-full / mf-api |
|---|---|---|
| 未仕訳明細の取得 | × | **○**（`start_date`/`end_date` 必須） |
| 未仕訳明細の仕訳化 | × | ○ |
| 証憑の添付 | × | **○**（`POST /vouchers` → 201・`file_id` が返る） |
| 証憑の紐付け解除 | × | **○**（`DELETE /vouchers` → 204） |
| 仕訳削除 | × | **○**（`DELETE /journals/{id}` → 204） |

どれでもできないこと:

- 証憑の**取得・ダウンロード**はできない。突合にはローカルのスキャンデータを使う
- 証憑の**後付け紐づけ**はできない（アップ時に `journal_id` を指定する以外に方法がない）
- 勘定科目・補助科目・部門・税区分の登録・編集はできない
- 期首残高（開始仕訳）の登録はできない
- **手動管理の連携サービスは API で作れない**（`POST /connected_accounts` は 404）。
  `postTransactions` には手動管理の連携サービスが要るので、先に画面で作っておくこと


## 仕訳の一括取得

全仕訳のバックアップや一括集計が必要な場合は、`recipes/bulk-journal-fetch.md` の手順に従う。

- **per_page=10,000** で通年一括取得（APIの実上限。2026-04-10実測確認済み）
- 10,000件以下の法人（大半）は **1回のAPI呼び出しで全件取得完了**
- 10,000件超の場合のみ page=2 で追加取得し、`scripts/merge_journals.py` で結合

## REST APIを直接叩く場合

MCPツールではなくREST APIを直接叩く場合（バッチ処理等）の注意事項。

### ベースURL

```
https://api-accounting.moneyforward.com/api/v3
```

- **APIリファレンス（Redoc）**: https://developers.api-accounting.moneyforward.com/
- **OpenAPI仕様（ローカルコピー）**: `~/claude/customer-dashboard/openapi.yaml`

### IDの%2F問題（重要）

journal ID・account ID等のリソースIDはBase64エンコードされており、`%2F`（= `/`）を含むことがある。
このIDをURLパスにそのまま渡すと、サーバー側で `%2F` がスラッシュとしてデコードされ、パスが壊れて **403 forbidden** になる。

**対策**: IDをURLパスに埋め込む前に `quote(id, safe='')` で**全体を再エンコード**すること。

```python
from urllib.parse import quote

journal_id = quote(raw_id, safe='')  # %2F → %252F, %3D → %253D 等
url = f"{BASE_URL}/journals/{journal_id}"
```

- `%2F` だけ二重エンコードする方法は **400エラー** になる（部分的な対処は不可）
- MCPツール経由の場合はMCPサーバーが自動処理するので問題ない
- REST API直叩きの場合のみ発生する

## スキーマ未定義だがAPIで利用可能な操作

以下はMCPツールスキーマに定義されていないが、アクセストークンで直接APIを叩けば利用可能:

| 操作 | エンドポイント | メソッド | 備考 |
|------|--------------|---------|------|
| 仕訳削除 | `/api/v3/journals/{id}` | DELETE | 204で成功。完全削除 |
| 証憑アップロード | `/api/v3/vouchers` | POST | journal_id指定で仕訳紐づけ |
