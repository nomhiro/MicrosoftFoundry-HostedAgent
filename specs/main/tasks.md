# タスク: 販売店スタッフエージェント

**入力**: `/specs/main/` の設計ドキュメント
**前提**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**テスト**: 明示的に要求されていないため、テストタスクは含まれていません。

**構成**: タスクはコンポーネント別（MCPサーバー → Hosted Agent）に整理され、独立した実装とテストが可能です。

## フォーマット: `[ID] [P?] [Story] 説明`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: 所属するユーザーストーリー（US1: 顧客情報, US2: 契約・来店, US3: 車両在庫, US4: エージェント）
- 説明には正確なファイルパスを含める

## パス規約

- **マルチプロジェクト**: リポジトリルートに `mcp-server-dealer/`, `sales-staff-agent/`

---

## フェーズ 1: セットアップ（共有インフラ）

**目的**: 両プロジェクトの初期化と基本構造の作成

- [x] T001 実装計画に従って mcp-server-dealer/ ディレクトリ構造を作成
- [x] T002 [P] 実装計画に従って sales-staff-agent/ ディレクトリ構造を作成
- [x] T003 mcp-server-dealer/pyproject.toml に pyproject.toml を作成（azure-functions, mcp, python-dotenv）
- [x] T004 [P] sales-staff-agent/pyproject.toml に pyproject.toml を作成（azure-ai-agentserver-agentframework, azure-identity, python-dotenv）
- [x] T005 [P] mcp-server-dealer/host.json に Azure Functions host.json 設定を作成
- [x] T006 [P] mcp-server-dealer/local.settings.json に Azure Functions local.settings.json を作成
- [x] T007 [P] sales-staff-agent/.env.example に .env.example テンプレートを作成

---

## フェーズ 2: 基盤（ブロッキング前提条件）

**目的**: ユーザーストーリー実装前に完了必須のコアインフラ

**重要**: このフェーズが完了するまでユーザーストーリーの作業は開始できません

- [x] T008 mcp-server-dealer/data/customers.json にサンプルデータ（3顧客）を作成
- [x] T009 [P] mcp-server-dealer/data/contracts.json にサンプルデータ（3契約）を作成
- [x] T010 [P] mcp-server-dealer/data/visits.json にサンプルデータ（4来店）を作成
- [x] T011 [P] mcp-server-dealer/data/vehicles.json にサンプルデータ（6車両）を作成
- [x] T012 mcp-server-dealer/tools/__init__.py にデータ読み込みユーティリティを作成
- [x] T013 mcp-server-dealer/function_app.py に Azure Functions エントリーポイントを作成
- [x] T014 mcp-server-dealer/mcp_handler.py に MCP プロトコルハンドラーを作成

**チェックポイント**: 基盤準備完了 - ユーザーストーリー実装を開始可能

---

## フェーズ 3: ユーザーストーリー 1 - 顧客情報ツール（優先度: P1）MVP

**ゴール**: MCPサーバーで顧客名検索・顧客詳細取得ツールを実装する

**独立テスト**: `func start` でMCPサーバーを起動し、`search_customer_by_name("田中")` と `get_customer_info("C001")` が動作することを確認

### ユーザーストーリー 1 の実装

- [x] T015 [US1] mcp-server-dealer/tools/customer.py に search_customer_by_name ツールを docstring 付きで実装
- [x] T016 [US1] mcp-server-dealer/tools/customer.py に get_customer_info ツールを docstring 付きで実装
- [x] T017 [US1] mcp-server-dealer/mcp_handler.py に customer ツールを登録

**チェックポイント**: 顧客情報ツールが単独で動作することを確認

---

## フェーズ 4: ユーザーストーリー 2 - 契約・来店履歴ツール（優先度: P1）

**ゴール**: MCPサーバーで契約履歴・来店履歴・サービス予定取得ツールを実装する

**独立テスト**: `get_contracts("C001")`, `get_visit_history("C001")`, `get_upcoming_services(30)` が動作することを確認

### ユーザーストーリー 2 の実装

- [x] T018 [P] [US2] mcp-server-dealer/tools/contract.py に get_contracts ツールを docstring 付きで実装
- [x] T019 [P] [US2] mcp-server-dealer/tools/visit.py に get_visit_history ツールを docstring 付きで実装
- [x] T020 [US2] mcp-server-dealer/tools/visit.py に get_upcoming_services ツールを docstring 付きで実装
- [x] T021 [US2] mcp-server-dealer/mcp_handler.py に contract と visit ツールを登録

**チェックポイント**: 契約・来店履歴ツールが動作することを確認

---

## フェーズ 5: ユーザーストーリー 3 - 車両在庫検索ツール（優先度: P2）

**ゴール**: MCPサーバーで車両在庫検索ツールを実装する（色は部分一致対応）

**独立テスト**: `search_vehicles("SUV", "赤")` が "ソウルレッド" の車両にマッチすることを確認

### ユーザーストーリー 3 の実装

- [x] T022 [US3] mcp-server-dealer/tools/vehicle.py に search_vehicles ツールを部分一致色検索付きで実装
- [x] T023 [US3] mcp-server-dealer/mcp_handler.py に vehicle ツールを登録

**チェックポイント**: MCPサーバーの全ツールが動作することを確認（6ツール完成）

---

## フェーズ 6: ユーザーストーリー 4 - Hosted Agent 基本実装（優先度: P1）

**ゴール**: Microsoft Agent Framework を使用して Hosted Agent を実装し、MCPツールと連携させる

**独立テスト**: `uv run python src/container.py` で起動し、`http://localhost:8088/responses` に「田中様の契約履歴を教えて」を送信して応答を確認

### ユーザーストーリー 4 の実装

- [x] T024 [US4] sales-staff-agent/src/__init__.py を作成
- [x] T025 [US4] sales-staff-agent/src/agent.py に MCPTool 接続付きのエージェント定義を実装
- [x] T026 [US4] sales-staff-agent/src/container.py に Hosting Adapter 付きのコンテナエントリーポイントを実装
- [x] T027 [US4] sales-staff-agent/agent.yaml にエージェント設定を作成

**チェックポイント**: Hosted Agent がローカルで動作し、MCPサーバーと連携できることを確認

---

## フェーズ 7: 仕上げ・横断的関心事

**目的**: デプロイ設定と最終調整

- [x] T028 [P] sales-staff-agent/Dockerfile に Dockerfile を作成
- [x] T029 [P] mcp-server-dealer/.gitignore に .env と __pycache__ のエントリを追加
- [x] T030 [P] sales-staff-agent/.gitignore に .env と __pycache__ のエントリを追加
- [x] T031 quickstart.md の検証を実行 - ローカル開発フローがエンドツーエンドで動作することを確認

---

## 依存関係と実行順序

### フェーズ依存関係

- **セットアップ（フェーズ 1）**: 依存関係なし - すぐに開始可能
- **基盤（フェーズ 2）**: セットアップ完了に依存 - 全ユーザーストーリーをブロック
- **ユーザーストーリー（フェーズ 3-6）**: すべて基盤フェーズ完了に依存
  - US1-3（MCPツール）は順次または並列で進行可能
  - US4（Agent）は完全な統合テストにUS1-3が必要だが、基本実装はフェーズ2後に開始可能
- **仕上げ（フェーズ 7）**: すべてのユーザーストーリー完了に依存

### ユーザーストーリー依存関係

- **ユーザーストーリー 1（顧客情報）**: 基盤後に開始可能 - 他ストーリーへの依存なし
- **ユーザーストーリー 2（契約・来店）**: 基盤後に開始可能 - US1への依存なし
- **ユーザーストーリー 3（車両在庫）**: 基盤後に開始可能 - US1/US2への依存なし
- **ユーザーストーリー 4（エージェント）**: 基盤後に開始可能 - 完全テストにはUS1-3が必要

### 各ユーザーストーリー内

- ツール実装 → ハンドラーに登録 → 個別テスト
- 統合前にコア実装
- 次の優先度に移る前にストーリー完了

### 並列実行の機会

- T001-T002: ディレクトリ構造作成は並列実行可能
- T003-T007: すべてのプロジェクト初期化は並列実行可能
- T008-T011: すべてのJSONデータファイルは並列実行可能
- T018-T019: contract.py と visit.py は並列実行可能
- T028-T030: すべての仕上げタスクは並列実行可能

---

## 並列実行例: フェーズ 2（基盤）

```bash
# すべてのJSONデータファイル作成を同時に起動:
タスク: "mcp-server-dealer/data/customers.json にサンプルデータを作成"
タスク: "mcp-server-dealer/data/contracts.json にサンプルデータを作成"
タスク: "mcp-server-dealer/data/visits.json にサンプルデータを作成"
タスク: "mcp-server-dealer/data/vehicles.json にサンプルデータを作成"
```

---

## 実装戦略

### MVP優先（MCPサーバー + 顧客情報のみ）

1. フェーズ 1: セットアップを完了
2. フェーズ 2: 基盤を完了
3. フェーズ 3: ユーザーストーリー 1（顧客情報ツール）を完了
4. **停止して検証**: `func start` でMCPサーバーが動作することを確認
5. 基本的な顧客検索のデモ準備完了

### インクリメンタルデリバリー

1. セットアップ + 基盤を完了 → 基盤準備完了
2. US1（顧客情報）を追加 → テスト → MCPサーバー部分デモ可能
3. US2（契約・来店）を追加 → テスト → より多くのツールが使用可能
4. US3（車両在庫）を追加 → テスト → MCPサーバー完成
5. US4（エージェント）を追加 → テスト → 完全な統合デモ可能
6. 仕上げを追加 → Docker化 → デプロイ準備完了

### PoC フォーカス

これはPoCプロジェクトです。以下に注力:
- 本番対応よりも動作するデモンストレーション
- 最適化されたコードよりも教育的で明確なコード
- 複雑なセキュリティよりもシンプルな認証（APIキー）

---

## タスクサマリー

| フェーズ | タスク数 | 説明 |
|---------|----------|------|
| フェーズ 1: セットアップ | 7 | プロジェクト初期化 |
| フェーズ 2: 基盤 | 7 | JSONデータ + MCPハンドラー |
| フェーズ 3: US1（顧客情報） | 3 | customer.py ツール |
| フェーズ 4: US2（契約・来店） | 4 | contract.py + visit.py ツール |
| フェーズ 5: US3（車両在庫） | 2 | vehicle.py ツール |
| フェーズ 6: US4（エージェント） | 4 | Agent 実装 |
| フェーズ 7: 仕上げ | 4 | Dockerfile + クリーンアップ |
| **合計** | **31** | |

---

## 備考

- [P] タスク = 異なるファイル、依存関係なし
- [Story] ラベル = 追跡用にタスクを特定のユーザーストーリーにマッピング
- 各ユーザーストーリーは独立して完了・テスト可能であるべき
- 各タスクまたは論理的なグループ後にコミット
- 任意のチェックポイントで停止してストーリーを独立して検証可能
- PoC フォーカス: 憲章「V. 完全性より簡潔性」に準拠
