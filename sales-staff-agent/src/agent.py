"""
販売店スタッフエージェント定義 - Agent Framework版

MCPツールと連携して顧客情報・契約履歴・来店履歴・車両在庫を検索
"""

import os
from agent_framework import ChatAgent, MCPStreamableHTTPTool
from agent_framework.azure import AzureOpenAIResponsesClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# 環境変数から設定を取得
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:7071/runtime/webhooks/mcp")

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

## 厳守ルール

- 顧客名の問い合わせは **必ず** `search_customer_by_name` で候補を取得してから対応する。
- `search_customer_by_name` の結果に含まれる `id` を **文字列のまま正確に使用**する（改変しない）。
- 候補が複数ある場合は **一覧を提示して選択を求め**、不確実な状態で `get_customer_info` / `get_contracts` / `get_visit_history` を呼び出さない。
- 候補が 0 件なら「該当なし」と回答し、憶測で情報を作らない。
- ユーザー入力に `C001` のようなIDが含まれている場合は、そのIDを使って該当ツールを呼ぶ。
- ツールから `error` が返っている場合は、その内容をそのまま伝え、再確認を依頼する。
- ツールを呼び出さずに推測で回答しない。必ずツール結果に基づいて回答する。

常に丁寧な日本語で回答してください。
"""


def create_agent() -> ChatAgent:
    """エージェントを作成"""
    credential = DefaultAzureCredential()

    # Azure OpenAI Responses Clientでエージェント作成
    agent = AzureOpenAIResponsesClient(
        endpoint=AZURE_OPENAI_ENDPOINT,
        deployment_name=MODEL_DEPLOYMENT_NAME,
        credential=credential,
    ).as_agent(
        name="SalesStaffAgent",
        instructions=SYSTEM_INSTRUCTIONS,
    )

    return agent


def create_mcp_tool() -> MCPStreamableHTTPTool:
    """MCPツールを作成"""
    return MCPStreamableHTTPTool(
        name="dealer-backend",
        url=MCP_SERVER_URL,
        # Azure Functions MCPサーバーはツールのみサポート
        load_prompts=False,
        load_resources=False,
    )
