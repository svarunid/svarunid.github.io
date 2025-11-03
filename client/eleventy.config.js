export default function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy({ "src/styles": "styles" });
  eleventyConfig.addWatchTarget("src/styles");
  eleventyConfig.addWatchTarget("src/scripts");
  eleventyConfig.addWatchTarget("src/components");

  return {
    dir: {
      input: "src",
      output: "dist",
      includes: "_includes",
      data: "_data"
    },
    templateFormats: ["liquid", "md", "html"],
    htmlTemplateEngine: "liquid",
    markdownTemplateEngine: "liquid"
  };
}
