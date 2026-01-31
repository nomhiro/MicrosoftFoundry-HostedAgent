# Data Model: 販売店スタッフエージェント

**Date**: 2026-01-31
**Storage**: JSON ファイル（Azure Functions にバンドル）

## エンティティ関連図

```
┌─────────────┐       ┌─────────────┐
│  Customer   │───┬───│  Contract   │
│  (顧客)     │   │   │  (契約)     │
└─────────────┘   │   └──────┬──────┘
                  │          │
                  │          │ vehicle_id
                  │          ▼
                  │   ┌─────────────┐
                  ├───│   Vehicle   │
                  │   │   (車両)    │
                  │   └─────────────┘
                  │
                  │   ┌─────────────┐
                  └───│    Visit    │
                      │  (来店履歴) │
                      └─────────────┘
```

## Entity: Customer（顧客）

**File**: `data/customers.json`

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| id | string | ✅ | 顧客ID | 形式: C001, C002, ... |
| name | string | ✅ | 顧客名（姓 名） | 空文字不可 |
| phone | string | ✅ | 電話番号 | 形式: XXX-XXXX-XXXX |
| email | string | | メールアドレス | メール形式 |
| address | string | | 住所 | |
| registered_date | string | ✅ | 登録日 | ISO8601形式 |

**Sample Data**:
```json
{
  "id": "C001",
  "name": "田中 太郎",
  "phone": "090-1234-5678",
  "email": "tanaka@example.com",
  "address": "東京都港区六本木1-2-3",
  "registered_date": "2020-04-15"
}
```

---

## Entity: Contract（契約）

**File**: `data/contracts.json`

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| id | string | ✅ | 契約ID | 形式: CT001, CT002, ... |
| customer_id | string | ✅ | 顧客ID | FK → Customer.id |
| vehicle_id | string | ✅ | 車両ID | FK → Vehicle.id |
| contract_date | string | ✅ | 契約日 | ISO8601形式 |
| type | string | ✅ | 契約種別 | Enum: 新車購入/中古購入/リース |
| amount | number | ✅ | 金額（円） | 正の整数 |
| status | string | ✅ | ステータス | Enum: 完了/進行中/キャンセル |

**State Transitions**:
```
進行中 → 完了
進行中 → キャンセル
```

**Sample Data**:
```json
{
  "id": "CT001",
  "customer_id": "C001",
  "vehicle_id": "V001",
  "contract_date": "2023-03-20",
  "type": "新車購入",
  "amount": 3500000,
  "status": "完了"
}
```

---

## Entity: Visit（来店履歴）

**File**: `data/visits.json`

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| id | string | ✅ | 来店ID | 形式: VS001, VS002, ... |
| customer_id | string | ✅ | 顧客ID | FK → Customer.id |
| visit_date | string | ✅ | 来店日 | ISO8601形式 |
| type | string | ✅ | 来店種別 | Enum: 12ヶ月点検/車検/修理/その他 |
| vehicle_id | string | ✅ | 対象車両ID | FK → Vehicle.id |
| notes | string | | メモ | |
| next_service_date | string | | 次回サービス予定日 | ISO8601形式 or null |

**Sample Data**:
```json
{
  "id": "VS001",
  "customer_id": "C001",
  "visit_date": "2025-12-15",
  "type": "12ヶ月点検",
  "vehicle_id": "V001",
  "notes": "オイル交換実施",
  "next_service_date": "2026-12-15"
}
```

---

## Entity: Vehicle（車両）

**File**: `data/vehicles.json`

| Field | Type | Required | Description | Validation |
|-------|------|----------|-------------|------------|
| id | string | ✅ | 車両ID | 形式: V001, V002, ... |
| model | string | ✅ | モデル名 | 空文字不可 |
| type | string | ✅ | 車種 | Enum: SUV/セダン/軽自動車/ミニバン |
| color | string | ✅ | 色 | |
| year | number | ✅ | 年式 | 4桁の年 |
| price | number | ✅ | 価格（円） | 正の整数 |
| status | string | ✅ | ステータス | Enum: 在庫あり/予約済み/売約済み |

**State Transitions**:
```
在庫あり → 予約済み → 売約済み
在庫あり → 売約済み
予約済み → 在庫あり（キャンセル時）
```

**Sample Data**:
```json
{
  "id": "V001",
  "model": "CX-5",
  "type": "SUV",
  "color": "ソウルレッド",
  "year": 2023,
  "price": 3200000,
  "status": "売約済み"
}
```

---

## Relationships

| From | To | Type | Description |
|------|----|------|-------------|
| Contract | Customer | N:1 | 1顧客は複数契約を持てる |
| Contract | Vehicle | N:1 | 1車両は複数契約に関連しうる |
| Visit | Customer | N:1 | 1顧客は複数来店履歴を持てる |
| Visit | Vehicle | N:1 | 1車両は複数来店に関連しうる |

## Data Volume (PoC)

| Entity | Count | Notes |
|--------|-------|-------|
| Customer | 3 | サンプルデータ |
| Contract | 3 | サンプルデータ |
| Visit | 4 | サンプルデータ |
| Vehicle | 6 | サンプルデータ |
