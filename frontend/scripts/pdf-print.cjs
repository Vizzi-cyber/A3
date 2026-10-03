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
    displayHeaderFooter: true,
    headerTemplate: '<div></div>',
    footerTemplate: '<div style="font-size:8pt;font-family:SimSun,serif;width:100%;text-align:center;color:#000;">2026 第八届全球校园人工智能算法精英大赛 · 第 <span class="pageNumber"></span> 页</div>',
    margin: { top: "25mm", bottom: "22mm", left: "30mm", right: "30mm" },
  });
  console.log("PDF_OK:", out);
  await browser.close();
})().catch((e) => { console.error("FATAL:", String(e).slice(0, 200)); process.exit(1); });
