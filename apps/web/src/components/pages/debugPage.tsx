// src/components/pages/DebugPage.tsx
import { SparkCard } from "@/components/molecules/SparkCard";
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
  return (
    <div className="text-smoke-100 min-h-screen space-y-10 p-10">
      <h1 className="text-ember-500 text-2xl font-bold">🎨 UI Playground</h1>

      {/* 1. 設定ファイルの実験エリア（生のHTMLで試す） */}
      <section className="rounded-card border-ash-500 space-y-4 border p-4">
        <h2 className="text-xl">🛠 Tailwind Config Check</h2>
        <div className="flex gap-4">
          <SparkCard spark={spark} />
        </div>
      </section>

      <div className="rounded-card shadow-glow-sm bg-night-900/40 relative overflow-hidden border border-white/10 p-6 backdrop-blur-md">
        {/* 燃えている時のハイライト装飾 */}
        {/* <div className="pointer-events-none absolute inset-0 bg-ember-500/10" /> */}

        <h2 className="font-display text-smoke-100 relative text-xl font-normal tracking-wide">
          星を紡ぐ焚き火
        </h2>
        <p className="font-base text-ash-500 relative text-sm leading-relaxed">
          境界線のない夜空に、言葉を溶かすように...
        </p>
      </div>

      <Button>button</Button>
    </div>
  );
};
