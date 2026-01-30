import EleventyVitePlugin from "@11ty/eleventy-plugin-vite";
import tailwindcss from "@tailwindcss/vite";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default function (eleventyConfig) {
  eleventyConfig.addPlugin(EleventyVitePlugin, {
    viteOptions: {
      plugins: [tailwindcss()],
      resolve: {
        alias: {
          "/scripts": path.resolve(__dirname, "src/scripts"),
          "/styles": path.resolve(__dirname, "src/styles"),
        },
      },
      build: {
        sourcemap: true,
      },
    },
  });

  eleventyConfig.addWatchTarget("src/scripts");
  eleventyConfig.addWatchTarget("src/_includes");

  eleventyConfig.addFilter("shuffle", (array) => {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  });

  return {
    dir: {
      input: "src",
      output: "dist",
      includes: "_includes",
      data: "_data",
    },
    templateFormats: ["liquid", "html"],
    htmlTemplateEngine: "liquid",
    serverOptions: {
      showVersion: true,
    },
  };
}
