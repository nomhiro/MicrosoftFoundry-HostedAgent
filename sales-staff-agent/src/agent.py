"""
販売店スタッフエージェント定義

MCPツールと連携して顧客情報・契約履歴・来店履歴・車両在庫を検索
"""

import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import MCPTool
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 環境変数から設定を取得
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:7071/api/mcp")

# システムプロンプト
SYSTEM_INSTRUCTIONS = """
あなたは自動車販売店のスタッフアシスタントです。
基幹システム（MCPサーバー）と連携して、以下の情報を検索・提供できます：

1. **顧客情報**: 顧客名から検索、詳細情報の取得
2. **契約履歴**: 顧客の過去の契約情報
3. **来店履歴**: 点検・車検・修理などの来店記録
4. **車両在庫**: 条件に合う車両の在庫検索
5. **サービス予定**: 今後のサービス予定一覧

## 使用するツール

- `search_customer_by_name`: 顧客名で検索（部分一致）
- `get_customer_info`: 顧客IDから詳細情報を取得
- `get_contracts`: 顧客の契約履歴を取得
- `get_visit_history`: 顧客の来店履歴を取得
- `search_vehicles`: 車種・色で車両在庫を検索（色は部分一致対応）
- `get_upcoming_services`: 今後のサービス予定を取得

## 対応パターン

顧客名で問い合わせがあった場合は、まず `search_customer_by_name` で顧客IDを特定してから、
`get_customer_info` / `get_contracts` / `get_visit_history` で詳細情報を取得してください。

常に丁寧な日本語で回答してください。
"""


def create_mcp_tool() -> MCPTool:
    """MCPツールの設定を作成"""
    return MCPTool(
        server_label="dealer-backend",
        server_url=MCP_SERVER_URL,
        allowed_tools=[
            "search_customer_by_name",
            "get_customer_info",
            "get_contracts",
            "get_visit_history",
            "search_vehicles",
            "get_upcoming_services"
        ]
    )


def create_agent_client() -> AIProjectClient:
    """AIProjectClient を作成"""
    credential = DefaultAzureCredential()
    return AIProjectClient(
        endpoint=PROJECT_ENDPOINT,
        credential=credential
    )


async def create_agent():
    """エージェントを作成"""
    client = create_agent_client()
    mcp_tool = create_mcp_tool()

    # エージェントの作成
    agent = await client.agents.create_agent(
        model=MODEL_DEPLOYMENT_NAME,
        name="SalesStaffAgent",
        instructions=SYSTEM_INSTRUCTIONS,
        tools=[mcp_tool]
    )

    return agent
