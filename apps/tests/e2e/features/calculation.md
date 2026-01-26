# Bonfire Threshold Calculation Logic

## Overview

焚き火（Bonfire）への昇格閾値を、コミュニティの活性度（DAU）に応じて動的に調整するロジックの定義。
「昨日のテレビ出演でバズった翌日、閾値が上がりすぎて誰も昇格できない」というような現象を防ぐため、**7日間移動平均**を採用する。

## Architecture
- **Source of Truth:** Redis (Key: `config:threshold:bonfire_uu`)
- **Calculator:** 日次バッチ
- **Consumer:** Backend API (昇格判定時)

## 1. Calculation Algorithm (Batch)
バッチは毎日深夜（例: 04:00 JST）に実行し、以下のロジックでRedisの値を更新する。

### Formula
$$
Threshold = Clamp( \lfloor Average(DAU_{last7days}) \times Ratio \rfloor, Min, Max )
$$

### Parameters
| Parameter | Value | Description |
| :--- | :--- | :--- |
| **Ratio (係数)** | `0.05` (5%) | DAUの何%が参加すれば「盛り上がっている」とみなすか |
| **Min Cap (安全弁・下限)** | `10` | 過疎日でも、最低これだけの人数が集まらないと焚き火にしない（自演防止） |
| **Max Cap (安全弁・上限)** | `50` | どんなにDAUが増えても、これ以上ハードルを上げない（参加障壁の維持） |

### Example
- **Case A: 平常時**
    - 7日間平均DAU: 300
    - 計算値: 300 * 0.05 = 15
    - **Result:** `15` (Min < 15 < Max なのでそのまま)

- **Case B: 過疎時**
    - 7日間平均DAU: 100
    - 計算値: 100 * 0.05 = 5
    - **Result:** `10` (Min Cap適用)

- **Case C: 繁忙時**
    - 7日間平均DAU: 2000
    - 計算値: 2000 * 0.05 = 100
    - **Result:** `50` (Max Cap適用)

## 2. Data Structure (Redis)
- **Key:** `config:threshold:bonfire_uu`
- **Value:** `Integer` (例: "15")
- **TTL:** 25時間 (バッチ失敗時に古い値が残りすぎないよう、しかし多少の重複期間は持たせる)

## 3. Fallback Strategy (Application Side)
アプリケーション側でRedisから値を取得できない場合（Connection Error / Key Missing）、以下の定数をデフォルトとして使用する。

```python
# fallback_config.py
DEFAULT_BONFIRE_THRESHOLD_UU = 10
```

## 4. kindlingへの昇格条件は固定値

Kindling（中火）の昇格条件は、DAUに関わらず **固定値（Default: 3 UU）** とする。

- **Reason 1 (Predictability):** ユーザーに対し「3人の共感を得れば、投稿は必ず生き残る」という一貫した体験を提供するため。
- **Reason 2 (Social Proof):** 「3人」という数字は、会話が1対1の閉じた関係から、コミュニティの話題へと開かれたことを示す最小単位であるため。

