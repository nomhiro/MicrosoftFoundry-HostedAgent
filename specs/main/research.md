# Research: 販売店スタッフエージェント

**Date**: 2026-01-31
**Status**: Complete

## 1. MCP on Azure Functions

### Question
Azure Functions で MCP サーバーを実装する最適な方法は？

### Research Findings

**Azure Functions v2 (Python)**:
- Flex Consumption Plan でコスト効率良好
- HTTP トリガーで MCP エンドポイントを公開
- Python 3.11+ サポート

**MCP ライブラリ選択**:
- `mcp` パッケージ: 公式MCPライブラリ
- `fastmcp`: シンプルなデコレータベースAPI

### Decision
`mcp` 公式パッケージを使用し、Azure Functions HTTP トリガーで公開

### Rationale
- 公式パッケージのため安定性が高い
- Azure Functions との相性が良い
- PoC として十分なシンプルさ

### Alternatives Rejected
| Alternative | Rejection Reason |
|-------------|------------------|
| Azure Container Apps | オーバースペック for PoC |
| Azure App Service | Flex Consumptionの方がコスト効率良い |
| fastmcp | 公式パッケージの方が長期的に安定 |

---

## 2. Microsoft Agent Framework

### Question
Hosted Agent を実装する最適なフレームワークは？

### Research Findings

**Microsoft Agent Framework**:
- `azure-ai-agentserver-agentframework` パッケージ
- Foundry とのネイティブ統合
- Hosting Adapter 内蔵（localhost:8088）
- MCP ツール接続をサポート

**代替フレームワーク**:
- LangGraph: 複雑なグラフ構造向け
- カスタムコード: 完全な制御が必要な場合

### Decision
Microsoft Agent Framework を使用

### Rationale
- Foundry との統合が最も容易
- Hosting Adapter が組み込まれている
- MCP 接続が標準サポート
- ブログ記事として最も分かりやすい

### Alternatives Rejected
| Alternative | Rejection Reason |
|-------------|------------------|
| LangGraph | 複雑なグラフ構造向け、今回は単純なツール呼び出しのみ |
| カスタムコード | Agent Framework の方が Foundry 統合が容易 |

---

## 3. MCP接続方式

### Question
Hosted Agent から MCP サーバーへの接続方式は？

### Research Findings

**Foundry Connections**:
- Azure Portal / Foundry Portal で接続を事前設定
- `project_connection_id` で参照
- 資格情報は Foundry が管理

**直接URL指定**:
- MCPTool の `server_url` パラメータで直接指定
- API キーを環境変数で管理

### Decision
PoC では直接 URL 指定（ローカル開発用）、本番では Foundry Connections

### Rationale
- ローカル開発時は直接 URL が便利
- Foundry デプロイ時は Connections を使用

---

## 4. 認証方式

### Question
PoC での認証方式は？

### Research Findings

**PoC向け**:
- API キー認証（シンプル）
- 環境変数で管理

**本番向け**:
- Managed Identity
- Azure Key Vault

### Decision
PoC では API キー認証

### Rationale
- セットアップが簡単
- ブログ読者が再現しやすい
- 憲章「V. 完全性より簡潔性」に準拠

---

## 5. データストレージ

### Question
サンプルデータの保存方式は？

### Research Findings

**JSON ファイル**:
- Azure Functions のローカルファイル
- シンプルで理解しやすい

**Azure Cosmos DB**:
- スケーラブルだがオーバースペック

**Azure Blob Storage**:
- 可能だがPoC には複雑

### Decision
JSON ファイル（Azure Functions にバンドル）

### Rationale
- 最もシンプル
- ブログ読者が理解しやすい
- 憲章「V. 完全性より簡潔性」に準拠

---

## Summary

| 領域 | Decision | 理由 |
|------|----------|------|
| MCP実装 | mcp パッケージ + Azure Functions | 公式、安定、コスト効率 |
| Agent Framework | Microsoft Agent Framework | Foundry ネイティブ統合 |
| MCP接続 | 直接URL（PoC）/ Connections（本番） | 開発の柔軟性 |
| 認証 | API キー | PoC 簡潔性 |
| ストレージ | JSON ファイル | シンプル、教育的 |
