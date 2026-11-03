/**
 * 消融实验 v2：用连续滚动协议，聚焦 3D 卡顿区间
 * 用法: node scripts/perf-ablation2.cjs [url]
 */
const { chromium } = require("playwright");

const URL = process.argv[2] || "http://localhost:5173/";

async function run(page, label, setup) {
  await page.reload({ waitUntil: "networkidle" });
  await page.waitForTimeout(4200);
  if (setup) await setup(page);

  await page.evaluate(() => {
    window.__tl = [];
    window.__stop = false;
    const canvas = document.querySelector("canvas");
    let last = performance.now();
    const tick = () => {
      const now = performance.now();
      const vh = window.innerHeight;
      const cr = canvas ? canvas.getBoundingClientRect() : null;
      window.__tl.push({
        dt: now - last,
        y: Math.round(window.scrollY),
        c3d: cr ? cr.top < vh && cr.bottom > 0 : false,
      });
      last = now;
      if (!window.__stop) requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
  });

  const total = await page.evaluate(
    () => document.body.scrollHeight - window.innerHeight,
  );
  // 只滚到 3D 区间之后一点，聚焦卡顿区
  const end = Math.min(total, 3000);
  for (let y = 0; y < end; y += 120) {
    await page.mouse.wheel(0, 120);
    await page.waitForTimeout(60);
  }
  await page.waitForTimeout(300);

  const t = await page.evaluate(() => {
    window.__stop = true;
    return window.__tl.filter((x) => x.dt > 0 && x.dt < 600);
  });

  // 只看 3D 在视口内的帧
  const with3d = t.filter((f) => f.c3d).map((f) => f.dt);
  with3d.sort((a, b) => a - b);
  const q = (p) => with3d.length ? with3d[Math.floor(with3d.length * p)] : NaN;
  console.log(
    `${label.padEnd(36)} | 中位 ${q(0.5).toFixed(1).padStart(5)} | P90 ${q(0.9).toFixed(1).padStart(5)} | 最大 ${(with3d[with3d.length - 1] || 0).toFixed(0).padStart(4)} | >32ms ${String(with3d.filter((x) => x > 32).length).padStart(3)}/${with3d.length}`,
  );
}

(async () => {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });

  console.log("仅统计「3D 在视口内」的帧\n");
  await run(page, "A 基线（原样）", null);
  await run(page, "B 关掉所有 backdrop-filter", (p) =>
    p.addStyleTag({
      content: `*{backdrop-filter:none!important;-webkit-backdrop-filter:none!important}`,
    }),
  );
  await run(page, "C 隐藏 3D 名称标签(.holo…)", (p) =>
    p.addStyleTag({ content: `canvas ~ div > div { }` }),
  );
  await run(page, "D 3D 区域整体 display:none", (p) =>
    p.addStyleTag({ content: `canvas{display:none!important}` }),
  );
  await run(page, "E 只留 canvas（去掉 Html 叠层）", (p) =>
    p.addStyleTag({
      content: `canvas{display:block!important} body div div[style*="translate"]{}
      #root > div > section:nth-of-type(3) > div:nth-child(2) > div > div > div[style]{opacity:0}`,
    }),
  );

  await browser.close();
})();
