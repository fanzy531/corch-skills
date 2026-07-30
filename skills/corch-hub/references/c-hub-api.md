# C-Hub API Reference (C-hub)

## 认证

所有 API 请求需在 Header 中携带：

```
X-API-Key: sk-xxxxx
```

## 端点

### POST `/knowledge-chat/:session_id`

基于知识库的 RAG 问答。流式响应（SSE）。

**请求体：**

| 参数 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `query` | string | 是 | 查询文本 |
| `knowledge_base_ids` | string[] | 否 | 知识库 ID 列表 |
| `knowledge_ids` | string[] | 否 | 知识文件 ID 列表 |
| `agent_id` | string | 否 | 智能体 ID |

**响应事件类型：**

| event | response_type | 说明 |
|---|---|---|
| `references` | `references` | 知识引用片段 |
| `answer` | `answer` | 回答内容（流式多帧，done=true 时结束） |

### POST `/agent-chat/:session_id`

Agent 模式问答，支持工具调用和网络搜索。

额外参数：
- `agent_enabled`: bool — 启用 Agent 模式
- `web_search_enabled`: bool — 启用网络搜索

## 环境变量

| 变量 | 默认值 | 说明 |
|---|---|---|
| `WEKNORA_BASE_URL` | `http://localhost:8080/api/v1` | 服务地址 |
| `WEKNORA_API_KEY` | — | API 密钥 |

## 更多

见官方文档：https://github.com/Tencent/C-Hub/blob/main/docs/api/
