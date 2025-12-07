/** @type {import('tailwindcss').Config} */
import customTheme from "../../packages/design_token/dist/tailwind.theme.js";

const {
  colors,
  boxShadow,
  borderRadius,
  opacity,
  fontFamily,
  animation,
  blur,
  backgroundImage,
  keyframes
} = customTheme;

export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    // -------------------------------------------------------------------------
    // 1. Overrides (Root)
    // -------------------------------------------------------------------------
    // ここに定義したキーは、Tailwindのデフォルト値を「完全に消去」します。
    // AIエージェントが、Kvellの世界観にない色や影を使うことを物理的に防ぎます。

    colors, // bg-red-500 等は使用不可になり、bg-night-900 等のみ有効化
    boxShadow, // shadow-xl 等は使用不可になり、shadow-glow-md 等のみ有効化
    borderRadius, // rounded-full 等は使用不可になり、rounded-card 等のみ有効化
    opacity, // opacity-50 等は使用不可になり、opacity-ash のみ有効化

    // -------------------------------------------------------------------------
    // 2. Extends
    // -------------------------------------------------------------------------
    // ここに定義したキーは、Tailwindのデフォルト値に「追加」されます。
    extend: {
      fontFamily: fontFamily.family,
      animation,
      keyframes,
      blur,
      backgroundImage,
    },
  },
  plugins: [],
};
