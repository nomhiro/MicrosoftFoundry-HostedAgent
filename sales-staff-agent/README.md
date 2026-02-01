# sales-staff-agent

自動車販売店スタッフ支援 Hosted Agent (Agent Framework版)

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
│   Hosted Agent (Agent Framework)    │
│   - Hosting Adapter (Port 8088)     │
│   - Observability / VS Code可視化   │
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
- Azure CLI でログイン済み (`az login`)

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
# Azure OpenAI設定（Project Endpointではない）
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# モデルデプロイメント名
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o

# MCPサーバーURL（ローカル開発時）
MCP_SERVER_URL=http://localhost:7071/runtime/webhooks/mcp

# Observability設定（オプション）
FOUNDRY_OTLP_PORT=4319
ENABLE_SENSITIVE_DATA=false
```

## ローカル起動

### 1. MCPサーバーを先に起動

別のターミナルで mcp-server-dealer を起動しておきます：

```bash
cd mcp-server-dealer
func start
```

### 2. エージェントを起動

#### コンテナモード（HTTPサーバー）

```bash
cd sales-staff-agent
uv run python src/container.py
```

起動すると以下のようなメッセージが表示されます：

```
Starting Sales Staff Agent (Agent Framework)...
Azure OpenAI Endpoint: https://your-resource.openai.azure.com/
Model: gpt-4o
MCP Server: http://localhost:7071/runtime/webhooks/mcp

Endpoints:
  POST http://localhost:8088/responses - Send messages

Press Ctrl+C to stop
```

#### 対話モード（開発・テスト用）

ターミナルから直接エージェントと対話できます：

```bash
cd sales-staff-agent
uv run python src/interactive.py
```

```
==================================================
Sales Staff Agent - 対話モード
==================================================
MCP Server: http://localhost:7071/runtime/webhooks/mcp

終了するには 'quit' と入力してください

You: 田中様の契約履歴を教えて
Agent: ...
```

## VS Code 可視化

VS Code の Microsoft Foundry 拡張機能を使用してワークフローを可視化できます。

1. エージェントを起動（container.py または interactive.py）
2. VS Code: `Ctrl+Shift+P` → `Microsoft Foundry: Open Visualizer for Hosted Agents`
3. リクエストを送信すると、可視化タブにエージェントのワークフローが表示されます

## 動作確認

### HTTPリクエストでテスト

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

Invoke-RestMethod -Uri "http://localhost:8088/responses" -Method POST -ContentType "application/json" -Body $body
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

### 動作確認シナリオ

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
  -e AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/ \
  -e AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4o \
  -e MCP_SERVER_URL=http://host.docker.internal:7071/runtime/webhooks/mcp \
  sales-staff-agent:v1
```

> **Note**: Docker 内から localhost の MCPサーバーにアクセスする場合は `host.docker.internal` を使用します。

## Foundry へのデプロイ

### 方法1: VS Code拡張機能（推奨）

1. VS Code: `Ctrl+Shift+P` → `Microsoft Foundry: Deploy Hosted Agent`
2. ターゲットワークスペースを選択
3. コンテナエージェントファイルとして `container.py` を指定
4. デプロイ完了後、Foundry拡張機能ツリービューの「Hosted Agents (Preview)」セクションに表示

### 方法2: Docker + ACR + Python SDK

```bash
# ACRにログイン
az acr login --name <your-registry>

# タグ付け
docker tag sales-staff-agent:v1 <your-registry>.azurecr.io/sales-staff-agent:v1

# プッシュ
docker push <your-registry>.azurecr.io/sales-staff-agent:v1
```

Python SDKでデプロイ:

```python
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ImageBasedHostedAgentDefinition
from azure.identity import DefaultAzureCredential

client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=DefaultAzureCredential()
)

agent = client.agents.create_version(
    agent_name="sales-staff-agent",
    definition=ImageBasedHostedAgentDefinition(
        cpu="1",
        memory="2Gi",
        image="<your-registry>.azurecr.io/sales-staff-agent:v1",
        environment_variables={
            "AZURE_OPENAI_ENDPOINT": os.environ["AZURE_OPENAI_ENDPOINT"],
            "AZURE_AI_MODEL_DEPLOYMENT_NAME": "gpt-4o",
            "MCP_SERVER_URL": "<deployed-mcp-server-url>"
        }
    )
)
```

## ディレクトリ構成

```
sales-staff-agent/
├── pyproject.toml       # Python依存関係
├── uv.lock              # 依存関係ロック
├── agent.yaml           # エージェント定義（参照用）
├── Dockerfile           # コンテナ化設定
├── .env.example         # 環境変数テンプレート
└── src/
    ├── __init__.py      # パッケージ初期化
    ├── agent.py         # エージェント定義（Agent Framework）
    ├── container.py     # コンテナモード（HTTPサーバー）
    └── interactive.py   # 対話モード（開発用）
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

3. プレリリース版パッケージの場合:
   ```bash
   uv sync --prerelease=allow
   ```

### MCPサーバーに接続できない

1. MCPサーバーが起動しているか確認:
   ```bash
   curl http://localhost:7071/api/health
   ```

2. `.env` の `MCP_SERVER_URL` が正しいか確認

### Azure 認証エラー

ローカル開発時は Azure CLI でログインしておく必要があります：

```bash
az login
```

### インポートエラー

パッケージがプレリリース版の場合があります。以下を試してください：

```bash
pip install --pre agent-framework-core agent-framework-azure-ai azure-ai-agentserver-agentframework
```

## 関連ドキュメント

- [mcp-server-dealer README](../mcp-server-dealer/README.md) - MCPサーバーの詳細
- [Microsoft Foundry Hosted Agent ドキュメント](https://learn.microsoft.com/azure/ai-foundry/agents/concepts/hosted-agents)
- [Microsoft Agent Framework](https://learn.microsoft.com/agent-framework/)
- [VS Code Hosted Agent ワークフロー](https://learn.microsoft.com/azure/ai-foundry/agents/how-to/vs-code-agents-workflow-pro-code)
