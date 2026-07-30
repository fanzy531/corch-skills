---
name: corch-digest
version: 1.4.0
description: Read articles from a URL, digest and rewrite content, save images to a local folder, output in a structured Tailwind CSS layout, and optionally publish directly to WordPress voice CPT (他山之石). Use when the user provides an article URL and asks for a digest, summary, rewritten version, or wants to publish to the site.
---

# Corch Digest

## 0. Input types

### Web article (default)
- Input: URL to a web page
- Process: Fetch HTML, extract article body, images, metadata
- Output: Standard corch-digest flow

### PDF document
- Input: Local file path or URL to a `.pdf` file
- Process:
  1. If URL, download the PDF first
  2. Use `markitdown` skill to convert PDF → Markdown text
  3. The extracted text becomes the article body
  4. Extract metadata from the document (title, author, date if available)
  5. Download any embedded/attached images if possible
- Limitation: PDF layout/formatting fidelity depends on markitdown

### Foreign language
- If the source text (web or PDF) is not in Chinese:
  1. Extract text as usual (via HTML fetch or markitdown)
  2. During **Step 4 (Digest & rewrite)**, translate the content to Chinese
  3. Keep the original publication name and author in metadata
  4. Note the original language in `voice_curator_note`
- The translation is done by the AI model itself during the rewrite step

## Workflow

### 1. Fetch

Read the full article from the provided URL. Use `curl` or `requests` to fetch the HTML. Extract the article body — headline, author, publication date, body paragraphs, images, captions.

### 2. Extract metadata

From the original article, identify:

| Field | Description |
|---|---|
| `title` | Article headline |
| `author` | Byline |
| `publication` | Source site / publication name |
| `original_url` | The provided URL |
| `published_date` | Article date (YYYY.MM.DD) |
| `keywords` | 3-6 tags inferred from content (e.g. #基层治理 #社区微更新) |
| `images` | All `<img>` src URLs and their captions/alt text |
| `curator_summary` | A 1-2 sentence summary of the article's argument for the 导读 |
| `translator` | Reprint translator credit (default: "corch 外部观察员译") |
| `reprint_date` | Current date (YYYY.MM.DD) |
| `copyright` | Standard copyright notice |

### 3. Download images

Pass all image URLs to `scripts/download_images.py <urls_json> <images_dir>`. Use the returned URL-to-local-path mapping to update `<img>` src attributes to relative local paths.

### 4. Digest & rewrite

- Keep the article's core facts, data, and direct quotes intact.
- Condense redundant phrasing while preserving the original section structure.
- Maintain the original reporting tone — plain Chinese, factual.
- Identify one key quote per section for Pull Quote formatting.
- Write a **导读 (Curator's Reflection)** paragraph: summarize the article's key argument and why it matters, in the curator's voice.

### 5. Generate body HTML fragment

Build the self-contained HTML fragment using the templates in `references/output-format.md` (§1). All styles are inline — **no `<style>` block, no `<script>`, no Tailwind or external classes**.

Structure in order:

1. Container `<div style="font-family:...; max-width:720px;">`
2. H2 headings with inline styles
3. Paragraphs — first character wrapped in `<span>` for drop cap
4. Figures with inline-styled `<figure>` and `<figcaption>`
5. Pull quotes with inline-styled `<blockquote>`
6. Unordered lists with inline styles
7. Source line — publication + original URL
8. `[ TRANSCRIPTION ENDS ]` marker

### 6. Deliver

Output the body HTML fragment. If `wp_site` is not set, also output the metadata (导读、关键词、出处等) as structured text for manual entry.

## 8. Publish to WordPress (voice CPT)

After generating all content, optionally publish directly to WordPress.

### 8.0 User interaction flow

**Before starting publish, follow this conversation pattern:**

1. **Check auth**: If `wp_site`/`wp_user`/`wp_password` are not provided:
   - Tell the user the article content is ready
   - Ask them to provide: WordPress site URL, username, and Application Password
   - Guide them: "登录 WP 后台 → 用户 → 个人资料 → Application Passwords → 生成一个"
   - If they prefer not to set up auth now, fall back to **output mode** (deliver HTML + metadata only)

2. **Select category**: Present the 5 `voice_category` options (see 8.3) and recommend one based on article content. Ask user to confirm.

3. **Confirm before publish**: Build the full payload summary and present it to the user:
   ```
   标题: {title}
   分类: {voice_category}
   出处: {publication}
   原作者: {author}
   图片: {count} 张
   标签: {keywords}
   ```
   Ask: "确认发布？(y/N)". Only proceed on explicit yes.

4. **If user says no or hesitates**: Fall back to output mode (deliver HTML + metadata for manual use).

### 8.1 Upload images to media library

Upload all locally downloaded images to WordPress via REST API.

```bash
# For each image in the images directory
curl -X POST \
  --user "$WP_USER:$WP_APP_PASSWORD" \
  -H "Content-Disposition: attachment; filename=\"$FILENAME\"" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@$LOCAL_PATH" \
  "$WP_SITE/wp-json/wp/v2/media"
```

Collect the returned media IDs. Build a mapping of `local_path -> media_id` and `local_path -> media_url`.

### 8.2 Update image URLs in body HTML

Replace all `<img src="images/...">` with the WordPress media URLs from step 8.1.

### 8.3 Select voice category

**`voice_category` 是必填字段。** 从以下选项中选择最贴近文章内容的分类：

| slug | 名称 | 适用内容 |
|---|---|---|
| `community-building` | 社区营造 | 社区营造综合案例、理论、政策 |
| `autonomy` | 地方自治 | 社区自治、居民自组织、地方治理 |
| `social-innovation` | 社会创新 | 社会企业、创新模式、跨界协作 |
| `methodology` | 设计方法论 | 参与式设计、行动研究、工具方法 |
| `informal` | 非正式空间 | 街头空间、临时用途、边缘社区 |

将所选 slug 填入 payload 的 `voice_category` 字段。

### 8.4 Build publish payload

```json
{
  "title": "Article headline",
  "content": "<full HTML body with updated image URLs>",
  "excerpt": "Curator's reflection (导读) — first 100-200 chars",
  "status": "publish",
  "featured_media": 123,
  "acf": {
    "voice_category": "community-building",
    "voice_subtitle": "Curator subtitle or lead-in",
    "voice_keywords": [{"keyword": "标签1"}, {"keyword": "标签2"}],
    "voice_publication": "Source publication name",
    "voice_original_author": "Original author",
    "voice_translator": "Reprint translator credit",
    "voice_curator_note": "Full curator's reflection"
  }
}
```

### 8.4 Publish

```bash
curl -X POST \
  --user "$WP_USER:$WP_PASSWORD" \
  -H "Content-Type: application/json" \
  -d @publish-payload.json \
  "$WP_SITE/wp-json/clab/v1/publish-voice"
```

- **推荐：** `WP_PASSWORD` 为 Application Password（WP 后台 → 用户 → 个人资料 → Application Passwords 生成）
- **降级：** 直接使用 WordPress 登录密码（安全性较低，但通用）
- 两种方式都走 HTTP Basic Auth，curl 的 `--user` 参数兼容两者

### 8.5 Verify

Check the response for `"code": 200`. Open the returned `edit_link` to review in WordPress admin.

## Input parameters

| Param | Description | Default |
|---|---|---|
| `url` | Article URL to process | required |
| `images_dir` | Directory for downloaded images | `./images/` |
| `translator` | Reprint translator credit | `"corch 外部观察员译"` |
| `reprint_date` | Reprint date | current date |
| `wp_site` | WordPress site URL (e.g. `https://c-lab.org`) | `""` (skip publish) |
| `wp_user` | WordPress username | `""` |
| `wp_password` | WordPress password — 推荐用 Application Password（后台生成），降级用登录密码 | `""` |

When `wp_site` is empty, the skill falls back to output-only mode (HTML + metadata). When provided, it completes the full publish-to-WordPress flow.

## Dependencies

The following tools must be available in the execution environment for PDF input support.

### Required: pdftotext (poppler)

Used for extracting text from PDF files. Installed via:

```bash
brew install poppler         # macOS
apt-get install poppler-utils # Ubuntu/Debian
```

Verify: `which pdftotext`

### Alternative: markitdown (Python)

Provides broader document support (DOCX, PPTX, XLSX, OCR). Install via:

```bash
pip install markitdown
```

Usage in skill:

```python
from markitdown import MarkItDown
md = MarkItDown()
result = md.convert("/path/to/file.pdf")
text = result.text_content
```

### Table: PDF extraction decision

| Condition | Tool | Notes |
|---|---|---|
| pdftotext available | `pdftotext input.pdf -` | Best for text PDFs |
| markitdown available | `MarkItDown.convert()` | Better for mixed content |
| Neither | Fallback to AI model reading raw PDF | May fail on compressed PDFs |

### OCR (scan-only PDFs)

If the PDF is a scan (no extractable text layer), neither tool will work. Options:
- Use `markitdown` with OCR dependencies configured
- Use a dedicated OCR service
- Inform the user that scanned PDFs cannot be processed

## Scripts


### `scripts/download_images.py`

Downloads article images to a local directory.

```
python3 scripts/download_images.py <urls_json> <output_dir>
```

- `urls_json`: JSON array of image URLs (any protocol) as a string.
- `output_dir`: Target directory (created if missing).
- Prints a JSON mapping of `{original_url: local_path}` to stdout.
- Failed downloads are logged to stderr but do not halt execution.
- Uses a safe filename derived from the URL path; falls back to MD5 hash on collision.

## References

- `references/output-format.md` — Complete output spec covering HTML fragment (§1), plain-text 导读 (§2), plain-text metadata spec (§3), color tokens, custom class definitions, and checklist.
