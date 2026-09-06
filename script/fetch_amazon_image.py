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
OUT_DIR = Path("assets/static/amazon")
DATA_FILE = Path("_data/amazon.yml")
POSTS_DIR = Path("_posts")
INCLUDE_URL_RE = re.compile(r'amazon_card\.html[^}]*?\burl="([^"]+)"')
ASIN_RE = re.compile(r"/(?:dp|gp/product|gp/aw/d)/([A-Z0-9]{10})")
OG_RE = re.compile(
    r'<meta[^>]+(?:property|name)=["\']og:image["\'][^>]+content=["\']([^"\']+)',
    re.I,
)
OG_RE_REV = re.compile(
    r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']og:image["\']',
    re.I,
)
PRODUCT_IMG_RE = re.compile(
    r'https://m\.media-amazon\.com/images/I/[A-Za-z0-9%+\-._]+\.(?:jpg|jpeg|png)',
    re.I,
)


def request(url: str) -> tuple[str, bytes]:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": UA, "Accept-Language": "ja,en;q=0.8"},
    )
    with urllib.request.urlopen(req, timeout=20) as res:
        return res.geturl(), res.read()


def extract_asin(url: str) -> str | None:
    m = ASIN_RE.search(url)
    return m.group(1) if m else None


def extract_og_image(html: str) -> str | None:
    for rx in (
        re.compile(r'data-old-hires="(https://m\.media-amazon\.com/images/I/[^"]+)"'),
        re.compile(r'id="landingImage"[^>]+src="(https://m\.media-amazon\.com/images/I/[^"]+)"'),
        re.compile(r'"hiRes"\s*:\s*"(https://m\.media-amazon\.com/images/I/[^"]+)"'),
        re.compile(r'"large"\s*:\s*"(https://m\.media-amazon\.com/images/I/[^"]+)"'),
    ):
        m = rx.search(html)
        if m:
            return m.group(1)
    for rx in (OG_RE, OG_RE_REV):
        m = rx.search(html)
        if not m:
            continue
        url = m.group(1).split(" ")[0].strip()
        if PRODUCT_IMG_RE.fullmatch(url) and "/images/I/" in url:
            return url
    return None


def load_map() -> dict[str, str]:
    mapping: dict[str, str] = {}
    if not DATA_FILE.exists():
        return mapping
    for line in DATA_FILE.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^"([^"]+)":\s+(\S+)\s*$', line)
        if m:
            mapping[m.group(1)] = m.group(2)
    return mapping


def save_map(mapping: dict[str, str]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    lines = [f'"{url}": {name}\n' for url, name in sorted(mapping.items())]
    DATA_FILE.write_text("".join(lines), encoding="utf-8")


def urls_from_posts() -> list[str]:
    urls: list[str] = []
    for path in POSTS_DIR.glob("*.md"):
        urls.extend(INCLUDE_URL_RE.findall(path.read_text(encoding="utf-8")))
    return urls


def fetch_image(url: str) -> tuple[str, Path]:
    final_url, body = request(url)
    asin = extract_asin(final_url)
    if not asin:
        sys.exit(f"ASIN not found: {final_url}")
    html = body.decode("utf-8", errors="ignore")
    image_url = extract_og_image(html)
    if not image_url:
        sys.exit(f"og:image not found: {final_url}")
    if image_url.startswith("//"):
        image_url = "https:" + image_url
    _, img = request(image_url)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    dest = OUT_DIR / f"{asin}.jpg"
    dest.write_bytes(img)
    return asin, dest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("urls", nargs="*")
    args = parser.parse_args()
    urls = args.urls or urls_from_posts()
    if not urls:
        sys.exit("no Amazon URLs found")
    mapping = load_map()
    for url in urls:
        asin, dest = fetch_image(url)
        mapping[url] = dest.name
        print(f"{asin}\t{dest.as_posix()}\t{url}")
    save_map(mapping)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
