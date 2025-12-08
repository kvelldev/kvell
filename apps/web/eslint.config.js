import js from "@eslint/js";
import { defineConfig } from "eslint/config";
import unicorn from "eslint-plugin-unicorn";
import globals from "globals";
import tseslint from "typescript-eslint";
import prettierConfig from "eslint-config-prettier";
import jsdoc from "eslint-plugin-jsdoc";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import eslintComments from "eslint-plugin-eslint-comments";
import tailwind from "eslint-plugin-tailwindcss";
export default defineConfig([
  {
    ignores: ["dist/**", "node_modules/**", "coverage/**"],
  },

  // 1. Global configs for all files
  js.configs.recommended,
  unicorn.configs["recommended"],
  ...tailwind.configs["flat/recommended"],
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2022,
      },
    },
    plugins: {
      "eslint-comments": eslintComments,
    },
    settings: {
      "import/resolver": {
        typescript: {},
      },
    },
    rules: {
      "eslint-comments/no-use": ["error", { allow: [] }],
      complexity: ["error", { max: 10 }],
      "max-len": [
        "error",
        { code: 120, ignoreStrings: true, ignoreTemplateLiterals: true },
      ],
      "no-console": ["warn", { allow: ["info", "warn", "error"] }],
      "no-underscore-dangle": ["error", { allow: ["_id"] }],
      "class-methods-use-this": "off",
      "unicorn/filename-case": [
        "error",
        {
          cases: {
            kebabCase: true,
            camelCase: true,
            pascalCase: true,
          },
        },
      ],
      "unicorn/prevent-abbreviations": [
        "error",
        {
          replacements: {
            props: false,
            ref: false,
            args: false,
            src: false,
            e: false,
            err: false,
            env: false,
            doc: false,
          },
        },
      ],
      "unicorn/catch-error-name": "off",
      "unicorn/no-null": "off",
    },
  },

  // 2. Clean Architecture Guard Rails
  // 2-1. Domain
  {
    files: ["src/domain/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["**/usecase/**", "**/adapter/**", "**/components/**"],
              message:
                "❌ VIOLATION: Domain layer must be pure. Do not import from outer layers.",
            },
            {
              group: ["react", "react-dom"],
              message:
                "❌ VIOLATION: Domain layer must not depend on UI Framework (React).",
            },
          ],
        },
      ],
    },
  },

  // 2-2. Usecase
  {
    files: ["src/usecase/**/*.{ts,tsx}"],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              group: ["**/components/**"],
              message:
                "❌ VIOLATION: UseCase layer must not depend on UI components.",
            },
            {
              group: ["**/adapter/**"],
              message:
                "❌ VIOLATION: UseCase must not depend on Adapter implementations. Use Domain interfaces (DIP).",
            },
          ],
        },
      ],
    },
  },

  // 2-3. Dumb Components
  {
    files: [
      "src/components/{atoms,molecules,organisms,templates}/**/*.{ts,tsx}",
    ],
    rules: {
      "no-restricted-imports": [
        "error",
        {
          patterns: [
            {
              // ロジック禁止（Propsで受け取れ）
              group: ["**/usecase/**", "@/usecase/**"],
              message:
                "❌ VIOLATION: Dumb components cannot import UseCases directly. Pass data/handlers via props.",
            },
            {
              group: ["**/adapter/**", "@/adapter/**"],
              message:
                "❌ VIOLATION: UI components cannot access Adapter layer directly.",
            },
          ],
        },
      ],
    },
  },

  // 3. TypeScript specific configurations
  ...tseslint.configs.strictTypeChecked.map((config) => ({
    ...config,
    files: ["src/**/*.{ts,tsx}", "tests/**/*.{ts,tsx}"],
  })),
  ...tseslint.configs.stylisticTypeChecked.map((config) => ({
    ...config,
    files: ["src/**/*.{ts,tsx}", "tests/**/*.{ts,tsx}"],
  })),

  // JSDoc Configuration
  {
    files: ["src/**/*.{ts,tsx}", "tests/**/*.{ts,tsx}"],
    languageOptions: {
      parserOptions: {
        project: ["./tsconfig.app.json", "./tsconfig.node.json"],
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      jsdoc: jsdoc,
    },
    rules: {
      ...jsdoc.configs["recommended-typescript-error"].rules,
      "jsdoc/require-jsdoc": [
        "error",
        {
          publicOnly: true,
          require: {
            ClassDeclaration: false,
            MethodDefinition: false,
            ArrowFunctionExpression: false,
            FunctionDeclaration: false,
          },
          contexts: ["TSInterfaceDeclaration", "TSTypeAliasDeclaration"],
        },
      ],
      "jsdoc/require-param": "off",
      "jsdoc/require-return": "off",
    },
  },

  // 4. Config specifically for React component files (.tsx)
  {
    files: ["src/**/*.tsx", "tests/unit/**/*.tsx"],
    plugins: {
      "react-hooks": reactHooks,
      "react-refresh": reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      "react-refresh/only-export-components": "warn",
    },
  },

  // Rule adjustment for test files
  {
    files: ["tests/unit/**/*.{ts,tsx}"],
    rules: {
      "@typescript-eslint/unbound-method": "off",
      "unicorn/filename-case": [
        "error",
        {
          case: "kebabCase",
          ignore: [/\.test\.tsx$/],
        },
      ],
    },
  },

  // 5. Config for TypeScript declaration files (.d.ts)
  {
    files: ["**/*.d.ts"],
    rules: {
      "unicorn/prevent-abbreviations": "off",
    },
  },

  // 6. Disable confliction rules with Prettier (should be last)
  prettierConfig,
]);
