import StyleDictionary from 'style-dictionary';

// ヘルパー関数
function formatObj(obj) {
  if (obj.hasOwnProperty('value')) {
    return obj.value;
  }
  const newObj = {};
  for (const name in obj) {
    if (obj.hasOwnProperty(name)) {
      newObj[name] = formatObj(obj[name]);
    }
  }
  return newObj;
}

// 設定オブジェクトの構築
const sd = new StyleDictionary({
  source: ['tokens.json'], // パスはプロジェクトルート相対
  platforms: {
    js: {
      transformGroup: 'js',
      buildPath: 'dist/',
      files: [{
        destination: 'tailwind.theme.js',
        format: 'tailwind/js'
      }]
    }
  }
});

// Custom Formatの登録 (ESM構文で記述)
sd.registerFormat({
  name: 'tailwind/js',
  format: function({ dictionary }) {
    const categoryMap = {
      'color': 'colors',
      'shadow': 'boxShadow',
      'radius': 'borderRadius',
      'font': 'fontFamily',
      'animation': 'animation',
      'opacity': 'opacity'
    };

    const output = {};

    dictionary.allTokens.forEach(token => {
      const category = token.attributes.category;
      const tailwindKey = categoryMap[category];
      if (!tailwindKey) return;

      if (!output[tailwindKey]) output[tailwindKey] = {};

      let current = output[tailwindKey];
      // 先頭のcategoryを除くパスを使用
      const path = token.path.slice(1);

      path.forEach((key, index) => {
        if (index === path.length - 1) {
          current[key] = token.value;
        } else {
          if (!current[key]) current[key] = {};
          current = current[key];
        }
      });
    });

    // 【重要】 ここだけは Tailwind Config (CJS) が読みやすいように CJS形式で吐き出す
    return `/**
 * Do not edit directly
 * Generated on ${new Date().toISOString()}
 */
module.exports = ${JSON.stringify(output, null, 2)};
`;
  }
});

// ビルド実行
await sd.buildAllPlatforms();
console.log('🔥 Design tokens built successfully (ESM)!');
