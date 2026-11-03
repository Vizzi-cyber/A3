/**
 * 消融实验 v4：连续滚动协议下，逐项定位（backdrop-filter / Html标签 / bloom / 像素比）
 * 用法: node scripts/perf-ablation4.cjs [url]
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
  for (let y = 800; y < 2600; y += 120) {
    await page.mouse.wheel(0, 120);
    await page.waitForTimeout(60);
  }
  await page.waitForTimeout(200);
  const f = await page.evaluate(() => {
    window.__stop = true;
    return window.__tl.filter((x) => x > 0 && x < 800).sort((a, b) => a - b);
  });
  const q = (p) => f[Math.floor(f.length * p)] ?? NaN;
  console.log(
    `${label.padEnd(36)} | 中位 ${q(0.5).toFixed(1).padStart(5)} | P90 ${q(0.9).toFixed(1).padStart(5)} | 最大 ${(f[f.length - 1] || 0).toFixed(0).padStart(4)} | >32ms ${String(f.filter((x) => x > 32).length).padStart(3)}/${f.length}`,
  );
}

async function fresh(page) {
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForTimeout(5000);
}

(async () => {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(5000);

  console.log("滚动 800→2600（3D 图谱在视口内）\n");

  // A 基线
  await scrollMeasure(page, "A 基线（原样）");

  // B 只去掉 35 个节点标签的 backdrop-filter
  const nLabels = await page.evaluate(() => {
    let n = 0;
    document.querySelectorAll("div").forEach((d) => {
      const cs = getComputedStyle(d);
      if (cs.backdropFilter && cs.backdropFilter.includes("blur(3px)")) n++;
    });
    return n;
  });
  console.log(`   （找到 ${nLabels} 个 blur(3px) 的 3D 节点标签）`);
  await page.addStyleTag({
    content: `div[style*="blur(3px)"] { backdrop-filter: none !important; -webkit-backdrop-filter: none !important; }`,
  });
  await scrollMeasure(page, "B 去掉节点标签 backdrop-blur(3px)");

  // C 在上面基础上把标签整块藏掉
  await page.addStyleTag({
    content: `div[style*="rgba(10, 14, 32"] { display: none !important; }`,
  });
  await scrollMeasure(page, "C 再隐藏全部节点名称标签");

  await fresh(page);

  // D 像素比降到 1
  await page.evaluate(() => window.__neo.gl.setPixelRatio(1));
  await scrollMeasure(page, "D 像素比 1（原为 devicePixelRatio）");

  // E 像素比 1 + 关标签 blur
  await page.addStyleTag({
    content: `div[style*="blur(3px)"] { backdrop-filter: none !important; }`,
  });
  await scrollMeasure(page, "E 像素比 1 + 关标签 blur");

  await fresh(page);

  // F 关 Bloom（后处理）
  await page.evaluate(() => {
    const { scene } = window.__neo;
    // postprocessing 的 composer 常挂在 scene 上或用 portal
    window.__neo.gl.__noBloom = true;
  });
  // 用 CSS 无法关，改用改 renderer 分辨率来推断 bloom 成本

  // G 降像素比到 0.75 看成本曲线
  for (const pr of [1.5, 1, 0.75, 0.5]) {
    await page.evaluate((p) => window.__neo.gl.setPixelRatio(p), pr);
    await scrollMeasure(page, `像素比 ${pr}`);
  }

  await browser.close();
})();
