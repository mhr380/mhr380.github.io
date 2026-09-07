from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)
OUT_DIR = Path("assets/static/links")
DATA_FILE = Path("_data/links.yml")
POSTS_DIR = Path("_posts")
INCLUDE_URL_RE = re.compile(r'link_card\.html[^}]*?\burl="([^"]+)"')


def request(url: str) -> tuple[str, bytes]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept-Language": "ja,en;q=0.8"},
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        return res.geturl(), res.read()


def meta(html: str, prop: str) -> str | None:
    m = re.search(
        rf'<meta[^>]+(?:property|name)=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']+)',
        html,
        re.I,
    )
    if m:
        return m.group(1)
    m = re.search(
        rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']{re.escape(prop)}["\']',
        html,
        re.I,
    )
    return m.group(1) if m else None


def yaml_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def load_map() -> dict[str, dict[str, str]]:
    mapping: dict[str, dict[str, str]] = {}
    if not DATA_FILE.exists():
        return mapping
    current: str | None = None
    for line in DATA_FILE.read_text(encoding="utf-8").splitlines():
        head = re.match(r'^"([^"]+)":\s*$', line)
        if head:
            current = head.group(1)
            mapping[current] = {}
            continue
        if current is None:
            continue
        field = re.match(r'^\s+(\w+):\s+"(.*)"\s*$', line)
        if field:
            mapping[current][field.group(1)] = field.group(2).replace('\\"', '"')
    return mapping


def save_map(mapping: dict[str, dict[str, str]]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for url, fields in sorted(mapping.items()):
        lines.append(f"{yaml_quote(url)}:\n")
        for key in ("image", "title", "brand"):
            if key in fields:
                lines.append(f"  {key}: {yaml_quote(fields[key])}\n")
    DATA_FILE.write_text("".join(lines), encoding="utf-8")


def urls_from_posts() -> list[str]:
    urls: list[str] = []
    for path in POSTS_DIR.glob("*.md"):
        urls.extend(INCLUDE_URL_RE.findall(path.read_text(encoding="utf-8")))
    return urls


def slug_from_url(url: str) -> str:
    path = url.split("?", 1)[0].rstrip("/").split("/")[-1]
    return re.sub(r"[^A-Za-z0-9_-]", "_", path) or "link"


def fetch_card(url: str) -> dict[str, str]:
    final_url, body = request(url)
    html = body.decode("utf-8", errors="ignore")
    title = meta(html, "og:title") or meta(html, "twitter:title")
    image_url = meta(html, "og:image") or meta(html, "twitter:image")
    brand = meta(html, "og:site_name")
    if not image_url:
        sys.exit(f"og:image not found: {final_url}")
    if image_url.startswith("//"):
        image_url = "https:" + image_url
    elif image_url.startswith("http://"):
        image_url = "https://" + image_url[len("http://") :]
    _, img = request(image_url)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUT_DIR / f"{slug_from_url(url)}.jpg"
    dest.write_bytes(img)
    fields = {"image": dest.name}
    if title:
        fields["title"] = re.sub(r"\s+", " ", title).strip()
    if brand:
        if "ダイソー" in brand:
            brand = "ダイソー"
        fields["brand"] = brand
    return fields


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="*")
    args = parser.parse_args()
    urls = args.urls or urls_from_posts()
    if not urls:
        sys.exit("no link-card URLs found")
    mapping = load_map()
    for url in urls:
        fields = fetch_card(url)
        mapping[url] = fields
        print(f"{fields.get('title', '')}\t{fields['image']}\t{url}")
    save_map(mapping)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
