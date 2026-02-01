"""
Hosted Agent コンテナエントリーポイント - Agent Framework版

azure-ai-agentserver-agentframework を使用して localhost:8088 で HTTP サーバーを起動し、
Microsoft Foundry Hosted Agent としてデプロイ可能
"""

import os
from dotenv import load_dotenv

# 環境変数の読み込み（observability設定前に必要）
load_dotenv()

# VS Code可視化を有効化
from agent_framework.observability import setup_observability

setup_observability(
    vs_code_extension_port=int(os.getenv("FOUNDRY_OTLP_PORT", "4319")),
    enable_sensitive_data=os.getenv("ENABLE_SENSITIVE_DATA", "").lower() == "true"
)

# エージェントとMCPツールをインポート
from agent import create_agent, create_mcp_tool

# Hosting Adapter
from azure.ai.agentserver.agentframework import from_agent_framework


def main():
    """エントリーポイント"""
    print("Starting Sales Staff Agent (Agent Framework)...")
    print(f"Azure OpenAI Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT', 'Not set')}")
    print(f"Model: {os.getenv('AZURE_AI_MODEL_DEPLOYMENT_NAME', 'gpt-4o')}")
    print(f"MCP Server: {os.getenv('MCP_SERVER_URL', 'Not set')}")
    print("\nEndpoints:")
    print("  POST http://localhost:8088/responses - Send messages")
    print("\nPress Ctrl+C to stop\n")

    # エージェントとMCPツールを作成
    agent = create_agent()
    mcp_tool = create_mcp_tool()

    # 標準アダプターでホスティング（localhost:8088）
    # これによりFoundry Responses API互換のHTTPサーバーが起動
    from_agent_framework(agent, tools=[mcp_tool]).run()


if __name__ == "__main__":
    main()
