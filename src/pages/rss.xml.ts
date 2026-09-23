import rss from "@astrojs/rss";
import { getCollection } from "astro:content";
import type { APIContext } from "astro";
import { entryDate, postSlug, sortPosts, site } from "../lib/site";

export async function GET(context: APIContext) {
  const posts = sortPosts(await getCollection("posts"));
  return rss({
    title: site.title,
    description: site.description,
    site: context.site!,
    items: posts.map((post) => ({
      title: post.data.title,
      pubDate: entryDate(post),
      description: post.data.description,
      link: `/posts/${postSlug(post.id)}/`,
    })),
  });
}
