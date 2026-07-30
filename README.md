# corch-skills

面向 c-lab 内容社区团队的 Codex 技能包。

## 一行安装

```bash
curl -sL https://raw.githubusercontent.com/fanzy531/corch-skills/main/scripts/install.py | python3
```

安装后重启 Codex 生效。

## 技能清单

### 可安装（6 个，安装器自动下载）

| 技能 | 作用 | 输出 |
|---|---|---|
| **corch-digest** | 读取文章URL → 消化改写 → 发布到「他山之石」 | voice CPT |
| **corch-action** | 解析项目MD文档 → 发布到「实践现场」 | action CPT |
| **corch-hub** | 社区营造知识库问答 | — |
| **corch-image-compressor** | 批量压缩图片（横幅1000w/竖幅1200w→JPG） | — |
| **corch-translate-helper** | 外文→中文翻译，保持术语一致 | — |
| **corch-interview-notes** | 访谈录音/笔记→结构化可发布内容 | — |

### 推荐（7 个，Corch 内置，无需安装）

以下能力是 Corch 系统自带的，在对话中直接使用即可：

| 能力 | 作用 | 备注 |
|---|---|---|
| **tavily-search** | 结构化联网搜索，带引用来源 | |
| **humanizer-zh** | 中文去AI痕迹 | digest/action 发布前自动调用 |
| **brainstorming** | 发散→收敛，活动/选题创意 | |
| **writing-skills** | 重复工作沉淀为 SOP | |
| **writing-plans** | 多人协作项目规划 | |
| **content-risk-detector** | 发布前合规审查 | |
| **verification-before-completion** | 交付前验收 | |

## 系统依赖

安装器会自动处理：

| 依赖 | 安装方式 | macOS | Windows | Linux | 用途 |
|---|---|---|---|---|---|
| Pillow | pip | ✓ | ✓ | ✓ | 图片压缩 |
| poppler | 系统包管理器 | brew | choco | apt | PDF提取 |

## 项目结构

```
corch-skills/
├── .skill-requirements.json    # 安装清单
├── CHANGELOG.md
├── scripts/
│   └── install.py              # 跨平台安装器
└── skills/
    ├── corch-digest/
    ├── corch-action/
    ├── corch-hub/
    ├── corch-image-compressor/
    ├── corch-translate-helper/
    └── corch-interview-notes/
```
