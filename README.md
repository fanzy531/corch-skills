# corch-skills

面向 c-lab 内容社区团队的 Corch 技能包。开箱即用，覆盖内容生产全流程。

## 一行安装

```bash
curl -sL https://raw.githubusercontent.com/fanzy531/corch-skills/main/scripts/install.py | python3
```

安装后重启 Codex 生效。

## 技能清单

### 自建（6 个）

| 技能 | 作用 | 输出 |
|---|---|---|
| **corch-digest** | 读取文章URL → 消化改写 → 发布到「他山之石」 | voice CPT |
| **corch-action** | 解析项目MD文档 → 发布到「实践现场」 | action CPT |
| **corch-hub** | 社区营造知识库问答 | — |
| **corch-image-compressor** | 批量压缩图片（横幅1200w/竖幅1000w→JPG） | — |
| **corch-translate-helper** | 外文→中文翻译，保持术语一致 | — |
| **corch-interview-notes** | 访谈录音/笔记→结构化可发布内容 | — |

`corch-action` 内置安全发布 CLI（login / status / validate / plan / upload-media / publish），凭证保存在 `~/.corch/config.json`（权限 600），不会输出到对话上下文。

### 外部源（9 个，自动安装）

| 技能 | 来源 | 作用 |
|---|---|---|
| **agent-reach** | Panniantong/Agent-Reach | 全网搜索：小红书/推特/B站/Reddit/YouTube/GitHub |
| **humanizer-zh** | op7418/Humanizer-zh | 去除中文文本AI痕迹 |
| **content-risk-detector** | liuxingqitd/content-risk-detector | 发布前合规审查（短视频/小红书/视频号） |
| **guizang-social-card-skill** | op7418/guizang-social-card-skill | 小红书图文+公众号封面（28布局） |
| **html-ppt** | lewislulu/html-ppt-skill | HTML PPT 演示（24主题31布局） |
| **brainstorming** | obra/superpowers | 头脑风暴发散收敛 |
| **verification-before-completion** | obra/superpowers | 交付前验收 |
| **writing-plans** | obra/superpowers | 项目规划文档 |
| **writing-skills** | obra/superpowers | 标准化流程沉淀 |

### 工具依赖

| 工具 | 用途 |
|---|---|
| **OptMem** | AI agent 永久记忆（自动安装到 ~/.optmem 并集成 agent.md） |
| **Pillow** | 图片压缩 |
| **poppler** | PDF 文字和图片提取 |

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
