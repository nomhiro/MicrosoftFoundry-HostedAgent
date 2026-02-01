"""
対話モード - 開発・テスト用

ターミナルから直接エージェントと対話するためのスクリプト
"""

import asyncio
import os
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# デバッグ用に詳細ログを有効化
from agent_framework.observability import setup_observability

setup_observability(enable_sensitive_data=True)

from agent import create_agent, create_mcp_tool


async def main():
    """対話モードのメインループ"""
    print("=" * 50)
    print("Sales Staff Agent - 対話モード")
    print("=" * 50)
    print(f"Azure OpenAI Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT', 'Not set')}")
    print(f"Model: {os.getenv('AZURE_AI_MODEL_DEPLOYMENT_NAME', 'gpt-4o')}")
    print(f"MCP Server: {os.getenv('MCP_SERVER_URL', 'Not set')}")
    print("\n終了するには 'quit' と入力してください\n")

    # エージェントを作成
    agent = create_agent()

    # MCPツールを作成してコンテキストマネージャーで管理
    async with create_mcp_tool() as mcp_tool:
        while True:
            try:
                user_input = input("You: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n終了します。")
                break

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("終了します。")
                break
            if not user_input:
                continue

            try:
                print("Agent: ", end="", flush=True)
                result = await agent.run(user_input, tools=[mcp_tool])
                print(result.text)
                print()
            except Exception as e:
                print(f"\nエラーが発生しました: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
