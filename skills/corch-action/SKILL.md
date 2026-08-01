---
name: corch-action
version: 0.3.0
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
| `action_period` | Date range in "项目时间" section → **YYYYMM01**（日默认1号） |
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

#### 3.1 `{.gallery}` 标记规则

MD 文档中的图片引用有两种写法，决定图片在文章中的位置：

```markdown
<!-- 嵌入正文：图片在 WYSIWYG body 的文字流中 -->
![社区活动照片](图片和附件/01.jpg)

<!-- 放入画廊：缩略图网格 + lightbox -->
![展览现场](图片和附件/07.jpg){.gallery}
```

| 写法 | 字段 | 输出 |
|---|---|---|
| `![alt](path)` | `section_body` | `<img src="media_url" alt="alt">` |
| `![alt](path){.gallery}` | `section_gallery` | media ID 加入数组 |

`{.gallery}` 必须是图片路径**末尾的后缀**，出现在 `)` 之前。

#### 3.2 归属章节

每张图片根据它在 MD 中出现的上下文，归属到**上一个 `## ` 标题**对应的 `action_sections` 项：

- 图片出现在 `## 一、项目简介` 下方 → 归属 sections[0]
- 图片出现在 `## 二、项目缘起` 下方 → 归属 sections[1]
- 以此类推

#### 3.3 处理流程

对文档中的每一张图片：

1. 提取 alt 文本和路径：`![alt](path){.gallery}` → alt="alt", path="path", is_gallery=True
2. 根据 MD 中的位置确定归属章节
3. 将本地路径映射为上传后的 WordPress 媒体 URL + ID
4. 生成输出：
   - **非 gallery 图片**：在 `section_body` 中插入 `<p><img src="media_url" alt="alt" style="width:100%;max-width:600px;height:auto;margin:12px 0;"></p>`
   - **gallery 图片**：将 media ID 加入 `section_gallery` 数组

#### 3.4 边缘情况

| 情况 | 处理 |
|---|---|
| 图片在两个 `##` 之间（严格位于前一个章节文本之后、下一个 `##` 之前） | 归属到**前一个**章节 |
| 同一张图片被多次引用 | 只上传一次，复用 media ID 和 URL |
| `{.gallery}` 写在 alt 内部而非路径末尾 | 不识别，按普通图片处理 |
| 文档末尾、最后一个 `##` 之后的图片（如附录末尾） | 归属到最后一个章节 |
| 图片文件不存在 | 跳过并输出警告，不中断流程 |

#### 3.5 示例

原始 MD：

```markdown
## 一、项目简介

项目从社区的旧衣和裁缝铺出发...

![旧衣收集现场](图片和附件/01.jpg)

## 二、项目缘起

始于一件2001年的手织毛衣...

![大头毛衣](图片和附件/02.jpg)

![展览海报](图片和附件/03.jpg){.gallery}
```

解析后 sections：

```json
{
  "section_number": "01 // PROJECT OVERVIEW",
  "section_title": "项目简介",
  "section_body": "<p>项目从社区的旧衣和裁缝铺出发...</p><p><img src="...01.jpg" alt="旧衣收集现场"></p>",
  "section_gallery": []
},
{
  "section_number": "02 // BACKGROUND",
  "section_title": "项目缘起",
  "section_body": "<p>始于一件2001年的手织毛衣...</p><p><img src="...02.jpg" alt="大头毛衣"></p>",
  "section_gallery": [84]
}
```

### 4. Optimize images

Before uploading, run `scripts/optimize_images.py` on the image directory:

```bash
python3 scripts/optimize_images.py "图片和附件/"
```

The script outputs a summary like:

```
  ✓ 03.jpg: 4000x3000 → 1000x750 (landscape)  2100KB → 180KB
  ✓ 07.jpg: 3000x4000 → 1200x1600 (portrait)  1800KB → 150KB
  - 49 images skipped (already optimal)

Optimized: 2  |  Skipped (already optimal): 49
```

**After compression, present the summary to the user and ask:**

> 图片压缩完成：X 张已优化，Y 张跳过。
> 
> | 文件 | 原尺寸 | 压缩后 |
> |---|---|---|
> | 03.jpg | 4000x3000 | 1000x750, 180KB |
> | 07.jpg | 3000x4000 | 1200x1600, 150KB |
> 
> 继续上传到媒体库？(y/N)

Only proceed to upload on explicit confirmation.

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
      "period_start": "20241101",
      "period_end": "20250501"
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

> **注意：** `date_picker` 字段 `period_start`/`period_end` 必须用 `Ymd` 格式（如 `20241101`；MD 只有年月时，日默认 01），不可用 `2024.11`、`202411` 或任何 strtotime 无法解析的格式

### 7. User confirm

Present summary → select `action_category` (fieldwork / inspirations) → confirm

### 8. Publish

```bash
curl -X POST --user "$WP_USER:$WP_PASSWORD" \
  -H "Content-Type: application/json" \
  -d @payload.json \
  "$WP_SITE/wp-json/clab/v1/publish-action"
```


## WordPress 凭证管理

发布前检查 `~/.corch/config.json` 中是否有 `wordpress` 字段（与 corch-digest 共享）：

```bash
python3 /path/to/corch-skills/scripts/wordpress-credentials.py --status
```

未配置时引导用户一次性认证：

```bash
python3 /path/to/corch-skills/scripts/wordpress-credentials.py --login
```

验证通过后永久保存（权限 600），后续发布无需重复输入。读取凭证：

```bash
python3 /path/to/corch-skills/scripts/wordpress-credentials.py --get
```

## User interaction flow

Same pattern as corch-digest:
1. Check credentials (`--status`) → ask if missing → `--login`
>>>>>>> a7e54af (feat: shared WordPress credential manager — one-time auth, permanent save, used by corch-digest & corch-action)
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
