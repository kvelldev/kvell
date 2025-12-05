# E2E Tests for Kvell

このディレクトリには、Kvellシステムの E2E (End-to-End) テストが含まれています。

## 技術スタック

- **Framework:** Playwright
- **BDD Layer:** playwright-bdd (Gherkin)
- **Target Browsers:** Chromium, Mobile Chrome

## ディレクトリ構造

```
apps/tests/e2e/
├── features/             # Gherkin仕様 (*.feature)
├── steps/                # Step Definitions (*.ts)
└── .features-gen/        # 自動生成されたPlaywrightテスト
```

## 前提条件

### 1. MongoDB と Redis の起動

プロジェクトルートで以下を実行：

```bash
docker compose up -d
```

### 2. API サーバーの起動

別のターミナルで、APIサーバーを起動してください：

```bash
cd ~/ws/kvell/apps/api && PYTHONPATH=src uv run uvicorn app.main:app --port 8000 --reload
```

APIサーバーは `http://localhost:8000` で起動します。

## テストの実行方法

### 通常実行（ヘッドレス）

```bash
npm run test
```

### ブラウザを表示して実行

```bash
npm run test:headed
```

### デバッグモード

```bash
npm run test:debug
```

### UI モード（対話的）

```bash
npm run test:ui
```

## 実装ワークフロー

1. **Define:** `features/*.feature` にGherkinシナリオを記述(人間)
2. **Implement:** `steps/*.ts` にStep Definitionsを実装(AI)
3. **Generate:** `npm run bddgen` でテストコードを生成(自動生成)
4. **Run:** `npm test` でテストを実行

## Data Management

- **Given句:** MongoDB直接操作でテストデータを投入
- **When句:** Playwright (page) でブラウザ操作
- **Then句:** `data-testid` ベースでアサーション

## Test ID ポリシー

すべてのE2E操作・検証対象要素には `data-testid` 属性を必須とします。

命名規則: `[context]-[action/role]-[element]` (kebab-case)

例:
- `health-echo-input`
- `health-fetch-button`
- `health-message-display`

詳細は `.prompts/31_E2E.md` を参照してください。

## トラブルシューティング

### テストが "Connection refused" エラーで失敗する場合

1. MongoDBが起動しているか確認: `docker compose ps`
2. APIサーバーが起動しているか確認: `http://localhost:8000/docs` にアクセス
3. Webサーバーが起動しているか確認: `http://localhost:5173` にアクセス

### BDD生成がエラーになる場合

```bash
# Step definitionsのシンタックスエラーをチェック
npm run bddgen
```
