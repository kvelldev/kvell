

# Project Kvell: Frontend Architecture & Implementation Guidelines

## 1\. Purpose & Scope

このドキュメントは、Project Kvellのフロントエンド開発における **「不変の憲法」** です。
AIエージェントはこのガイドラインに準拠し、Reactの柔軟性が招く「無秩序」を徹底的に排除しなければなりません。
本ドキュメントは「構造と責務」を定義します。具体的な色やサイズ等の「意匠」については、別定義の`21_design_tokens.md`に従ってください。

## 2\. Tech Stack (Strict)

以下の技術スタック以外の使用を禁止します。

  * **Framework:** Vite
  * **Language:** TypeScript (Strict Mode)
  * **Styling:** Tailwind CSS (Utility-first) + CSS Modules (for complex animations)
  * **State Management:** React Context + Hooks (Global), Local State (Component)
  * **Visual Effects:** Framer Motion or Canvas API (for Fire/Particle effects)
  * **HTTP Client:** Fetch API (wrapped in Adapter)

## 3\. Architecture Pattern: Clean Architecture + Atomic Design

**関心の分離**を徹底します。
「見た目 (UI)」と「ロジック (UseCase)」と「データ定義 (Domain)」を明確に分割します。

### A. Layers & Dependency (Clean Architecture)

依存の方向は **UI (Components) -> UseCase (Hooks) -> Domain (Types)** です。

1.  **Domain (Inner)**: `src/domain/`
      * アプリケーションのコアデータ型定義。
      * UIライブラリやAPIクライアントに依存してはならない。純粋なTypeScriptの型と純粋関数のみ。
      * **Entities**: `type Spark = { ... }`
2.  **UseCase (Middle)**: `src/usecase/`
      * アプリケーションのビジネスロジック。React Custom Hooksとして実装することを推奨する。
      * **Hooks**: `useIgnite()`, `useFetchTimeline()`
      * UI操作を含まない、純粋な「振る舞い」の定義。
3.  **Adapter (Outer)**: `src/adapter/`
      * 外部との通信。
      * **Repository**: APIのエンドポイントを叩く関数群。`fetch` はここに閉じ込める。
      * **Presenters**: データをView用に整形する関数（必要な場合）。
4.  **UI (Presentation)**: `src/components/` & `src/app/`
      * Atomic Designに基づくコンポーネント群。
      * **ロジックを持たない**: UIコンポーネント内で直接 `fetch` したり、複雑な計算をしてはならない。全て `usecase` フックに委譲すること。

### B. Atomic Design (Component Structure)

UIコンポーネントは以下の粒度で分割・管理します。

  * **Atoms**: 最小単位。状態を持たない (Stateless)。
      * *Example:* Button, Icon, Label, FireParticle
  * **Molecules**: Atomの組み合わせ。ドメインの文脈を少し持ち始める。
      * *Example:* FuelButton (Icon + Count), SearchInput
  * **Organisms**: 独立して機能するUIパーツ。ここで初めてUseCase(Hooks)を呼び出すことが許可される。
      * *Example:* TimelineCard, BonfireViewer, Header
  * **Templates**: ページレイアウトの骨組み。
      * *Example:* MainLayout, FocusLayout
  * **Pages (`src/app/`)**: ルーティングのエンドポイント。Templatesにデータを流し込む場所。

## 4\. Implementation Principles

### A. The "Smart vs Dumb" Rule

**ここを理解することが一番重要です。**
コンポーネントの役割を明確に区別してください。

  * **Smart Components (Container/Organisms/Pages):**
      * UseCase (Hooks) を呼び出し、データを取得・操作する。
      * Dumb Components に props を渡す。
  * **Dumb Components (Atoms/Molecules):**
      * **一切のロジックを持たない。**
      * データは全て `props` で受け取る。
      * 見た目の表示と、イベントの通知(`onClick` 等)のみを行う。

繰り返しになりますが、**「Smart Componentsのみがロジックを持てる**(=UseCaseをimportできる)」ということを厳守してください。
こうすることで、UIの変更とロジックの変更を完全に分離できます。

### B. Visual & Performance (Fire Effects)

Kvellの核である「炎」の表現は、パフォーマンスへの影響が大きいため、以下の特別ルールを設けます。

  * **Isolation:** 炎のエフェクト描画ロジックは、独立したコンポーネント (`BonfireCanvas` 等) に切り出し、Reactの再レンダリングサイクルの影響を最小限に抑えること（`React.memo` や `useRef` の活用）。
  * **Animation Library:** CSS Animation で完結するものはTailwind/CSSで。物理演算が必要なものは Framer Motion または Canvas を使用する。

### C. Domain Richness
コードは仕様書です。UIの「見た目」や「操作」ではなく、「ドメインの意図」を名前で表現してください。

* **Ubiquitous Language:** 変数名・ファイル名・クラス名は、必ず`01_ubiquitous.md`にて定義されたユビキタス言語（`Spark`, `Bonfire`, `Ash`, `Fuel` 等）に従うこと。
* **Action Naming:** `handleClick()` や `increment()` ではなく -> **`addFuel()`**
* **Component Naming:** `RedButton` や `FireWrapper` ではなく -> **`FuelButton`**, **`BonfireContainer`**


## 5\. Directory Structure (The Map)
ファイル作成時はこの構造に従ってください。

```text
src/
├── domain/                 # Types & Pure Logic
│   └── model/
│       ├── spark.ts
│       └── bonfire.ts
├── usecase/                # Application Logic (Hooks)
│   ├── useAddFuel.ts       # Action: Add Fuel (was useIgnite)
│   └── useTimeline.ts
├── adapter/                # API & Infra
│   └── repository/
│       └── sparkRepository.ts
├── components/             # Atomic Design
│   ├── atoms/              # Button, Icon
│   ├── molecules/          # Cards, ListItems
│   ├── organisms/          # Sections, Complex Widgets (Hooks OK)
│   └── templates/          # Layouts
├── routes/                 # React Router Components (Pages)
│   ├── TimelinePage.tsx
│   └── NotFoundPage.tsx
├── App.tsx                 # Routing Definition & Global Providers
└── main.tsx                # Entrypoint (Vite)
```

## 6\. Reference Implementation (Few-shot Example)

以下は「薪をくべるボタン」のフロントエンド実装例です。

### [Layer 1] Domain & Adapter

```ts
// src/domain/model/spark.ts
export type Spark = {
  id: string;
  fuelCount: number;
};

// src/adapter/repository/sparkRepository.ts
export const addFuel = async (sparkId: string): Promise<Spark> => {
  const res = await fetch(`/api/v1/sparks/${sparkId}/fuel`, { method: 'POST' });
  return res.json();
};
```


### [Layer 2] UseCase (Custom Hook)

```ts
// src/usecase/useAddFuel.ts
import { useState } from 'react';
import { addFuel as addFuelRepo } from '@/adapter/repository/sparkRepository';

export const useAddFuel = () => {
  const [isAdding, setIsAdding] = useState(false);

  const addFuel = async (sparkId: string) => {
    setIsAdding(true);
    try {
      await addFuelRepo(sparkId);
      // ここでGlobal State更新や、成功時のエフェクト発火指示を行う
      // もし結果としてSparkがBonfireになった場合(Ignite)、
      // APIレスポンスに含まれるステータスを見てここでハンドリングする
    } finally {
      setIsAdding(false);
    }
  };

  return { addFuel, isAdding };
};
```


### [Layer 3] UI (Atomic Design)

```ts
// src/components/atoms/FireIcon.tsx (Dumb)
export const FireIcon = ({ size = 'md' }: { size?: 'sm'|'md' }) => (
  <span className={size === 'md' ? 'text-2xl' : 'text-xl'}>🔥</span>
);

// src/components/molecules/FuelButton.tsx (Dumb)
// 見た目だけを責務とする。ロジックは知らない。
type Props = {
  onClick: () => void;
  disabled: boolean;
  count: number;
};
export const FuelButton = ({ onClick, disabled, count }: Props) => (
  <button onClick={onClick} disabled={disabled} className="flex items-center gap-2">
    <FireIcon />
    <span>{count}</span>
  </button>
);

// src/components/organisms/SparkCard.tsx (Smart)
// ここでUseCaseとUIを結合する。
import { useAddFuel } from '@/usecase/useAddFuel';
import { FuelButton } from '@/components/molecules/FuelButton';

export const SparkCard = ({ spark }: { spark: Spark }) => {
  const { addFuel, isAdding } = useAddFuel();

  return (
    <div className="card-border">
      <p>{spark.content}</p>
      <FuelButton 
        onClick={() => addFuel(spark.id)} 
        disabled={isAdding}
        count={spark.fuelCount}
      />
    </div>
  );
};
```
