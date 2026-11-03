/**
 * 滚动性能探针 v2：在真实滚轮滚动过程中测量帧间隔
 * 用法: node scripts/perf-scroll-probe.cjs [url]
 */
const { chromium } = require("playwright");

const URL = process.argv[2] || "http://localhost:5173/";
const VH = 900;

async function measureScrolling(page, fromY, toY) {
  // 先把视口定位到 fromY
  await page.evaluate((y) => window.scrollTo(0, y), fromY);
  await page.waitForTimeout(600);

  // 开始记录 rAF 帧间隔 + longtask
  await page.evaluate(() => {
    window.__probe = { frames: [], longtasks: [], start: performance.now() };
    window.__probeStop = false;
    window.__raf = () => {
      let last = performance.now();
      const tick = () => {
        const now = performance.now();
        window.__probe.frames.push(now - last);
        last = now;
        if (!window.__probeStop) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    window.__raf();
    try {
      window.__po = new PerformanceObserver((l) => {
        l.getEntries().forEach((e) =>
          window.__probe.longtasks.push({
            dur: Math.round(e.duration),
            // 找到当时滚动位置附近的元素
          }),
        );
      });
      window.__po.observe({ entryTypes: ["longtask"] });
    } catch {}
  });

  // 真实滚轮滚动 fromY → toY
  const delta = toY - fromY;
  const steps = 30;
  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, delta / steps);
    await page.waitForTimeout(50); // ≈ 20 次/秒 的滚轮节奏
  }
  await page.waitForTimeout(200);

  return await page.evaluate(() => {
    window.__probeStop = true;
    const f = window.__probe.frames.filter((x) => x > 0 && x < 500);
    f.sort((a, b) => a - b);
    const scrollY = window.scrollY;
    const vh = window.innerHeight;
    const canvas = document.querySelector("canvas");
    const cr = canvas && canvas.getBoundingClientRect();
    return {
      scrollY,
      median: +f[Math.floor(f.length / 2)].toFixed(1),
      p95: +f[Math.floor(f.length * 0.95)].toFixed(1),
      max: +f[f.length - 1].toFixed(1),
      long: f.filter((x) => x > 32).length,
      total: f.length,
      longtasks: window.__probe.longtasks,
      canvasInView: cr ? Math.round(cr.top) < vh && Math.round(cr.bottom) > 0 : false,
      canvasTop: cr ? Math.round(cr.top) : null,
    };
  });
}

(async () => {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: VH } });
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(4500);

  const total = await page.evaluate(() => document.body.scrollHeight);
  console.log(`页面总高 ${total}px | 视口 ${VH}px | 约 ${(total / VH).toFixed(1)} 屏\n`);

  console.log("滚动区间    | 中位帧 | P95  | 最大 | >32ms(掉帧) | 3D在视口 | longtask");
  console.log("------------|--------|------|------|-------------|----------|---------");

  const step = 600;
  const results = [];
  for (let y = 0; y + step <= total - VH; y += step) {
    const r = await measureScrolling(page, y, y + step);
    results.push({ y, ...r });
    const lt = r.longtasks.length
      ? r.longtasks.map((l) => l.dur + "ms").join(",")
      : "-";
    const flag = r.p95 > 25 || r.long > 5 ? "  <<< 卡" : "";
    console.log(
      `${String(y).padStart(5)}→${String(y + step).padEnd(5)} | ${String(r.median).padStart(6)} | ${String(r.p95).padStart(4)} | ${String(r.max).padStart(4)} | ${String(r.long).padStart(4)}/${String(r.total).padEnd(3)} | ${String(r.canvasInView).padStart(8)} | ${lt}${flag}`,
    );
  }

  console.log("\n=== 高开销 CSS 元素（滚动时逐帧重绘）===");
  const heavy = await page.evaluate(() => {
    const out = [];
    const counts = {};
    document.querySelectorAll("*").forEach((el) => {
      const cs = getComputedStyle(el);
      let key = null;
      if (cs.backdropFilter && cs.backdropFilter !== "none")
        key = `backdrop-filter:${cs.backdropFilter}`;
      else if (cs.filter && cs.filter !== "none") key = `filter:${cs.filter}`;
      if (key) counts[key] = (counts[key] || 0) + 1;
    });
    return counts;
  });
  Object.entries(heavy)
    .sort((a, b) => b[1] - a[1])
    .forEach(([k, v]) => console.log(`  ${String(v).padStart(3)} 个   ${k}`));

  await browser.close();
})();
