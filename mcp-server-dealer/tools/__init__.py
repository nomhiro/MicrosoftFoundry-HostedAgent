"""
MCPサーバーツールモジュール

データ読み込みユーティリティと各ツールをエクスポート
"""

import json
import logging
import re
from pathlib import Path
from typing import Any

# データディレクトリのパス
DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json(filename: str) -> list[dict[str, Any]]:
    """JSONファイルを読み込んでリストとして返す

    Args:
        filename: JSONファイル名（例: "customers.json"）

    Returns:
        JSONデータのリスト
    """
    file_path = DATA_DIR / filename
    try:
        if not file_path.exists():
            logging.error("Data file not found: %s", file_path)
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        logging.info("Loaded data file: %s (count=%d)", file_path, len(data))
        return data
    except Exception:
        logging.exception("Failed to load data file: %s", file_path)
        return []


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


def normalize_customer_id(value: str) -> str:
    """顧客IDを正規化（例: 'C001の顧客情報' -> 'C001'）"""
    if not value:
        return ""
    text = str(value).replace("\u3000", " ").strip()
    match = re.search(r"C\d{3,}", text, re.IGNORECASE)
    if match:
        return match.group(0).upper()
    return text
