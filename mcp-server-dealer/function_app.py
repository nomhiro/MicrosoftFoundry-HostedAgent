"""
Azure Functions エントリーポイント

MCPサーバーを Azure Functions HTTP トリガーとして公開
"""

import azure.functions as func
from mcp_handler import mcp_app

# Azure Functions アプリケーション
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="runtime/webhooks/mcp/{*path}", methods=["GET", "POST"])
async def mcp_webhook_endpoint(req: func.HttpRequest) -> func.HttpResponse:
    """MCPエンドポイント（Azure Functions MCP Webhook互換）

    /runtime/webhooks/mcp/* へのリクエストをMCPハンドラーに転送
    """
    return await mcp_app.handle_request(req)


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """ヘルスチェックエンドポイント"""
    return func.HttpResponse(
        '{"status": "healthy", "service": "mcp-server-dealer"}',
        status_code=200,
        mimetype="application/json"
    )
