
# Project Kvell: Backend Architecture & Implementation Guidelines

B/Eのタスクでは本ファイルを参照してください。

## 1. Purpose & Scope
このドキュメントは、Project Kvellのバックエンド開発における **「不変の憲法」** です。
AIエージェントは、個別のPBI（User Story）を実装する際、必ずこのガイドラインに準拠しなければなりません。
ここに記載されたルールは、個別の指示がない限り、バックエンドの全ての機能実装に適用されます。

## 2. Tech Stack (Strict)
以下の技術スタック以外の使用を禁止します。

* **Language:** Python 3.11+
* **Framework:** FastAPI (Async native)
* **Database:** MongoDB (via Motor or Beanie) - *No RDBMS/SQL.*
* **KVS:** Redis (via redis-py) - For counters, rate limiting, and ephemeral states.
* **Testing:** Pytest

## 3. Architecture Pattern: Clean Architecture
我々は **Clean Architecture** を採用します。依存性の方向を絶対に遵守してください。

### Layers & Dependency
1.  **Domain (Inner)**: `src/domain/`
    * 外部ライブラリ（FastAP等）に依存してはならない。Pydanticのみ許可。
    * **Entities (`model/`)**: ドメインロジックとデータをカプセル化する。
    * **Output Ports (`repository/`)**: データの入出力インターフェース。
    * **Domain Services (`service/`)**: 複数のEntityにまたがるロジック。
2.  **UseCase (Middle)**: `src/usecase/`
    * Domain層とUseCase層の定義のみに依存する。
    * **Input Ports (`interface.py`)**: UseCaseのインターフェース。
    * **Interactors (`interactor.py`)**: アプリケーション固有のビジネスルール実装。
3.  **Adapter (Outer)**: `src/adapter/`
    * 詳細な技術実装（FastAPI, DB接続など）。
    * **Entrypoints (`entrypoints/`)**: Driving Adapters (例: FastAPI Router)。
    * **Gateways (`gateways/`)**: Driven Adapters (例: MongoDB Repository 実装)。

### Dependency Inversion Principle

DIPを厳密に遵守してください。
依存の方向は必ず**Outer->Middle->Inner**であり、内側の層はそれより外の層のことを関知してはいけません。

* ❌ Controller (`adapter`) imports Interactor Implementation (`usecase`) -> **Bad**
* ✅ Controller (`adapter`) imports Input Port (`usecase/interface`) -> **Good**
* ❌ Interactor (`usecase`) imports Repository Implementation (`adapter`) -> **Bad**
* ✅ Interactor (`usecase`) imports Repository Interface (`domain`) -> **Good**

## 4. Implementation Principles

### A. Concurrency & Scalability
Kvellは「瞬間的な熱狂」を扱うため、アクセス集中時の整合性が重要です。
* **Atomic Operations:** カウンターやステータス変更は、必ずRedisのAtomic操作（`INCR`, `SETNX`等）またはMongoDBのアトミック更新演算子（`$inc`, `$set`）を使用すること。
* **Read-Modify-Write 禁止:** データをPythonメモリ上に取得して計算し、再度保存する処理は、Race Conditionの温床になるため、高負荷が予想される箇所では禁止します。

### B. Domain Richness
コードは仕様書です。無機質なSetter/Getterではなく、意味のあるメソッド名を使用してください。
* `set_status(Status.BURNING)` ではなく -> `ignite()`
* **Ubiquitous Language:** 変数名やクラス名は、必ず`01_ubiquitous.md`にて定義されたユビキタス言語（`Spark`, `Bonfire`, `Ash`, `Fuel` 等）に従うこと。

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
├── domain/
│   ├── model/              # e.g., spark.py
│   ├── repository/         # e.g., spark_repository.py (Output Port)
│   └── service/            # e.g., ignition_service.py
├── usecase/
│   ├── {feature_name}/     # e.g., add_fuel/
│   │   ├── interface.py    # Input Port
│   │   └── interactor.py   # Implementation
│   └── dto/                # Data Transfer Objects
├── adapter/
│   ├── entrypoints/        # FastAPI Routers
│   └── gateways/           # DB Implementations (Mongo/Redis)
└── main.py
```

-----

## 7\. Reference Implementation (Few-shot Example)

以下は「薪をくべる」機能の実装例です。
**注意: これはあくまで構造のサンプルです。実際のタスクは別途提供されるPBIに従ってください。**

### [Contract] Domain & Interface

```python
# src/domain/repository/spark_repository.py
from abc import ABC, abstractmethod
from domain.model.spark import Spark

class ISparkRepository(ABC):
    @abstractmethod
    async def add_fuel_atomic(self, spark_id: str) -> Spark:
        """Redis/DB上でアトミックに燃料を追加し、更新後のEntityを返す"""
        pass

# src/usecase/add_fuel/interface.py
from abc import ABC, abstractmethod
from usecase.dto.fuel_dto import AddFuelInput

class IAddFuelUseCase(ABC):
    @abstractmethod
    async def execute(self, input_data: AddFuelInput) -> None:
        pass
```

### [Logic] UseCase Implementation

```python
# src/usecase/add_fuel/interactor.py
class AddFuelInteractor(IAddFuelUseCase):
    def __init__(self, spark_repo: ISparkRepository, ignition_service: IgnitionService):
        self.spark_repo = spark_repo
        self.ignition_service = ignition_service

    async def execute(self, input_data: AddFuelInput) -> None:
        # 1. Atomic Update in Gateway
        updated_spark = await self.spark_repo.add_fuel_atomic(input_data.spark_id)

        # 2. Domain Service Check
        if self.ignition_service.should_ignite(updated_spark):
            # ... Ignition logic
            pass
```

### [Adapter] Gateway Implementation

```python
# src/adapter/gateways/redis_spark_repository.py
class RedisSparkRepository(ISparkRepository):
    async def add_fuel_atomic(self, spark_id: str) -> Spark:
        # Use Redis INCR for thread-safe counting
        new_count = await self.redis.incr(f"spark:{spark_id}:fuel")
        # ... Map to Entity and return
```

