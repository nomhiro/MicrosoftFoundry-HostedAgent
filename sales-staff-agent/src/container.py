"""
Hosted Agent コンテナエントリーポイント

aiohttp を使用して localhost:8088 で HTTP サーバーを起動し、
Azure Foundry API 経由でエージェントを呼び出す
"""

import os
import json
from functools import partial
from aiohttp import web
from dotenv import load_dotenv

# JSONレスポンス用（ensure_ascii=Falseで日本語やクォートをエスケープしない）
json_dumps = partial(json.dumps, ensure_ascii=False)

# 環境変数の読み込み
load_dotenv()


async def create_app():
    """アプリケーションを作成"""
    from azure.ai.projects import AIProjectClient
    from azure.ai.projects.models import MCPTool, PromptAgentDefinition, AgentReference
    from azure.identity import DefaultAzureCredential

    # 環境変数から設定を取得
    project_endpoint = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
    model_deployment = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:7071/runtime/webhooks/mcp")

    print("Initializing Sales Staff Agent...")
    print(f"Project Endpoint: {project_endpoint}")
    print(f"Model: {model_deployment}")
    print(f"MCP Server: {mcp_server_url}")

    # Azure認証
    credential = DefaultAzureCredential()

    # プロジェクトクライアント
    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=credential
    )

    # MCPツールの設定
    mcp_tool = MCPTool(
        server_label="dealer-backend",
        server_url=mcp_server_url,
        require_approval="never",
        allowed_tools=[
            "search_customer_by_name",
            "get_customer_info",
            "get_contracts",
            "get_visit_history",
            "search_vehicles",
            "get_upcoming_services"
        ]
    )

    # システムプロンプト
    instructions = """
あなたは自動車販売店のスタッフアシスタントです。
基幹システムと連携して、顧客情報、契約履歴、来店履歴、車両在庫を検索できます。

顧客名で問い合わせがあった場合は、まず search_customer_by_name で
顧客IDを特定してから、詳細情報を取得してください。

常に丁寧な日本語で回答してください。
"""

    # エージェントの作成/更新
    agent_name = "sales-staff-agent"
    agent = project_client.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_deployment,
            instructions=instructions,
            tools=[mcp_tool]
        )
    )
    print(f"Agent created: {agent.name} (version: {agent.version})")

    # OpenAIクライアントを取得
    openai_client = project_client.get_openai_client()

    # ルートハンドラー
    async def health_handler(request):
        """ヘルスチェック"""
        return web.json_response({"status": "healthy", "agent": agent.name}, dumps=json_dumps)

    async def responses_handler(request):
        """メッセージ処理エンドポイント"""
        try:
            body = await request.json()

            # 入力を取得
            input_data = body.get("input", "")

            # 文字列の場合はメッセージ形式に変換
            if isinstance(input_data, str):
                messages = [{"role": "user", "content": input_data}]
            elif isinstance(input_data, dict) and "messages" in input_data:
                messages = input_data["messages"]
            elif isinstance(input_data, list):
                messages = input_data
            else:
                messages = [{"role": "user", "content": str(input_data)}]

            # エージェントを呼び出し
            response = openai_client.responses.create(
                input=messages,
                extra_body={"agent": AgentReference(name=agent.name, version=str(agent.version)).as_dict()}
            )

            # レスポンスを返す
            return web.json_response({
                "id": response.id,
                "output": response.output_text,
                "status": "completed"
            }, dumps=json_dumps)

        except Exception as e:
            return web.json_response(
                {"error": str(e), "status": "failed"},
                status=500,
                dumps=json_dumps
            )

    # アプリケーション作成
    app = web.Application()
    app.router.add_get("/health", health_handler)
    app.router.add_post("/responses", responses_handler)

    return app


def main():
    """エントリーポイント"""
    print("Starting Sales Staff Agent HTTP Server...")
    print("Endpoints:")
    print("  GET  http://localhost:8088/health    - Health check")
    print("  POST http://localhost:8088/responses - Send messages")
    print("\nPress Ctrl+C to stop\n")

    try:
        import asyncio

        async def run():
            app = await create_app()
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, "0.0.0.0", 8088)
            await site.start()
            print("\n✓ Server is running on http://localhost:8088")
            # 無限に待機
            while True:
                await asyncio.sleep(3600)

        asyncio.run(run())

    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
