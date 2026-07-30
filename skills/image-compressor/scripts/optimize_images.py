#!/usr/bin/env python3
"""
Optimize images for WordPress upload.
- Landscape (w > h): resize width to 1000px
- Portrait (w <= h): resize width to 1200px
- Only resize if current width exceeds target
- Convert all to JPEG (quality 85, optimize=True)
- Already-optimal JPGs are skipped
"""

import os
import sys
from PIL import Image

LANDSCAPE_W = 1000
PORTRAIT_W = 1200
JPEG_QUALITY = 85


def optimize_image(path):
    """Compress a single image. Returns stats dict or None if skipped."""
    try:
        img = Image.open(path)
    except Exception as e:
        print(f"  ✗ Cannot open {path}: {e}")
        return None

    w, h = img.size
    is_landscape = w > h
    target_w = LANDSCAPE_W if is_landscape else PORTRAIT_W
    needs_resize = w > target_w
    is_jpg = path.lower().endswith(('.jpg', '.jpeg'))

    # Determine output path (force .jpg extension)
    out_path = os.path.splitext(path)[0] + '.jpg'
    if out_path == path and not needs_resize:
        return None  # Already optimal

    if needs_resize:
        ratio = target_w / w
        new_size = (target_w, int(h * ratio))
        img = img.resize(new_size, Image.LANCZOS)

    # Convert RGBA/P to RGB for JPEG
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    img.save(out_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)

    orig_kb = os.path.getsize(path) // 1024
    new_kb = os.path.getsize(out_path) // 1024
    return {
        'file': os.path.basename(path),
        'from': f"{w}x{h}",
        'to': f"{img.width}x{img.height}" if needs_resize else f"{w}x{h}",
        'size': f"{orig_kb}KB → {new_kb}KB",
    }


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 optimize_images.py <images_dir>")
        sys.exit(1)

    img_dir = sys.argv[1]
    if not os.path.isdir(img_dir):
        print(f"Error: {img_dir} is not a directory")
        sys.exit(1)

    files = sorted(os.listdir(img_dir))
    results = []
    skipped = 0

    for fname in files:
        path = os.path.join(img_dir, fname)
        if not os.path.isfile(path):
            continue
        if not fname.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff')):
            continue

        result = optimize_image(path)
        if result:
            results.append(result)
            print(f"  ✓ {result['file']}: {result['from']} → {result['to']}, {result['size']}")
        else:
            skipped += 1

    print(f"\nOptimized: {len(results)}  |  Skipped (already optimal): {skipped}")


if __name__ == '__main__':
    main()
