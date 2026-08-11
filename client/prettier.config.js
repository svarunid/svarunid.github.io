/** @type {import("prettier").Config} */
export default {
  plugins: ["@shopify/prettier-plugin-liquid"],
  overrides: [
    {
      files: "src/**/*.html",
      options: {
        parser: "liquid-html",
      },
    },
  ],
};
