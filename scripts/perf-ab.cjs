/**
 * 严格 A/B 交替测试：同页面反复切换，消除漂移与预热偏差
 * 用法: node scripts/perf-ab.cjs [url]
 */
const { chromium } = require("playwright");
const URL = process.argv[2] || "http://localhost:5173/";

const STYLE_ID = "__ab_style";

async function setVariant(page, variant) {
  await page.evaluate(
    (args) => {
      let el = document.getElementById(args.id);
      if (!el) {
        el = document.createElement("style");
        el.id = args.id;
        document.head.appendChild(el);
      }
      el.textContent = args.css;
      // 验证是否生效
    },
    { id: STYLE_ID, css: variant.css },
  );
}

async function scrollMeasure(page) {
  await page.evaluate(() => window.scrollTo(0, 700));
  await page.waitForTimeout(450);
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
  for (let y = 700; y < 2600; y += 100) {
    await page.mouse.wheel(0, 100);
    await page.waitForTimeout(55);
  }
  await page.waitForTimeout(150);
  const f = await page.evaluate(() => {
    window.__stop = true;
    return window.__tl.filter((x) => x > 0 && x < 800).sort((a, b) => a - b);
  });
  const q = (p) => f[Math.floor(f.length * p)] ?? NaN;
  return {
    p50: q(0.5),
    p90: q(0.9),
    p99: q(0.99),
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

  const VARIANTS = {
    A基线: "",
    B关标签blur: `div[style*="blur(3px)"]{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}`,
    C关卡片blur: `.neo-panel{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}`,
  };

  console.log("同页面交替 6 轮，每轮 A→B→C\n");
  const acc = { A基线: [], B关标签blur: [], C关卡片blur: [] };

  for (let round = 0; round < 6; round++) {
    for (const [name, css] of Object.entries(VARIANTS)) {
      await setVariant(page, { css });
      await page.waitForTimeout(300);
      const r = await scrollMeasure(page);
      acc[name].push(r);
      console.log(
        `第${round + 1}轮 ${name.padEnd(12)} 中位 ${r.p50.toFixed(1).padStart(5)} | P90 ${r.p90.toFixed(1).padStart(5)} | 最大 ${r.max.toFixed(0).padStart(4)} | >32ms ${String(r.long).padStart(2)}/${r.n}`,
      );
    }
    console.log("");
  }

  console.log("=== 汇总（中位数）===");
  for (const [name, runs] of Object.entries(acc)) {
    const med = (key) => {
      const v = runs.map((r) => r[key]).sort((a, b) => a - b);
      return v[Math.floor(v.length / 2)];
    };
    console.log(
      `  ${name.padEnd(12)} P50 ${med("p50").toFixed(1)} | P90 ${med("p90").toFixed(1)} | 最大 ${med("max").toFixed(0)} | >32ms 中位 ${med("long")}`,
    );
  }

  await browser.close();
})();
