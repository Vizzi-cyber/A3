/**
 * 技术方案分体打印：cover（无页眉脚）+ body（页眉 AIC+大赛名 / 页脚纯页码）合并
 * 用法: node pdf-print.cjs <输入.html> <输出.pdf>
 */
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");
(async () => {
  const src = process.argv[2];
  const out = process.argv[3];
  let html = fs.readFileSync(src, "utf-8");
  const headEnd = html.indexOf("</head>");
  const head = html.slice(0, headEnd + 7);
  const ci = html.indexOf('<div class="cover">');
  if (ci === -1) { console.error("no cover div"); process.exit(1); }
  const coverHtml = head + "<body>" + html.slice(ci, html.indexOf("</div>", html.indexOf('class="cd"')) + 6) + "</body></html>";
  const bodyHtml = head + "<body>" + html.slice(html.indexOf('<div class="toc">', ci)) + "</body></html>";
  const tmp = path.dirname(src);
  fs.writeFileSync(path.join(tmp, "_cover.html"), coverHtml);
  fs.writeFileSync(path.join(tmp, "_body.html"), bodyHtml);

  const browser = await chromium.launch({ channel: "chrome" });
  const page = await browser.newPage();
  const u = (f) => "file:///" + path.resolve(f).split("\\").join("/");
  await page.goto(u(path.join(tmp, "_cover.html")), { waitUntil: "networkidle" });
  await page.pdf({ path: path.join(tmp, "_cover.pdf"), format: "A4", printBackground: false,
    margin: { top: "25mm", bottom: "22mm", left: "30mm", right: "30mm" } });
  await page.goto(u(path.join(tmp, "_body.html")), { waitUntil: "networkidle" });
  await page.pdf({ path: path.join(tmp, "_body.pdf"), format: "A4", printBackground: false,
    displayHeaderFooter: true,
    headerTemplate: '<div style="font-size:8pt;font-family:SimHei,serif;width:100%;padding:0 30mm;display:flex;justify-content:space-between;align-items:center;border-bottom:0.5pt solid #999;"><span style="color:#1e5bb8;font-weight:bold;font-style:italic;font-size:12pt;">AIC</span><span style="color:#555;">2026 第八届全球校园人工智能算法精英大赛</span></div>',
    footerTemplate: '<div style="font-size:9pt;font-family:SimSun,serif;width:100%;text-align:center;color:#000;"><span class="pageNumber"></span></div>',
    margin: { top: "25mm", bottom: "22mm", left: "30mm", right: "30mm" } });
  await browser.close();
  console.log("PDF_OK:", out);
})().catch((e) => { console.error("FATAL:", String(e).slice(0, 300)); process.exit(1); });
