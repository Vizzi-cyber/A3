/**
 * 修复效果验证：冷启动协议，模拟 DPR=2 的高分屏（用 CDP 强制 deviceScaleFactor）
 * 用法: node scripts/perf-verify.cjs [url]
 */
const { chromium } = require("playwright");
const URL = process.argv[2] || "http://localhost:5173/";

async function coldPass(label, dsf) {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const ctx = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: dsf,
  });
  const page = await ctx.newPage();
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(4500);

  const info = await page.evaluate(() => {
    const c = document.querySelector("canvas");
    return {
      dpr: window.devicePixelRatio,
      canvas: c ? `${c.width}×${c.height}` : "无",
    };
  });

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
  console.log(
    `${label.padEnd(22)} DPR=${info.dpr} canvas=${String(info.canvas).padStart(9)} | 中位 ${q(0.5).toFixed(1).padStart(5)} | P90 ${q(0.9).toFixed(1).padStart(5)} | 最大 ${(f[f.length - 1] || 0).toFixed(0).padStart(4)} | >32ms ${String(f.filter((x) => x > 32).length).padStart(2)}/${f.length}`,
  );
}

(async () => {
  console.log("修复后（dpr=1 + Bloom resolutionScale=0.5），冷启动滚动 0→2600\n");
  for (let r = 1; r <= 3; r++) {
    console.log(`── 第 ${r} 轮 ──`);
    await coldPass("DPR=1 (1080p)", 1);
    await coldPass("DPR=2 (2K/高分屏)", 2);
  }
})();
