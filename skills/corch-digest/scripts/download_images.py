#!/usr/bin/env python3
"""Download images from URLs to a local directory.

Usage:
    python3 download_images.py <urls_json> <output_dir>

Args:
    urls_json: JSON array of image URL strings.
    output_dir: Target directory (created if missing).

Outputs a JSON mapping of {original_url: local_path} to stdout.
"""

import hashlib
import json
import os
import sys
import urllib.parse
from pathlib import Path
from urllib.request import urlopen, Request


def _safe_filename(url: str) -> str:
    """Extract a safe filename from a URL."""
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    basename = os.path.basename(path)
    if basename and '.' in basename:
        # strip query params
        return basename.split('?')[0]
    # fallback: hash the URL
    return hashlib.md5(url.encode()).hexdigest() + '.jpg'


def download_images(image_urls: list[str], output_dir: str) -> dict[str, str]:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    mapping: dict[str, str] = {}
    seen = set()

    for url in image_urls:
        if not url or not url.startswith(('http://', 'https://')):
            continue
        try:
            filename = _safe_filename(url)
            dest = out_path / filename

            # avoid collisions
            while dest.name in seen:
                stem = dest.stem
                suffix = dest.suffix or '.jpg'
                dest = out_path / f"{stem}_{hashlib.md5(url.encode()).hexdigest()[:8]}{suffix}"

            seen.add(dest.name)

            req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urlopen(req, timeout=30) as resp:
                data = resp.read()
            dest.write_bytes(data)

            mapping[url] = str(dest)
        except Exception as e:
            print(f"[WARN] Failed to download {url}: {e}", file=sys.stderr)

    return mapping


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: download_images.py <urls_json> <output_dir>", file=sys.stderr)
        sys.exit(1)

    urls = json.loads(sys.argv[1])
    out_dir = sys.argv[2]
    result = download_images(urls, out_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
