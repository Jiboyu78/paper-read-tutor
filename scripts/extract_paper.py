#!/usr/bin/env python3
"""extract_paper.py — 从论文 PDF 抽取结构化英文段落 JSON。

解决 PDF 抽取的两大坑：词间空格丢失（用词级抽取重建）、双栏串行（按 x 分栏）。
用法：
    python3 extract_paper.py input.pdf -o blocks.json [--two-col] [--no-cn-filter]
输出：{ "pages": { "<page0>": ["block1", ...], ... }, "meta": {...} }
"""
import argparse, json, re, sys

try:
    import pdfplumber
except ImportError:
    sys.exit("缺少 pdfplumber：pip install pdfplumber")

CJK = re.compile(r'[\u4e00-\u9fff]')
# 页眉/水印/页码等噪声行（arXiv 侧边水印、纯页码、日期行）
NOISE = re.compile(r'^\d{1,2}$|^(6202|tcO|]LC|\.sc\[|3v)')


def cjk_ratio(t: str) -> float:
    return len(CJK.findall(t)) / max(len(t), 1) if t else 0.0


def page_lines(page, xmin=0.0, xmax=None):
    """词级抽取 → 按行聚类，返回 [(top, text), ...]（已过滤噪声行）。"""
    words = page.extract_words(x_tolerance=2.0)
    if xmax is None:
        xmax = page.width
    words = [w for w in words if xmin <= w['x0'] < xmax]
    rows = {}
    for w in words:
        top = round(w['top'])
        key = next((k for k in rows if abs(k - top) <= 2), None)
        if key is None:
            key = top
            rows[key] = []
        rows[key].append(w)
    out = []
    for top in sorted(rows):
        line = ' '.join(x['text'] for x in sorted(rows[top], key=lambda x: x['x0']))
        if not NOISE.match(line.strip()):
            out.append((top, line))
    return out


def lines_to_blocks(lines, base_gap=11.0):
    """按行距切段：行距 ≥ base_gap + 3.5 视为段界。base_gap 取全文小行距众数更佳。"""
    if not lines:
        return []
    blocks, cur = [], [lines[0][1]]
    for (t0, _), (t1, l1) in zip(lines, lines[1:]):
        if t1 - t0 >= base_gap + 3.5:
            blocks.append(' '.join(cur))
            cur = [l1]
        else:
            cur.append(l1)
    blocks.append(' '.join(cur))
    return [b for b in blocks if len(b.strip()) >= 3]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('-o', '--out', default='en_blocks.json')
    ap.add_argument('--two-col', action='store_true', help='双栏排版：按页面中线分左右栏分别抽取')
    ap.add_argument('--no-cn-filter', action='store_true', help='不过滤中文页（默认跳过 CJK 占比>5%% 的页）')
    args = ap.parse_args()

    result, meta = {}, {'pdf': args.pdf, 'skipped_pages': [], 'two_col': args.two_col}
    with pdfplumber.open(args.pdf) as pdf:
        meta['total_pages'] = len(pdf.pages)
        for pno, page in enumerate(pdf.pages):
            raw = page.extract_text() or ''
            if not args.no_cn_filter and cjk_ratio(raw) > 0.05:
                meta['skipped_pages'].append(pno + 1)
                continue
            if args.two_col:
                mid = page.width / 2
                lines = page_lines(page, 0, mid) + page_lines(page, mid)
            else:
                lines = page_lines(page)
            result[str(pno)] = lines_to_blocks(lines)

    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump({'pages': result, 'meta': meta}, f, ensure_ascii=False, indent=1)
    n_blocks = sum(len(v) for v in result.values())
    print(f'共 {meta["total_pages"]} 页，抽取英文页 {len(result)}，跳过中文/译文页 {len(meta["skipped_pages"])}，段落块 {n_blocks}')
    print('已写入:', args.out)


if __name__ == '__main__':
    main()
