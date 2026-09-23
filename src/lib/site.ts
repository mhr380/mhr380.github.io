import type { CollectionEntry } from "astro:content";
import site from "../data/site.json";

export { site };

export function withBase(path: string) {
  if (/^https?:\/\//i.test(path)) return path;
  const base = (import.meta.env.BASE_URL || "/").replace(/\/$/, "");
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalized}` || "/";
}

export function isHome(pathname: string) {
  const base = (import.meta.env.BASE_URL || "/").replace(/\/$/, "") || "/";
  const path = pathname.replace(/\/$/, "") || "/";
  return path === base;
}

export function pageLabel(pathname: string) {
  if (isHome(pathname)) return "About";
  const base = (import.meta.env.BASE_URL || "/").replace(/\/$/, "");
  const path = pathname.replace(/\/$/, "") || "/";
  const posts = `${base === "/" ? "" : base}/posts`;
  if (path === posts) return "Posts";
  return "";
}

export function postSlug(id: string) {
  return id.replace(/^\d{4}-\d{2}-\d{2}-/, "");
}

export function postHref(id: string) {
  return withBase(`/posts/${postSlug(id)}/`);
}

export function entryDate(post: CollectionEntry<"posts">) {
  if (post.data.date) return post.data.date;
  const match = post.id.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (match) return new Date(Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3])));
  return new Date(0);
}

export function formatDate(date: Date, style: "short" | "long" = "short") {
  const locale = site.lang || "en";
  if (style === "long") {
    return new Intl.DateTimeFormat(locale, {
      timeZone: "UTC",
      year: "numeric",
      month: "long",
      day: "numeric",
    }).format(date);
  }
  return new Intl.DateTimeFormat(locale, {
    timeZone: "UTC",
    month: "short",
    day: "numeric",
  }).format(date);
}

export function htmlDate(date: Date) {
  return date.toISOString().slice(0, 10);
}

export function sortPosts(posts: CollectionEntry<"posts">[]) {
  return [...posts].sort((a, b) => entryDate(b).valueOf() - entryDate(a).valueOf());
}

export function postsByYear(posts: CollectionEntry<"posts">[]) {
  const groups: { year: number; posts: CollectionEntry<"posts">[] }[] = [];
  for (const post of sortPosts(posts)) {
    const year = entryDate(post).getUTCFullYear();
    const last = groups[groups.length - 1];
    if (!last || last.year !== year) groups.push({ year, posts: [post] });
    else last.posts.push(post);
  }
  return groups;
}
