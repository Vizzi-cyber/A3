/**
 * 决定性实验：分离「r3f 循环 CPU」「WebGL 绘制 GPU」「DOM 叠层」三者
 * 每个变体独立浏览器实例 + 冷启动滚动
 * 用法: node scripts/perf-decisive.cjs [url]
 */
const { chromium } = require("playwright");
const URL = process.argv[2] || "http://localhost:5173/";

async function coldPass(label, setup) {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(4500);
  if (setup) await setup(page);

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
    `${label.padEnd(30)} 中位 ${r.p50.toFixed(1).padStart(5)} | P90 ${r.p90.toFixed(1).padStart(5)} | 最大 ${r.max.toFixed(0).padStart(4)} | >32ms ${String(r.long).padStart(2)}/${String(r.n).padStart(3)}`,
  );
  return r;
}

const VARIANTS = [
  ["① 基线（原样）", null],
  [
    "② 3D 不绘制（循环照跑）",
    (p) =>
      p.evaluate(() => {
        window.__neo.scene.children.forEach((o, i) => {
          if (i > 0) o.visible = false;
        });
      }),
  ],
  [
    "③ 画布缩小到 240px",
    (p) =>
      p.evaluate(() => {
        const c = document.querySelector("canvas");
        c.style.width = "240px";
        c.style.height = "140px";
      }),
  ],
  [
    "④ 隐藏全部 3D DOM 叠层",
    (p) =>
      p.addStyleTag({
        content: `canvas ~ div, canvas + div { display:none !important }`,
      }),
  ],
  [
    "⑤ 关 Bloom 后处理",
    (p) =>
      p.evaluate(() => {
        // postprocessing EffectComposer 通过 gl 渲染，用 scene 上标记 + 直接屏蔽后处理 pass
        const gl = window.__neo.gl;
        gl.__origRender = gl.render.bind(gl);
        gl.render = function () {};
      }),
  ],
];

(async () => {
  for (let round = 1; round <= 2; round++) {
    console.log(`\n──── 第 ${round} 轮 ────`);
    for (const [name, setup] of VARIANTS) {
      try {
        await coldPass(name, setup);
      } catch (e) {
        console.log(`${name.padEnd(30)} 失败: ${e.message.slice(0, 60)}`);
      }
    }
  }
})();
