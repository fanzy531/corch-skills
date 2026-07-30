---
name: corch-action
version: 0.1.0
description: Parse structured markdown project documents, convert to WordPress action CPT (实践现场) with all ACF fields (repeater, gallery, group), and publish. Use when the user provides a markdown project file and asks to publish it as an action article.
---

# Corch Action

## 0. Input

- **Input**: Local `.md` file path (structured project document)
- **Images**: Co-located `图片和附件/` directory, or paths referenced in the MD
- **Convention**: `{.gallery}` suffix on image references → `section_gallery` field; unmarked images → embedded in `section_body`

## Workflow

### 1. Parse metadata

Extract from the MD document:

| Field | Source |
|---|---|
| `title` | `# ` heading, or filename |
| `action_subtitle` | First paragraph or subtitle line |
| `action_category` | `fieldwork` or `inspirations` (ask user if unclear) |
| `action_location` | Text after "项目地点" or similar |
| `action_period` | Date range in "项目时间" section |
| `action_initiator` | "发起人" section |
| `action_type` | Keywords from the opening metadata block |
| `action_tags` | Tags/keywords listed in the document |
| `action_proposition` | Core value statement → select key sentence |
| `action_outcomes` | "项目成果" section → outcome cards |

### 2. Parse sections

Each `## ` heading (excluding the document title and outcomes/appendix) becomes an `action_sections` item:

```json
{
  "section_number": "01 // PROJECT OVERVIEW",
  "section_title": "项目概览",
  "section_body": "<p>... paragraphs with inline <img>...</p>",
  "section_gallery": [21, 22]  ← media IDs for {.gallery} images
}
```

### 3. Parse images

Scan all `![alt](path)` references in the MD:

- **Without `{.gallery}`** → embed in `section_body` as `<img src="media_url">`
- **With `{.gallery}`** → add to `section_gallery` array (media IDs)

Images outside any section heading (e.g. appendix) → inline in the appendix section_body.

### 4. Optimize images

Before uploading, run `scripts/optimize_images.py` on all images:

| Image type | Target width |
|---|---|
| Landscape (w > h) | 1000px |
| Portrait (w ≤ h) | 1200px |

- Only resize if current width exceeds target
- Convert all to JPEG (quality 85, optimize=True)
- Already-optimal JPGs are skipped

### 5. Upload images

Upload optimized images to WordPress media library:

```bash
curl -X POST --user "$WP_USER:$WP_PASSWORD" \
  -F "file=@image.jpg" \
  "$WP_SITE/wp-json/wp/v2/media"
```

Collect returned media IDs for gallery and inline references.

### 6. Build publish payload

```json
{
  "title": "【关于穿的记忆】 社区参与式艺术实践",
  "content": "",
  "excerpt": "Brief project summary",
  "status": "publish",
  "featured_media": 123,
  "acf": {
    "action_subtitle": "副标题",
    "action_category": "fieldwork",
    "action_location": "成都社区",
    "action_period": {
      "period_start": "202411",
      "period_end": "202505"
    },
    "action_initiator": "发起人",
    "action_type": "项目类型",
    "action_tags": [{"tag": "标签1"}, {"tag": "标签2"}],
    "action_proposition": "核心价值主张",
    "action_sections": [...],
    "action_outcomes": [...],
    "action_gallery": [...]
  }
}
```

> **注意：** `date_picker` 字段 `period_start`/`period_end` 必须用 `Ymd` 格式（如 `202411`），不可用 `2024.11`

### 7. User confirm

Present summary → select `action_category` (fieldwork / inspirations) → confirm

### 8. Publish

```bash
curl -X POST --user "$WP_USER:$WP_PASSWORD" \
  -H "Content-Type: application/json" \
  -d @payload.json \
  "$WP_SITE/wp-json/clab/v1/publish-action"
```

## User interaction flow

Same pattern as corch-digest:
1. Check auth → ask if missing
2. Select category (fieldwork / inspirations)
3. Confirm before publish

## Dependencies

### Image processing: Pillow

```bash
pip install Pillow
```

### PDF extraction (if input is PDF)

Same as corch-digest: poppler (pdftotext + pdfimages)

## Scripts

### `scripts/optimize_images.py`

Batch optimize images before upload:

```
python3 scripts/optimize_images.py <images_dir>
```

Scans all images in the directory, resizes according to landscape/portrait rules, converts to JPG, saves optimized versions.

### `scripts/download_images.py`

Same as corch-digest — reuse from corch-digest/skills.

## References

- `references/output-format.md` — ACF field mapping and HTML body format
