/**
 * 对照验证：在同一页面内交替切换「旧配置」与「新配置」，只测 3D 区块滚动
 *   旧配置 = dpr 2（模拟高分屏的 dpr:[1,2]）+ Bloom resolutionScale 1
 *   新配置 = dpr 1 + Bloom resolutionScale 0.5
 * 用法: node scripts/perf-verify2.cjs [url]
 */
const { chromium } = require("playwright");
const URL = process.argv[2] || "http://localhost:5173/";

async function scrollMeasure(page) {
  await page.evaluate(() => window.scrollTo(0, 800));
  await page.waitForTimeout(600);
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
  for (let y = 800; y < 2700; y += 100) {
    await page.mouse.wheel(0, 100);
    await page.waitForTimeout(55);
  }
  await page.waitForTimeout(200);
  const f = await page.evaluate(() => {
    window.__stop = true;
    return window.__tl.filter((x) => x > 0 && x < 800).sort((a, b) => a - b);
  });
  const q = (p) => f[Math.floor(f.length * p)] ?? NaN;
  return {
    p50: q(0.5),
    p90: q(0.9),
    max: f[f.length - 1] || 0,
    long: f.filter((x) => x > 32).length,
    n: f.length,
  };
}

(async () => {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(6000);

  const setOld = () =>
    page.evaluate(() => {
      window.__neo.gl.setPixelRatio(2); // 旧：高分屏下 dpr 取 2
    });
  const setNew = () =>
    page.evaluate(() => {
      window.__neo.gl.setPixelRatio(1); // 新：固定 1
    });

  const report = (label, r) =>
    console.log(
      `${label.padEnd(26)} 中位 ${r.p50.toFixed(1).padStart(5)} | P90 ${r.p90.toFixed(1).padStart(5)} | 最大 ${r.max.toFixed(0).padStart(4)} | >32ms ${String(r.long).padStart(2)}/${r.n}`,
    );

  console.log("滚动 800→2700（3D 板块在视口内），同页交替\n");
  const acc = { 旧: [], 新: [] };
  for (let r = 1; r <= 4; r++) {
    await setOld();
    await page.waitForTimeout(400);
    const a = await scrollMeasure(page);
    acc["旧"].push(a);
    report(`第${r}轮 旧 dpr=2`, a);

    await setNew();
    await page.waitForTimeout(400);
    const b = await scrollMeasure(page);
    acc["新"].push(b);
    report(`第${r}轮 新 dpr=1`, b);
    console.log("");
  }

  const med = (arr, k) => {
    const v = arr.map((x) => x[k]).sort((a, b) => a - b);
    return v[Math.floor(v.length / 2)];
  };
  console.log("=== 汇总（中位数）===");
  for (const [k, arr] of Object.entries(acc))
    console.log(
      `  ${k.padEnd(4)} P50 ${med(arr, "p50").toFixed(1)} | P90 ${med(arr, "p90").toFixed(1)} | 最大 ${med(arr, "max").toFixed(0)} | >32ms ${med(arr, "long").toFixed(1)}`,
    );

  await browser.close();
})();
