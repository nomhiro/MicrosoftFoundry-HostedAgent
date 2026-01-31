"""
顧客情報ツール

顧客の検索と詳細情報取得を提供
"""

from typing import Optional
from tools import get_customers
def search_customer_by_name(name: str) -> list[dict]:
    """顧客名からIDを検索します（部分一致）

    Args:
        name: 顧客名（例: "田中"）

    Returns:
        マッチした顧客のリスト [{id, name, phone}, ...]
        該当なしの場合は空リスト
    """
    customers = get_customers()
    results = []

    for customer in customers:
        if name in customer["name"]:
            results.append({
                "id": customer["id"],
                "name": customer["name"],
                "phone": customer["phone"]
            })

    return results


def get_customer_info(customer_id: str) -> dict:
    """顧客IDから詳細情報を取得します

    Args:
        customer_id: 顧客ID（例: "C001"）

    Returns:
        顧客の詳細情報
        該当なしの場合は {"error": "Customer not found"}
    """
    customers = get_customers()

    for customer in customers:
        if customer["id"] == customer_id:
            return customer

    return {"error": "Customer not found"}
