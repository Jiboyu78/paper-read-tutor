#!/usr/bin/env python3
"""render_preview.py — 把 PDF 每页渲染为 JPG 预览图，供视觉 QA 逐页核对。

用法：
    python3 render_preview.py input.pdf -o preview_dir [--long-edge 1000]
输出 preview_dir/p01.jpg, p02.jpg ...（供图像检查工具按 ≤3 张/批核对）
"""
import argparse, os, sys

try:
    import fitz  # pymupdf
except ImportError:
    sys.exit("缺少 pymupdf：pip install pymupdf")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdf')
    ap.add_argument('-o', '--out', default='preview')
    ap.add_argument('--long-edge', type=int, default=1000, help='预览图长边像素（视觉 QA 推荐 800–1000）')
    ap.add_argument('--quality', type=int, default=80)
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    # 清空旧预览，避免新旧混杂
    for f in os.listdir(args.out):
        if f.lower().endswith(('.jpg', '.png')):
            os.remove(os.path.join(args.out, f))

    doc = fitz.open(args.pdf)
    n = len(doc)
    for i, page in enumerate(doc):
        zoom = args.long_edge / max(page.rect.width, page.rect.height)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        pix.save(os.path.join(args.out, f'p{i+1:02d}.jpg'), jpg_quality=args.quality)
    doc.close()
    print(f'共 {n} 页，预览图已写入 {args.out}/（p01.jpg … p{n:02d}.jpg）')
    print('视觉 QA 提示：按每批 ≤3 张逐页核对分栏/字体/公式/表格/孤立标题；')
    print('批量超时的降级链：≤3 张/批 → 单张 → 原生视觉直读；每张成功后立即把判读结果落盘。')


if __name__ == '__main__':
    main()
