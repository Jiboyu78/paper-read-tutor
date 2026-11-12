---
name: paper-read-tutor
description: 生成"论文带读旁批版"PDF——把一篇学术论文做成"左栏英文原文+中文译文对照、右栏彩色导师旁批卡"的可打印讲义。适用于：用户要求对论文做带读/逐段讲解/旁批，并产出对照版 PDF、HTML 讲义或精读笔记。流程覆盖 PDF 文本抽取与清洗、段落级中英翻译、旁批撰写、双栏 HTML 排版、无头浏览器渲染 PDF、逐页视觉 QA。
---

# paper-read-tutor · 论文带读旁批版生成器

将任意一篇英文学术论文 PDF 转化为**双栏旁批对照讲义**：左栏为英文原文 + 中文译文逐段对照，右栏为分类型导师旁批卡。产出可直接打印/阅读的 PDF，并保留可再编辑的 HTML 源。

## 一、产物形态与版式规范

- **纸张**：A4 竖版；左 : 右 ≈ 1.6 : 1（flex 布局）。
- **左栏（原文主体）**：英文原文（Georgia 类衬线）在上、中文译文（无衬线，灰色）在下，两段间以虚线分隔；节选处用 `⋯` 标出，保证忠实原文。
- **右栏（旁批栏）**：每条旁批一张彩色卡片，左侧色条 + 类型标签，四类固定配色：
  - 🔵 概念解释 `#eef4ff / #2563eb`：术语、背景知识、公式拆解。
  - 🟠 读法点评 `#fdf6e3 / #d97706`：该段在全文论证链中的作用、读法建议。
  - 🔴 批判性思考 `#fdeeee / #dc2626`：假设、局限、可追问之处。
  - 🟢 数据解读 `#ecf8f1 / #059669`：实验数字口径、表格读法。
- **锚点**：每段开头放页码标签（如 `p.5`），便于与原 PDF 对照。
- **结构件**：深色章节标题块（每章一条，附英文小字）、公式展示框、迷你数据表、首页封面（标题/作者/机构/一句话逻辑链）、末页带读小结。
- **公式**：用 HTML 上下标 + 符号重排为简化可读形式，不直接贴 PDF 抽取的破碎公式文本。

## 二、执行流程（严格按顺序）

### Step 1 · 抽取与结构重建
1. 用 `pdfplumber` 抽取每页文本；识别是否存在译文页/双语页（统计 CJK 比例），英文页与译文页交替出现时只取英文页重建。
2. 关键坑：PDF 词间空格常丢失。用 `page.extract_words(x_tolerance=2.0)` 按词级抽取，再按行聚类（top 容差 ±2）、按行距切段（段间距阈值 ≈ 单倍行距 + 3.5pt）重建段落。
3. 逐章通读，记录：章节标题、核心公式编号、图表位置、页码映射。输出结构化 JSON 作为内容底稿。

### Step 2 · 翻译与旁批撰写
- **中文译文**：逐段自译（不使用现成机翻页，除非用户指定），忠实学术语义；术语保持中英对照（首次出现附英文）。
- **旁批**：每 1–2 段配 1–2 张卡，四类混合，密度以"不留大段无批正文"为宜。写作遵循三条：不重复正文、给出论证角色定位、敢于指出假设与局限。
- 关键数字必须回到原文复核口径（如"closes X% of the gap"类指标要写出计算式）。

### Step 3 · HTML 排版
- 参考 `references/annotated-paper-template.html`：内联全部 CSS（无外部依赖），`@page { size: A4 }`，使用系统中文字体（macOS 推荐 `Songti SC` 正文 + `PingFang SC` 旁批；其他平台换成 Noto Serif CJK / Noto Sans CJK）。
- 大文件分块写入后拼接，避免超长单文件。
- **分页 CSS 三条铁律**：`.sec-head { break-after: avoid-page }` 防页底孤立标题；表格必须 `<table><thead>…</thead><tbody>…</tbody></table>` 完整闭合，跨页才能重复表头；行/卡片 `break-inside: avoid`。

### Step 4 · 渲染 PDF
- 首选 Chrome headless（中文字体支持最稳）：
  ```bash
  CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # macOS
  "$CHROME" --headless --disable-gpu --no-sandbox \
    --print-to-pdf="out.pdf" --no-pdf-header-footer "file://$PWD/out.html"
  ```
  Linux 用 `google-chrome`/`chromium`；Windows 用 Chrome 安装路径。无头模式打印 `CVDisplayLink` 之类警告可忽略。
- 备选：weasyprint / wkhtmltopdf / Playwright print。

### Step 5 · 视觉 QA（必做，不可省略）
1. 用 `pymupdf` 把每页渲染为长边 ~1000px 的 JPG：
   ```python
   import fitz
   doc = fitz.open("out.pdf")
   for i, page in enumerate(doc):
       zoom = 1000 / max(page.rect.width, page.rect.height)
       pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
       pix.save(f"preview/p{i+1:02d}.jpg", jpg_quality=80)
   ```
2. 用图像检查工具逐页核对：分栏是否重叠、中文是否有豆腐块、公式符号是否清晰、章节标题是否页底孤立、表格是否断裂、是否有溢出/大片空白。
3. **批量看图降级链**：每批 ≤3 张（长边 ≤800–1000px）；批量超时就改单张；单张仍超时就换原生视觉直读；每张成功后立即把判读结果落盘，失败项留待补核。绝不因超时跳过任何一页。
4. 发现版式问题→回 Step 3 修 CSS→重渲染→只复核受影响页。全部通过后清理预览图，交付 PDF（HTML 源可选保留）。

## 三、交付规范

- 文件名建议：`<短标题>_带读旁批版.pdf`（或用户指定语言命名）。
- 交付时说明：页数、覆盖章节、旁批四类配比、已修复与遗留版式问题。
- 遗留可接受项（如末页自然留白）如实说明，不无限返工。

## 四、依赖清单

- Python 包：`pdfplumber`（抽取）、`pymupdf`（QA 渲染）、`pypdf`（可选，页数/合并）。
- 系统：Chrome/Chromium（渲染）、图像检查工具（视觉 QA）。
- 字体：任一完整 CJK 字体族。

## 五、常见坑速查

| 坑 | 对策 |
|---|---|
| 抽取文本单词粘连 | 词级 `extract_words(x_tolerance=2.0)` 重建，勿用整段 `extract_text()` |
| 双栏论文段落串栏 | 按 x 坐标分左右栏分别抽取再拼接 |
| 公式抽取破碎 | 人工重排为 HTML 简化公式，不贴原始碎片 |
| 页底孤立章节标题 | 标题块 `break-after: avoid-page` |
| 表格样式失效/跨页断行 | 检查 `</table>` 闭合、thead/tbody 结构 |
| 批量视觉 QA 超时 | 见 Step 5 降级链 |
