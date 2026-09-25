/**
 * HTML → PDF 打印工具（用于重新生成交付材料 PDF）
 * 用法: node scripts/pdf-print.cjs <输入.html> <输出.pdf>
 * 依赖: Playwright + 系统 Chrome（channel: "chrome"）
 */
const { chromium } = require("playwright");
(async () => {
  const browser = await chromium.launch({ channel: "chrome" });
  const page = await browser.newPage();
  const src = process.argv[2];
  const out = process.argv[3];
  const url = "file:///" + src.split("\\").join("/");
  await page.goto(url, { waitUntil: "networkidle" });
  await page.pdf({
    path: out,
    format: "A4",
    printBackground: false,
    margin: { top: "0mm", bottom: "0mm", left: "0mm", right: "0mm" },
  });
  console.log("PDF_OK:", out);
  await browser.close();
})().catch((e) => { console.error("FATAL:", String(e).slice(0, 200)); process.exit(1); });
