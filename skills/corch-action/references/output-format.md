# Output Format — Corch Action

## ACF Field Mapping

| MD Source | ACF Field | Type | Notes |
|---|---|---|---|
| `# ` heading | `post_title` | text | Article title |
| First paragraph | `action_subtitle` | text | Default if no explicit subtitle |
| Metadata block | `action_category` | select | fieldwork / inspirations |
| Location line | `action_location` | text | |
| Time period | `action_period` | group | `{period_start, period_end}` — use Ymd format |
| Initiator | `action_initiator` | text | |
| Type keywords | `action_type` | text | |
| Tags | `action_tags` | repeater | `[{"tag": "..."}]` |
| Proposition | `action_proposition` | textarea | Key sentence |
| ## sections | `action_sections` | repeater | See below |
| 项目成果 | `action_outcomes` | repeater | `{outcome_label, outcome_title, outcome_desc}` |
| 影像记录 | `action_gallery` | repeater | `{gallery_image: media_id, gallery_caption: "..."}` |

## Section Body (section_body)

The `section_body` field is WYSIWYG (HTML). Content rules:

- Paragraphs: `<p>text</p>`
- Inline images (no `{.gallery}`): `<p><img src="media_url" alt="description" style="width:100%;max-width:600px;height:auto;margin:12px 0;"></p>`
- Headings within sections: `<h3>subheading</h3>` or `<h4>subheading</h4>`
- Lists: `<ul><li>item</li></ul>`
- Do NOT include `<style>` or `<script>` blocks

## Date Format

**CRITICAL:** `action_period` sub-fields are ACF `date_picker` type. Must use `Ymd` format **with day** (8 digits):

```json
"action_period": {
  "period_start": "20241101",
  "period_end": "20250501"
}
```

Using `2024.11` (Y.m), `202411` (6-digit Ymd), or any format `strtotime()` cannot parse will result in `1970.01` (epoch fallback). Always use `20241101` (YYYYMMDD).

## Color Values

All inline styles use the same palette as corch-digest:

| Token | Value |
|---|---|
| ink | `#1A1C1A` |
| ink/85 | `rgba(26,28,26,0.85)` |
| clay | `#C85A3C` |
| sage | `#849682` |
| warmWhite | `#FAF8F3` |
