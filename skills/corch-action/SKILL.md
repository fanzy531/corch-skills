---
name: corch-action
version: 0.4.0
description: Parse structured markdown project documents, convert to WordPress action CPT (实践现场) with all ACF fields (repeater, gallery, group), and publish. Use when the user provides a markdown project file and asks to publish it as an action article.
---

# Corch Action

## 0. Input

- **Input**: Local `.md` file path (structured project document)
- **Images**: Co-located `图片和附件/` directory, or paths referenced in the MD
- **Convention**: `{.gallery}` suffix on image references → `section_gallery` field; unmarked images → embedded in `section_body`

所有命令在本技能目录下执行。脚本位于 `scripts/`，不要在命令中读取或打印 WordPress 应用密码。

## Workflow

### 1. Parse metadata

Extract from the MD document:

| Field | Source |
|---|---|
| `title` | `# ` heading, or filename |
| `action_subtitle` | First paragraph or subtitle line |
| `action_category` | `fieldwork` or `inspirations` (ask user if unclear) |
| `action_location` | Text after "项目地点" or similar |
| `action_period` | Date range in "项目时间" section → **YYYYMMDD**（日默认 01） |
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
  "section_gallery": [21, 22]
}
```

完整 ACF 映射、时间线组件和时间线识别规则见 [references/output-format.md](references/output-format.md)。

### 3. Parse images

#### 3.1 `{.gallery}` 标记规则

```markdown
<!-- 嵌入正文：图片在 section_body 的文字流中 -->
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

每张图片根据它在 MD 中出现的上下文，归属到**上一个 `## ` 标题**对应的 `action_sections` 项。

#### 3.3 处理流程

1. 提取 alt 文本和路径：`![alt](path){.gallery}` → alt、path、is_gallery
2. 根据 MD 中的位置确定归属章节
3. 图片压缩后，将本地路径映射为上传后的 WordPress 媒体 URL + ID
4. 非 gallery 图片在 `section_body` 中插入 `<p><img ...></p>`；gallery 图片将 media ID 加入 `section_gallery`

#### 3.4 边缘情况

| 情况 | 处理 |
|---|---|
| 图片在两个 `##` 之间 | 归属到**前一个**章节 |
| 同一张图片被多次引用 | 只上传一次，复用 media ID 和 URL |
| `{.gallery}` 写在 alt 内部而非路径末尾 | 不识别，按普通图片处理 |
| 文档末尾、最后一个 `##` 之后的图片 | 归属到最后一个章节 |
| 图片文件不存在 | 跳过并输出警告，不中断流程 |

### 4. Optimize images

在发布前压缩，保留原图：

```bash
python3 scripts/optimize_images.py "图片和附件/" \
  --output-dir "图片和附件/optimized/" \
  --manifest "media-manifest.json"
```

规则：

| 类型 | 目标宽度 |
|---|---|
| 横幅 (w > h) | 1200px |
| 竖幅 (w ≤ h) | 1000px |

- 只缩小，不放大
- 统一转 JPEG，quality 85，optimize=True
- 已是最优的 JPG 跳过
- `--output-dir` 保持原图不动；`media-manifest.json` 记录 source → output 映射

压缩完成后向用户展示统计表，确认后才继续上传。payload 中的图片路径一律指向压缩后的文件。

### 5. Credentials

发布前检查凭证（与 corch-digest 共享 `~/.corch/config.json`）：

```bash
python3 scripts/corch_action.py status
```

未配置时引导用户一次性认证：

```bash
python3 scripts/corch_action.py login
```

认证通过后永久保存（文件权限 600）。脚本内部读取凭证，**不要**把密码作为命令行参数；非交互环境使用 `--password-stdin`。

### 6. Upload images

上传压缩后的图片到 WordPress 媒体库：

```bash
python3 scripts/corch_action.py upload-media "图片和附件/optimized/01.jpg" "图片和附件/optimized/02.jpg" \
  --map "media-map.json" \
  --alt-map "alt-map.json"
```

- `media-map.json` 保存源文件哈希 → media ID/URL；重复执行自动复用，失败重试不会重复创建附件
- `alt-map.json` 是 `{"图片路径": "alt 文本"}` 映射，来自 MD 中的 `![alt](path)`；没有映射时才用 `--alt` 兜底
- 用返回的 `url` 替换 `section_body` 中的图片 src，用返回的 `id` 填充 gallery 字段
- 上传失败时保留 map，只重试失败文件

### 7. Build publish payload

```json
{
  "title": "【关于穿的记忆】 社区参与式艺术实践",
  "content": "",
  "excerpt": "Brief project summary",
  "status": "draft",
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
    "action_sections": [],
    "action_outcomes": [{"outcome_label": "01", "outcome_title": "成果标题", "outcome_desc": "成果说明"}],
    "action_gallery": [{"gallery_image": 84, "gallery_caption": "展览现场"}]
  }
}
```

> **注意：** `date_picker` 字段 `period_start`/`period_end` 必须用 8 位 `Ymd`（如 `20241101`；MD 只有年月时，日默认 01），不可用 `2024.11`、`202411` 或任何 `strtotime` 无法解析的格式。

### 8. Validate and plan

发布前必须本地校验，再展示计划：

```bash
python3 scripts/corch_action.py validate payload.json
python3 scripts/corch_action.py plan payload.json
```

校验覆盖：必填字段、日期格式、HTML 中的 img alt/绝对 URL、gallery media ID、repeater 结构，以及 payload 中禁止出现凭证字段。校验失败时修复后重新执行，不要跳过。

### 9. User confirm

展示计划摘要 → 确认 `action_category`（fieldwork / inspirations）→ 确认发布状态。

### 10. Publish

默认发布为**草稿**：

```bash
python3 scripts/corch_action.py publish payload.json
```

正式发布必须同时满足：payload 中 `"status": "publish"`，且用户明确同意后加确认参数：

```bash
python3 scripts/corch_action.py publish payload.json --confirm-publish
```

### 11. Failure handling

- `validate` 报错：按字段信息修复，重新 validate
- `plan` 摘要与预期不符：停下来和用户核对，不要直接发布
- 上传超时/部分成功：保留 `media-map.json`，只重试失败文件；不要删除已上传附件
- 发布超时：先用返回的 `post_id` 或 wp-admin 查询结果，确认未创建再重试；不要盲目重复提交
- 401/403：运行 `corch_action.py login` 重新认证，检查用户角色和 CPT 权限
- 任何错误提示都可能包含响应内容：先脱敏再转述，不展示 Authorization 头或应用密码

## User interaction flow

1. 检查凭证：`corch_action.py status`；缺失时引导 `login`，只认证一次
2. 解析 MD，生成 payload 与图片清单
3. 压缩图片，展示结果并确认
4. 上传图片，生成 media map
5. `validate` + `plan`，展示计划并确认
6. 发布草稿，或经确认后正式发布

## Dependencies

- Python 3.10+
- Pillow
- 无需 curl 和外部凭证工具

## Scripts

### `scripts/corch_action.py`

安全发布 CLI，凭证只在脚本内部读取，不会输出到对话上下文：

```text
status         验证已保存的凭证
login          交互式验证并保存凭证（永久保存，权限 600）
validate       本地校验 payload（不访问网络）
plan           校验并输出创建/更新计划
upload-media   上传图片，支持 media map 复用
publish        发布 action 文章
```

### `scripts/optimize_images.py`

批量压缩图片并生成 source → output 映射：

```text
python3 scripts/optimize_images.py <images_dir> [--output-dir DIR] [--manifest FILE]
```

## References

- `references/output-format.md` — ACF field mapping, HTML body format, and timeline component
