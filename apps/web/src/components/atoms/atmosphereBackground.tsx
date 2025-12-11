import { clsx } from "clsx";
const NOISE_SVG_DATA = `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.65' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E")`;

export const AtmosphereBackground = () => {
  return (
    <div className="bg-night-900 fixed inset-0 -z-10 overflow-hidden">
      {/* ------------------------------------------------------- */}
      {/* Layer 1: Venus Belt (上層) */}
      {/* ------------------------------------------------------- */}
      <div
        className={clsx(
          // [1] 配置・サイズ（あまりいじらない）
          "absolute left-0 w-full",

          // [2] 色・グラデーション
          "from-venus-500 via-venus-500/50 bg-gradient-to-t to-transparent",

          // [3] 調整パラメータ（ここをいじる）
          "h-[65vh]",
          "bottom-[5%]",
          "blur-[100px]",
          "opacity-50",
        )}
      />

      {/* ------------------------------------------------------- */}
      {/* Layer 2: Earth's Shadow (下層) */}
      {/* ------------------------------------------------------- */}
      <div
        className={clsx(
          // [1] 配置・サイズ
          "absolute bottom-0 left-0 w-full",

          // [2] 色・グラデーション
          "from-earthshadow-base via-earthshadow-base/60 bg-gradient-to-t to-transparent",

          // [3] 調整パラメータ
          "h-[38.5vh]",
          "blur-[100px]",
          "opacity-[0.82]",
        )}
      />

      {/* ------------------------------------------------------- */}
      {/* Layer 3: Noise Overlay (質感) */}
      {/* ------------------------------------------------------- */}
      <div
        className={clsx(
          // [1] 配置・基本設定
          "pointer-events-none absolute inset-0 size-full",
          "mix-blend-overlay",

          // [2] 調整パラメータ
          "opacity-10", // 0.05 (5%)
        )}
        style={{
          backgroundImage: NOISE_SVG_DATA,
        }}
      />
    </div>
  );
};

// import { useControls, folder } from "leva";

// /**
//  * ノイズフィルター用SVGコンポーネント
//  * CSS変数 (--noise-frequency, --noise-opacity) を受け取って動的に変化します。
//  */
// const NoiseSVG = () => (
//   <svg
//     className="pointer-events-none fixed inset-0 z-50 h-full w-full"
//     xmlns="http://www.w3.org/2000/svg"
//   >
//     <filter id="noiseFilter">
//       {/* baseFrequencyがノイズの「粗さ」を決めます。CSS変数で制御します。 */}
//       <feTurbulence
//         type="fractalNoise"
//         baseFrequency="var(--noise-frequency, 0.65)"
//         numOctaves="3"
//         stitchTiles="stitch"
//       />
//       {/* ノイズの色を白黒のアルファ値に変換します */}
//       <feColorMatrix type="saturate" values="0" />
//     </filter>
//     {/* CSS変数で不透明度を制御し、mix-blend-modeで重ねます */}
//     <rect
//       width="100%"
//       height="100%"
//       filter="url(#noiseFilter)"
//       style={{
//         opacity: "var(--noise-opacity, 0.03)",
//         mixBlendMode: "overlay",
//       }}
//     />
//   </svg>
// );

// export const AtmosphereBackground = () => {
//   const values = useControls({
//     // ----------------------------------------
//     // 1. Venus Belt (ビーナスベルト層 - ピンク)
//     // ----------------------------------------
//     Venus: folder({
//       vOpacity: { value: 0.5, min: 0, max: 1, step: 0.01 },
//       vHeight: { value: 40, min: 10, max: 100, label: "Height (vh)" }, // 層の厚み
//       vBottom: { value: 10, min: 0, max: 50, label: "Bottom (%)" }, // 地平線からの位置
//       vBlur: { value: 100, min: 0, max: 300, label: "Blur (px)" }, // 境界のぼかし
//     }),

//     // ----------------------------------------
//     // 2. Earth's Shadow (地球影層 - 深い青)
//     // ----------------------------------------
//     Shadow: folder({
//       // 色は night-800 (#0F172A) を想定
//       sOpacity: { value: 0.8, min: 0, max: 1, step: 0.01 },
//       sHeight: { value: 25, min: 5, max: 50, label: "Height (vh)" },
//       sBlur: { value: 50, min: 0, max: 200, label: "Blur (px)" },
//     }),

//     // ----------------------------------------
//     // 3. Grain (ノイズ粒子) - CSS制御版
//     // ----------------------------------------
//     Grain: folder({
//       gOpacity: {
//         value: 0.03,
//         min: 0,
//         max: 0.15,
//         step: 0.001,
//         label: "Opacity",
//       },
//       // 値が小さいほど粒子が大きく（粗く）なります。0.5〜0.9あたりが実用的。
//       gFrequency: {
//         value: 0.65,
//         min: 0.1,
//         max: 1.5,
//         step: 0.01,
//         label: "Roughness",
//       },
//     }),
//   });

//   return (
//     // ベースレイヤー：宇宙（空全体）
//     <div
//       className="fixed inset-0 -z-10 overflow-hidden bg-night-900"
//       // ノイズ用のCSS変数を定義
//       style={{
//         "--noise-opacity": values.gOpacity,
//         "--noise-frequency": values.gFrequency,
//       }}
//     >
//       {/* ------------------------------------------------------- */}
//       {/* Layer 1: ビーナスベルト (Belt of Venus) */}
//       {/* 下から上へのグラデーションで、ピンクの帯を表現 */}
//       {/* ------------------------------------------------------- */}
//       <div
//         className="absolute left-0 w-full bg-gradient-to-t from-venus-500 via-venus-500/50 to-transparent transition-all duration-75"
//         style={{
//           opacity: values.vOpacity,
//           height: `${values.vHeight}vh`,
//           bottom: `${values.vBottom}%`,
//           filter: `blur(${values.vBlur}px)`,
//         }}
//       />

//       {/* ------------------------------------------------------- */}
//       {/* Layer 2: 地球影 (Earth's Shadow) */}
//       {/* 最下部（地平線直上）にある最も暗い青の層 */}
//       {/* ------------------------------------------------------- */}
//       <div
//         className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-earthshadow-base via-earthshadow-base to-transparent transition-all duration-75"
//         style={{
//           opacity: values.sOpacity,
//           height: `${values.sHeight}vh`,
//           filter: `blur(${values.sBlur}px)`,
//           // ビーナスベルトより手前（下）に来るように少しzIndexを調整しても良いが、
//           // blurで混ざるのでそのままでもOK
//         }}
//       />

//       {/* ------------------------------------------------------- */}
//       {/* Layer 3: ノイズオーバーレイ */}
//       {/* ------------------------------------------------------- */}
//       <NoiseSVG />
//     </div>
//   );
// };
