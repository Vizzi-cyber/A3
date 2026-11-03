/**
 * 连续滚动帧时间线：记录每一帧的耗时 + 当时的 scrollY + 视口内是否有 3D
 * 用法: node scripts/perf-continuous.cjs [url]
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
  await page.waitForTimeout(4500);

  await page.evaluate(() => {
    window.__timeline = [];
    window.__stop = false;
    const canvas = document.querySelector("canvas");
    let last = performance.now();
    const tick = () => {
      const now = performance.now();
      const vh = window.innerHeight;
      const cr = canvas.getBoundingClientRect();
      window.__timeline.push({
        dt: now - last,
        y: Math.round(window.scrollY),
        c3d: cr.top < vh && cr.bottom > 0,
      });
      last = now;
      if (!window.__stop) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  });

  // 全程匀速滚动到底
  const total = await page.evaluate(() => document.body.scrollHeight - window.innerHeight);
  const chunk = 120;
  for (let y = 0; y < total; y += chunk) {
    await page.mouse.wheel(0, chunk);
    await page.waitForTimeout(60);
  }
  await page.waitForTimeout(300);

  const t = await page.evaluate(() => {
    window.__stop = true;
    return window.__timeline.filter((x) => x.dt > 0 && x.dt < 600);
  });

  // 按滚动位置分桶统计
  const BUCKET = 400;
  const buckets = new Map();
  t.forEach((f) => {
    const b = Math.floor(f.y / BUCKET) * BUCKET;
    if (!buckets.has(b)) buckets.set(b, { frames: [], c3d: 0, n: 0 });
    const e = buckets.get(b);
    e.frames.push(f.dt);
    e.n++;
    if (f.c3d) e.c3d++;
  });

  console.log("\nscrollY 区间 | 中位帧 | P90  | 最大 | 掉帧>32ms | 3D在视口占比");
  console.log("-------------|--------|------|------|-----------|-------------");
  [...buckets.keys()].sort((a, b) => a - b).forEach((b) => {
    const e = buckets.get(b);
    const f = [...e.frames].sort((a, c) => a - c);
    const median = f[Math.floor(f.length / 2)];
    const p90 = f[Math.floor(f.length * 0.9)];
    const max = f[f.length - 1];
    const long = f.filter((x) => x > 32).length;
    const flag = long > 3 ? "  <<< 卡" : "";
    console.log(
      `${String(b).padStart(5)}-${String(b + BUCKET).padEnd(6)} | ${median.toFixed(1).padStart(6)} | ${p90.toFixed(1).padStart(4)} | ${max.toFixed(1).padStart(4)} | ${String(long).padStart(4)}/${String(e.n).padEnd(3)} | ${((e.c3d / e.n) * 100).toFixed(0).padStart(3)}%${flag}`,
    );
  });

  // 掉帧最严重的 10 帧
  console.log("\n=== 最严重的 10 帧 ===");
  [...t]
    .sort((a, b) => b.dt - a.dt)
    .slice(0, 10)
    .forEach((f) => console.log(`  ${f.dt.toFixed(1)}ms @ scrollY=${f.y} 3D=${f.c3d}`));

  await browser.close();
})();
