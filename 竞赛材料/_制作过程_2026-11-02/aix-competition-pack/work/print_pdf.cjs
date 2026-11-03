/**
 * AI+X 成品打印脚本（基于 frontend/scripts/pdf-print.cjs 改造）：
 * - 不做 cover/body 分体（小文档无封面）
 * - 页眉不带 AIC（原脚本硬编码 AIC 页眉，不能复用）
 * - 页边距沿用原脚本：top 25 / bottom 22 / 左右 30mm
 * 用法: node print_pdf.cjs <输入.html> <输出.pdf>
 */
const path = require("path");
module.paths.unshift("e:/开发/learnlabAI教学平台/frontend/node_modules");
const { chromium } = require("playwright");
const fs = require("fs");

(async () => {
  const src = process.argv[2];
  const out = process.argv[3];
  if (!src || !out) { console.error("用法: node print_pdf.cjs <in.html> <out.pdf>"); process.exit(1); }
  const browser = await chromium.launch({ channel: "chrome" });
  const page = await browser.newPage();
  const u = "file:///" + path.resolve(src).split("\\").join("/");
  await page.goto(u, { waitUntil: "networkidle" });
  await page.pdf({ path: out, format: "A4", printBackground: false,
    displayHeaderFooter: true,
    headerTemplate: "<span></span>",
    footerTemplate: `<div style="width:100%;text-align:center;font-family:'SimSun',serif;font-size:9px;color:#000;"><span class="pageNumber"></span></div>`,
    margin: { top: "25mm", bottom: "22mm", left: "30mm", right: "30mm" } });
  await browser.close();
  console.log("PDF_OK:", out);
})().catch((e) => { console.error("FATAL:", String(e).slice(0, 300)); process.exit(1); });
