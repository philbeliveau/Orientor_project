import { dirname } from "path";
import { fileURLToPath } from "url";
import { FlatCompat } from "@eslint/eslintrc";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    plugins: ["tailwindcss"],
    rules: {
      "tailwindcss/classnames-order": "warn",
      "tailwindcss/no-custom-classname": "off",
      "at-rule-no-unknown": [
        true,
        {
          ignoreAtRules: ["apply", "tailwind", "layer", "variants", "responsive", "screen"],
        },
      ],
    },
  },
];

export default eslintConfig;
