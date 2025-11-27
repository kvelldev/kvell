import js from '@eslint/js';
import { defineConfig } from 'eslint/config';
import unicorn from 'eslint-plugin-unicorn';
import globals from 'globals';
import tseslint from 'typescript-eslint';
import prettierConfig from 'eslint-config-prettier';
import jsdoc from 'eslint-plugin-jsdoc';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';

export default defineConfig([
  {
    ignores: ['dist/**', 'node_modules/**', 'coverage/**'],
  },

  // 1. Global configs for all files
  js.configs.recommended,
  unicorn.configs['recommended'],
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.es2022,
      },
    },
    settings: {
      'import/resolver': {
        typescript: {},
      },
    },
    rules: {
      complexity: ['error', { max: 10 }],
      'max-len': ['error', { code: 120, ignoreStrings: true, ignoreTemplateLiterals: true }],
      'no-console': ['warn', { allow: ['info', 'warn', 'error'] }],
      'no-underscore-dangle': ['error', { allow: ['_id'] }],
      'class-methods-use-this': 'off',
      'unicorn/filename-case': [
        'error',
        {
          cases: {
            kebabCase: true,
            camelCase: true,
            pascalCase: true,
          },
        },
      ],
      'unicorn/prevent-abbreviations': [
        'error',
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
      'unicorn/catch-error-name': 'off',
      'unicorn/no-null': 'off',
    },
  },

  // 2. TypeScript specific configurations
  ...tseslint.configs.strictTypeChecked.map((config) => ({
    ...config,
    files: ['src/**/*.{ts,tsx}', 'tests/**/*.{ts,tsx}'],
  })),
  ...tseslint.configs.stylisticTypeChecked.map((config) => ({
    ...config,
    files: ['src/**/*.{ts,tsx}', 'tests/**/*.{ts,tsx}'],
  })),

  // JSDoc Configuration
  {
    files: ['src/**/*.{ts,tsx}', 'tests/**/*.{ts,tsx}'],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.app.json', './tsconfig.node.json'],
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      jsdoc: jsdoc,
    },
    rules: {
      ...jsdoc.configs['recommended-typescript-error'].rules,
      'jsdoc/require-jsdoc': [
        'error',
        {
          publicOnly: true,
          require: {
            ClassDeclaration: false,
            MethodDefinition: false,
            ArrowFunctionExpression: false,
            FunctionDeclaration: false,
          },
          contexts: ['TSInterfaceDeclaration', 'TSTypeAliasDeclaration'],
        },
      ],
      'jsdoc/require-param': 'off',
      'jsdoc/require-return': 'off',
    },
  },

  // 3. Config specifically for React component files (.tsx)
  {
    files: ['src/**/*.tsx', 'tests/unit/**/*.tsx'],
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': 'warn',
    },
  },

  // Rule adjustment for test files
  {
    files: ['tests/unit/**/*.tsx'],
    rules: {
      'unicorn/filename-case': [
        'error',
        {
          case: 'kebabCase',
          ignore: [/\.test\.tsx$/],
        },
      ],
    },
  },

  // 4. Config for TypeScript declaration files (.d.ts)
  {
    files: ['**/*.d.ts'],
    rules: {
      'unicorn/prevent-abbreviations': 'off',
    },
  },

  // 5. Disable confliction rules with Prettier (should be last)
  prettierConfig,
]);
