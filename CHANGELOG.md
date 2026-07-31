# 更新日志

## 2.1.0 (2026-07-31)

### 新增
- 外部 skill 源支持：`op7418/Humanizer-zh`、`obra/superpowers`
- 安装器支持从任意 GitHub 仓库安装 skill
- OptMem 永久记忆自动安装 + agent.md 集成

### 变更
- 安装清单：6 自建 + 5 外部源 + 2 Corch 内置推荐
- `humanizer-zh`、`brainstorming` 等从"推荐"升级为"可安装"

---

## 2.0.0 (2026-07-31)

### 新增
- 预装清单扩容至 13 个 skill
- 新增自建 skill：corch-image-compressor、corch-translate-helper、corch-interview-notes
- 跨平台安装脚本 install.py
- 所有 SKILL.md 使用中文描述

---

## 1.5.1 (2026-07-30)

### 修复
- 发布前必须主动询问用户认证信息

## 1.5.0 (2026-07-30)

### 新增
- PDF 图片提取（pdfimages）

## 1.4.0 (2026-07-30)

### 新增
- 依赖管理：pdftotext + markitdown

## 1.3.0 (2026-07-30)

### 新增
- 支持 PDF 输入和外文内容

## 1.2.0 (2026-07-30)

### 新增
- 用户交互流程：认证引导、分类选择、发布确认

## 1.1.0 (2026-07-30)

### 变更
- 移除纯文本输出，元数据改为 API payload

## 1.0.0 (2026-07-30)

### 新增
- corch-digest skill 初始版本
