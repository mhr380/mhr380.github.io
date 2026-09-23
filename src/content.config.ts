import fs from "node:fs";
import path from "node:path";
import { defineCollection, z } from "astro:content";
import { expandJekyll } from "./lib/remark-jekyll.mjs";

function parseFrontmatter(raw: string) {
  const match = raw.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) return { data: {} as Record<string, string>, body: raw };
  const data: Record<string, string> = {};
  for (const line of match[1].split(/\r?\n/)) {
    const pair = line.match(/^(\w+):\s*(.*)$/);
    if (!pair) continue;
    data[pair[1]] = pair[2].replace(/^["']|["']$/g, "");
  }
  return { data, body: match[2] };
}

const posts = defineCollection({
  loader: {
    name: "jekyll-posts",
    load: async ({ store, parseData, renderMarkdown, watcher }) => {
      const dir = path.resolve(import.meta.dirname, "../_posts");
      watcher?.add(dir);
      store.clear();
      if (!fs.existsSync(dir)) return;
      for (const file of fs.readdirSync(dir)) {
        if (!file.endsWith(".md")) continue;
        const raw = fs.readFileSync(path.join(dir, file), "utf8");
        const { data, body } = parseFrontmatter(raw);
        const id = file.replace(/\.md$/, "");
        const expanded = expandJekyll(body);
        store.set({
          id,
          data: await parseData({
            id,
            data: {
              title: data.title,
              description: data.description,
              date: data.date,
            },
          }),
          body: expanded,
          rendered: await renderMarkdown(expanded),
        });
      }
    },
  },
  schema: z.object({
    title: z.string(),
    description: z.string().optional(),
    date: z.coerce.date().optional(),
  }),
});

export const collections = { posts };
