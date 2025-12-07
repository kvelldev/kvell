// src/components/pages/DebugPage.tsx
import { useState } from "react";

export const DebugPage = () => {
  // アニメーションの再生用（keyを変えるとリセットされるハック）
  const [key, setKey] = useState(0);

  return (
    <div className="min-h-screen space-y-10 bg-night-900 p-10 text-smoke-100">
      <h1 className="text-2xl font-bold text-ember-500">🎨 UI Playground</h1>

      {/* 1. 設定ファイルの実験エリア（生のHTMLで試す） */}
      <section className="space-y-4 rounded-card border border-ash-500 p-4">
        <h2 className="text-xl">🛠 Tailwind Config Check</h2>
        <div className="flex gap-4">
          {/* 枠線バグの確認 */}
          <div className="rounded-card border-2 border-ember-500 p-4 text-smoke-100">
            Border Ember
          </div>
          {/* 透過の確認 */}
          <div className="rounded-card border-2 border-transparent p-4 text-ash-500">
            Border Transparent
          </div>
        </div>
      </section>

      {/* 2. アニメーション実験エリア */}
      <section className="space-y-4 rounded-card border border-ash-500 p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl">💨 Animation Check</h2>
          <button
            onClick={() => { setKey(k => k + 1 ); }}
            className="rounded-button border border-ash-500 bg-night-800 px-4 py-2 hover:bg-ash-500"
          >
            Replay
          </button>
        </div>

        <div className="flex h-40 items-end justify-center gap-10">
          <div key={key} className="origin-bottom animate-smoke">
             <div className="rounded-card border-2 border-ember-500 p-4 text-smoke-100">
               Component
             </div>
           </div>
        </div>
      </section>
    </div>
  );
};
