import { useState, useEffect, useRef } from "react";
import type { Spark, SparkViewModel } from "@/domain/model/spark";
import { computeSparkViewModel } from "@/domain/service/sparkService";

const UPDATE_INTERVAL_MS = 1000;

export const useSparkTransformer = (rawSparks: Spark[]) => {
  const [viewModels, setViewModels] = useState<SparkViewModel[]>([]);

  // setInterval のクロージャ内で最新の rawSparks を参照するために Ref に保持する
  const sparksRef = useRef(rawSparks);

  // 1. データが更新されたら Ref を更新し、即座に ViewModel も再計算して反映する
  useEffect(() => {
    sparksRef.current = rawSparks;

    // データ到着時は即時反映
    const now = Date.now();
    setViewModels(
      rawSparks
        .filter((s) => now < new Date(s.decayAt).getTime())
        .map((s) => computeSparkViewModel(s)),
    );
  }, [rawSparks]);

  // 2. 定期的な時間更新（データ更新によるリセットを防ぐため、依存配列は空）
  useEffect(() => {
    const timer = setInterval(() => {
      const now = Date.now();
      // Ref から最新のデータを取り出して計算
      const currentSparks = sparksRef.current;

      const activeViewModels = currentSparks
        .filter((s) => now < new Date(s.decayAt).getTime())
        .map((s) => computeSparkViewModel(s));

      // ここで State 更新（中身が変わっていなくても残り時間のために再レンダリングが必要）
      setViewModels(activeViewModels);
    }, UPDATE_INTERVAL_MS);

    return () => {
      clearInterval(timer);
    };
  }, []); // 空配列！これでタイマーはマウント中ずっと生き続ける

  return viewModels;
};
