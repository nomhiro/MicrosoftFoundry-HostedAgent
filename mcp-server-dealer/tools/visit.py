"""
来店履歴ツール

来店履歴とサービス予定の取得
"""

from datetime import datetime, timedelta
from tools import get_visits, get_customers
from mcp_handler import mcp_app


@mcp_app.register(
    name="get_visit_history",
    description="顧客IDから来店履歴を取得します",
    parameters={
        "type": "object",
        "properties": {
            "customer_id": {
                "type": "string",
                "description": "顧客ID（例: 'C001'）"
            }
        },
        "required": ["customer_id"]
    }
)
def get_visit_history(customer_id: str) -> list[dict]:
    """顧客IDから来店履歴を取得します

    Args:
        customer_id: 顧客ID（例: "C001"）

    Returns:
        来店履歴のリスト
        [
            {
                "id": "VS001",
                "visit_date": "2025-12-15",
                "type": "12ヶ月点検",
                "vehicle_id": "V001",
                "notes": "オイル交換実施"
            }
        ]
    """
    visits = get_visits()
    results = []

    for visit in visits:
        if visit["customer_id"] == customer_id:
            results.append({
                "id": visit["id"],
                "visit_date": visit["visit_date"],
                "type": visit["type"],
                "vehicle_id": visit["vehicle_id"],
                "notes": visit.get("notes", "")
            })

    return results


@mcp_app.register(
    name="get_upcoming_services",
    description="今後のサービス予定一覧を取得します",
    parameters={
        "type": "object",
        "properties": {
            "days": {
                "type": "integer",
                "description": "何日先まで検索するか（デフォルト: 30）",
                "default": 30
            }
        },
        "required": []
    }
)
def get_upcoming_services(days: int = 30) -> list[dict]:
    """今後のサービス予定一覧を取得します

    Args:
        days: 何日先まで検索するか（デフォルト: 30）

    Returns:
        サービス予定のリスト
        [
            {
                "customer_id": "C001",
                "customer_name": "田中 太郎",
                "scheduled_date": "2026-02-15",
                "type": "車検",
                "vehicle_model": "CX-5"
            }
        ]
    """
    visits = get_visits()
    customers = get_customers()

    # 顧客IDから名前へのマッピング
    customer_names = {c["id"]: c["name"] for c in customers}

    today = datetime.now().date()
    end_date = today + timedelta(days=days)
    results = []

    for visit in visits:
        # next_service_date がある場合はそれを使用、なければ visit_date を確認
        scheduled_date_str = visit.get("next_service_date") or visit.get("visit_date")
        if not scheduled_date_str:
            continue

        try:
            scheduled_date = datetime.strptime(scheduled_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        if today <= scheduled_date <= end_date:
            results.append({
                "customer_id": visit["customer_id"],
                "customer_name": customer_names.get(visit["customer_id"], "不明"),
                "scheduled_date": scheduled_date_str,
                "type": visit["type"],
                "vehicle_id": visit["vehicle_id"]
            })

    # 日付でソート
    results.sort(key=lambda x: x["scheduled_date"])

    return results
