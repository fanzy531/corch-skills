---
name: corch-hub
description: Query the C-Hub knowledge base for community placemaking knowledge. Use when the user asks questions about community building, urban renewal, social innovation, or any topic that should be answered from the C-Hub curated knowledge base.
---

# Corch Hub

Bridge between the Corch agent and the C-Hub knowledge base.仅限 Corch 用户使用，首次使用需通过 C-Hub 邮箱密码认证。

## First-time setup（首次认证）

用户第一次调用时，引导其完成一次认证即可：

```bash
python3 scripts/c-hub-query.py --login-email
```

按提示输入 C-Hub 邮箱和密码，脚本自动验证并保存凭证到 `~/.corch/config.json`。

非交互式（适合脚本/自动化）：

```bash
python3 scripts/c-hub-query.py --login-email --email user@corch.com --password "xxx"
```

查看认证状态：

```bash
python3 scripts/c-hub-query.py --status
```

也可通过环境变量直接注入（适合 Corch 平台托管）：

```bash
export WEKNORA_BASE_URL="https://c-hub.cschool.ac.cn/api/v1"
export WEKNORA_API_KEY="sk-xxxxx"
```

## Two query modes

| Mode | Command | When to use |
|---|---|---|
| **search** | `c-hub-query.py search <query>` | 默认模式。全文关键词搜索，文档无需分块，立即可用 |
| **chat** | `c-hub-query.py chat <query>` | RAG 问答，LLM 根据检索内容生成回答，需文档已分块 |

## Usage

### Search（推荐，无需配置）

```bash
python3 scripts/c-hub-query.py search "社区居民参与案例" --top-n 5
```

返回结果包含匹配文档的标题、得分、内容片段和来源链接。

### Chat（RAG 问答，需分块后生效）

```bash
python3 scripts/c-hub-query.py chat "成都社区营造有哪些典型案例？"
```

自动创建会话，通过 SSE 流获取 LLM 生成的回答 + 引用来源。

### 工具命令

```bash
# 列出知识库（含 chunk_count，>0 表示已分块）
python3 scripts/c-hub-query.py --list-kbs

# 列出知识库内所有文档
python3 scripts/c-hub-query.py --list-docs <kb_id>
```

### 按知识库筛选

```bash
python3 scripts/c-hub-query.py search "社区基金" --kb-ids "kb-id-1,kb-id-2"
```

不指定 `--kb-ids` 时默认搜索所有知识库。

### 会话延续（chat 模式）

```bash
python3 scripts/c-hub-query.py chat "追问" --session "<上一轮的 session_id>"
```

## Citation

回答末尾须列出本次引用的知识库文章标题。搜索结果的 `results[].knowledge_title` 即为文章标题。格式：

```
---

📚 参考资料：
1. 网格营造案例 | "五V工作法"赋能，织密网格"V链条"
2. 莫筱筱和明亮 - 2016 - 台湾社区营造的经验及启示
```

若无引用知识库内容则不列出。

## Scripts

### `scripts/c-hub-query.py`

| 命令 | 说明 |
|---|---|
| `--login-email` | 首次认证，用 C-Hub 邮箱密码登录 |
| `--status` | 查看认证状态 |
| `search <query>` | 关键词搜索 |
| `chat <query>` | RAG 问答 |
| `--list-kbs` | 列出知识库 |
| `--list-docs <kb_id>` | 列出知识库文档 |

## References

- `references/c-hub-api.md` — C-Hub REST API 参考
