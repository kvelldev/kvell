# Backend Architecture Rules (FastAPI + Clean Architecture)

## 0. Context & User Story

以下のルールとコード例は、"Project Kvell"におけるコア機能である「薪をくべる」機能を実装するケースを想定しています。


> User Story:
As a ユーザー
I want to 気に入った投稿（Spark）に対して「薪」ボタンを押す
So that その話題を盛り上げることができる（システム的には薪カウントが増え、一定数を超えると焚き火(Bonfire)になる）


実装の際は、常にこの「ユーザーにとっての価値」と「データの流れ」を意識してください。

## 1. Project Directory Structure (The Map)

コーディングを開始する前に、現在のディレクトリ構成を確認した上で、下記のようにファイル作成計画を立ててください。

```text
src/
├── domain/                 # 最も内側のレイヤー（外部依存なし）
│   ├── model/              # Entities (Pydantic/DataClass)
│   │   ├── spark.py        # 種火 (Entity)
│   │   └── bonfire.py      # 焚き火 (Entity)
│   ├── service/            # Domain Services (複数Entityに跨るロジック)
│   │   └── ignition.py     # 焚き火化判定ロジック
│   └── repository/         # Repository Interfaces (Output Ports)
│       ├── spark_repo.py   # class ISparkRepository(ABC)
│       └── bonfire_repo.py
├── usecase/                # アプリケーション固有のビジネスルール
│   ├── add_fuel/           # 機能単位でディレクトリを切る
│   │   ├── interface.py    # UseCase Interface (Input Ports)
│   │   └── interactor.py   # UseCase Implementation
│   └── dto/                # Data Transfer Objects
├── driver_adapter/                # Interface Adapters
│   ├── controller/         # FastAPI Routers
│   │   └── add_fuel_router.py
│   └── presenter/          # Response formatting (Optional)
├── driven_adapter/                  # Frameworks & Drivers (外部依存あり)
│   ├── repository/         # Repository Implementations
│   │   ├── redis_spark_repo.py # カウント処理はRedis推奨
│   │   └── sql_bonfire_repo.py
│   └── db/
└── main.py                 # DI Configuration & App Entrypoint
```



## 2. Architecture Layers & Dependency Rule

Clean Architectureを採用します。
各レイヤーの説明を下記に記載します。

### Layers

#### The Core
ビジネスロジックが存在する聖域。外部（DB, Web）のことを一切知らず、依存もしない。

1.  **Domain (domain/model, domain/service)**
    * **Entity:** コアビジネスルール。他の何にも依存しない。
    * **Domain Service:** 複数のEntityに跨る純粋なドメインルール。
2.  **Application (usecase/interactor)**
    * **UseCase:** ビジネスロジックの実装。EntityとRepository Interfaceにのみ依存する。

#### Ports (Interfaces)
Coreと外界を繋ぐ契約。**全てCoreパッケージ内に定義される。**

3.  **Input Port (usecase/interface)**
    * Coreが「外部から何をされたいか」を定義したInterface。
    * UseCaseがこれを実装(`implements`)する。
4.  **Output Port (domain/repository)**
    * Coreが「外部に何をしてほしいか」を定義したInterface。
    * UseCaseがこれを利用(`uses`)する。

#### Adapters (Outer World)
Coreを具体的な技術（Web, SQL, Redis）に適合させる変換層。

5.  **Driving Adapter**
    * **Controller:** HTTPリクエストを受け取り、Input Portを呼び出す。
6.  **Driven Adapter**
    * **Repository** Output Portを実装し、具体的なインフラ操作(DB, Redis等)を行う。


### Dependency Rule

**Adapters -> Ports (in Core)**
すべてのアダプターは、Core内で定義されたPortに依存します。
* Driving Adapterは Input Port を呼ぶ。
* Driven Adapterは Output Port を実装する。
* **CoreがAdapterに依存することは絶対にない。**

## 3. Contract-Driven Development

AIは実装コードを書く前に、必ず **「全てのレイヤー間のインターフェース（契約）」** を定義し、コンパイル（型チェック）が通る状態にしてください。

**重要**: 各種シグネチャは`01_ubiquitous.md`にあるユビキタス言語を参考に命名してください。

### Coding Flow

以下の順序でコードを生成・提示してください。

1. Define Contracts (The "What")
    - Entities
    - Output Ports
    - Input Ports
    - Input/Output DTOs
2. Wait for Review (※思考プロセス内での自己レビュー、またはユーザー確認)
3. Implement Details (The "How")
    - UseCase Implementation
    - Adapter Implementation

## 4. Implementation Example

下記にFew-shot Promptとして実装例を示します。

### Step 1: Define Contracts

```python
# 1. Entities (domain/model/spark.py)
from pydantic import BaseModel
from datetime import datetime

class Spark(BaseModel):
    """種火: ユーザーの投稿。燃料(fuel_count)を持つ。"""
    id: str
    content: str
    fuel_count: int = 0

class Bonfire(BaseModel):
    """焚き火: Sparkが成長してスレになった状態"""
    id: str
    root_spark_id: str
    ignited_at: datetime

# 2. Domain Service (domain/service/ignition.py)
class IgnitionService:
    THRESHOLD = 50
    
    @staticmethod
    def should_ignite(spark: Spark) -> bool:
        """Sparkが焚き火になるべきか判定する"""
        return spark.fuel_count >= IgnitionService.THRESHOLD

# 3. Repository Interface (domain/repository/spark_repo.py)
from abc import ABC, abstractmethod
from domain.model.spark import Spark

class ISparkRepository(ABC):
    @abstractmethod
    async def add_fuel(self, spark_id: str) -> Spark:
        """
        指定された種火に薪をくべる（カウントアップ）。
        実装はRedisのINCR等を想定。ロック待ちを発生させないこと。
        """
        pass

class IBonfireRepository(ABC):
    @abstractmethod
    async def save(self, bonfire: Bonfire) -> None:
        pass

# 4. UseCase Input Port (usecase/add_fuel/interface.py)
from abc import ABC, abstractmethod
from usecase.dto.add_fuel_dto import AddFuelInput

class IAddFuelUseCase(ABC):
    @abstractmethod
    async def add_fuel(self, input_data: AddFuelInput) -> None:
        """薪をくべるビジネスロジックの契約"""
        pass
```


### Step 2: Implement Details

```python
# 5. UseCase Implementation (usecase/add_fuel/interactor.py)
from domain.repository.spark_repo import ISparkRepository
from domain.repository.bonfire_repo import IBonfireRepository
from domain.service.ignition import IgnitionService
from usecase.add_fuel.interface import IAddFuelUseCase
from usecase.dto.add_fuel_dto import AddFuelInput
# ... imports

class AddFuelInteractor(IAddFuelUseCase):
    def __init__(
        self, 
        spark_repo: ISparkRepository,
        bonfire_repo: IBonfireRepository
    ):
        self.spark_repo = spark_repo
        self.bonfire_repo = bonfire_repo

    async def add_fuel(self, input_data: AddFuelInput) -> None:
        # 1. 薪をくべる
        spark = await self.spark_repo.add_fuel(input_data.spark_id)
        
        # 2. 焚き火化判定 (Domain Service)
        # ドメインルールに基づき、焚き火に昇格させるか判断
        if IgnitionService.should_ignite(spark):
            new_bonfire = Bonfire(
                id="...", 
                root_spark_id=spark.id, 
                ignited_at=now()
            )
            await self.bonfire_repo.save(new_bonfire)
```

### Step 3: Adapter (Controller)

```python
# 6. Controller (adapter/controller/add_fuel_router.py)
from fastapi import APIRouter, Depends
from usecase.add_fuel.interface import IAddFuelUseCase
from usecase.dto.add_fuel_dto import AddFuelInput

router = APIRouter()

@router.post("/add_fuel")
async def add_fuel(
    input_data: AddFuelInput,
    usecase: IAddFuelUseCase = Depends(get_add_fuel_usecase) # DI
):
    await usecase.add_fuel(input_data)
```

## 5. YAGNI & Shortcut Rules

複雑なビジネスロジックを持たない単純なCRUD操作（例: お知らせ一覧の取得）については、UseCase層の作成を省略し、ControllerからRepositoryを直接呼び出すことを許可します。

ただし、以下の条件を厳守してください:

- **Interfaceの使用は必須**: Controllerは `SQLNewsRepository` ではなく `INewsRepository` (Interface) に依存すること。
- **ディレクトリ構造**: 省略する場合も `domain/repository` にInterfaceを置くこと。
