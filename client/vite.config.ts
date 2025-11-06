import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: "dist/assets",
    emptyOutDir: false,
    sourcemap: true,
    rollupOptions: {
      input: {
        chat: "src/scripts/chat.ts",
      },
      output: {
        entryFileNames: "[name].js",
        format: "es",
      },
    },
  },
});
