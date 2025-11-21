
# Pull Request Generation Rules

実装完了後、以下のフォーマットでPRの説明文(Description)を作成してください。

## PR Title
[Type] PBIタイトル (e.g., [Feat] 薪投げ機能の実装)

## Description Format

### 1. What (PBI Link & Summary)
- 実装した機能の概要と、対応するIssue/PBIへのリンク

### 2. Architecture Check (Self-Review)
- [ ] **Layer Isolation**: UseCaseがInfraに依存していないことを確認しましたか？
- [ ] **Dependency Rule**: 依存方向は内側に向かっていますか？
- [ ] **Separation**: (FE) ロジックはCustom Hookに分離されていますか？

### 3. Verification (Test Proof)
テストの実行結果ログをここに貼り付けてください。
```text
(Paste pytest or jest output here)
passed: 5, failed: 0
```

