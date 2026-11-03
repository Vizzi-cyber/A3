/**
 * 最终确认：分离「节点标签 blur(3px)」与「卡片环 blur(14px)」各自的贡献
 * 用法: node scripts/perf-final-check.cjs [url]
 */
const { chromium } = require("playwright");
const URL = process.argv[2] || "http://localhost:5173/";

async function scrollMeasure(page, label) {
  await page.evaluate(() => window.scrollTo(0, 800));
  await page.waitForTimeout(500);
  await page.evaluate(() => {
    window.__tl = [];
    window.__stop = false;
    let last = performance.now();
    const tick = () => {
      const now = performance.now();
      window.__tl.push(now - last);
      last = now;
      if (!window.__stop) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  });
  for (let y = 800; y < 2600; y += 100) {
    await page.mouse.wheel(0, 100);
    await page.waitForTimeout(55);
  }
  await page.waitForTimeout(200);
  const f = await page.evaluate(() => {
    window.__stop = true;
    return window.__tl.filter((x) => x > 0 && x < 800).sort((a, b) => a - b);
  });
  const q = (p) => f[Math.floor(f.length * p)] ?? NaN;
  console.log(
    `${label.padEnd(34)} | 中位 ${q(0.5).toFixed(1).padStart(5)} | P90 ${q(0.9).toFixed(1).padStart(5)} | 最大 ${(f[f.length - 1] || 0).toFixed(0).padStart(4)} | >32ms ${String(f.filter((x) => x > 32).length).padStart(3)}/${f.length}`,
  );
}

const fresh = async (page) => {
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForTimeout(5000);
};

(async () => {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(5000);

  const count = await page.evaluate(() => {
    let labels = 0,
      panels = 0;
    document.querySelectorAll("div").forEach((d) => {
      const bf = getComputedStyle(d).backdropFilter;
      if (!bf || bf === "none") return;
      if (bf.includes("3px")) labels++;
      if (bf.includes("14px")) panels++;
    });
    return { labels, panels };
  });
  console.log(
    `3D 区域内：节点标签 blur(3px) ${count.labels} 个，卡片 blur(14px) ${count.panels} 个\n`,
  );

  console.log("滚动 800→2600（3D 在视口内）\n");
  await scrollMeasure(page, "A 基线（原样）");

  await page.addStyleTag({
    content: `div[style*="blur(3px)"]{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}`,
  });
  await scrollMeasure(page, "B 只关节点标签 blur(3px)");

  await page.addStyleTag({
    content: `.neo-panel{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}`,
  });
  await scrollMeasure(page, "C 再关卡片 blur(14px)");

  await fresh(page);

  await page.addStyleTag({
    content: `.neo-panel{backdrop-filter:none!important}`,
  });
  await scrollMeasure(page, "D 只关卡片 blur(14px)");

  await browser.close();
})();
