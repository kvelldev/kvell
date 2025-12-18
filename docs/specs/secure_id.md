# Secure User Identification Specification

## 1. Overview
ユーザーのプライバシー保護と、システム内での同一性追跡を両立させるためのID生成ロジック仕様。
本システムではユーザーログイン機能を持たないため、IPアドレス等をSeedとしたハッシュ値をユーザーIDとして利用する。

## 2. Security Requirements

### 2.1. Irreversibility (不可逆性)
*   **Method:** HMAC-SHA256
*   **Objective:** 生成されたIDから、元のIPアドレスや個人情報を逆引きできないこと。
*   **Counter-measure:** レインボーテーブル攻撃を防ぐため、システム固有の `SECRET_KEY` を使用する。

### 2.2. Determinism (決定性)
*   **Constraint:** 同じSeed（IPアドレス）と `SECRET_KEY` からは、常に **完全に同一のID** が生成されなければならない。
*   **Reason:** これが保証されないと、ユーザーがページをリロードするたびに「別人」と判定されてしまう。

### 2.3. System Integrity
*   システムは起動時に `SECRET_KEY` の強度を検証しなければならない。
*   32文字未満の場合は、セキュリティリスクが高いためシステムを起動させてはならない（Panic）。

## 3. Specifications

### 3.1. Interface
`src/app/domain/service/security.py`

```python
class SecurityService:
    def __init__(self, secret_key: str):
        # Validation on initialization
        pass

    def generate_secure_id(self, seed: str) -> str:
        pass
```

### 3.2. Detailed Behavior

| Input (Seed) | Condition | Output | Note |
| :--- | :--- | :--- | :--- |
| Any valid string | Normal | `HMAC-SHA256(key, seed).hexdigest()` | 64 chars hex string |
| Empty string `""` | Normal | `ValueError` | 無効なSeedは弾く |
| `None` | N/A | `AttributeError/TypeError` | Pythonの型ヒントで防ぐ |

### 3.3. Configuration

*   **Key Source:** Environment Variable `SERVER_SECRET_KEY`
*   **Injection:** Adapter Layer (`main.py` composition root) reads env and injects into Domain Service.

## 4. Error Handling

*   **Invalid Configuration:** `ValueError: SERVER_SECRET_KEY must be at least 32 characters long.`
*   **Invalid Input:** `ValueError: Seed cannot be empty.`
