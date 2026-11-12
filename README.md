# paper-read-tutor

> 把任意英文学术论文 PDF 变成一份「带读旁批版」讲义：**左栏英文原文 + 中文译文逐段对照，右栏彩色导师旁批卡**，最终输出可打印的 A4 PDF。

这是一个可泛化的 AI Agent Skill（`SKILL.md` + 参考模板 + 可复跑脚本），适用于"论文带读 / 逐段讲解 / 精读笔记"类任务。

## 产物长什么样

```
┌────────────────────────────┬──────────────────┐
│ p.5 摘要前两句              │ ┌ 概念解释（蓝）  │
│ English paragraph...        │ │ 术语与背景     │
│ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─   │ └───────────────┘
│ 中文译文……                 │ ┌ 读法点评（橙）  │
│                             │ │ 论证角色定位   │
│ ┌ 公式框 (2) ────────────┐ │ └───────────────┘
│ │ d_k,t(v) := log ...     │ │ ┌ 批判性思考（红）│
│ └─────────────────────────┘ │ │ 假设与局限     │
└────────────────────────────┴──────────────────┘
```

旁批四类固定配色：**🔵 概念解释 / 🟠 读法点评 / 🔴 批判性思考 / 🟢 数据解读**；每段开头带原文页码锚点（`p.5`），可与原 PDF 对照。

## 仓库结构

```
paper-read-tutor/
├── SKILL.md                              # Skill 主说明：产物规范 + 5 步流程 + 常见坑
├── references/
│   └── annotated-paper-template.html     # 双栏旁批版 HTML 模板（含全部内联 CSS 与占位符）
└── scripts/
    ├── extract_paper.py                  # PDF → 结构化英文段落 JSON（处理空格丢失/双栏）
    ├── render_pdf.sh                     # Chrome/Chromium headless 打印 HTML → PDF
    └── render_preview.py                 # PDF → 每页 JPG 预览图（供视觉 QA）
```

## 快速上手

```bash
# 0. 依赖
pip install pdfplumber pymupdf pypdf     # 另需本机 Chrome/Chromium

# 1. 抽取原文段落（自动跳过中文/译文页；双栏论文加 --two-col）
python3 scripts/extract_paper.py paper.pdf -o en_blocks.json

# 2. 基于模板撰写译文与旁批，生成带批注 HTML（此步由 AI/作者完成内容创作）
cp references/annotated-paper-template.html my_paper_annotated.html
#    … 替换 {{PLACEHOLDER}}，逐段填入原文 / 译文 / 四类旁批卡 …

# 3. 渲染 PDF
bash scripts/render_pdf.sh my_paper_annotated.html my_paper_带读旁批版.pdf

# 4. 视觉 QA：逐页核对排版
python3 scripts/render_preview.py my_paper_带读旁批版.pdf -o preview
#    … 用图像检查工具按每批 ≤3 张核对：分栏重叠/字体豆腐块/公式/表格断裂/孤立标题 …
```

## 流程要点（详见 SKILL.md）

1. **抽取**：`pdfplumber` 词级抽取（`x_tolerance=2.0`）修复单词粘连，按行距切段重建段落；双栏按 x 坐标分列。
2. **翻译与旁批**：逐段自译中文（术语首次出现附英文）；旁批密度以"不留大段无批正文"为宜，关键数字回到原文复核口径。
3. **排版**：内联 CSS、A4；三条分页铁律——标题块 `break-after: avoid-page`、表格 `thead/tbody` 完整闭合、行/卡片 `break-inside: avoid`。
4. **渲染**：Chrome headless `--print-to-pdf`（中文字体最稳）。
5. **视觉 QA**：必做。批量看图超时按「≤3 张/批 → 单张 → 原生直读」降级，每张成功后立即落盘，绝不跳过任何一页。

## 适用场景

- 把一篇 arXiv 论文做成导师带读式精读讲义
- 组会论文分享的批注版阅读材料
- 文献综述写作前的逐段拆解笔记

## License

MIT
