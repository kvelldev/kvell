
# BDD (Behavior Driven Development) Workflow

機能実装は以下のプロセスを厳守してください。いきなり実装コードを書くことを禁止します。

## Phase 1: Scenario Definition (Human Review Required)
PBIを受け取ったら、まずはGherkin形式 (`.feature`) でシナリオを作成し、ユーザーのレビューを受けてください。

### Example (.feature)
```gherkin
Feature: 薪をくべる (Add Fuel)
  As a 参加者
  I want to 投稿に対して「薪」ボタンを押す
  So that その話題を盛り上げることができる

  Scenario: 薪をくべるとカウントが増える
    Given "UserA" が "Post1" を閲覧している
    When "UserA" が "薪ボタン" を押す
    Then "Post1" の薪カウントが 1 増える
    And "UserA" には「火の粉が舞う」エフェクトが表示される
```

## Phase 2: Red (Write Test)

承認されたGherkinシナリオを満たすテストコードを書いてください。

  - Backend: `pytest` / `pytest-bdd`
  - Frontend: `Jest` / `Testing Library`

## Phase 3: Green (Implementation)

テストがPassするように実装コードを書いてください。

```

