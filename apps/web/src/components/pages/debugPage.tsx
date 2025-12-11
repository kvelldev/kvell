// src/components/pages/DebugPage.tsx
import { useState } from "react";
import { SparkCard } from "../atoms/SparkCard";
import { SparkViewModel } from "@/domain/model/spark";
import { Button } from "../ui/button";

const now = new Date();
const createdAt = new Date(now.getTime() - 5 * 60 * 1000);
const decayAt = new Date(now.getTime() + 24 * 60 * 60 * 1000);
const remainingSeconds = Math.floor((decayAt.getTime() - now.getTime()) / 1000);
const spark: SparkViewModel = {
  id: "mock-spark-001",
  content:
    "ここに投稿内容が入ります。これは24時間で消えるSparkのテスト投稿です。",
  createdAt: createdAt.toISOString(),
  decayAt: decayAt.toISOString(),
  temperature: "ash",
  remainingTimeInSeconds: remainingSeconds,
};

export const DebugPage = () => {
  // アニメーションの再生用（keyを変えるとリセットされるハック）
  const [key, setKey] = useState(0);

  return (
    <div className="min-h-screen space-y-10 p-10 text-smoke-100">
      <h1 className="text-2xl font-bold text-ember-500">🎨 UI Playground</h1>

      {/* 1. 設定ファイルの実験エリア（生のHTMLで試す） */}
      <section className="rounded-card space-y-4 border border-ash-500 p-4">
        <h2 className="text-xl">🛠 Tailwind Config Check</h2>
        <div className="flex gap-4">
          <SparkCard spark={spark} />
        </div>
      </section>

      <div className="rounded-card shadow-glow-sm relative overflow-hidden border border-white/10 bg-night-900/40 p-6 backdrop-blur-md">
        {/* 燃えている時のハイライト装飾 */}
        {/* <div className="pointer-events-none absolute inset-0 bg-ember-500/10" /> */}

        <h2 className="font-display relative text-xl font-normal tracking-wide text-smoke-100">
          星を紡ぐ焚き火
        </h2>
        <p className="font-base relative text-sm leading-relaxed text-ash-500">
          境界線のない夜空に、言葉を溶かすように...
        </p>
      </div>

      <Button>button</Button>
    </div>
  );
};
