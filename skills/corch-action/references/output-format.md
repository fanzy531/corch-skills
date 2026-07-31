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

当 MD 章节为时间线类内容（标题含"时间线"、内容由"日期｜事件"组成），使用以下 Tailwind 结构。每个时间节点可包含 0-N 张图片。

### HTML 模板（含图片节点）

```html
<div class="timeline relative pl-8 border-l border-ink/10 space-y-14">
  <!-- 时间节点 1：无图 -->
  <div class="relative">
    <span class="absolute -left-[37px] top-1.5 w-3 h-3 rounded-full bg-clay ring-4 ring-warmWhite"></span>
    <span class="font-mono text-xs uppercase tracking-widest text-clay font-bold">2024年11月</span>
    <h4 class="font-serif text-xl font-bold text-ink mt-2">社区裁缝铺调研启动</h4>
    <p class="text-sm md:text-base text-ink/75 leading-relaxed mt-2">从成都玉林片区出发，寻找仍在经营的社区裁缝铺……</p>
  </div>

  <!-- 时间节点 2：带图片（figure 结构，健壮） -->
  <div class="relative">
    <span class="absolute -left-[37px] top-1.5 w-3 h-3 rounded-full bg-clay ring-4 ring-warmWhite"></span>
    <span class="font-mono text-xs uppercase tracking-widest text-clay font-bold">2025年1月</span>
    <h4 class="font-serif text-xl font-bold text-ink mt-2">衡门画廊旧衣展</h4>
    <p class="text-sm md:text-base text-ink/75 leading-relaxed mt-2">约50件旧衣按照年份排列，形成一条时间线……</p>
    <figure class="mt-5 border border-ink/10 p-2 bg-warmWhite">
      <img src="https://c-lab.org/wp-content/uploads/2026/07/05.jpg"
           alt="衡门画廊展览现场"
           loading="lazy"
           class="w-full h-auto block">
      <figcaption class="font-mono text-[12px] text-ink/50 text-center mt-2">衡门画廊展览现场</figcaption>
    </figure>
  </div>

  <!-- 时间节点 3：多图（grid 2 列） -->
  <div class="relative">
    <span class="absolute -left-[37px] top-1.5 w-3 h-3 rounded-full bg-clay ring-4 ring-warmWhite"></span>
    <span class="font-mono text-xs uppercase tracking-widest text-clay font-bold">2025年4月</span>
    <h4 class="font-serif text-xl font-bold text-ink mt-2">不弃升级再造中心巡展</h4>
    <p class="text-sm md:text-base text-ink/75 leading-relaxed mt-2">……</p>
    <div class="mt-5 grid grid-cols-1 sm:grid-cols-2 gap-3">
      <figure class="border border-ink/10 p-2 bg-warmWhite">
        <img src="..." alt="..." loading="lazy" class="w-full h-auto block">
      </figure>
      <figure class="border border-ink/10 p-2 bg-warmWhite">
        <img src="..." alt="..." loading="lazy" class="w-full h-auto block">
      </figure>
    </div>
  </div>
</div>
```

### 结构健壮性规则（重要）

1. **图片必须包在 `<figure>` 内**，不使用裸 `<img>` —— `wpautop` 不会拆分 figure，布局稳定
2. **`<img>` 必须有 `loading="lazy"` 和 `alt`**（alt 取自 MD 的 `![alt](path)`）
3. **图片宽度**：单图 `w-full h-auto block`；多图 `grid grid-cols-1 sm:grid-cols-2 gap-3` 包 figure
4. **figure 边框**：`border border-ink/10 p-2 bg-warmWhite`（与主题插图风格一致）
5. **figcaption 可选**：MD 图片 alt 非空时输出 `figcaption`，空则省略
6. **节点间距**：容器 `space-y-14`，多图节点与文字间距 `mt-5`
7. **禁止裸 div 嵌套图片**：图片一律 figure 包裹，即使模板直出 div 也保持语义

### 样式规则

| 元素 | Tailwind 类 | 说明 |
|---|---|---|
| 容器 | `timeline relative pl-8 border-l border-ink/10 space-y-14` | 左侧竖线 + 缩进 |
| 节点圆点 | `absolute -left-[37px] top-1.5 w-3 h-3 rounded-full bg-clay ring-4 ring-warmWhite` | 陶土色实心点 |
| 日期 | `font-mono text-xs uppercase tracking-widest text-clay font-bold` | 等宽小字、陶土色 |
| 小标题 | `font-serif text-xl font-bold text-ink mt-2` | 衬线加粗 |
| 描述 | `text-sm md:text-base text-ink/75 leading-relaxed mt-2` | 正文灰墨色 |
| 单图 figure | `mt-5 border border-ink/10 p-2 bg-warmWhite` | 插图边框 |
| 多图容器 | `mt-5 grid grid-cols-1 sm:grid-cols-2 gap-3` | 响应式两列 |

### 时间线 vs 普通段落

- 章节标题含"时间线" → 用时间线组件
- 其他章节 → 普通段落结构（p / h3 / figure img）


## Timeline Detection（时间线识别规则）

### 判定条件（满足任一即判定为时间线章节）

1. **标题关键词**：`##` 标题含以下任一 → 时间线
   - `时间线` / `时间轴` / `timeline`
   - `大事记` / `历程` / `进展` / `时间脉络`

2. **结构模式**（主要依据）：章节内 **≥2 个** `###` 子标题匹配日期开头模式

```python
# 日期开头模式（子标题）
DATE_PREFIX = [
    r'^\d{4}年\d{1,2}月',            # 2024年11月
    r'^\d{4}年\d{1,2}月至\d{1,2}月',  # 2024年11月至12月
    r'^\d{4}[.\-/]\d{1,2}',          # 2024.11 / 2024-11 / 2024/11
    r'^\d{4}年\d{1,2}月—\d{4}年\d{1,2}月',  # 2024年11月—2025年5月
]
```

### 识别流程

```
扫描所有 ## 章节
  │
  ├─ 标题含时间线关键词 → 判定时间线
  │
  └─ 否则统计该章节 ### 子标题
       ├─ 日期开头子标题 ≥2 个 → 判定时间线
       └─ 日期开头子标题 <2 个 → 普通章节（即使标题像时间线，只有1个节点不算）
```

### 节点映射规则

| MD 元素 | 时间线输出 |
|---|---|
| `### 2024年11月｜社区裁缝铺调研启动` | 日期=`2024年11月`，标题=`社区裁缝铺调研启动`（按 `｜`/`|` 分隔，无分隔符则整行作标题） |
| 节点下的段落 | 节点描述（`<p>`） |
| 节点下的图片 | figure（单图 16:10 / 多图 grid 2 列） |
| 节点顺序 | 按 MD 出现顺序（通常已是时间递进） |

### 边界情况

| 情况 | 处理 |
|---|---|
| 只有 1 个日期子标题 | 不算时间线，用普通章节 |
| 日期在段落开头而非子标题 | 不算时间线结构，用普通段落 |
| 标题含"时间线"但全是普通段落 | 仍用时间线组件（标题信号优先） |
| 子标题日期格式混乱（如 `第一阶段`） | 不匹配日期模式，用普通章节 |
| 时间线章节含 `{.gallery}` 图片 | 归入 section_gallery，不放节点内 |

### 示例：正确识别

```markdown
## 四、项目时间线

### 2024年11月｜社区裁缝铺调研启动
描述...

### 2025年1月｜衡门画廊旧衣展
描述...
![衡门画廊](图片和附件/05.jpg)
```

→ 判定：标题含"时间线" + 2 个日期子标题 → 时间线组件
