
# Backend Architecture & Implementation Guidelines

B/Eのタスクでは本ファイルを参照してください。

## 1. Purpose & Scope

このドキュメントは、本プロジェクトのバックエンド開発における **「不変の憲法」** です。
AIエージェントはこのガイドラインに準拠し、Python/FastAPIの柔軟性が招く「無秩序」を徹底的に排除しなければなりません。
本ドキュメントは「構造と責務」を定義します。具体的なAPI定義やビジネスルールは、個別のPBI（User Story）に従ってください。


## 2. Tech Stack (Strict)
以下の技術スタック以外の使用を禁止します。

* **Language:** Python 3.11+
* **Framework:** FastAPI (Async native)
* **Package Manager:** uv
* **Database:** MongoDB (via Motor or Beanie)
* **KVS:** Redis (via redis-py)
* **Observability:** AWS CloudWatch (via JSON stdout), Sentry
* **Testing:** Pytest

## 3. Architecture Pattern: Clean Architecture
**関心の分離**を徹底します。
「API/Infraの都合 (Adapter)」と「ビジネスロジック (UseCase)」と「データ定義 (Domain)」を明確に分割します。

### Layers & Dependency

依存の方向は **Adapter -> UseCase -> Domain** です。
円の中心に向かってのみ依存します。外側の変更が内側に影響を与えてはいけません。

1.  **Domain (Inner)**: `src/domain/`
    * アプリケーションのコアデータ型定義と、リポジトリのインターフェース定義。
    * FastAPIやDBドライバに依存してはならない。純粋なPythonクラスのみ。
    * **Entities**: ドメインモデル（例: `User`, `Order`）。
    * **Repository Interfaces**: データアクセスの抽象定義 (例: `IUserRepository`)。
    * **Domain Services**: 複数のEntityにまたがる純粋な計算ロジック。
2.  **UseCase (Middle)**: `src/usecase/`
    * アプリケーションのビジネスロジック。
    * **DTO (Data Transfer Object):** 入出力データ構造の定義には **Pydantic (`BaseModel`)** を使用し、型安全性とバリデーションを担保する。
    * **feature folder(`{feature name}/`)**:
    * **feature folder(`{feature name}/`)**: 
        * **Input Ports (`interface.py`)**: UseCaseのポート。
        * **Interactors (`interactor.py`)**: 機能固有のビジネスルール実装。
    * **ports(`ports/`)**: 機能横断(ユースケース全体)で使用する機能のポート(例: `ILogger`)。
3.  **Adapter (Outer)**: `src/adapter/`
    * 外部との通信の実装詳細。
    * **Entrypoints (`entrypoints/`)**: Driving Adapters (例: FastAPI Router)。
    * **Gateways (`gateways/`)**: Driven Adapters (例: MongoDB Repository 実装)。
    * **Infra**: ロガー等の実装 (`JsonLogger`)。

### Dependency Inversion Principle

DIPを厳密に遵守してください。
依存の方向は必ず**Outer->Middle->Inner**であり、内側の層はそれより外の層のことを関知してはいけません。

* ❌ Controller (`adapter`) imports Interactor Implementation (`usecase`) -> **Bad**
* ✅ Controller (`adapter`) imports Input Port (`usecase/interface`) -> **Good**
* ❌ Interactor (`usecase`) imports Repository Implementation (`adapter`) -> **Bad**
* ✅ Interactor (`usecase`) imports Repository Interface (`domain`) -> **Good**

## 4. Implementation Principles

### A. Concurrency & Scalability
B/E実装では、アクセス集中時の整合性やレースコンディションの考慮が重要です。
* **Atomic Operations:** カウンターやステータス変更は、必ずRedisのAtomic操作（`INCR`, `SETNX`等）またはMongoDBのアトミック更新演算子（`$inc`, `$set`）を使用すること。
* **Read-Modify-Write 禁止:** データをPythonメモリ上に取得して計算し、再度保存する処理は、Race Conditionの温床になるため、高負荷が予想される箇所では禁止します。

### B. Domain Richness

コードは仕様書です。無機質なSetter/Getterではなく、意味のあるメソッド名を使用してください。

* **Ubiquitous Language:** 変数名・ファイル名・クラス名は、必ずプロジェクトで定義されたユビキタス言語に従うこと。
* **Action Naming:** `setStatus(Status.DONE)` ではなく -> **`complete()`, `publish()`** (具体的なビジネスアクション名)

### C. Error Handling Strategy

エラーは「ドメインエラー」と「インフラエラー」を区別し、Adapter層でHTTPステータスへ変換します。

1.  **Throwing:** UseCaseやDomain層では、HTTPステータスコードを意識せず、ビジネス上の意味を持つエラー（`AppError` + `InternalStatusCode`）を送出します。
2.  **Catching:** Adapter層(RouterまたはException Handler)でこれを捕捉し、`INTERNAL_TO_HTTP_MAP` を用いて適切なHTTPレスポンスに変換します。

### D. Log Event Standards

ログはすべて **JSON形式の構造化ログ** とし、トレース可能な **Event ID** を付与します。
テストではログメッセージ（自然言語）ではなく、Event IDが出力されたかを検証します。

* **Bad:** `logger.info("処理を開始しました")`
* **Good:** `logger.info(LOG_EVENTS.PROCESS_STARTED, "Started...", context={"id": 123})`

## 5. Coding Workflow (Contract-Driven)
実装は以下のステップで行うこと。**いきなり実装コードを書かないでください。**

1.  **Step 1: Define Contracts (Interfaces)**
    * Entity, Repository Interface, UseCase Interfaceを定義。
    * ここで「型の整合性」を確認する。
2.  **Step 2: Implementation (Core)**
    * UseCaseの実装（ビジネスロジック）。
3.  **Step 3: Implementation (Adapter)**
    * DB操作の実装、APIエンドポイントの実装。

## 6. Directory Structure (The Map)
ファイル作成時はこの構造に従ってください。

```text
src/
├── domain/                 # Pure Python
│   ├── model/              # Entities (e.g. user.py)
│   ├── repository/         # Repository Interfaces
│   ├── service/            # Domain Services
│   └── constants.py        # InternalStatusCodes
├── usecase/                # Business Logic
│   ├── {feature}/          # e.g. health/
│   │   ├── interactor.py
│   │   └── interface.py    # Interface & Feature-specific DTOs
│   ├── ports/              # e.g. logger.py
│   └── dto/                # Shared DTOs (e.g. Pagination, Common Filters)
├── adapter/                # Implementation Details
│   ├── entrypoints/        # FastAPI Routers
│   ├── gateways/           # DB Implementations (Mongo/Redis)
│   ├── infra/              # Logger impl, Sentry
│   └── constants.py        # HTTP Status Mapping
├── main.py                 # App Entrypoint & DI Wiring
└── tests/
```



## 7. Testing Strategy

各レイヤーの責務分離に基づき、テストの「対象（Unit）」と「モック（Boundary）」を明確に定義します。

### A. Level 1: Domain Unit Testing

  * **Target:** `src/domain/`
  * **Strategy:** 純粋なPythonロジックの検証。外部依存がないためモック不要。

### B. Level 2: UseCase Unit Testing

  * **Target:** `src/usecase/`
  * **Strategy:** ビジネスロジックの検証。
  * **Mocking:** RepositoryやLoggerをモック化（`unittest.mock` や `pytest-mock`）し、Interactorが正しくリポジトリを呼び出し、正しい値を返すかを検証する。DBには接続しない。

### C. Level 3: API Integration Testing

  * **Target:** `src/adapter/entrypoints` (via FastAPI TestClient)
  * **Strategy:** エンドポイントのE2E検証。
  * **Environment:** テスト用DB（コンテナ等）に接続するか、DIコンテナレベルでRepositoryをインメモリ実装に差し替えて実行する。正常系レスポンスと、エラーマッピング（4xx/5xx）が正しいかを検証する。

---


## 8\. Reference Implementation (Few-shot Example)

以下は、汎用的な「ヘルスチェック（System Health Check）」機能の実装例です。
この例は、**レイヤー間の責務分離**、**依存性逆転の原則(DIP)**、および **Pydanticを用いた型契約** の基準となります。

### Step 1: Define Contracts (Domain & Interfaces)

まず、ドメインモデルと、外部リソース（DB等）へのアクセス仕様（Repository Interface）を定義します。

```python
# src/domain/model/health.py
from dataclasses import dataclass
from enum import Enum

class HealthStatus(str, Enum):
    OK = "ok"
    ERROR = "error"

@dataclass
class SystemHealth:
    """Domain Entity: システムの状態"""
    db_status: HealthStatus
    redis_status: HealthStatus
    
    @property
    def is_healthy(self) -> bool:
        return (
            self.db_status == HealthStatus.OK and 
            self.redis_status == HealthStatus.OK
        )

# src/domain/repository/health_repository.py
from abc import ABC, abstractmethod
from domain.model.health import HealthStatus

class IHealthRepository(ABC):
    @abstractmethod
    async def check_db_connection(self) -> HealthStatus:
        """DBへの接続を確認しステータスを返す"""
        pass

    @abstractmethod
    async def check_redis_connection(self) -> HealthStatus:
        """Redisへの接続を確認しステータスを返す"""
        pass

# src/usecase/health/interface.py
from abc import ABC, abstractmethod
from pydantic import BaseModel
from domain.model.health import HealthStatus

class HealthCheckOutput(BaseModel):
    status: HealthStatus
    details: dict[str, HealthStatus]

class IHealthCheckUseCase(ABC):
    @abstractmethod
    async def execute(self) -> HealthCheckOutput:
        pass
```

### Step 2: Implementation (UseCase / Business Logic)

具体的なインフラ技術（Mongo/Redisのドライバ等）は知らず、抽象インターフェースを通じてロジックを記述します。

```python
# src/usecase/health/interactor.py
import asyncio
from domain.repository.health_repository import IHealthRepository
from domain.model.health import SystemHealth, HealthStatus
from usecase.health.interface import IHealthCheckUseCase, HealthCheckOutput

class HealthCheckInteractor(IHealthCheckUseCase):
    def __init__(self, health_repo: IHealthRepository):
        self.health_repo = health_repo

    async def execute(self) -> HealthCheckOutput:
        # 並列で各インフラのチェックを実行
        db_status, redis_status = await asyncio.gather(
            self.health_repo.check_db_connection(),
            self.health_repo.check_redis_connection()
        )

        # ドメインエンティティの生成
        health = SystemHealth(db_status=db_status, redis_status=redis_status)

        # Output DTOへの変換
        return HealthCheckOutput(
            status=HealthStatus.OK if health.is_healthy else HealthStatus.ERROR,
            details={
                "database": health.db_status,
                "redis": health.redis_status
            }
        )
```

### Step 3: Implementation (Adapter / Gateway)

ここで初めて具体的な技術（Motor/Redis-py）が登場します。

```python
# src/adapter/gateways/infra_health_repository.py
from motor.motor_asyncio import AsyncIOMotorClient
from redis.asyncio import Redis
from domain.repository.health_repository import IHealthRepository
from domain.model.health import HealthStatus

class InfraHealthRepository(IHealthRepository):
    def __init__(self, mongo: AsyncIOMotorClient, redis: Redis):
        self.mongo = mongo
        self.redis = redis

    async def check_db_connection(self) -> HealthStatus:
        try:
            # 具体的なPingコマンド
            await self.mongo.admin.command('ping')
            return HealthStatus.OK
        except Exception:
            return HealthStatus.ERROR

    async def check_redis_connection(self) -> HealthStatus:
        try:
            await self.redis.ping()
            return HealthStatus.OK
        except Exception:
            return HealthStatus.ERROR
```

### Step 4: Implementation (Adapter / Entrypoint)

FastAPIのRouter実装です。UseCaseを呼び出し、HTTPレスポンスへ変換します。

```python
# src/adapter/entrypoints/health_router.py
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from usecase.health.interface import IHealthCheckUseCase
from domain.model.health import HealthStatus
from adapter.deps import get_health_check_usecase # DI Provider

router = APIRouter()

@router.get("/health", response_model=None)
async def check_health(
    usecase: IHealthCheckUseCase = Depends(get_health_check_usecase)
):
    output = await usecase.execute()
    
    http_status = status.HTTP_200_OK
    if output.status != HealthStatus.OK:
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return JSONResponse(
        status_code=http_status,
        content=output.model_dump()
    )
```
