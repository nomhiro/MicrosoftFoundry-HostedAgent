"""
契約情報ツール

顧客の契約履歴を取得
"""

from tools import get_contracts as _get_contracts, normalize_customer_id
def get_contracts(customer_id: str) -> list[dict]:
    """顧客IDから契約履歴を取得します

    Args:
        customer_id: 顧客ID（例: "C001"）

    Returns:
        契約履歴のリスト
        [
            {
                "id": "CT001",
                "vehicle_id": "V001",
                "contract_date": "2023-03-20",
                "type": "新車購入",
                "amount": 3500000,
                "status": "完了"
            }
        ]
    """
    contracts = _get_contracts()
    normalized_id = normalize_customer_id(customer_id)
    results = []

    for contract in contracts:
        if contract["customer_id"] == normalized_id:
            results.append({
                "id": contract["id"],
                "vehicle_id": contract["vehicle_id"],
                "contract_date": contract["contract_date"],
                "type": contract["type"],
                "amount": contract["amount"],
                "status": contract["status"]
            })

    return results
