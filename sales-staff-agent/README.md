# sales-staff-agent

自動車販売店スタッフ支援 Hosted Agent

Microsoft Foundry の Hosted Agent として動作し、MCPサーバー（mcp-server-dealer）と連携して顧客対応を支援します。

## 概要

```
┌─────────────────────────────────────┐
│   販売スタッフ                       │
└──────────────┬──────────────────────┘
               │ 自然言語での問い合わせ
               ▼
┌─────────────────────────────────────┐
│   sales-staff-agent                 │
│   Hosted Agent                      │
│   - Hosting Adapter (Port 8088)     │
│   - Microsoft Agent Framework       │
└──────────────┬──────────────────────┘
               │ MCP Protocol
               ▼
┌─────────────────────────────────────┐
│   mcp-server-dealer                 │
│   (顧客/契約/来店/車両情報)          │
└─────────────────────────────────────┘
```

## 機能

スタッフからの自然言語での質問に対し、MCPサーバーのツールを呼び出して回答します。

| 対応する問い合わせ例 | 使用するMCPツール |
|---------------------|------------------|
| 「田中様の情報を教えて」 | `search_customer_by_name` → `get_customer_info` |
| 「鈴木様の契約履歴」 | `search_customer_by_name` → `get_contracts` |
| 「C001の来店履歴」 | `get_visit_history` |
| 「赤いSUVの在庫は？」 | `search_vehicles` |
| 「今月のサービス予定」 | `get_upcoming_services` |

## 必要な環境

- Python 3.11以上
- [uv](https://docs.astral.sh/uv/) - パッケージマネージャー
- mcp-server-dealer が起動していること（ローカルテスト時）

### インストール確認

```bash
python --version   # Python 3.11+
uv --version       # uv がインストールされていること
```

## セットアップ

```bash
cd sales-staff-agent

# 依存関係のインストール
uv sync

# 環境変数の設定
cp .env.example .env
```

### 環境変数の設定

`.env` ファイルを編集して、必要な値を設定します：

```env
# Azure AI Foundry プロジェクトエンドポイント
AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project

# モデルデプロイメント名
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o

# MCPサーバーURL（ローカル開発時）
MCP_SERVER_URL=http://localhost:7071/runtime/webhooks/mcp/sse
```

## ローカル起動

### 1. MCPサーバーを先に起動

別のターミナルで mcp-server-dealer を起動しておきます：

```bash
cd mcp-server-dealer
func start
```

### 2. エージェントを起動

```bash
cd sales-staff-agent
uv run python src/container.py
```

起動すると以下のようなメッセージが表示されます：

```
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8088 (Press CTRL+C to quit)
```

## 動作確認

### 1. ヘルスチェック（起動確認）

```powershell
Invoke-RestMethod -Uri "http://localhost:8088/health"
```

または

```bash
curl http://localhost:8088/health
```

### 2. エージェントへの問い合わせ

#### PowerShell

```powershell
$body = @{
    input = @{
        messages = @(
            @{
                role = "user"
                content = "田中様の契約履歴を教えて"
            }
        )
    }
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://localhost:8088/responses" -Method POST -ContentType "application/json" -Body $body |
  Select-Object -ExpandProperty output
```

#### bash/curl

```bash
curl -X POST http://localhost:8088/responses \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "messages": [
        {"role": "user", "content": "田中様の契約履歴を教えて"}
      ]
    }
  }'
```

### 3. 動作確認シナリオ（顧客ID特定 → 詳細取得）

顧客名だけでは一意に特定できない場合があるため、以下の2ステップで確認します。

1) 顧客候補とIDの取得

```powershell
$body = @{
  input = @{
    messages = @(
      @{ role = "user"; content = "田中 太郎の顧客情報を教えて" }
    )
  }
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://localhost:8088/responses" -Method POST -ContentType "application/json" -Body $body |
  Select-Object -ExpandProperty output
```

2) 取得したIDで契約履歴と顧客情報を取得

```powershell
$body = @{
  input = @{
    messages = @(
      @{ role = "user"; content = "C001の契約履歴を教えて" }
    )
  }
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://localhost:8088/responses" -Method POST -ContentType "application/json" -Body $body |
  Select-Object -ExpandProperty output
```

```powershell
$body = @{
  input = @{
    messages = @(
      @{ role = "user"; content = "C001の顧客情報を教えて" }
    )
  }
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://localhost:8088/responses" -Method POST -ContentType "application/json" -Body $body |
  Select-Object -ExpandProperty output
```

以下の問い合わせが正常に応答されることを確認してください：

| シナリオ | 問い合わせ例 | 期待される動作 |
|---------|-------------|---------------|
| 顧客検索 | 「田中で検索して候補とIDを教えて」 | 田中太郎などの候補と顧客IDを返す |
| 契約履歴 | 「C001の契約履歴」 | CX-5の新車購入契約を返す |
| 顧客情報 | 「C001の顧客情報」 | 顧客の詳細情報を返す |
| 来店履歴 | 「鈴木様の来店履歴」 | 鈴木花子の点検履歴を返す |
| 車両検索 | 「赤いSUVの在庫」 | ソウルレッドのCX-5を返す |
| サービス予定 | 「今後30日のサービス予定」 | 予定されている点検・車検を返す |

## Docker での起動

### イメージのビルド

```bash
cd sales-staff-agent
docker build -t sales-staff-agent:v1 .
```

### コンテナの起動

```bash
docker run -p 8088:8088 \
  -e AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project \
  -e AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o \
  -e MCP_SERVER_URL=http://host.docker.internal:7071/runtime/webhooks/mcp/sse \
  sales-staff-agent:v1
```

> **Note**: Docker 内から localhost の MCPサーバーにアクセスする場合は `host.docker.internal` を使用します。

### Azure Container Registry へのプッシュ

```bash
# ACRにログイン
az acr login --name <your-registry>

# タグ付け
docker tag sales-staff-agent:v1 <your-registry>.azurecr.io/sales-staff-agent:v1

# プッシュ
docker push <your-registry>.azurecr.io/sales-staff-agent:v1
```

## ディレクトリ構成

```
sales-staff-agent/
├── pyproject.toml       # Python依存関係
├── uv.lock              # 依存関係ロック
├── agent.yaml           # エージェント定義（Azure Developer CLI用）
├── Dockerfile           # コンテナ化設定
├── .env.example         # 環境変数テンプレート
└── src/
    ├── __init__.py      # パッケージ初期化
    ├── agent.py         # エージェント定義（MCPツール接続）
    └── container.py     # コンテナエントリーポイント
```

## Foundry へのデプロイ

### Azure Developer CLI を使用

```bash
# エージェントの初期化
azd ai agent init -m ./agent.yaml

# デプロイ
azd up
```

### Python SDK を使用

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ImageBasedHostedAgentDefinition, MCPTool

agent = client.agents.create_version(
    agent_name="sales-staff-agent",
    definition=ImageBasedHostedAgentDefinition(
        cpu="1",
        memory="2Gi",
        image="<your-registry>.azurecr.io/sales-staff-agent:v1",
        tools=[
            MCPTool(
                server_label="dealer-backend",
                project_connection_id="mcp-dealer-connection"
            )
        ]
    )
)
```

## トラブルシューティング

### エージェントが起動しない

1. 環境変数が正しく設定されているか確認:
   ```bash
   cat .env
   ```

2. 依存関係が正しくインストールされているか確認:
   ```bash
   uv sync
   ```

### MCPサーバーに接続できない

1. MCPサーバーが起動しているか確認:
   ```bash
   curl http://localhost:7071/api/health
   ```

2. `.env` の `MCP_SERVER_URL` が正しいか確認

### ポート 8088 が使用中

環境変数でポートを変更できます：

```bash
PORT=8089 uv run python src/container.py
```

### Azure 認証エラー

ローカル開発時は Azure CLI でログインしておく必要があります：

```bash
az login
```

## 関連ドキュメント

- [mcp-server-dealer README](../mcp-server-dealer/README.md) - MCPサーバーの詳細
- [Microsoft Foundry Hosted Agent ドキュメント](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/hosted-agents)
- [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/)
