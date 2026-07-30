# Output Format — Corch Digest

> 产出物共三份：
> 1. **正文 HTML 片段** — 纯 inline style，不依赖任何外部 CSS/JS
> 2. **导读** — 纯文本，策展人总结
> 3. **元数据 Spec** — 结构化文本

---

## 1. 正文 HTML 片段

所有样式直接写在 `style=""` 中，**不含 `<style>`、`<script>` 块，不含 Tailwind 或任何外部类**。

### 容器

```html
<div style="font-family:Georgia,'Source Han Serif CN','Songti SC','STSong',serif; font-size:16px; line-height:1.8; color:rgba(26,28,26,0.85); max-width:720px; margin:0 auto;">
  <!-- 所有子元素 -->
</div>
```

---

### 1.1 一级标题 H2

```html
<h2 style="font-family:Georgia,'Source Han Serif CN','Songti SC','STSong',serif; font-size:24px; font-weight:bold; color:#1A1C1A; padding-top:16px; padding-bottom:8px; border-bottom:1px solid rgba(26,28,26,0.1); margin-bottom:16px;">
  小资金撬动大民生 多元共治激活"一池春水"
</h2>
```

---

### 1.2 正文段落 P

```html
<p><span style="float:left; font-size:56px; line-height:0.9; padding-right:8px; font-weight:bold; color:#C85A3C;">今</span>年以来，成都市新都区聚焦民生实事小切口...</p>
<p>第二段及之后的段落正常输出即可。</p>
```

- 仅**首段首字**需要 `<span>` 包裹做首字下沉
- 其余段落为裸 `<p>`

---

### 1.3 插图 Figure

```html
<figure style="margin:32px 0; border:1px solid rgba(26,28,26,0.1); padding:8px; background:#FAF8F3;">
  <img src="images/img-01.jpg" alt="图说文字" style="width:100%; height:auto; display:block;">
  <figcaption style="font-family:'Courier New',Courier,monospace; font-size:12px; color:rgba(26,28,26,0.5); text-align:center; margin-top:12px;">
    图说：原文图片的标题或说明
  </figcaption>
</figure>
```

---

### 1.4 拉引引用块 Pull Quote

```html
<blockquote style="margin:32px 0; border-top:1px solid rgba(200,90,60,0.3); border-bottom:1px solid rgba(200,90,60,0.3); padding:24px 0; text-align:center;">
  <p style="font-style:italic; font-size:20px; color:#C85A3C; font-weight:bold; margin:0;">
    "过去社区建设多是政府主导，居民被动参与..."
  </p>
</blockquote>
```

---

### 1.5 无序列表 UL

```html
<ul style="list-style:disc; padding-left:20px; margin:16px 0;">
  <li style="margin-bottom:8px;"><strong>关键要点 A：</strong>具体描述内容</li>
  <li style="margin-bottom:8px;"><strong>关键要点 B：</strong>具体描述内容</li>
</ul>
```

---

### 1.6 底部来源行

```html
<p style="font-size:12px; color:rgba(26,28,26,0.5); margin-top:32px; padding-top:16px; border-top:1px solid rgba(26,28,26,0.1);">
  来源：人民网－四川频道｜原文链接：http://sc.people.com.cn/n2/2025/0801/c345167-41310409.html
</p>
<p style="font-size:12px; font-family:'Courier New',Courier,monospace; color:rgba(26,28,26,0.3);">
  [ TRANSCRIPTION ENDS ]
</p>
```

---

## 2. 导读（纯文本）

独立输出，不套 HTML。格式：

```
【corch 导读 / Curator's Reflection】
成都新都区把功夫下在细节里。今年以来，当地创新实施"点亮社区"微更新行动...
```

---

## 3. 元数据 Spec（纯文本）

独立输出，不套 HTML。格式：

```
**关键词**： #基层治理 #社区微更新 #成都新都区 #居民共建 #人民城市

**出处来源**：人民网－四川频道
**原作者**：赵祖乐
**译介编译**：corch 外部观察员译
**转载日期**：2026.07.11

**版权声明**：
本文由 corch 根据"知识共享署名-非商业性使用"许可协议转载此节选，
供社区营造同行研究。如果涉及侵犯您的著作权，请联系 @teresa 删除。

**原文链接**：http://sc.people.com.cn/n2/2025/0801/c345167-41310409.html
```

---

## 色值表（固定）

| 变量 | 色值 | 用途 |
|---|---|---|
| `ink` | `#1A1C1A` | 主文字色 |
| `ink/85` | `rgba(26,28,26,0.85)` | 正文默认色 |
| `ink/50` | `rgba(26,28,26,0.5)` | 图注、次要文字 |
| `ink/30` | `rgba(26,28,26,0.3)` | 极弱文字 |
| `ink/10` | `rgba(26,28,26,0.1)` | 边框、分割线 |
| `clay` | `#C85A3C` | 引用块强调色 |
| `clay/30` | `rgba(200,90,60,0.3)` | 引用块边框 |
| `warmWhite` | `#FAF8F3` | 插图背景 |

---

## 自检清单

- [ ] 正文容器使用了 inline style，无 Tailwind 类、无 `<style>`/`<script>` 块
- [ ] 首段首字用 `<span>` 包裹做了首字下沉
- [ ] 每个 `<figure>` 中 `<img>` 的 `src` 指向本地下载路径
- [ ] 底部来源行格式正确
- [ ] 导读已作为纯文本单独输出
- [ ] 元数据 Spec 已作为纯文本单独输出
