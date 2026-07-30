---
name: image-compressor
version: 0.1.0
description: Batch resize and compress images for web publishing. Landscape → 1000w, Portrait → 1200w, all to JPEG quality 85.
---

# Image Compressor

## Usage

```bash
python3 scripts/compress.py <images_dir>
```

## Rules

| Image type | Target width |
|---|---|
| Landscape (w > h) | 1000px |
| Portrait (w ≤ h) | 1200px |

- Only resize if current width exceeds target
- Convert all to JPEG (quality 85, optimize=True)
- Non-JPG inputs (PNG, WebP, etc.) → JPEG
- Already-optimal JPGs are skipped

## Dependencies

```bash
pip install Pillow
```
