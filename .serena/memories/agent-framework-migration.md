# sales-staff-agent Agent Framework移行

## 移行日
2026-02-01

## 概要
sales-staff-agentをMicrosoft Agent Framework (`agent-framework`)へ完全移行。
Hosted Agent対応、VS Code可視化、Observabilityをサポート。

## 変更内容

### SDK変更
- 旧: `azure-ai-projects` (AIProjectClient, MCPTool)
- 新: `agent-framework-core`, `agent-framework-azure-ai`, `azure-ai-agentserver-agentframework`

### 主要コンポーネント
| コンポーネント | 新しいクラス/関数 |
|---------------|-----------------|
| エージェント | `ChatAgent` via `AzureOpenAIResponsesClient.create_agent()` |
| MCPツール | `MCPStreamableHTTPTool` |
| HTTPサーバー | `from_agent_framework().run()` |
| 可視化 | `setup_observability(vs_code_extension_port=4319)` |

### ファイル構成
```
sales-staff-agent/src/
├── agent.py       # ChatAgent + MCPStreamableHTTPTool定義
├── container.py   # コンテナモード (from_agent_framework)
└── interactive.py # 対話モード (新規追加)
```

### 環境変数変更
- `AZURE_AI_PROJECT_ENDPOINT` → `AZURE_OPENAI_ENDPOINT`
- 追加: `FOUNDRY_OTLP_PORT`, `ENABLE_SENSITIVE_DATA`

## 使用方法

### 対話モード
```bash
uv run python src/interactive.py
```

### コンテナモード
```bash
uv run python src/container.py
# POST http://localhost:8088/responses
```

### VS Code可視化
1. container.py実行
2. Ctrl+Shift+P → `Microsoft Foundry: Open Visualizer for Hosted Agents`

## デプロイ
VS Code拡張: `Microsoft Foundry: Deploy Hosted Agent` → container.py指定

## 注意点
- パッケージはプレリリース版の可能性あり (`--pre` フラグ必要)
- ACR権限: プロジェクトマネージドIDに `AcrPull` ロール必要
