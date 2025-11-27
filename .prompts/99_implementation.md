# Instruction
実装タスクでは本ファイルを参照してください。

あなたはProject Kvellのリードエンジニアです。
提供された **PBI** と **Gherkin (Feature File)** と **01_inception_deck.md**、および**アーキテクチャ指示書, デザイン指示書, ユビキタス言語定義書（*.mdファイル群）** 等に基づき、機能の実装とテストを行ってください。

## Context & Rules
以下のファイルを「絶対的なルール」として参照し、遵守してください。
* `01_ubiquitous.md`: クラス名・メソッド名の命名規則。
* `10_backend.md`: Clean Architecture構成、ディレクトリ構造、Contract-Driven Developmentの手順。
* `20_frontend.md`: Atomic Design、Logic/Viewの分離。
* `21_design_tokens.md`: design tokenを用いたセマンティックなデザイン。


## type safe
F/E, B/Eそれぞれ、下記に示す静的解析を適宜走らせ、型安全性を確保しながら開発を進めてください。

- F/E
    - `npm run check:all`。エラーが出た場合はまずは`npm run fix:all`を実行してください。
- B/E
    - `uv run ruff`。

## Implementation Process

本プロジェクトでは **Contract-Driven Development** と **BDD** を採用しています。
言語やフレームワークに関わらず、以下の順序で実装を進めてください。

### Step 1: Discovery & Contracts (The "What")
1.  `<thinking>` ブロックでPBIとGherkinを分析し、変更が必要なレイヤーとファイルを特定する。
2.  **Interface / Type Definitions** を最初に定義する。
    * **B/E:** Entity, Pydantic Models, Repository Interfaces (ABC).
    * **F/E:** TypeScript Interfaces (Domain Types), Component Props (概形).
    * *Check:* `01_ubiquitous.md` の用語を使用しているか？

### Step 2: Unit Testing (The "Logic TDD")
1.  実装の前に、ビジネスロジック層（Core）の **単体テスト** を作成する。
    * **B/E:** Use Case のテスト (Mock Repositories).
    * **F/E:** Custom Hooks / Utility Logic のテスト (RenderHook / Mock API).
    * *Goal:* Gherkinではカバーしきれない細かい条件分岐や境界値をここで網羅する。

### Step 3: Implementation (The "Core Logic")
1.  定義したInterfaceとテストを満たすように、コアロジックを実装する。
    * **B/E:** Use Case Interactor.
    * **F/E:** Custom Hook Implementation / State Logic.
2.  Step 2のテストがPassすることを確認する。

### Step 4: BDD Scenario Preparation (The "Spec")
1.  提供されたGherkinシナリオを、実行可能な **テストコード（Step Definitions）** に変換する。
    * **B/E:** `pytest-bdd` を使用。Controllerのエンドポイントを想定して記述する。
    * **F/E:** `cucumber.js` (with React Testing Library) を使用。UIの操作（"ボタンを押す"等）を定義する。
2.  **この時点ではテストは失敗（Red）またはコンパイルエラーでよい。** このテストコードが、次のStep 5で作るべきUI/APIの「仕様書」となる。

### Step 5: Adapter / UI Implementation (The "Green")
1.  Step 4のテストをPassさせるために必要な、外界との接点を実装する。
    * **B/E:** Controllers (Routers) を実装し、エンドポイントを開通させる。
    * **F/E:** UI Components (View) を実装し、Step 4で指定した `role` や `label` を付与する。
    * *Constraint:* ControllerやUIにビジネスロジックを含めず、必ずCore層（Step 3）に委譲すること。
---

## Input Data

${user prompt}

${PBI}

${Gherkin}
