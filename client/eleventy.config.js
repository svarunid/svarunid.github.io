export default function (eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "src/styles": "styles" });
  eleventyConfig.addWatchTarget("src/styles");
  eleventyConfig.addWatchTarget("src/scripts");
  eleventyConfig.addWatchTarget("src/components");

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
