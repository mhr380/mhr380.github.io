from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageOps

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
DEFAULT_DIR = Path("assets/static")
DEFAULT_MAX = 1600
DEFAULT_QUALITY = 82


def resize_image(path: Path, max_size: int, quality: int) -> None:
    with Image.open(path) as src:
        im = ImageOps.exif_transpose(src)
        w, h = im.size
        if max(w, h) <= max_size:
            print(f"skip {path} ({w}x{h})")
            return
        im.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        ext = path.suffix.lower()
        save_kwargs: dict = {}
        if ext in {".jpg", ".jpeg"}:
            if im.mode not in {"RGB", "L"}:
                im = im.convert("RGB")
            save_kwargs = {
                "quality": quality,
                "optimize": True,
                "progressive": True,
            }
        elif ext == ".png":
            save_kwargs = {"optimize": True}
        elif ext == ".webp":
            save_kwargs = {"quality": quality, "method": 6}
        im.save(path, **save_kwargs)
        print(f"resized {path} {w}x{h} -> {im.size[0]}x{im.size[1]}")


def collect_files(paths: list[Path]) -> list[Path]:
    if not paths:
        if not DEFAULT_DIR.is_dir():
            sys.exit(f"missing {DEFAULT_DIR}")
        paths = [DEFAULT_DIR]
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            files.extend(
                sorted(p for p in path.iterdir() if p.suffix.lower() in IMAGE_EXTS)
            )
        elif path.suffix.lower() in IMAGE_EXTS:
            files.append(path)
        else:
            sys.exit(f"not an image: {path}")
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Resize blog images for the web")
    parser.add_argument("paths", nargs="*", type=Path)
    parser.add_argument("--max", type=int, default=DEFAULT_MAX)
    parser.add_argument("--quality", type=int, default=DEFAULT_QUALITY)
    args = parser.parse_args()
    for path in collect_files(args.paths):
        resize_image(path, args.max, args.quality)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
