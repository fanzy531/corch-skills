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

**CRITICAL:** `action_period` sub-fields are ACF `date_picker` type. Must use `Ymd` format **with day** (8 digits). When the MD only provides year+month, default the day to `01`:

```json
"action_period": {
  "period_start": "20241101",
  "period_end": "20250501"
}
```

When MD says `2024年11月—2025年5月`, write `20241101` and `20250501`. Using `2024.11`, `202411`, or any format `strtotime()` cannot parse results in `1970.01`.

## Color Values

All inline styles use the same palette as corch-digest:

| Token | Value |
|---|---|
| ink | `#1A1C1A` |
| ink/85 | `rgba(26,28,26,0.85)` |
| clay | `#C85A3C` |
| sage | `#849682` |
| warmWhite | `#FAF8F3` |


## Timeline Component（时间线组件）

当 MD 章节为时间线类内容（标题含"时间线"、内容由"日期｜事件"组成），使用以下 Tailwind 结构：

### HTML 模板

```html
<div class="timeline relative pl-8 border-l border-ink/10 space-y-12">
  <div class="relative">
    <span class="absolute -left-[37px] top-1.5 w-3 h-3 rounded-full bg-clay ring-4 ring-warmWhite"></span>
    <span class="font-mono text-xs uppercase tracking-widest text-clay font-bold">2024年11月</span>
    <h4 class="font-serif text-xl font-bold text-ink mt-2">社区裁缝铺调研启动</h4>
    <p class="text-sm md:text-base text-ink/75 leading-relaxed mt-2">从成都玉林片区出发，寻找仍在经营的社区裁缝铺……</p>
  </div>
  <!-- 每个时间节点重复此结构 -->
</div>
```

### 样式规则

| 元素 | Tailwind 类 | 说明 |
|---|---|---|
| 容器 | `timeline relative pl-8 border-l border-ink/10 space-y-12` | 左侧竖线 + 缩进 |
| 节点圆点 | `absolute -left-[37px] top-1.5 w-3 h-3 rounded-full bg-clay ring-4 ring-warmWhite` | 陶土色实心点 |
| 日期 | `font-mono text-xs uppercase tracking-widest text-clay font-bold` | 等宽小字、陶土色 |
| 小标题 | `font-serif text-xl font-bold text-ink mt-2` | 衬线加粗 |
| 描述 | `text-sm md:text-base text-ink/75 leading-relaxed mt-2` | 正文灰墨色 |

### 识别规则

- MD 标题：`## 四、项目时间线` 或类似含"时间线"的标题
- 内容模式：`### 2024年11月｜事件标题` + 描述段落
- 每个 `###` 子标题对应一个时间节点
- 日期格式：保持 MD 原文（如 `2024年11月`），不转换成 action_period

### 时间线 vs 普通段落

- 章节标题含"时间线" → 用时间线组件
- 其他章节 → 普通段落结构（p / h3 / img）
