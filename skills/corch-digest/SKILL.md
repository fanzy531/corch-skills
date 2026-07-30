---
name: corch-digest
description: Read articles from a URL, digest and rewrite content, save images to a local folder, output in a structured Tailwind CSS layout, and optionally publish directly to WordPress voice CPT (他山之石). Use when the user provides an article URL and asks for a digest, summary, rewritten version, or wants to publish to the site.
---

# Corch Digest

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

### 6. Output plain text pieces

Generate two separate plain text outputs (no HTML):

**导读 (Curator's Reflection)** — prefixed with `【corch 导读 / Curator's Reflection】`

**元数据 Spec** — structured with the fields from Step 2, following the format in `references/output-format.md` (§3).

### 7. Deliver

Present all three outputs:

| # | What | Format | Where it goes |
|---|---|---|---|
| 1 | Body HTML fragment | HTML (inline styles) | WordPress post_content or any CMS |
| 2 | 导读 | Plain text | WordPress excerpt / 摘要 or lead-in |
| 3 | 元数据 Spec | Plain text | WordPress tags, categories, custom fields |

## 8. Publish to WordPress (voice CPT)

After generating all content, optionally publish directly to WordPress.

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

### 8.3 Build publish payload

```json
{
  "title": "Article headline",
  "content": "<full HTML body with updated image URLs>",
  "excerpt": "Curator's reflection (导读) — first 100-200 chars",
  "status": "publish",
  "featured_media": 123,
  "acf": {
    "voice_category": "term_slug_from_taxonomy",
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
