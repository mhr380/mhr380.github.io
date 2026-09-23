import amazon from "../data/amazon.json" with { type: "json" };
import links from "../data/links.json" with { type: "json" };
import site from "../data/site.json" with { type: "json" };

const RELATIVE_RE = /\{\{\s*['"]([^'"]+)['"]\s*\|\s*relative_url\s*\}\}/g;

function prefix(path) {
  if (/^https?:\/\//i.test(path)) return path;
  const base = (process.env.ASTRO_BASE || site.pathPrefix || "/").replace(/\/$/, "");
  const normalized = path.startsWith("/") ? path : `/${path}`;
  return `${base}${normalized}`;
}

function esc(value = "") {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function attrs(raw) {
  const out = {};
  for (const match of raw.matchAll(/(\w+)="([^"]*)"/g)) out[match[1]] = match[2];
  return out;
}

function amazonMeta(url) {
  const entry = amazon[url];
  if (!entry) return { image: "", title: "", brand: "" };
  if (typeof entry === "string") return { image: entry, title: "", brand: "" };
  return {
    image: entry.image || "",
    title: entry.title || "",
    brand: entry.brand || "",
  };
}

function cardImage(file, folder) {
  if (!file) return "";
  if (file.includes("://")) return file;
  return prefix(`/assets/static/${folder}/${file}`);
}

function ctaFor(url) {
  if (url.includes("daisonet.com")) return "ダイソーで見る";
  if (url.includes("sony.jp")) return "ソニーで見る";
  if (url.includes("muji.com")) return "無印良品で見る";
  if (url.includes("wexley.com")) return "Wexleyで見る";
  return "サイトで見る";
}

function cardHtml({ href, image, title, brand, cta, rel }) {
  return `<div class="amazon-card"><a class="amazon-card-link" href="${esc(href)}" target="_blank" rel="${rel}"><span class="amazon-card-image"><img src="${esc(image)}" alt="${esc(title)}"></span><span class="amazon-card-body"><span class="amazon-card-title">${esc(title)}</span>${brand ? `<span class="amazon-card-brand">${esc(brand)}</span>` : ""}<span class="amazon-card-cta">${esc(cta)}</span></span></a></div>`;
}

function renderInclude(name, a) {
  if (name === "image") {
    const src = prefix(`/assets/static/${a.file}`);
    const alt = a.alt || "Image";
    return `<a href="${esc(src)}" target="_blank" class="image"><img src="${esc(src)}" alt="${esc(alt)}"></a>`;
  }

  if (name === "amazon_card") {
    const meta = amazonMeta(a.url);
    return cardHtml({
      href: a.url,
      image: cardImage(a.image || meta.image, "amazon"),
      title: a.title || meta.title,
      brand: a.brand || meta.brand,
      cta: "Amazonで見る",
      rel: "noopener sponsored",
    });
  }

  if (name === "link_card") {
    const card = links[a.url] || {};
    return cardHtml({
      href: a.url,
      image: cardImage(a.image || card.image, "links"),
      title: a.title || card.title || "",
      brand: a.brand || card.brand || "",
      cta: a.cta || ctaFor(a.url),
      rel: "noopener noreferrer",
    });
  }

  if (name === "github_card") {
    const slug = (a.url.split("github.com/")[1] || "").split(/[?#]/)[0].replace(/\.git$/, "");
    const [owner = "", repo = ""] = slug.split("/");
    const title = a.title || `${owner}/${repo}`;
    const image = a.image || `https://github.com/${owner}.png?size=240`;
    return cardHtml({
      href: a.url,
      image,
      title,
      brand: a.brand || owner,
      cta: "GitHubで見る",
      rel: "noopener noreferrer",
    });
  }

  return "";
}

export function expandJekyll(markdown) {
  return markdown.replace(RELATIVE_RE, (_, p) => prefix(p)).replace(
    /^[ \t]*\{%\s*include\s+(\w+)\.html\s+([^%]*)%\}[ \t]*$/gm,
    (_, name, raw) => renderInclude(name, attrs(raw)) || _,
  );
}
