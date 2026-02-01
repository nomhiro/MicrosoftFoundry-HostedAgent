"""
Azure Functions エントリーポイント

MCPサーバーを Azure Functions HTTP トリガーとして公開
"""

import azure.functions as func
import json
import logging

from tools.customer import search_customer_by_name as _search_customer_by_name
from tools.customer import get_customer_info as _get_customer_info
from tools.contract import get_contracts as _get_contracts
from tools.visit import get_visit_history as _get_visit_history
from tools.visit import get_upcoming_services as _get_upcoming_services
from tools.vehicle import search_vehicles as _search_vehicles

try:
    from azure.functions import McpToolProperty
except ImportError:  # Fallback for local environments without MCP helpers
    class McpToolProperty:
        def __init__(self, name: str, description: str, property_type: str, is_required: bool, enum: list[str] | None = None, default: object | None = None):
            self.name = name
            self.description = description
            self.property_type = property_type
            self.is_required = is_required
            self.enum = enum
            self.default = default

        def to_dict(self) -> dict:
            data = {
                "name": self.name,
                "description": self.description,
                "type": self.property_type,
                "required": self.is_required,
            }
            if self.enum:
                data["enum"] = self.enum
            if self.default is not None:
                data["default"] = self.default
            return data

# Azure Functions アプリケーション
app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def _get_arguments(context) -> dict:
    """MCP Tool Trigger の入力から arguments を取得"""
    if isinstance(context, str):
        payload = json.loads(context)
    elif isinstance(context, dict):
        payload = context
    else:
        payload = {}

    if "arguments" in payload:
        return payload.get("arguments", {}) or {}

    if "mcptoolargs" in payload:
        return payload.get("mcptoolargs", {}) or {}

    if "params" in payload and isinstance(payload["params"], dict):
        params = payload["params"]
        if "arguments" in params:
            return params.get("arguments", {}) or {}
        if "mcptoolargs" in params:
            return params.get("mcptoolargs", {}) or {}

    return {}


tool_properties_search_customer = json.dumps([
    McpToolProperty(
        name="name",
        description="顧客名（例: '田中'）",
        property_type="string",
        is_required=True,
    ).to_dict()
])

tool_properties_get_customer_info = json.dumps([
    McpToolProperty(
        name="customer_id",
        description="顧客ID（例: 'C001'）",
        property_type="string",
        is_required=True,
    ).to_dict()
])

tool_properties_get_contracts = json.dumps([
    McpToolProperty(
        name="customer_id",
        description="顧客ID（例: 'C001'）",
        property_type="string",
        is_required=True,
    ).to_dict()
])

tool_properties_get_visit_history = json.dumps([
    McpToolProperty(
        name="customer_id",
        description="顧客ID（例: 'C001'）",
        property_type="string",
        is_required=True,
    ).to_dict()
])

tool_properties_get_upcoming_services = json.dumps([
    McpToolProperty(
        name="days",
        description="何日先まで検索するか（デフォルト: 30）",
        property_type="integer",
        is_required=False,
        default=30,
    ).to_dict()
])

tool_properties_search_vehicles = json.dumps([
    McpToolProperty(
        name="type",
        description="車種（'SUV', 'セダン', '軽自動車', 'ミニバン'）",
        property_type="string",
        is_required=True,
        enum=["SUV", "セダン", "軽自動車", "ミニバン"],
    ).to_dict(),
    McpToolProperty(
        name="color",
        description="色（部分一致、例: '赤' → 'ソウルレッド' にマッチ）",
        property_type="string",
        is_required=False,
    ).to_dict(),
])


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="search_customer_by_name",
    description="顧客名からIDを検索します（部分一致）",
    toolProperties=tool_properties_search_customer,
)
def search_customer_by_name(context) -> list[dict]:
    try:
        args = _get_arguments(context)
        logging.info("search_customer_by_name args: %s", args)
        return _search_customer_by_name(args.get("name", ""))
    except Exception:
        logging.exception("search_customer_by_name failed")
        return [{"error": "search_customer_by_name failed"}]


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_customer_info",
    description="顧客IDから詳細情報を取得します",
    toolProperties=tool_properties_get_customer_info,
)
def get_customer_info(context) -> dict:
    try:
        args = _get_arguments(context)
        logging.info("get_customer_info args: %s", args)
        return _get_customer_info(args.get("customer_id", ""))
    except Exception:
        logging.exception("get_customer_info failed")
        return {"error": "get_customer_info failed"}


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_contracts",
    description="顧客IDから契約履歴を取得します",
    toolProperties=tool_properties_get_contracts,
)
def get_contracts(context) -> list[dict]:
    try:
        args = _get_arguments(context)
        logging.info("get_contracts args: %s", args)
        return _get_contracts(args.get("customer_id", ""))
    except Exception:
        logging.exception("get_contracts failed")
        return [{"error": "get_contracts failed"}]


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_visit_history",
    description="顧客IDから来店履歴を取得します",
    toolProperties=tool_properties_get_visit_history,
)
def get_visit_history(context) -> list[dict]:
    try:
        args = _get_arguments(context)
        logging.info("get_visit_history args: %s", args)
        return _get_visit_history(args.get("customer_id", ""))
    except Exception:
        logging.exception("get_visit_history failed")
        return [{"error": "get_visit_history failed"}]


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_upcoming_services",
    description="今後のサービス予定一覧を取得します",
    toolProperties=tool_properties_get_upcoming_services,
)
def get_upcoming_services(context) -> list[dict]:
    try:
        args = _get_arguments(context)
        logging.info("get_upcoming_services args: %s", args)
        days = args.get("days", 30)
        return _get_upcoming_services(days=days)
    except Exception:
        logging.exception("get_upcoming_services failed")
        return [{"error": "get_upcoming_services failed"}]


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="search_vehicles",
    description="条件に合う車両在庫を検索します（色は部分一致対応）",
    toolProperties=tool_properties_search_vehicles,
)
def search_vehicles(context) -> list[dict]:
    try:
        args = _get_arguments(context)
        logging.info("search_vehicles args: %s", args)
        return _search_vehicles(args.get("type", ""), args.get("color"))
    except Exception:
        logging.exception("search_vehicles failed")
        return [{"error": "search_vehicles failed"}]


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """ヘルスチェックエンドポイント"""
    return func.HttpResponse(
        '{"status": "healthy", "service": "mcp-server-dealer"}',
        status_code=200,
        mimetype="application/json"
    )
