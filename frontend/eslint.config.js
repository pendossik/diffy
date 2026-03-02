import js from "@eslint/js";
import globals from "globals";
import reactHooks from "eslint-plugin-react-hooks";
import reactRefresh from "eslint-plugin-react-refresh";
import tseslint from "typescript-eslint";
import { globalIgnores } from "eslint/config";
// 1. Добавляем импорт плагина
import reactPlugin from "eslint-plugin-react";

export default tseslint.config([
    globalIgnores(["dist"]),
    {
        files: ["**/*.{ts,tsx}"],

        plugins: {
            react: reactPlugin,
            "react-hooks": reactHooks,
            "react-refresh": reactRefresh,
        },

        extends: [js.configs.recommended, ...tseslint.configs.recommended],

        languageOptions: {
            ecmaVersion: 2020,
            globals: globals.browser,
            parserOptions: {
                ecmaFeatures: {
                    jsx: true,
                },
            },
        },

        rules: {
            indent: ["error", 4],
            "react/jsx-indent": ["error", 4],
            "react-refresh/only-export-components": [
                "warn",
                { allowConstantExport: true },
            ],
        },

        settings: {
            react: {
                version: "detect",
            },
        },
    },
]);
