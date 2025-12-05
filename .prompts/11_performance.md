# Project Kvell: Performance & Testing Guidelines

B/Eのテスト実装タスクでは本ドキュメントを参照してください。

## 1. Capacity Planning & Metrics

本プロジェクトのキャパシティ計画は、**Base DAU** を唯一の変数として算出する。
全てのメトリクスは、DAUに対する係数（Conversion Rate / Action Rate）によって定義される。

### A. Base Assumptions (Variables)

| Variable | Value | Description |
| :--- | :--- | :--- |
| **Base DAU** | **50** | 想定する1日あたりのアクティブユーザー数 |
| **Post Rate** | 10% | 投稿を行うユーザーの割合 (ROM専率 90%) |
| **Posts / User** | 2.0 | アクティブユーザー1人あたりの平均投稿数/日 |
| **Ignition Rate** | 20% | 投稿された種火が焚き火化する確率 |
| **Constellation Rate** | 10% | 焚き火が星座（殿堂入り）化する確率 |
| **Fuels / Spark** | 20 | 1つの種火に投下される平均薪数 |

### B. Calculated Metrics (Daily)

上記係数に基づき、1日あたりに生成されるデータ量を算出する。

| Metric | Formula | Value (DAU=50) | Description |
| :--- | :--- | :--- | :--- |
| **Post Users** | `DAU * Post Rate` | **5** | 実際に種火を投稿する人数 |
| **Sparks** (種火) | `Post Users * Posts/User` | **10** | 1日に生まれる種火の総数 |
| **Bonfires** (焚き火) | `Sparks * Ignition Rate` | **2** | 1日に発生する祭りの数 |
| **Constellations** (星座) | `Bonfires * Constellation Rate` | **0.2** | 1日にアーカイブされる伝説の数 |
| **Fuels** (薪/Action) | `Sparks * Fuels/Spark` | **200** | 1日に発生する書き込み(更新)アクション数 |

### C. Stress Scenarios (The "Buzz" Moment)

負荷試験で保証すべき「瞬間最大風速」の定義。
DAUの規模にかかわらず、**「全ユーザーが同時に集合する」** シチュエーションを前提とする。

| Scenario Metric | Formula | Value (DAU=50) | Description |
| :--- | :--- | :--- | :--- |
| **Max CCU** | `DAU * 100%` | **50** | 全員同時接続 (推しのTV出演時など) |
| **Peak Write RPS** | `Max CCU * 1 req/sec` | **50 req/sec** | 全員が秒間1回薪をくべる状態 |
| **Peak Read RPS** | `Max CCU * 2 req/sec` | **100 req/sec** | 全員が秒間2回ポーリングする状態 |

---

## 2. Load Testing Strategy (k6)

機能テスト（Pytest）とは分離し、上記「Stress Scenarios」を満たせるかを検証する。

### A. Test Scenarios
1.  **Smoke Test:**
    * **負荷:** 1 VU (Minimal)
    * **目的:** エラー率 0% であることの確認。
2.  **Spike Test (最重要):**
    * **負荷:** 0 VU -> `Max CCU` (in 10s) -> Stay -> 0
    * **目的:** Redis/DBコネクションプールの枯渇、オートスケールの追従性確認。
3.  **Soak Test:**
    * **負荷:** `Max CCU * 20%` (Average Load), Duration: 1h
    * **目的:** メモリリーク、長時間稼働時のレイテンシ悪化の検知。

---

## 3. Seeding Strategy (Data Preparation)

シーディングデータ量もマジックナンバーを使用せず、**「想定運用期間」** に基づいて算出する。
これにより、フェーズに応じた適切な「DBの汚れ具合（インデックス負荷）」を再現する。

### A. Seeding Variables

| Variable | Value | Description |
| :--- | :--- | :--- |
| **Operation Years** | **3** | 何年運用した状態をシミュレートするか |
| **Days** | 1095 | `Operation Years * 365` |

### B. Target Data Volume

k6実行前にPythonスクリプトにて投入するデータ量。

| Data Type | Formula | Value (Target) | Role in Testing |
| :--- | :--- | :--- | :--- |
| **Past Sparks** (Trash) | `Sparks/Day * Days` | **10,950** | **[Noise]** インデックス性能（除外性能）の検証用重り。95%以上は期限切れデータとする。 |
| **Constellations** (Asset) | `Constellations/Day * Days` | **219** | **[Asset]** 過去ログ一覧取得のパフォーマンス検証用。 |
| **Active Sparks** (Target) | `Sparks/Day * 0.5` | **5** | **[Target]** 負荷試験時の攻撃対象（Write先）。内訳想定: 4つは通常の種火、1つは燃え上がっている焚き火とする。|

### C. Implementation Notes
* **Consistency:** MongoDBにSparkを作成する際は、必ずRedisのCounter (`spark:{id}:fuel`) も初期化すること。
* **Tooling:** `pymongo` (Bulk Insert) と `redis-py` (Pipeline) を使用し、テスト開始前に高速にセットアップを行う。
