/**
 * 截图对比：3D 知识空间板块（修复前 dpr=2 / 修复后 dpr=1）
 * 用法: node scripts/perf-shot.cjs [url]
 */
const { chromium } = require("playwright");
const URL = process.argv[2] || "http://localhost:5173/";

(async () => {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(8000); // 等入场动画结束

  const top = await page.evaluate(() => {
    const c = document.querySelector("canvas");
    return Math.round(c.getBoundingClientRect().top + window.scrollY);
  });
  await page.evaluate((y) => window.scrollTo(0, y), top - 60);
  await page.waitForTimeout(2500);

  const gl = await page.evaluate(() => {
    const c = document.querySelector("canvas");
    return { w: c.width, h: c.height, client: `${c.clientWidth}×${c.clientHeight}` };
  });
  console.log("当前后端缓冲:", gl.w + "×" + gl.h, "| CSS 尺寸:", gl.client);

  await page.screenshot({
    path: "E:/开发/learnlabAI教学平台/scripts/shot-fixed.png",
  });
  console.log("已保存 scripts/shot-fixed.png");

  await browser.close();
})();
