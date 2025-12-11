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

### A. Overrides (Root Definition)

**以下のカテゴリは Tailwindのデフォルト値を「無効化（上書き）」しています。**
Kvellの世界観に存在しない色や形状は使用不可能です。

  * **Colors:** `bg-night-900`, `text-ember-500` 等
      * *Note:* 配色は定義されていますが、背景色として使用する際は **Opacity Utility (例: `bg-night-800/60`)** との併用を基本とします。
  * **Shadows (Glow):** `shadow-glow-md` 等
  * **Border Radius:** `rounded-card`, `rounded-button`

### B. Extends (Theme Extension)

**以下のカテゴリは Tailwindのデフォルト値を「維持」しつつ、カスタム定義を「追加」しています。**

  * **Font Family:** `font-base` (推奨), `font-sans` (Fallback)
  * **Blur:** `backdrop-blur-sm`, `backdrop-blur-md` (すりガラス表現用)
  * **Animation:** `animate-flicker` (炎), `animate-float` (火の粉)

### C. Defaults (No Configuration)

**以下のカテゴリは Tailwindのデフォルト値を「そのまま」使用します。**
これらを独自トークン化することは禁止します（例: `p-card-padding` は不要）。

  * **Spacing:** `p-4`, `m-2`, `gap-4`
  * **Sizing:** `w-full`, `h-64`, `max-w-md`
  * **Layout:** `flex`, `grid`, `absolute`, `z-10`
  * **Font Size:** `text-sm`, `text-xl`

-----

## 3\. Implementation Rules (Visual Identity)

### 1\. Shadow is Atmosphere ("Glow")

Kvellにおいて `shadow` は「影を落とす」ものではなく、**「自らが発光している（Glow）」**、または**「空気感（Atmosphere）を纏う」**表現として使用してください。

  * ❌ `shadow-lg` (黒い影) -\> **使用不可**
  * ✅ `shadow-[0_0_20px_rgba(255,149,0,0.25)]` (JIT) または `shadow-glow-md` -\> **推奨**
  * **Design Note:** 境界線を曖昧にし、夜空に溶け込ませるために使用します。

### 2\. Glassmorphism (Translucency)

Kvellの背景は「メッシュグラデーション（夜空とビーナスベルト）」です。
この美しい背景を遮断しないよう、コンポーネント（Card, Modal等）は **「不透明（Solid）」で塗りつぶすことを禁止します。**

  * ❌ `bg-night-800` (不透明)
  * ✅ `bg-night-800/40 backdrop-blur-md` (半透明 + すりガラス)
  * **Concept:** UIは「夜空に浮かぶガラス板」あるいは「光の凝縮」として表現されます。

### 3\. No Hard Borders

世界観を壊す「くっきりとした実線」の使用を避けてください。
境界線が必要な場合は、透明度を下げた線や、光彩（Ring/Shadow）で表現します。

  * ❌ `border border-ember-500` (工事現場のような強い線)
  * ✅ `border border-white/10` (ガラスの縁)
  * ✅ `ring-1 ring-ember-500/50` (内側からの発光)

### 4\. Radius Strategy

Skyのような「優しさ・チル」を表現するため、角丸は大きめを維持します。

  * **Card:** `rounded-card` (12px ~ 16px)
  * **Button:** `rounded-button` (9999px / Pill型)

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

### ✅ Correct Implementation (Glass & Glow)

「背景透過」「ブラー」「ソフトな境界線」が適用され、夜空のグラデーションと馴染む実装。

```tsx
// 良い例: Glassmorphism + Glow
<div className="
  relative overflow-hidden
  rounded-card
  border border-white/10        /* ガラスの縁 */
  bg-night-900/40               /* 透過背景 */
  backdrop-blur-md              /* すりガラス効果 */
  shadow-glow-sm                /* ほのかな発光 */
  p-6
">
  {/* 燃えている時のハイライト装飾 */}
  <div className="absolute inset-0 bg-ember-500/10 pointer-events-none" />
  
  <h2 className="relative font-display text-xl text-smoke-100 font-normal tracking-wide">
    星を紡ぐ焚き火
  </h2>
  <p className="relative font-base text-sm text-ash-100 leading-relaxed">
    境界線のない夜空に、言葉を溶かすように...
  </p>
</div>
```

### ❌ Incorrect Implementation

下記実装は悪い例です。このような実装は避けてください。

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

### Case 3: Solid & Hard (不透明・実線)
以前のWeb2.0的な実装。Kvellの世界観では「異物」となります。

```TypeScript

// Bad: 不透明な黒背景、くっきりしたオレンジの枠線、黒い影
<div className="bg-night-800 border-2 border-ember-500 shadow-xl p-4">
  ...
</div>
```
