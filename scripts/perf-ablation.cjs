/**
 * 消融实验：逐个关闭可疑因素，测同一滚动区间的帧耗时
 * 用法: node scripts/perf-ablation.cjs [url]
 */
const { chromium } = require("playwright");

const URL = process.argv[2] || "http://localhost:5173/";
const FROM = 1100;
const TO = 1900; // 最卡区间

async function run(page, label, setup) {
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForTimeout(4200);
  if (setup) await setup(page);

  await page.evaluate((y) => window.scrollTo(0, y), FROM);
  await page.waitForTimeout(600);

  await page.evaluate(() => {
    window.__f = [];
    window.__stop = false;
    let last = performance.now();
    const tick = () => {
      const now = performance.now();
      window.__f.push(now - last);
      last = now;
      if (!window.__stop) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  });

  const steps = 32;
  for (let i = 0; i < steps; i++) {
    await page.mouse.wheel(0, (TO - FROM) / steps);
    await page.waitForTimeout(50);
  }
  await page.waitForTimeout(200);

  const r = await page.evaluate(() => {
    window.__stop = true;
    const f = window.__f.filter((x) => x > 0 && x < 500).sort((a, b) => a - b);
    return {
      median: +f[Math.floor(f.length / 2)].toFixed(1),
      p95: +f[Math.floor(f.length * 0.95)].toFixed(1),
      max: +f[f.length - 1].toFixed(1),
      long: f.filter((x) => x > 32).length,
      n: f.length,
    };
  });
  console.log(
    `${label.padEnd(34)} | 中位 ${String(r.median).padStart(5)} | P95 ${String(r.p95).padStart(5)} | 最大 ${String(r.max).padStart(5)} | >32ms ${String(r.long).padStart(3)}/${r.n}`,
  );
  return r;
}

(async () => {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  console.log(`滚动区间 ${FROM}→${TO}（3D 知识空间在视口内的位置）\n`);
  console.log("消融项".padEnd(30) + " | 结果");

  await run(page, "A 基线（原样）", null);

  await run(page, "B 关闭所有 backdrop-filter", async (p) => {
    await p.addStyleTag({
      content: `* { backdrop-filter: none !important; -webkit-backdrop-filter: none !important; }`,
    });
  });

  await run(page, "C 隐藏 3D 卡片环（Html 叠层）", async (p) => {
    await p.addStyleTag({
      content: `.holo-ring-card { display: none !important; }`,
    });
  });

  await run(page, "D 隐藏所有 3D Html 叠层", async (p) => {
    await p.addStyleTag({
      content: `body > div > canvas ~ * { display: none !important; } .holo-ring-card{display:none!important}`,
    });
  });

  await run(page, "E 隐藏整个 Canvas", async (p) => {
    await p.addStyleTag({ content: `canvas { display: none !important; }` });
  });

  await run(page, "F B+C 同时关闭", async (p) => {
    await p.addStyleTag({
      content: `* { backdrop-filter: none !important; -webkit-backdrop-filter: none !important; } .holo-ring-card { display: none !important; }`,
    });
  });

  await browser.close();
})();
