# Quickstart: 販売店スタッフエージェント

**Date**: 2026-01-31
**Prerequisites**: Python 3.11+, uv, Docker, Azure CLI

## 前提条件

### 必要なツール

```bash
# Python 3.11+ 確認
python --version

# uv インストール
pip install uv

# Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Docker
docker --version
```

### Azure リソース（デプロイ時のみ）

- Microsoft Foundry プロジェクト
- Azure Container Registry
- Azure Functions App (Flex Consumption)

## ローカル開発

### Step 1: MCPサーバーのセットアップ

```bash
cd mcp-server-dealer

# 依存関係インストール
uv sync

# ローカル起動
func start
```

MCPサーバーは `http://localhost:7071` で起動します。

### Step 2: Hosted Agentのセットアップ

```bash
cd sales-staff-agent

# 依存関係インストール
uv sync

# 環境変数設定
cp .env.example .env
# .env を編集して必要な値を設定
```

**.env の設定内容**:
```
AZURE_AI_PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o
MCP_SERVER_URL=http://localhost:7071/api/mcp
```

```bash
# ローカル起動
uv run python src/container.py
```

Agentは `http://localhost:8088` で起動します。

### Step 3: ローカルテスト

REST Client または curl でテスト:

```http
POST http://localhost:8088/responses
Content-Type: application/json

{
    "input": {
        "messages": [
            {"role": "user", "content": "田中様の契約履歴を教えて"}
        ]
    }
}
```

期待されるレスポンス:
- `search_customer_by_name("田中")` が呼ばれる
- `get_contracts("C001")` が呼ばれる
- 田中太郎様の契約履歴が日本語で回答される

## コンテナビルドとACRプッシュ

```bash
cd sales-staff-agent

# Docker イメージビルド
docker build -t sales-staff-agent:v1 .

# ACR ログイン
az acr login --name <your-registry>

# タグ付けとプッシュ
docker tag sales-staff-agent:v1 <your-registry>.azurecr.io/sales-staff-agent:v1
docker push <your-registry>.azurecr.io/sales-staff-agent:v1
```

## Azure Functionsへのデプロイ

```bash
cd mcp-server-dealer

# デプロイ
func azure functionapp publish <your-function-app> --python
```

## Foundry Hosted Agent作成

### Azure Developer CLI（推奨）

```bash
cd sales-staff-agent

# エージェント初期化
azd ai agent init -m ./agent.yaml

# デプロイ
azd up
```

### Python SDK

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ImageBasedHostedAgentDefinition, MCPTool

client = AIProjectClient.from_connection_string(
    conn_str="your-connection-string"
)

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

### MCPサーバーが起動しない

```bash
# ログ確認
func start --verbose

# ポート確認
netstat -an | grep 7071
```

### Agentが起動しない

```bash
# 環境変数確認
cat .env

# Python パス確認
uv run python -c "import azure.ai.agentserver; print('OK')"
```

### MCP接続エラー

```bash
# MCPサーバーのヘルスチェック
curl http://localhost:7071/api/mcp/health
```

## 次のステップ

1. `/speckit.tasks` でタスクリストを生成
2. タスクに従って実装を進める
3. ローカルテストを実行
4. Azure にデプロイ
