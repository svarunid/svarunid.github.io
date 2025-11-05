import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: "dist/assets",
    emptyOutDir: false,
    sourcemap: true,
    rollupOptions: {
      input: {
        home: "src/scripts/home.ts",
        chat: "src/scripts/chat.ts",
      },
      output: {
        entryFileNames: "[name].js",
        format: "es",
      },
    },
  },
});
