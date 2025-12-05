# Project Kvell: Design Tokens & SSOT Guidelines

F/Eのタスク（実装およびレビュー）では本ファイルを参照してください。

## 1\. Purpose & SSOT

Kvellの視覚的アイデンティティ（"Night & Bonfire"）は、全て **JSON形式のDesign Tokens (`design_token/tokens.json`)** をSSOT（信頼できる唯一の情報源）として管理します。

AIエージェントは、UI実装時にHEX値などのハードコードを禁止し、必ず `tailwind.config.js` を通じて生成されたクラス名を使用しなければなりません。

## 2\. The Hybrid Token Strategy (Strict Rule)

Kvellでは、ブランドの統一と開発効率を両立するため、`tailwind.config.js` の設定において以下の**ハイブリッド戦略**を採用しています。
基本的な考え方は、「ブランドイメージに直結するものはsemanticに、汎用的なものはデフォルト値を」です。
実装時はこの挙動を理解し、適切なクラスを選択してください。

### A. Overrides (Root Definition)

**以下のカテゴリは Tailwindのデフォルト値を「無効化（上書き）」しています。**
Kvellの世界観に存在しない色や形状（例: `bg-blue-500`, `shadow-xl`, `rounded-full`）は **使用不可能（コンパイルエラー）** となります。必ず定義されたトークンを使用してください。

  * **Colors:** `bg-night-900`, `text-ember-500` 等
  * **Shadows (Glow):** `shadow-glow-md` 等
  * **Border Radius:** `rounded-card`, `rounded-button`
  * **Opacity:** `opacity-ash` 等

### B. Extends (Theme Extension)

**以下のカテゴリは Tailwindのデフォルト値を「維持」しつつ、カスタム定義を「追加」しています。**
基本的にはカスタム定義（Semantic）を優先しますが、デバッグや汎用的な用途でデフォルト値を使用することも許可されます。

  * **Font Family:** `font-base` (推奨), `font-sans` (Fallback)
  * **Animation:** `animate-flicker` (炎), `animate-spin` (Loading)

### C. Defaults (No Configuration)

**以下のカテゴリは Tailwindのデフォルト値を「そのまま」使用します。**
これらを独自トークン化することは禁止します（例: `p-card-padding` は不要）。

  * **Spacing:** `p-4`, `m-2`, `gap-4`
  * **Sizing:** `w-full`, `h-64`, `max-w-md`
  * **Layout:** `flex`, `grid`, `absolute`, `z-10`
  * **Font Size:** `text-sm`, `text-xl`

-----

## 3\. Implementation Rules

### 1\. Shadow is Light ("Glow")

Kvellにおいて `shadow` は「影を落とす」ものではなく、**「自らが発光している（Glow）」** 表現として使用してください。

  * ❌ `shadow-lg` (デフォルトの黒い影) -\> **存在しません（使用不可）**
  * ✅ `shadow-glow-md` (オレンジ色の発光) -\> **推奨**

### 2\. Radius Strategy

  * **Card:** `rounded-card` (12px) を使用。
  * **Button:** `rounded-button` (9999px / Pill型) を使用。
  * ❌ `rounded-lg`, `rounded-full` -\> **存在しません（使用不可）**

### 3\. Typography & Weight

夜の静寂（Silence）を表現するため、フォントウェイトは細めを基本とします。

  * **Weight:** `font-light (300)` 〜 `font-regular (400)` を基本とする。
  * **Usage:** `font-bold` は、着火した焚き火（Bonfire）のタイトルなど、強い熱量を持つ要素にのみ限定的に使用する。

---

## 4. Workflow for Missing Tokens (Extending the Brand)

実装中に既存のセマンティックトークン（色、アニメーション、形状など）では表現しきれないデザイン要件が発生した場合、以下のフローに従って拡張を行ってください。
**`apps/web/tailwind.config.js` に直接値を書き込むことは禁止します。**

また、セマンティックトークンの拡張を行った場合は必ずユーザーに報告を行ってください。

### Step 1: Update SSOT
`packages/design_token/tokens.json` を編集し、新しいトークンを追加してください。
この際、必ず **`01_ubiquitous.md` (Ubiquitous Language)** を参照し、Kvellの世界観と用語に整合する命名を行ってください。

* **Naming Convention:** `[Concept/Metaphor]-[State/Scale]`
* **Referenced Concepts:** Spark, Bonfire, Fuel, Ignite, Decay, Ash, Ember...

#### Examples
* **Color:**
    * ❌ `"red-500": "#ff0000"` (色名ベースの命名は禁止)
    * ✅ `"magma-500": "#ff0000"` (世界観ベース)
* **Animation:**
    * ❌ `"fade-out": "opacity 0 to 1..."` (機能ベースの命名は禁止)
    * ✅ `"decay": "opacity 0 to 1..."` (ユビキタス言語 `Decay` に基づく命名)
* **Radius/Shape:**
    * ❌ `"circle-large": "50%"`
    * ✅ `"fuel-lump": "50%"` (ユビキタス言語 `Fuel` に基づく命名)

### Step 2: Generate Theme
Design Tokenパッケージのビルドコマンドを実行し、`tailwind.theme.js` を更新してください。

### Step 3: Implementation
更新されたトークンが `tailwind.config.js` 経由で反映され、クラス名（例: `animate-decay`, `text-magma-500`）として利用可能になります。

繰り返しになりますが、`tailwind.config.js`の編集は禁止です。`token.json`から`tailwind.theme.js`へのビルドを通じた間接的な拡張のみを許可しています。

---

## 5\. Coding Example (Do's and Don'ts)

### ✅ Correct Implementation (Hybrid)

「色はトークン（Default不可）、余白はUtility（Default）」のルールが守られている。

```tsx
// 良い例: KvellのトークンとTailwindのUtilityが正しく混ざっている
<div className="bg-night-800 rounded-card shadow-glow-sm p-6 flex flex-col gap-4">
  <h2 className="font-display text-xl text-ember-500 font-normal">
    焚き火のタイトル
  </h2>
  <p className="font-base text-sm text-smoke-100 opacity-ash">
    投稿本文テキスト...
  </p>
</div>
```

### ❌ Incorrect Implementation

#### Case 1: 存在しないクラスの使用

設定ファイルで上書きされているため、以下のクラスは機能しないかエラーになります。

```tsx
// Bad: bg-black, rounded-lg, shadow-xl は無効化されているため使用禁止
<div className="bg-black rounded-lg shadow-xl p-4">...</div>
```

#### Case 2: 過剰なトークン化

SpacingやFontSizeを勝手にセマンティック化しないこと。

```tsx
// Bad: p-card-padding, text-body-size は定義されていない
<div className="bg-night-800 p-card-padding text-body-size">...</div>
```
