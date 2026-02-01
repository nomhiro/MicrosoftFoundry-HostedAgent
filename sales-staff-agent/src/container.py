"""
Hosted Agent コンテナエントリーポイント - Agent Framework版

azure-ai-agentserver-core の FoundryCBAgent を継承して
localhost:8088 で Foundry Responses API 互換の HTTP サーバーを起動
"""

import os
from typing import AsyncGenerator, Union
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# Observabilityを有効化
from agent_framework.observability import enable_instrumentation

enable_instrumentation(
    enable_sensitive_data=os.getenv("ENABLE_SENSITIVE_DATA", "").lower() == "true"
)

from azure.ai.agentserver.core import FoundryCBAgent, AgentRunContext
from azure.ai.agentserver.core.models.projects import Response, ResponseStreamEvent
from azure.identity import DefaultAzureCredential

# srcディレクトリをパスに追加
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agent import create_agent, create_mcp_tool


class SalesStaffAgent(FoundryCBAgent):
    """販売店スタッフエージェント - Hosted Agent実装"""

    def __init__(self):
        super().__init__(credentials=DefaultAzureCredential())
        self.agent = None
        self.mcp_tool = None

    async def _ensure_initialized(self):
        """エージェントとMCPツールの遅延初期化"""
        if self.agent is None:
            self.agent = create_agent()
            self.mcp_tool = create_mcp_tool()

    async def agent_run(
        self, context: AgentRunContext
    ) -> Union[Response, AsyncGenerator[ResponseStreamEvent, None]]:
        """
        エージェント実行のメインロジック

        Args:
            context: リクエストコンテキスト（メッセージ等を含む）

        Returns:
            Response または ResponseStreamEvent のストリーム
        """
        await self._ensure_initialized()

        # 入力メッセージを取得
        messages = context.input_messages or []

        # 最後のユーザーメッセージを取得
        user_message = ""
        for msg in reversed(messages):
            if hasattr(msg, 'role') and msg.role == "user":
                if hasattr(msg, 'content'):
                    content = msg.content
                    if isinstance(content, str):
                        user_message = content
                    elif isinstance(content, list) and len(content) > 0:
                        # content が TextContent のリストの場合
                        first_content = content[0]
                        if hasattr(first_content, 'text'):
                            user_message = first_content.text
                        elif isinstance(first_content, dict) and 'text' in first_content:
                            user_message = first_content['text']
                break

        if not user_message:
            return Response(
                id=context.response_id or "error",
                output=[],
                output_text="メッセージが見つかりませんでした。",
                status="completed"
            )

        try:
            # MCPツールをコンテキストマネージャーとして使用
            async with self.mcp_tool as tool:
                result = await self.agent.run(user_message, tools=[tool])

                return Response(
                    id=context.response_id or "response",
                    output=[],
                    output_text=result.text,
                    status="completed"
                )
        except Exception as e:
            return Response(
                id=context.response_id or "error",
                output=[],
                output_text=f"エラーが発生しました: {str(e)}",
                status="failed"
            )


def main():
    """エントリーポイント"""
    print("Starting Sales Staff Agent (Agent Framework)...")
    print(f"Azure OpenAI Endpoint: {os.getenv('AZURE_OPENAI_ENDPOINT', 'Not set')}")
    print(f"Model: {os.getenv('AZURE_AI_MODEL_DEPLOYMENT_NAME', 'gpt-4o')}")
    print(f"MCP Server: {os.getenv('MCP_SERVER_URL', 'Not set')}")
    print("\nEndpoints:")
    print("  POST http://localhost:8088/responses - Send messages")
    print("  GET  http://localhost:8088/liveness  - Health check")
    print("\nPress Ctrl+C to stop\n")

    agent = SalesStaffAgent()
    agent.run(port=8088)


if __name__ == "__main__":
    main()
