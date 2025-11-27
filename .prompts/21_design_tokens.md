# Project Kvell: Design Tokens & SSOT Guidelines (Style Dictionary)

F/Eのタスクでは本ファイルを参照してください。

## 1. Purpose & SSOT
Kvellの視覚的アイデンティティ（"Night & Bonfire"）は、全て **JSON形式のDesign Tokens** として管理します。
これがSSOTです。
AIエージェントは、UI実装時にハードコード（HEX値など）を禁止し、必ずこのトークン定義から生成されたクラス名を使用しなければなりません。

## 2. Token Definition (tokens.json)

`design_token/tokens.json` を参照してください。
Tailwindのデフォルト値（Spacing, FontSize等）はそのまま使用しますが、以下の要素はKvell独自の世界観に合わせて拡張します。

* **Color:** Night & Fire パレット
* **Shadow:** Kvellはダークモードが基本のため、"Glow"（発光）としての定義
* **Radius:** カードやボタンの形状
* **Animation:** 炎の揺らぎ


## 3. Implementation Rules

### 1. Shadow is Light
Kvellにおいて `shadow` は「影を落とす」ものではなく、**「自らが発光している（Glow）」** 表現として使用してください。
* ❌ `shadow-lg` (デフォルトの黒い影) -> 禁止（背景が黒なので見えない/汚くなる）
* ✅ `shadow-glow-md` (オレンジ色の発光) -> 推奨

### 2. Semantic Naming Only
マジックナンバーの使用を禁止します。
必ず `tokens.json` で定義された意味のある名前（Semantic Name）を使用してください。

### 3. Typography
* **Weight:** 夜の静けさを表現するため、`Light (300)` 〜 `Regular (400)` を基本とします。

