/**
 * 冷启动对照实验（每个变体独立浏览器实例，彻底隔离预热与上下文残留）
 * 用法: node scripts/perf-cold.cjs [url]
 */
const { chromium } = require("playwright");
const URL = process.argv[2] || "http://localhost:5173/";

async function coldPass(label, css) {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(4500);

  if (css) await page.addStyleTag({ content: css });

  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForTimeout(300);
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

  for (let y = 0; y < 2600; y += 100) {
    await page.mouse.wheel(0, 100);
    await page.waitForTimeout(55);
  }
  await page.waitForTimeout(150);

  const f = await page.evaluate(() => {
    window.__stop = true;
    return window.__tl.filter((x) => x > 0 && x < 800).sort((a, b) => a - b);
  });
  await browser.close();

  const q = (p) => f[Math.floor(f.length * p)] ?? NaN;
  const r = {
    p50: q(0.5),
    p90: q(0.9),
    max: f[f.length - 1] || 0,
    long: f.filter((x) => x > 32).length,
    n: f.length,
  };
  console.log(
    `${label.padEnd(28)} 中位 ${r.p50.toFixed(1).padStart(5)} | P90 ${r.p90.toFixed(1).padStart(5)} | 最大 ${r.max.toFixed(0).padStart(4)} | >32ms ${String(r.long).padStart(2)}/${String(r.n).padStart(3)}`,
  );
  return r;
}

const VARIANTS = [
  ["① 对照（原样）", null],
  [
    "② 去掉所有 backdrop-filter",
    `*{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}`,
  ],
  ["③ 隐藏 3D 画布", `canvas{display:none!important}`],
  [
    "④ 两者都去掉",
    `*{backdrop-filter:none!important}canvas{display:none!important}`,
  ],
];

(async () => {
  for (let round = 1; round <= 3; round++) {
    console.log(`\n──── 第 ${round} 轮（每项独立浏览器实例 + 冷启动）────`);
    for (const [name, css] of VARIANTS) await coldPass(name, css);
  }
})();
