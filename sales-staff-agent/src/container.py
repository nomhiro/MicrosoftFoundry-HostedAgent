"""
Hosted Agent コンテナエントリーポイント

aiohttp を使用して localhost:8088 で HTTP サーバーを起動し、
Azure Foundry API 経由でエージェントを呼び出す
"""

import os
import json
import logging
from functools import partial
from aiohttp import web
from dotenv import load_dotenv

# ロギング設定
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

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
    mcp_server_url = os.getenv("MCP_SERVER_URL", "http://localhost:7071/runtime/webhooks/mcp/sse")

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

## 厳守ルール

- 顧客名の問い合わせは **必ず** search_customer_by_name で候補を取得してから対応する。
- search_customer_by_name の結果に含まれる id を **文字列のまま正確に使用**する（改変しない）。
- 候補が複数ある場合は **一覧を提示して選択を求め**、不確実な状態で get_customer_info / get_contracts / get_visit_history を呼び出さない。
- 候補が 0 件なら「該当なし」と回答し、憶測で情報を作らない。
- ユーザー入力に C001 のようなIDが含まれている場合は、そのIDを使って該当ツールを呼ぶ。
- ツールから error が返っている場合は、その内容をそのまま伝え、再確認を依頼する。
- ツールを呼び出さずに推測で回答しない。必ずツール結果に基づいて回答する。

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

    def _log_args(args_data):
        """引数をログ出力用にフォーマット"""
        if isinstance(args_data, str):
            try:
                return json.dumps(json.loads(args_data), ensure_ascii=False)
            except Exception:
                return args_data
        return json.dumps(args_data, ensure_ascii=False) if args_data else "{}"

    def _safe_dump(item) -> str:
        """オブジェクトを安全に文字列化してログ出力"""
        try:
            if hasattr(item, "as_dict"):
                return json.dumps(item.as_dict(), ensure_ascii=False, default=str)
            if hasattr(item, "to_dict"):
                return json.dumps(item.to_dict(), ensure_ascii=False, default=str)
            if isinstance(item, (dict, list, tuple)):
                return json.dumps(item, ensure_ascii=False, default=str)
            return json.dumps(getattr(item, "__dict__", str(item)), ensure_ascii=False, default=str)
        except Exception:
            return "(log failed)"

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

            # リクエストログ
            logger.info("=" * 50)
            logger.info("リクエスト受信")
            for msg in messages:
                logger.info(f"  [{msg.get('role', 'unknown')}] {msg.get('content', '')}")

            # エージェントを呼び出し（ストリーミングモード）
            logger.info("-" * 50)
            logger.info("LLM呼び出し開始")

            stream_response = openai_client.responses.create(
                stream=True,
                input=messages,
                extra_body={"agent": AgentReference(name=agent.name, version=str(agent.version)).as_dict()}
            )

            # ストリーミングイベントを処理
            response_id = None
            output_text = ""

            for event in stream_response:
                event_type = event.type

                if event_type == "response.created":
                    response_id = event.response.id
                    logger.info(f"  レスポンスID: {response_id}")

                elif event_type == "response.output_item.done":
                    item = event.item
                    item_type = getattr(item, 'type', None)

                    # MCPツール呼び出しのログ
                    if item_type == "mcp_tool_call":
                        tool_name = getattr(item, 'name', 'unknown')
                        tool_args = getattr(item, 'arguments', None)
                        logger.info("-" * 50)
                        logger.info(f"ツール呼び出し: {tool_name}")
                        logger.info(f"  引数: {_log_args(tool_args)}")

                    # MCPツール呼び出し結果のログ
                    elif item_type == "mcp_tool_call_output":
                        output = getattr(item, 'output', None)
                        logger.info(f"  結果: {_log_args(output)}")

                    # 新しいMCPイベント（SDK差異）
                    elif item_type == "mcp_list_tools":
                        logger.info("-" * 50)
                        logger.info("ツール一覧取得: mcp_list_tools")
                        logger.info(f"  内容: {_safe_dump(item)}")
                    elif item_type == "mcp_call":
                        logger.info("-" * 50)
                        logger.info("ツール呼び出し: mcp_call")
                        logger.info(f"  内容: {_safe_dump(item)}")
                    elif item_type == "mcp_call_output":
                        logger.info("-" * 50)
                        logger.info("ツール呼び出し結果: mcp_call_output")
                        logger.info(f"  内容: {_safe_dump(item)}")

                    # メッセージ（LLM応答）のログ
                    elif item_type == "message":
                        content_list = getattr(item, 'content', [])
                        for content in content_list:
                            if getattr(content, 'type', None) == "output_text":
                                output_text = getattr(content, 'text', '')
                    else:
                        logger.info(f"出力アイテム: type={item_type}")
                        logger.info(f"  内容: {_safe_dump(getattr(item, 'content', None) or item)}")

                elif event_type == "response.completed":
                    final_response = event.response
                    response_id = final_response.id
                    output_text = getattr(final_response, 'output_text', output_text)
                    logger.info("-" * 50)
                    logger.info("レスポンス完了")
                    logger.info(f"  出力: {output_text[:200]}..." if len(output_text) > 200 else f"  出力: {output_text}")
                    logger.info("=" * 50)

            # レスポンスを返す
            return web.json_response({
                "id": response_id,
                "output": output_text,
                "status": "completed"
            }, dumps=json_dumps)

        except Exception as e:
            logger.error(f"エラー発生: {e}")
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
