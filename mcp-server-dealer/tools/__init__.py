"""
MCPサーバーツールモジュール

データ読み込みユーティリティと各ツールをエクスポート
"""

import json
from pathlib import Path
from typing import Any

# データディレクトリのパス
DATA_DIR = Path(__file__).parent.parent / "data"


def load_json(filename: str) -> list[dict[str, Any]]:
    """JSONファイルを読み込んでリストとして返す

    Args:
        filename: JSONファイル名（例: "customers.json"）

    Returns:
        JSONデータのリスト
    """
    file_path = DATA_DIR / filename
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_customers() -> list[dict[str, Any]]:
    """顧客データを取得"""
    return load_json("customers.json")


def get_contracts() -> list[dict[str, Any]]:
    """契約データを取得"""
    return load_json("contracts.json")


def get_visits() -> list[dict[str, Any]]:
    """来店履歴データを取得"""
    return load_json("visits.json")


def get_vehicles() -> list[dict[str, Any]]:
    """車両データを取得"""
    return load_json("vehicles.json")
