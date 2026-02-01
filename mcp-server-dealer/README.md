# mcp-server-dealer

自動車販売店向け基幹システム MCPサーバー

Azure Functions 上で稼働し、Model Context Protocol (MCP) を通じて顧客情報・契約履歴・来店履歴・車両在庫などのデータを提供します。

## 概要

```
┌─────────────────────────────────────┐
│   AI Agent (MCP Client)             │
└──────────────┬──────────────────────┘
               │ HTTP (MCP Protocol)
               ▼
┌─────────────────────────────────────┐
│   mcp-server-dealer                 │
│   Azure Functions                   │
│   - /runtime/webhooks/mcp  (MCP endpoint) │
│   - /health                 (GET)         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   data/*.json                       │
│   (顧客/契約/来店/車両)              │
└─────────────────────────────────────┘
```

## 機能（MCPツール）

| ツール名 | 説明 | 必須パラメータ |
|---------|------|---------------|
| `search_customer_by_name` | 顧客名からID検索（部分一致） | `name` |
| `get_customer_info` | 顧客IDから詳細情報を取得 | `customer_id` |
| `get_contracts` | 顧客IDから契約履歴を取得 | `customer_id` |
| `get_visit_history` | 顧客IDから来店履歴を取得 | `customer_id` |
| `get_upcoming_services` | 今後のサービス予定一覧 | `days`（任意、デフォルト30） |
| `search_vehicles` | 車両在庫検索（色は部分一致対応） | `type`（必須）、`color`（任意） |

## 必要な環境

- Python 3.11以上
- [uv](https://docs.astral.sh/uv/) - パッケージマネージャー
- [Azure Functions Core Tools](https://learn.microsoft.com/azure/azure-functions/functions-run-local) v4

### インストール確認

```bash
python --version   # Python 3.11+
uv --version       # uv がインストールされていること
func --version     # Azure Functions Core Tools 4.x
```

## セットアップ

```bash
cd mcp-server-dealer

# 依存関係のインストール
uv sync
```

## ローカル起動

```bash
cd mcp-server-dealer
func start
```

起動すると以下のようなメッセージが表示されます：

```
Functions:

        health_check: [GET] http://localhost:7071/health
        mcp_tool_*:   [MCP] http://localhost:7071/runtime/webhooks/mcp
```

## 動作確認

> **注意**: MCPエンドポイントはSSE形式でレスポンスを返すため、Unicodeエスケープのデコードが必要です。

### PowerShell ヘルパー関数

以下の関数を定義してから各コマンドを実行してください：

```powershell
# MCPリクエスト用ヘルパー関数（日本語を正しく表示）
function Invoke-McpLocal {
    param([string]$Body)
    $headers = @{ Accept = "application/json, text/event-stream" }
    $response = Invoke-WebRequest -Uri "http://localhost:7071/runtime/webhooks/mcp" -Method POST -ContentType "application/json" -Headers $headers -Body $Body
    $json = ($response.Content -replace "^event:.*\r?\ndata:\s*", "")
    $json | ConvertFrom-Json | ConvertTo-Json -Depth 10
}
```

### 1. ヘルスチェック

```powershell
Invoke-RestMethod -Uri "http://localhost:7071/health"
```

レスポンス:
```json
{"status": "healthy", "service": "mcp-server-dealer"}
```

### 2. MCP ツール一覧の取得（JSON-RPC）

```powershell
Invoke-McpLocal -Body '{"jsonrpc":"2.0","id":"1","method":"tools/list"}'
```

### 3. ツール呼び出し例（JSON-RPC）

#### 顧客検索（名前から）

```powershell
Invoke-McpLocal -Body '{"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"search_customer_by_name","arguments":{"name":"田中"}}}'
```

レスポンス例:
```json
{
  "result": {
    "content": [{
      "type": "text",
      "text": "[{\"id\": \"C001\", \"name\": \"田中 太郎\", \"phone\": \"090-1234-5678\"}]"
    }]
  }
}
```

#### 顧客詳細取得

```powershell
Invoke-McpLocal -Body '{"jsonrpc":"2.0","id":"3","method":"tools/call","params":{"name":"get_customer_info","arguments":{"customer_id":"C001"}}}'
```

#### 契約履歴取得

```powershell
Invoke-McpLocal -Body '{"jsonrpc":"2.0","id":"4","method":"tools/call","params":{"name":"get_contracts","arguments":{"customer_id":"C001"}}}'
```

#### 来店履歴取得

```powershell
Invoke-McpLocal -Body '{"jsonrpc":"2.0","id":"5","method":"tools/call","params":{"name":"get_visit_history","arguments":{"customer_id":"C001"}}}'
```

#### サービス予定一覧

```powershell
Invoke-McpLocal -Body '{"jsonrpc":"2.0","id":"6","method":"tools/call","params":{"name":"get_upcoming_services","arguments":{"days":60}}}'
```

#### 車両在庫検索

```powershell
# SUVを検索
Invoke-McpLocal -Body '{"jsonrpc":"2.0","id":"7","method":"tools/call","params":{"name":"search_vehicles","arguments":{"type":"SUV"}}}'

# 赤色のSUVを検索（"赤" → "ソウルレッド" にもマッチ）
Invoke-McpLocal -Body '{"jsonrpc":"2.0","id":"8","method":"tools/call","params":{"name":"search_vehicles","arguments":{"type":"SUV","color":"赤"}}}'
```

## bash/Linux での動作確認

```bash
# ヘルスチェック
curl http://localhost:7071/health

# ツール一覧
curl -X POST http://localhost:7071/runtime/webhooks/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list"}'

# 顧客検索
curl -X POST http://localhost:7071/runtime/webhooks/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"search_customer_by_name","arguments":{"name":"田中"}}}'
```

## データ構造

`data/` ディレクトリ配下のJSONファイルでデータを管理：

| ファイル | 内容 |
|---------|------|
| `customers.json` | 顧客マスタ（ID, 氏名, 電話, メール, 住所, 登録日） |
| `contracts.json` | 契約履歴（顧客ID, 車両ID, 契約日, 種別, 金額, ステータス） |
| `visits.json` | 来店履歴（顧客ID, 来店日, 種別, 車両ID, 備考） |
| `vehicles.json` | 車両在庫（車種, 型式, 色, 年式, 価格, 在庫状況） |

### サンプルデータ

**顧客**
- C001: 田中 太郎
- C002: 鈴木 花子
- C003: 佐藤 一郎

**車種**
- SUV, セダン, 軽自動車, ミニバン

## Azure へのデプロイ

```bash
# Azure にデプロイ（Function Appが作成済みの場合）
func azure functionapp publish mcp-server-dealer --python
```

## Azureデプロイ後の動作確認

Azure上のMCPサーバーはSSE（Server-Sent Events）形式でレスポンスを返すため、確認方法がローカルと異なります。

### curl（推奨）

日本語が正しく表示されます：

```bash
# ツール一覧
curl -X POST "https://mcp-server-dealer.azurewebsites.net/runtime/webhooks/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":"1","method":"tools/list"}'

# 顧客検索
curl -X POST "https://mcp-server-dealer.azurewebsites.net/runtime/webhooks/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"search_customer_by_name","arguments":{"name":"田中"}}}'
```

### PowerShell

SSEレスポンスのUnicodeエスケープをデコードする必要があります：

```powershell
# ヘルパー関数
function Invoke-McpRequest {
    param([string]$Body)
    $headers = @{ Accept = "application/json, text/event-stream" }
    $response = Invoke-WebRequest -Uri "https://mcp-server-dealer.azurewebsites.net/runtime/webhooks/mcp" -Method POST -ContentType "application/json" -Headers $headers -Body $Body
    $json = ($response.Content -replace "^event:.*\r?\ndata:\s*", "")
    $json | ConvertFrom-Json | ConvertTo-Json -Depth 10
}

# ツール一覧
Invoke-McpRequest -Body '{"jsonrpc":"2.0","id":"1","method":"tools/list"}'

# 顧客検索
Invoke-McpRequest -Body '{"jsonrpc":"2.0","id":"2","method":"tools/call","params":{"name":"search_customer_by_name","arguments":{"name":"田中"}}}'
```

## ディレクトリ構成

```
mcp-server-dealer/
├── function_app.py      # Azure Functions エントリーポイント
├── mcp_handler.py       # MCPプロトコル処理
├── host.json            # Azure Functions設定
├── local.settings.json  # ローカル環境設定
├── pyproject.toml       # Python依存関係
├── uv.lock              # 依存関係ロック
├── data/                # データファイル
│   ├── customers.json
│   ├── contracts.json
│   ├── visits.json
│   └── vehicles.json
└── tools/               # MCPツール実装
    ├── __init__.py      # データ読み込みユーティリティ
    ├── customer.py      # 顧客検索・詳細取得
    ├── contract.py      # 契約履歴取得
    ├── visit.py         # 来店履歴・サービス予定
    └── vehicle.py       # 車両在庫検索
```

## トラブルシューティング

### `func start` でエラーが出る場合

1. `.venv` を有効化してから起動:
   ```bash
   # Windows
   .venv\Scripts\activate
   func start

   # macOS/Linux
   source .venv/bin/activate
   func start
   ```

2. または `local.settings.json` で仮想環境を指定

### ポートが使用中の場合

```bash
func start --port 7072
```

### Python のバージョンエラー

`pyproject.toml` で Python 3.11以上を要求しています。適切なバージョンをインストールしてください。
