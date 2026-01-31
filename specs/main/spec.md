# 販売店スタッフエージェント仕様書

## 概要

自動車販売店のスタッフを支援するAIエージェントシステム。
基幹システム（MCPサーバー）と連携し、顧客情報・契約履歴・来店履歴・車両在庫をリアルタイムで検索・提供する。

## システム構成

### コンポーネント

```
┌─────────────────────────────────────────────────────────────┐
│                    Microsoft Foundry                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Hosted Agent (コンテナ)                  │   │
│  │  - Microsoft Agent Framework                         │   │
│  │  - MCP ツール接続                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Azure Functions (Flex Consumption)              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                MCPサーバー                            │   │
│  │  - 顧客情報 API                                       │   │
│  │  - 契約情報 API                                       │   │
│  │  - 来店履歴 API                                       │   │
│  │  - 車両情報 API                                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                              │                               │
│                              ▼                               │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              JSONデータファイル                       │   │
│  │  - customers.json                                    │   │
│  │  - contracts.json                                    │   │
│  │  - visits.json                                       │   │
│  │  - vehicles.json                                     │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### プロジェクト構造

```
microsoft-foundry-hosted-agent/
├── mcp-server-dealer/           # MCPサーバー（Azure Functions）
│   ├── pyproject.toml
│   ├── function_app.py
│   ├── mcp_handler.py
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── customer.py
│   │   ├── contract.py
│   │   ├── visit.py
│   │   └── vehicle.py
│   ├── data/
│   │   ├── customers.json
│   │   ├── contracts.json
│   │   ├── visits.json
│   │   └── vehicles.json
│   └── host.json
│
├── sales-staff-agent/           # Hosted Agent
│   ├── pyproject.toml
│   ├── agent.yaml
│   ├── Dockerfile
│   ├── src/
│   │   ├── __init__.py
│   │   ├── container.py
│   │   └── agent.py
│   └── .env.example
│
└── articles/                    # ブログ記事
    └── microsoft-foundry-hosted-agent.md
```

---

## 機能要件

### MCPサーバー（mcp-server-dealer）

#### FR-MCP-001: 顧客名検索

- **ツール名**: `search_customer_by_name`
- **説明**: 顧客名から顧客IDを検索する（部分一致）
- **入力**:
  - `name` (str, 必須): 顧客名（例: "田中"）
- **出力**: 顧客リスト
  ```json
  [
    {"id": "C001", "name": "田中 太郎", "phone": "090-1234-5678"}
  ]
  ```
- **エラー**: 該当なしの場合は空リストを返す

#### FR-MCP-002: 顧客詳細取得

- **ツール名**: `get_customer_info`
- **説明**: 顧客IDから詳細情報を取得する
- **入力**:
  - `customer_id` (str, 必須): 顧客ID（例: "C001"）
- **出力**: 顧客詳細情報
  ```json
  {
    "id": "C001",
    "name": "田中 太郎",
    "phone": "090-1234-5678",
    "email": "tanaka@example.com",
    "address": "東京都港区...",
    "registered_date": "2020-04-15"
  }
  ```
- **エラー**: 該当なしの場合は `{"error": "Customer not found"}` を返す

#### FR-MCP-003: 契約履歴取得

- **ツール名**: `get_contracts`
- **説明**: 顧客IDから契約履歴を取得する
- **入力**:
  - `customer_id` (str, 必須): 顧客ID
- **出力**: 契約履歴リスト
  ```json
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
  ```

#### FR-MCP-004: 来店履歴取得

- **ツール名**: `get_visit_history`
- **説明**: 顧客IDから来店履歴を取得する
- **入力**:
  - `customer_id` (str, 必須): 顧客ID
- **出力**: 来店履歴リスト
  ```json
  [
    {
      "id": "VS001",
      "visit_date": "2025-12-15",
      "type": "12ヶ月点検",
      "vehicle_id": "V001",
      "notes": "オイル交換実施"
    }
  ]
  ```

#### FR-MCP-005: 車両在庫検索

- **ツール名**: `search_vehicles`
- **説明**: 条件に合う車両在庫を検索する
- **入力**:
  - `type` (str, 必須): 車種（"SUV", "セダン", "軽自動車", "ミニバン"）
  - `color` (str, 任意): 色
- **出力**: 車両リスト
  ```json
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
  ```

#### FR-MCP-006: サービス予定取得

- **ツール名**: `get_upcoming_services`
- **説明**: 今後のサービス予定一覧を取得する
- **入力**:
  - `days` (int, 任意, default=30): 何日先まで検索するか
- **出力**: サービス予定リスト
  ```json
  [
    {
      "customer_id": "C001",
      "customer_name": "田中 太郎",
      "scheduled_date": "2026-02-15",
      "type": "車検",
      "vehicle_model": "CX-5"
    }
  ]
  ```

---

### Hosted Agent（sales-staff-agent）

#### FR-AGENT-001: 自然言語での問い合わせ対応

- **説明**: スタッフからの自然言語での質問を理解し、適切なMCPツールを呼び出して情報取得、分かりやすい日本語で回答する
- **対応パターン**:
  - 「〇〇様の情報を教えて」
  - 「〇〇様の契約履歴」
  - 「〇〇様の点検履歴」
  - 「在庫を調べて」

#### FR-AGENT-002: 顧客情報照会フロー

- **説明**: 顧客名からIDを検索し、IDを使って詳細情報・履歴を取得する
- **フロー**:
  1. `search_customer_by_name` で顧客ID取得
  2. `get_customer_info` または `get_contracts` / `get_visit_history` で詳細取得
  3. 結果を整形して回答

#### FR-AGENT-003: 在庫照会対応

- **説明**: 車種・色などの条件で在庫検索し、在庫状況を分かりやすく提示する
- **フロー**:
  1. ユーザーの発話から車種・色を抽出
  2. `search_vehicles` で検索
  3. 結果を一覧形式で回答

---

## 非機能要件

### NFR-001: レスポンス時間

- 通常の問い合わせ: **5秒以内**

### NFR-002: 可用性

- Azure Functions: 99.9% SLA
- Hosted Agent: Foundry SLA に準拠

### NFR-003: スケーラビリティ

- min_replica: 1
- max_replica: 3

### NFR-004: セキュリティ

- APIキーによる認証（PoC向け簡易実装）
- 環境変数でAPIキーを管理
- 本番環境では Managed Identity / Key Vault への移行を推奨

---

## データ仕様

### customers.json

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| id | string | ✅ | 顧客ID（C001形式） |
| name | string | ✅ | 顧客名 |
| phone | string | ✅ | 電話番号 |
| email | string | | メールアドレス |
| address | string | | 住所 |
| registered_date | string | ✅ | 登録日（ISO8601） |

**サンプルデータ**:
```json
[
  {
    "id": "C001",
    "name": "田中 太郎",
    "phone": "090-1234-5678",
    "email": "tanaka@example.com",
    "address": "東京都港区六本木1-2-3",
    "registered_date": "2020-04-15"
  },
  {
    "id": "C002",
    "name": "鈴木 花子",
    "phone": "080-9876-5432",
    "email": "suzuki@example.com",
    "address": "神奈川県横浜市中区1-2-3",
    "registered_date": "2021-08-20"
  },
  {
    "id": "C003",
    "name": "佐藤 一郎",
    "phone": "070-1111-2222",
    "email": "sato@example.com",
    "address": "千葉県千葉市中央区1-2-3",
    "registered_date": "2022-01-10"
  }
]
```

### contracts.json

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| id | string | ✅ | 契約ID（CT001形式） |
| customer_id | string | ✅ | 顧客ID |
| vehicle_id | string | ✅ | 車両ID |
| contract_date | string | ✅ | 契約日（ISO8601） |
| type | string | ✅ | 契約種別（新車購入/中古購入/リース） |
| amount | number | ✅ | 金額 |
| status | string | ✅ | ステータス（完了/進行中/キャンセル） |

**サンプルデータ**:
```json
[
  {
    "id": "CT001",
    "customer_id": "C001",
    "vehicle_id": "V001",
    "contract_date": "2023-03-20",
    "type": "新車購入",
    "amount": 3500000,
    "status": "完了"
  },
  {
    "id": "CT002",
    "customer_id": "C001",
    "vehicle_id": "V005",
    "contract_date": "2025-01-15",
    "type": "新車購入",
    "amount": 4200000,
    "status": "進行中"
  },
  {
    "id": "CT003",
    "customer_id": "C002",
    "vehicle_id": "V002",
    "contract_date": "2024-06-10",
    "type": "中古購入",
    "amount": 1800000,
    "status": "完了"
  }
]
```

### visits.json

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| id | string | ✅ | 来店ID（VS001形式） |
| customer_id | string | ✅ | 顧客ID |
| visit_date | string | ✅ | 来店日（ISO8601） |
| type | string | ✅ | 来店種別（12ヶ月点検/車検/修理/その他） |
| vehicle_id | string | ✅ | 対象車両ID |
| notes | string | | メモ |
| next_service_date | string | | 次回サービス予定日 |

**サンプルデータ**:
```json
[
  {
    "id": "VS001",
    "customer_id": "C001",
    "visit_date": "2025-12-15",
    "type": "12ヶ月点検",
    "vehicle_id": "V001",
    "notes": "オイル交換実施",
    "next_service_date": "2026-12-15"
  },
  {
    "id": "VS002",
    "customer_id": "C001",
    "visit_date": "2024-03-20",
    "type": "車検",
    "vehicle_id": "V001",
    "notes": "ブレーキパッド交換",
    "next_service_date": "2026-03-20"
  },
  {
    "id": "VS003",
    "customer_id": "C002",
    "visit_date": "2025-11-01",
    "type": "修理",
    "vehicle_id": "V002",
    "notes": "バンパー修理",
    "next_service_date": null
  },
  {
    "id": "VS004",
    "customer_id": "C003",
    "visit_date": "2026-02-10",
    "type": "車検",
    "vehicle_id": "V003",
    "notes": "予定",
    "next_service_date": null
  }
]
```

### vehicles.json

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|------|------|
| id | string | ✅ | 車両ID（V001形式） |
| model | string | ✅ | モデル名 |
| type | string | ✅ | 車種（SUV/セダン/軽自動車/ミニバン） |
| color | string | ✅ | 色 |
| year | number | ✅ | 年式 |
| price | number | ✅ | 価格 |
| status | string | ✅ | ステータス（在庫あり/予約済み/売約済み） |

**サンプルデータ**:
```json
[
  {
    "id": "V001",
    "model": "CX-5",
    "type": "SUV",
    "color": "ソウルレッド",
    "year": 2023,
    "price": 3200000,
    "status": "売約済み"
  },
  {
    "id": "V002",
    "model": "アクセラ",
    "type": "セダン",
    "color": "ホワイト",
    "year": 2022,
    "price": 1800000,
    "status": "売約済み"
  },
  {
    "id": "V003",
    "model": "CX-30",
    "type": "SUV",
    "color": "マシングレー",
    "year": 2024,
    "price": 2800000,
    "status": "在庫あり"
  },
  {
    "id": "V004",
    "model": "CX-5",
    "type": "SUV",
    "color": "ソウルレッド",
    "year": 2025,
    "price": 3500000,
    "status": "在庫あり"
  },
  {
    "id": "V005",
    "model": "CX-60",
    "type": "SUV",
    "color": "ロジウムホワイト",
    "year": 2025,
    "price": 4200000,
    "status": "予約済み"
  },
  {
    "id": "V006",
    "model": "MAZDA2",
    "type": "軽自動車",
    "color": "ブルー",
    "year": 2024,
    "price": 1500000,
    "status": "在庫あり"
  }
]
```

---

## 技術スタック

### MCPサーバー

- Python 3.11+
- Azure Functions (Flex Consumption)
- mcp パッケージ
- uv（パッケージ管理）

### Hosted Agent

- Python 3.11+
- Microsoft Agent Framework
- azure-ai-agentserver-agentframework
- Docker コンテナ
- uv（パッケージ管理）

---

## デプロイ環境

| コンポーネント | 環境 |
|--------------|------|
| MCPサーバー | Azure Functions (Flex Consumption Plan) |
| コンテナレジストリ | Azure Container Registry |
| Hosted Agent | Microsoft Foundry (East Japan リージョン) |
| モデル | gpt-4o |

---

## テストシナリオ

### TS-001: 顧客名による契約履歴照会

- **入力**: 「田中様の契約履歴を教えて」
- **期待結果**:
  1. `search_customer_by_name("田中")` が呼ばれる
  2. `get_contracts("C001")` が呼ばれる
  3. 田中太郎様の契約履歴が日本語で回答される

### TS-002: 車両在庫検索

- **入力**: 「赤いSUVの在庫を調べて」
- **期待結果**:
  1. `search_vehicles("SUV", "ソウルレッド")` が呼ばれる
  2. 該当車両の一覧が回答される

### TS-003: サービス予定確認

- **入力**: 「今月の車検予定を教えて」
- **期待結果**:
  1. `get_upcoming_services(30)` が呼ばれる
  2. 車検予定の顧客一覧が回答される

### TS-004: 該当なしケース

- **入力**: 「山田様の情報を教えて」
- **期待結果**:
  1. `search_customer_by_name("山田")` が呼ばれる
  2. 該当顧客が見つからない旨が丁寧に回答される

---

## Clarifications

### Session 2026-01-31

**Ambiguity Assessment**: PoCとして実装に十分な詳細度があることを確認

- Q: MCP障害時の挙動は？ → A: PoC範囲外（エラーメッセージを返すのみで可）
- Q: 色検索のマッチングロジックは？ → A: 部分一致（"赤" → "ソウルレッド"にマッチ）

### Deferred Items (Planning Phase)

- 詳細なエラーハンドリング設計
- ログ・モニタリング要件（本番移行時）
