#!/usr/bin/env bash
# render_pdf.sh — 用 Chrome/Chromium headless 把 HTML 打印成 PDF。
# 用法：bash render_pdf.sh input.html output.pdf
set -euo pipefail

HTML="${1:?用法: render_pdf.sh input.html output.pdf}"
PDF="${2:?用法: render_pdf.sh input.html output.pdf}"

if [ -x "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
  CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"   # macOS
elif command -v google-chrome >/dev/null 2>&1; then
  CHROME="google-chrome"                                                    # Linux
elif command -v chromium >/dev/null 2>&1; then
  CHROME="chromium"                                                         # Linux
elif command -v chromium-browser >/dev/null 2>&1; then
  CHROME="chromium-browser"
else
  echo "未找到 Chrome/Chromium；可改用 weasyprint 或 wkhtmltopdf。" >&2
  exit 1
fi

HTML_ABS="$(cd "$(dirname "$HTML")" && pwd)/$(basename "$HTML")"
"$CHROME" --headless --disable-gpu --no-sandbox \
  --print-to-pdf="$PDF" --no-pdf-header-footer \
  "file://$HTML_ABS" 2>&1 | grep -v 'CVDisplayLink' || true

ls -lh "$PDF"
