# Backend Tests for Kvell API

このディレクトリには、Kvell APIのバックエンドテスト（Unit / Integration）が含まれています。

## 技術スタック

- **Framework:** pytest
- **Async Support:** pytest-asyncio
- **Database:** MongoDB (Motor / pymongo)
- **Architecture:** Clean Architecture

## ディレクトリ構造

```
apps/api/tests/
├── unit/                      # 単体テスト（モック使用）
│   ├── adapter/               # Router, Gateway層のテスト
│   ├── usecase/               # UseCase層のテスト
│   └── domain/                # Domain層のテスト
└── integration/               # 結合テスト（実DB使用）
    ├── conftest.py            # テスト用DB設定
    └── adapter/entrypoints/   # API統合テスト
```

## 前提条件

### MongoDB の起動

プロジェクトルートで以下を実行：

```bash
docker compose up -d mongo
```

## テストの実行方法

### 全テスト実行

```bash
cd apps/api
uv run pytest -v
```

### Unit Tests のみ

```bash
uv run pytest tests/unit/ -v
```

### Integration Tests のみ

```bash
uv run pytest tests/integration/ -v
```

### カバレッジ付き実行

```bash
uv run pytest --cov=src --cov-report=term-missing
```

### 特定のテストファイル実行

```bash
uv run pytest tests/integration/adapter/entrypoints/test_health_router_integration.py -v
```

## テストの種類と役割

### Unit Tests（単体テスト）

- **対象:** Router, UseCase, Domain層
- **DB接続:** なし（モック使用）
- **検証内容:** バリデーション、ビジネスロジック、境界値
- **実行速度:** 高速

### Integration Tests（結合テスト）

- **対象:** API Endpoint → UseCase → Repository → MongoDB
- **DB接続:** あり（テスト用DB: `kvell_test`）
- **検証内容:** DB操作、レイヤー統合、データ永続化
- **実行速度:** 中速

## Data Management

### Integration Tests

- **Test DB:** `kvell_test`（本番DBと分離）
- **Cleanup:** 各テスト実行**前**に自動クリーンアップ
- **Debugging:** テスト失敗時はデータが残るため、デバッグ可能

## 静的解析

### 型チェック・Lintの実行

```bash
uv run task check-all
```

### 自動修正

```bash
uv run task fix-all
```

## トラブルシューティング

### Integration テストが "Connection refused" で失敗する場合

1. MongoDBが起動しているか確認:
```bash
docker compose ps mongo
```

2. MongoDBに接続できるか確認:
```bash
mongosh mongodb://localhost:27017
```

### Event loop エラーが発生する場合

- `conftest.py`のfixture scopeを確認
- pytest-asyncioのバージョンを確認: `uv run pip list | grep pytest-asyncio`

## 命名規則

テストメソッド名は **Action-Condition-Result** 形式を使用：

```python
def test_saveMessage_whenInputIsValid_returns200AndData():
    """
    Action: saveMessage (テスト対象のメソッド)
    Condition: whenInputIsValid (前提条件)
    Result: returns200AndData (期待される結果)
    """
```

詳細は `.prompts/10_backend.md` を参照してください。
