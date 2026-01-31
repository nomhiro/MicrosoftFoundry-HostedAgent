# Implementation Plan: 販売店スタッフエージェント

**Branch**: `main` | **Date**: 2026-01-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/main/spec.md`

## Summary

自動車販売店のスタッフを支援するAIエージェントシステムを構築する。
MCPサーバー（Azure Functions）とHosted Agent（Microsoft Foundry）の2コンポーネントで構成され、
顧客情報・契約履歴・来店履歴・車両在庫をリアルタイムで検索・提供する。

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**:
- MCPサーバー: azure-functions, mcp, python-dotenv
- Hosted Agent: azure-ai-agentserver-agentframework, azure-identity, python-dotenv

**Storage**: JSONファイル（customers.json, contracts.json, visits.json, vehicles.json）
**Testing**: pytest（PoC範囲外だが必要に応じて追加可能）
**Target Platform**:
- MCPサーバー: Azure Functions (Flex Consumption)
- Hosted Agent: Microsoft Foundry (East Japan)

**Project Type**: マルチプロジェクト（MCPサーバー + Hosted Agent）
**Performance Goals**: レスポンス5秒以内
**Constraints**: min_replica: 1, max_replica: 3
**Scale/Scope**: PoC（3顧客、6車両のサンプルデータ）

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 状態 | 検証 |
|------|------|------|
| I. PoC優先の考え方 | ✅ PASS | デモ目的、教育的コード、過剰設計なし |
| II. 仕様駆動開発 | ✅ PASS | spec.md完成、clarify完了、plan作成中 |
| III. Azure ネイティブ統合 | ✅ PASS | Azure Functions, Foundry, ACR使用 |
| IV. MCPプロトコル準拠 | ✅ PASS | MCPツール定義あり、docstring必須 |
| V. 完全性より簡潔性 | ✅ PASS | JSONストレージ、APIキー認証 |

**Gate Result**: ✅ ALL PASSED - Phase 0に進む

## Project Structure

### Documentation (this feature)

```text
specs/main/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
mcp-server-dealer/              # MCPサーバー（Azure Functions）
├── pyproject.toml              # uv プロジェクト設定
├── function_app.py             # Azure Functions エントリーポイント
├── mcp_handler.py              # MCP プロトコル処理
├── tools/
│   ├── __init__.py
│   ├── customer.py             # 顧客情報ツール
│   ├── contract.py             # 契約情報ツール
│   ├── visit.py                # 来店履歴ツール
│   └── vehicle.py              # 車両情報ツール
├── data/
│   ├── customers.json
│   ├── contracts.json
│   ├── visits.json
│   └── vehicles.json
├── host.json
└── local.settings.json

sales-staff-agent/              # Hosted Agent（コンテナ）
├── pyproject.toml              # uv プロジェクト設定
├── agent.yaml                  # エージェント定義
├── Dockerfile                  # コンテナ化設定
├── src/
│   ├── __init__.py
│   ├── container.py            # エントリーポイント（Hosting Adapter）
│   └── agent.py                # エージェント定義
├── .env.example                # 環境変数テンプレート
└── .env                        # 環境変数（gitignore）
```

**Structure Decision**: マルチプロジェクト構成を採用。MCPサーバーとHosted Agentは独立してデプロイ可能。

## Complexity Tracking

> 憲章違反なし - このセクションは空

## Phase 0: Research Summary

### MCP on Azure Functions

**Decision**: Azure Functions v2 (Python) + FastMCP ライブラリ
**Rationale**: Flex Consumption Planでコスト効率良好、MCPプロトコルはFastMCPで簡易実装
**Alternatives considered**:
- Azure Container Apps: オーバースペック for PoC
- Azure App Service: Flex Consumptionの方がコスト効率良い

### Microsoft Agent Framework

**Decision**: azure-ai-agentserver-agentframework パッケージ使用
**Rationale**: Foundryとのネイティブ統合、Hosting Adapter内蔵
**Alternatives considered**:
- LangGraph: 複雑なグラフ構造向け、今回は単純なツール呼び出しのみ
- カスタムコード: Agent Framework の方が Foundry 統合が容易

### MCP接続方式

**Decision**: Foundry Connections経由でMCPサーバーに接続
**Rationale**: project_connection_id でセキュアに接続管理
**Alternatives considered**:
- 直接URL指定: セキュリティ上の懸念

## Phase 1: Design Artifacts

### Data Model

エンティティ定義は [data-model.md](./data-model.md) を参照

### API Contracts

MCPツールコントラクトは [spec.md](./spec.md) の機能要件セクションで定義済み

### Quickstart

ローカル実行手順は [quickstart.md](./quickstart.md) を参照

## Next Steps

1. `/speckit.tasks` を実行してタスクリストを生成
2. タスクに従って実装を進める
