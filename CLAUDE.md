# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Microsoft Foundry Hosted Agent PoC - 自動車販売店スタッフ支援AIエージェントシステム。
Zennブログ記事とともに、仕様駆動開発（Speckit）で実装を進める。

## Architecture

```
┌─────────────────────────────────────┐
│     Hosted Agent (sales-staff-agent) │  ← Microsoft Foundry上で実行
│     Microsoft Agent Framework        │
└──────────────┬──────────────────────┘
               │ MCP Protocol
               ▼
┌─────────────────────────────────────┐
│   MCP Server (mcp-server-dealer)     │  ← Azure Functions
│   顧客/契約/来店/車両 情報API         │
│   JSONファイルでデータ管理            │
└─────────────────────────────────────┘
```

## Project Structure

| Path | Description |
|------|-------------|
| `mcp-server-dealer/` | MCPサーバー（Azure Functions） |
| `sales-staff-agent/` | Hosted Agent（コンテナ） |
| `articles/` | Zennブログ記事 |
| `specs/main/spec.md` | 機能仕様書（Speckit管理） |
| `specs/main/plan.md` | 実装計画（Speckit生成） |
| `specs/main/tasks.md` | タスク一覧（Speckit生成） |
| `.specify/templates/` | Speckitテンプレート |
| `.specify/memory/constitution.md` | プロジェクト憲章 |

## Commands

### MCP Server (mcp-server-dealer/)
```bash
cd mcp-server-dealer
uv sync                    # 依存関係インストール
func start                 # ローカル起動
func azure functionapp publish mcp-server-dealer --python  # デプロイ
```

### Hosted Agent (sales-staff-agent/)
```bash
cd sales-staff-agent
uv sync                    # 依存関係インストール
uv run python src/container.py  # ローカル起動（localhost:8088）
docker build -t sales-staff-agent:v1 .  # コンテナビルド
```

### ローカルテスト

#### PowerShell
```powershell
$body = @{
    input = @{
        messages = @(
            @{ role = "user"; content = "田中様の契約履歴を教えて" }
        )
    }
} | ConvertTo-Json -Depth 4

Invoke-RestMethod -Uri "http://localhost:8088/responses" -Method POST -ContentType "application/json" -Body $body
```

#### HTTP (REST Client等)
```http
POST http://localhost:8088/responses
Content-Type: application/json

{"input": {"messages": [{"role": "user", "content": "田中様の契約履歴を教えて"}]}}
```

## Development Workflow

Speckit仕様駆動開発を使用:
1. `/speckit.clarify` - 仕様の明確化
2. `/speckit.plan` - 設計計画
3. `/speckit.tasks` - タスク分解
4. `/speckit.implement` - 実装

## Tech Stack

- **Python**: 3.11+
- **Package Manager**: uv
- **MCP Server**: Azure Functions (Flex Consumption) + mcp パッケージ
- **Agent**: Microsoft Agent Framework (azure-ai-agentserver-agentframework)
- **Container**: Docker → Azure Container Registry → Microsoft Foundry

## MCP Tools

| Tool | Description |
|------|-------------|
| `search_customer_by_name` | 顧客名からID検索（部分一致） |
| `get_customer_info` | 顧客詳細取得 |
| `get_contracts` | 契約履歴取得 |
| `get_visit_history` | 来店履歴取得 |
| `search_vehicles` | 車両在庫検索 |
| `get_upcoming_services` | サービス予定一覧 |

## Notes

- セキュリティ: PoC向けにAPIキー認証（環境変数管理）
- 言語: 日本語でのユーザー対応
