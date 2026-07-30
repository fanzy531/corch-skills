# 更新日志

## 2.0.0 (2026-07-31)

### 新增
- 预装清单扩容至 13 个 skill，覆盖内容社区团队日常工作
- 新增自建 skill：
  - `corch-image-compressor` — 批量压缩图片（横幅1000w/竖幅1200w）
  - `corch-translate-helper` — 外文→中文翻译，术语一致性
  - `corch-interview-notes` — 访谈→结构化笔记
- 新增 Corch 内置 skill 包装（带中文描述）：
  - `tavily-search`、`humanizer-zh`、`brainstorming`
  - `writing-skills`、`writing-plans`
  - `content-risk-detector`、`verification-before-completion`
- `humanizer-zh` 集成到 `corch-digest` 和 `corch-action` 的发布流程中，自动执行
- 所有 SKILL.md 使用中文描述
- `.skill-requirements.json` 升级至 v2

### 基础设施
- 新增跨平台安装脚本 `scripts/install.py`（支持 macOS / Windows / Linux）
- `.skill-requirements.json` 按平台声明系统依赖（brew / choco / apt）

---

## 1.5.1 (2026-07-30)

### 修复
- 发布前必须主动询问用户认证信息，不能静默跳过

## 1.5.0 (2026-07-30)

### 新增
- PDF 图片提取（pdfimages）

## 1.4.0 (2026-07-30)

### 新增
- 依赖管理：pdftotext + markitdown 用于 PDF 提取

## 1.3.0 (2026-07-30)

### 新增
- 支持 PDF 输入和外文内容

## 1.2.0 (2026-07-30)

### 新增
- 用户交互流程：认证引导、分类选择、发布确认

## 1.1.0 (2026-07-30)

### 变更
- 移除纯文本输出，元数据改为 API payload 提交
- corch-hub 加入仓库

## 1.0.0 (2026-07-30)

### 新增
- corch-digest skill 初始版本
