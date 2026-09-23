import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";
import site from "./src/data/site.json";

const base = process.env.ASTRO_BASE || site.pathPrefix || "/";

export default defineConfig({
  site: site.url,
  base,
  trailingSlash: "always",
  integrations: [sitemap()],
  markdown: {
    shikiConfig: {
      themes: {
        light: "github-light",
        dark: "github-dark",
      },
    },
  },
});
