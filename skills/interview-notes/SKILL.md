---
name: interview-notes
version: 0.1.0
description: Transform interview recordings or notes into structured, publishable content for the c-lab community archive.
---

# Interview Notes

## Input

- Raw interview transcript (text)
- Interview audio recording file (optional)
- Interviewer's notes / observations

## Output structure

```
# 【访谈】{interviewee name} — {topic}

## 基本信息
- 受访人：{name}
- 日期：{date}
- 地点：{location}
- 访谈人：{interviewer}
- 主题：{topic}

## 摘要
2-3 sentences summarizing the interview's key contribution.

## 访谈记录
Organized by themes, not by Q&A order.
Each theme section:
- Theme heading
- Key quotes (marked with "")
- Interviewer's contextual notes [in brackets]

## 观察与反思
Interviewer's post-interview observations.

## 相关链接 / 延伸阅读
```

## Rules

- Preserve the interviewee's voice in quotes — do not paraphrase
- Separate factual content from interviewer interpretation (use brackets)
- Remove interviewers's filler questions ("嗯", "对", "然后呢")
- Group related topics even if they appeared at different points in the conversation
- Tag with relevant community-building keywords
