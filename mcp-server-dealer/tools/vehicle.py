"""
車両情報ツール

車両在庫の検索
"""

from typing import Optional
from tools import get_vehicles

# 色のマッピング（部分一致検索用）
COLOR_ALIASES = {
    "赤": ["ソウルレッド", "レッド", "赤"],
    "白": ["ホワイト", "ロジウムホワイト", "白"],
    "黒": ["ブラック", "ジェットブラック", "黒"],
    "グレー": ["マシングレー", "グレー", "灰"],
    "青": ["ブルー", "ディープブルー", "青"],
}


def matches_color(vehicle_color: str, search_color: Optional[str]) -> bool:
    """色が検索条件にマッチするかチェック（部分一致）

    Args:
        vehicle_color: 車両の色
        search_color: 検索条件の色（None の場合は全てマッチ）

    Returns:
        マッチする場合 True
    """
    if not search_color:
        return True

    # 完全一致
    if search_color in vehicle_color or vehicle_color in search_color:
        return True

    # エイリアスチェック
    search_lower = search_color.lower()
    for alias_key, aliases in COLOR_ALIASES.items():
        if search_color in alias_key or alias_key in search_color:
            for alias in aliases:
                if alias in vehicle_color:
                    return True

    # 部分一致
    return search_color in vehicle_color


def search_vehicles(type: str, color: Optional[str] = None) -> list[dict]:
    """条件に合う車両在庫を検索します

    色は部分一致対応: "赤" → "ソウルレッド" にマッチ

    Args:
        type: 車種（"SUV", "セダン", "軽自動車", "ミニバン"）
        color: 色（任意、部分一致）

    Returns:
        車両リスト
        [
            {
                "id": "V001",
                "model": "CX-5",
                "type": "SUV",
                "color": "ソウルレッド",
                "year": 2023,
                "price": 3200000,
                "status": "在庫あり"
            }
        ]
    """
    vehicles = get_vehicles()
    results = []

    for vehicle in vehicles:
        # 車種チェック
        if vehicle["type"] != type:
            continue

        # 色チェック（部分一致）
        if not matches_color(vehicle["color"], color):
            continue

        results.append({
            "id": vehicle["id"],
            "model": vehicle["model"],
            "type": vehicle["type"],
            "color": vehicle["color"],
            "year": vehicle["year"],
            "price": vehicle["price"],
            "status": vehicle["status"]
        })

    return results
