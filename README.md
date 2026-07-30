# corch-skills

面向 c-lab 内容社区团队的 Codex 技能包。开箱即用，覆盖内容生产全流程。

## 一行安装

```bash
curl -sL https://raw.githubusercontent.com/fanzy531/corch-skills/main/scripts/install.py | python3
```

## 技能清单（13 个）

### 核心工作流（自建）

| 技能 | 作用 | 输出 |
|---|---|---|
| **corch-digest** | 读取文章URL → 消化改写 → 发布到他山之石 | voice CPT |
| **corch-action** | 解析项目MD文档 → 发布到实践现场 | action CPT |
| **corch-hub** | 社区营造知识库问答 | — |

### 内容生产配套（自建）

| 技能 | 作用 |
|---|---|
| **corch-image-compressor** | 批量压缩图片（横幅1000w/竖幅1200w→JPG） |
| **corch-translate-helper** | 外文→中文翻译，保持术语一致 |
| **corch-interview-notes** | 访谈录音/笔记→结构化可发布内容 |

### 通用能力（Corch 内置包装）

| 技能 | 作用 |
|---|---|
| **tavily-search** | 结构化联网搜索，带引用来源 |
| **humanizer-zh** | 中文去AI痕迹（digest/action 发布前自动调用） |
| **brainstorming** | 发散→收敛，活动/选题/方案创意 |
| **writing-skills** | 重复工作沉淀为 SOP |
| **writing-plans** | 多人协作项目规划 |
| **content-risk-detector** | 发布前合规审查 |
| **verification-before-completion** | 交付前验收 |

## 系统依赖

| 依赖 | 安装方式 | 用途 |
|---|---|---|
| Pillow | `pip install Pillow` | 图片压缩 |
| poppler | `brew` / `choco` / `apt` | PDF 文字和图片提取 |

## 项目结构

```
corch-skills/
├── .skill-requirements.json    # 安装清单（13 skills）
├── CHANGELOG.md
├── scripts/
│   ├── install.py              # 跨平台安装器（macOS/Windows/Linux）
│   └── setup.sh                # Mac 专用（向后兼容）
└── skills/
    ├── corch-digest/            # 转载文献
    ├── corch-action/            # 发布项目
    ├── corch-hub/               # 知识库
    ├── corch-image-compressor/  # 图片压缩
    ├── corch-translate-helper/  # 外文翻译
    ├── corch-interview-notes/   # 访谈笔记
    └── ...（7 个 Corch 内置包装）
```
