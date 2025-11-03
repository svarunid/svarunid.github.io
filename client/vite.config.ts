import { defineConfig } from "vite";

export default defineConfig({
  build: {
    outDir: "dist/assets",
    emptyOutDir: false,
    sourcemap: true,
    lib: {
      entry: "src/scripts/main.ts",
      formats: ["es"],
      fileName: () => "main.js"
    }
  }
});
