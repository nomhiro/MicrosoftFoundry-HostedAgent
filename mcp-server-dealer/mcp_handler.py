"""
MCP プロトコルハンドラー

Model Context Protocol (MCP) サーバーの実装
各ツールを登録してMCPリクエストを処理
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
import azure.functions as func
import json

# MCPサーバーインスタンス
server = Server("mcp-server-dealer")

# 登録されたツール関数を保持
_tool_handlers = {}


def register_tool(name: str, description: str, parameters: dict):
    """ツールを登録するデコレータ"""
    def decorator(func):
        _tool_handlers[name] = {
            "handler": func,
            "description": description,
            "parameters": parameters
        }
        return func
    return decorator


class MCPApp:
    """Azure Functions用MCPアプリケーション"""

    def __init__(self):
        self.tools = {}

    def register(self, name: str, description: str, parameters: dict):
        """ツールを登録"""
        def decorator(func):
            self.tools[name] = {
                "handler": func,
                "description": description,
                "parameters": parameters
            }
            return func
        return decorator

    async def handle_request(self, req: func.HttpRequest) -> func.HttpResponse:
        """MCPリクエストを処理"""
        path = req.route_params.get("path", "")

        # ツール一覧を返す
        if path == "tools/list" or req.method == "GET":
            tools_list = [
                {
                    "name": name,
                    "description": info["description"],
                    "inputSchema": info["parameters"]
                }
                for name, info in self.tools.items()
            ]
            return func.HttpResponse(
                json.dumps({"tools": tools_list}, ensure_ascii=False),
                status_code=200,
                mimetype="application/json"
            )

        # ツール呼び出し
        if path == "tools/call" and req.method == "POST":
            try:
                body = req.get_json()
                tool_name = body.get("name")
                arguments = body.get("arguments", {})

                if tool_name not in self.tools:
                    return func.HttpResponse(
                        json.dumps({"error": f"Tool '{tool_name}' not found"}, ensure_ascii=False),
                        status_code=404,
                        mimetype="application/json"
                    )

                handler = self.tools[tool_name]["handler"]
                result = handler(**arguments)

                return func.HttpResponse(
                    json.dumps({"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]}, ensure_ascii=False),
                    status_code=200,
                    mimetype="application/json"
                )
            except Exception as e:
                return func.HttpResponse(
                    json.dumps({"error": str(e)}, ensure_ascii=False),
                    status_code=500,
                    mimetype="application/json"
                )

        # ヘルスチェック
        if path == "health":
            return func.HttpResponse(
                json.dumps({"status": "healthy"}, ensure_ascii=False),
                status_code=200,
                mimetype="application/json"
            )

        return func.HttpResponse(
            json.dumps({"error": "Unknown endpoint"}, ensure_ascii=False),
            status_code=404,
            mimetype="application/json"
        )


# MCPアプリケーションインスタンス
mcp_app = MCPApp()

# ツールのインポートと登録
# デコレータにより、インポート時に自動的に mcp_app に登録される
from tools.customer import search_customer_by_name, get_customer_info
from tools.contract import get_contracts
from tools.visit import get_visit_history, get_upcoming_services
from tools.vehicle import search_vehicles
