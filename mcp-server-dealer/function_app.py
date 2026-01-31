"""
Azure Functions エントリーポイント

MCPサーバーを Azure Functions HTTP トリガーとして公開
"""

import azure.functions as func
import json

from tools.customer import search_customer_by_name as _search_customer_by_name
from tools.customer import get_customer_info as _get_customer_info
from tools.contract import get_contracts as _get_contracts
from tools.visit import get_visit_history as _get_visit_history
from tools.visit import get_upcoming_services as _get_upcoming_services
from tools.vehicle import search_vehicles as _search_vehicles

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
    return payload.get("arguments", {}) or {}


tool_properties_search_customer = json.dumps([
    {
        "name": "name",
        "propertyType": "string",
        "description": "顧客名（例: '田中'）",
        "isRequired": True
    }
])

tool_properties_get_customer_info = json.dumps([
    {
        "name": "customer_id",
        "propertyType": "string",
        "description": "顧客ID（例: 'C001'）",
        "isRequired": True
    }
])

tool_properties_get_contracts = json.dumps([
    {
        "name": "customer_id",
        "propertyType": "string",
        "description": "顧客ID（例: 'C001'）",
        "isRequired": True
    }
])

tool_properties_get_visit_history = json.dumps([
    {
        "name": "customer_id",
        "propertyType": "string",
        "description": "顧客ID（例: 'C001'）",
        "isRequired": True
    }
])

tool_properties_get_upcoming_services = json.dumps([
    {
        "name": "days",
        "propertyType": "integer",
        "description": "何日先まで検索するか（デフォルト: 30）",
        "isRequired": False
    }
])

tool_properties_search_vehicles = json.dumps([
    {
        "name": "type",
        "propertyType": "string",
        "description": "車種（'SUV', 'セダン', '軽自動車', 'ミニバン'）",
        "isRequired": True
    },
    {
        "name": "color",
        "propertyType": "string",
        "description": "色（部分一致、例: '赤' → 'ソウルレッド' にマッチ）",
        "isRequired": False
    }
])


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="search_customer_by_name",
    description="顧客名からIDを検索します（部分一致）",
    toolProperties=tool_properties_search_customer,
)
def search_customer_by_name(context) -> list[dict]:
    args = _get_arguments(context)
    return _search_customer_by_name(args.get("name", ""))


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_customer_info",
    description="顧客IDから詳細情報を取得します",
    toolProperties=tool_properties_get_customer_info,
)
def get_customer_info(context) -> dict:
    args = _get_arguments(context)
    return _get_customer_info(args.get("customer_id", ""))


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_contracts",
    description="顧客IDから契約履歴を取得します",
    toolProperties=tool_properties_get_contracts,
)
def get_contracts(context) -> list[dict]:
    args = _get_arguments(context)
    return _get_contracts(args.get("customer_id", ""))


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_visit_history",
    description="顧客IDから来店履歴を取得します",
    toolProperties=tool_properties_get_visit_history,
)
def get_visit_history(context) -> list[dict]:
    args = _get_arguments(context)
    return _get_visit_history(args.get("customer_id", ""))


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="get_upcoming_services",
    description="今後のサービス予定一覧を取得します",
    toolProperties=tool_properties_get_upcoming_services,
)
def get_upcoming_services(context) -> list[dict]:
    args = _get_arguments(context)
    days = args.get("days", 30)
    return _get_upcoming_services(days=days)


@app.generic_trigger(
    arg_name="context",
    type="mcpToolTrigger",
    toolName="search_vehicles",
    description="条件に合う車両在庫を検索します（色は部分一致対応）",
    toolProperties=tool_properties_search_vehicles,
)
def search_vehicles(context) -> list[dict]:
    args = _get_arguments(context)
    return _search_vehicles(args.get("type", ""), args.get("color"))


@app.route(route="health", methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """ヘルスチェックエンドポイント"""
    return func.HttpResponse(
        '{"status": "healthy", "service": "mcp-server-dealer"}',
        status_code=200,
        mimetype="application/json"
    )
