#!/usr/bin/env python3
"""Optimize action images while keeping a source-to-output manifest.

Landscape images use a 1200px target width; portrait and square images use
1000px. JPEG quality is 85. Use --output-dir to keep originals untouched.
"""

import argparse
import json
import os
import tempfile
from pathlib import Path

from PIL import Image, ImageOps


LANDSCAPE_W = 1200
PORTRAIT_W = 1000
JPEG_QUALITY = 85
SUPPORTED = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp", ".tif", ".tiff"}


def output_path(source, source_root, output_root):
    if output_root is None:
        candidate = source.with_suffix(".jpg")
        if candidate == source:
            return candidate
        if not candidate.exists():
            return candidate
        index = 1
        while True:
            candidate = source.with_name(f"{source.stem}-optimized{index if index > 1 else ''}.jpg")
            if not candidate.exists():
                return candidate
            index += 1
    relative = source.relative_to(source_root).with_suffix(".jpg")
    return output_root / relative


def prepare_rgb(image):
    if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
        rgba = image.convert("RGBA")
        canvas = Image.new("RGB", rgba.size, "white")
        canvas.paste(rgba, mask=rgba.getchannel("A"))
        return canvas
    if image.mode not in ("RGB", "L"):
        return image.convert("RGB")
    return image


def save_atomic(image, target):
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f"{target.stem}.", suffix=".tmp", dir=target.parent)
    os.close(fd)
    try:
        image.save(temp_name, "JPEG", quality=JPEG_QUALITY, optimize=True)
        os.replace(temp_name, target)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def optimize_image(source, source_root, output_root):
    try:
        with Image.open(source) as opened:
            image = ImageOps.exif_transpose(opened)
            if getattr(image, "is_animated", False):
                image.seek(0)
            image.load()
            width, height = image.size
            target_width = LANDSCAPE_W if width > height else PORTRAIT_W
            needs_resize = width > target_width
            is_jpeg = source.suffix.lower() in {".jpg", ".jpeg"}
            needs_conversion = not is_jpeg or image.mode not in ("RGB", "L")
            target = output_path(source, source_root, output_root)

            if output_root is None and target == source and not needs_resize and not needs_conversion:
                return {"source": str(source), "output": str(source), "skipped": True,
                        "from": f"{width}x{height}", "to": f"{width}x{height}"}

            if needs_resize:
                ratio = target_width / width
                image = image.resize((target_width, max(1, int(height * ratio))), Image.Resampling.LANCZOS)
            image = prepare_rgb(image)
            save_atomic(image, target)
            orig_kb = source.stat().st_size // 1024
            new_kb = target.stat().st_size // 1024
            size_text = f"{width}x{height} -> {image.width}x{image.height}"
            return {"source": str(source), "output": str(target), "skipped": False,
                    "from": f"{width}x{height}", "to": f"{image.width}x{image.height}",
                    "size": size_text, "file_size": f"{orig_kb}KB -> {new_kb}KB"}
    except Exception as exc:
        return {"source": str(source), "error": str(exc)}


def main():
    parser = argparse.ArgumentParser(description="Optimize images for corch-action")
    parser.add_argument("images_dir", help="directory containing source images")
    parser.add_argument("--output-dir", help="write JPEGs here and keep source files unchanged")
    parser.add_argument("--manifest", help="write source-to-output JSON mapping")
    args = parser.parse_args()

    source_root = Path(args.images_dir).expanduser().resolve()
    if not source_root.is_dir():
        parser.error(f"not a directory: {source_root}")
    output_root = Path(args.output_dir).expanduser().resolve() if args.output_dir else None
    if output_root == source_root:
        parser.error("--output-dir must differ from images_dir")

    results = []
    for source in sorted(path for path in source_root.rglob("*") if path.is_file() and path.suffix.lower() in SUPPORTED):
        if output_root and output_root in source.parents:
            continue
        result = optimize_image(source, source_root, output_root)
        results.append(result)
        relative = source.relative_to(source_root)
        if "error" in result:
            print(f"  x {relative}: {result['error']}")
        elif result["skipped"]:
            print(f"  - {relative}: already optimal")
        else:
            print(f"  + {relative}: {result['from']} -> {result['to']} ({result['file_size']}) => {result['output']}")

    if args.manifest:
        manifest = Path(args.manifest).expanduser()
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_text(json.dumps({"version": 1, "images": results}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    failed = sum("error" in result for result in results)
    optimized = sum(not result.get("skipped") and "error" not in result for result in results)
    skipped = sum(result.get("skipped", False) for result in results)
    print(f"\nOptimized: {optimized} | Skipped: {skipped} | Failed: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
