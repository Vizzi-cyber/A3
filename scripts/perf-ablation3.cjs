/**
 * 消融实验 v3：连续滚动协议 + 运行时切换 3D 元素
 * 用法: node scripts/perf-ablation3.cjs [url]
 */
const { chromium } = require("playwright");
const URL = process.argv[2] || "http://localhost:5173/";

// 连续滚动 800→2600（卡顿区间），统计每帧 dt
async function scrollAndMeasure(page, label) {
  await page.evaluate(() => {
    window.scrollTo(0, 800);
  });
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
  const long = f.filter((x) => x > 32).length;
  console.log(
    `${label.padEnd(38)} | 中位 ${q(0.5).toFixed(1).padStart(5)} | P90 ${q(0.9).toFixed(1).padStart(5)} | 最大 ${(f[f.length - 1] || 0).toFixed(0).padStart(4)} | >32ms ${String(long).padStart(3)}/${f.length}`,
  );
  return { median: q(0.5), long };
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

  const build = () =>
    page.evaluate(() => {
      const { scene } = window.__neo;
      return scene.children.map((c, i) => {
        let n = 0;
        c.traverse(() => n++);
        return { i, type: c.type, n };
      });
    });

  const groups = await build();
  const bigGroup = groups.reduce((a, b) => (b.n > a.n ? b : a));

  console.log("滚动 800→2600（3D 在视口内）连续帧统计\n");

  // 基线
  await scrollAndMeasure(page, "A 基线（原样）");

  // 关 Bloom（postprocessing 全链路）
  await page.evaluate(() => {
    const { scene } = window.__neo;
    scene.traverse((o) => {
      if (o.__r3f && /EffectComposer/.test(o.type || "")) o.visible = false;
    });
    // r3f postprocessing 的 EffectComposer 会接管渲染，标记它不可见
    window.__neo.scene.userData.__noPost = true;
  });
  await scrollAndMeasure(page, "B 标记禁用后处理（占位）");

  // 隐藏最大 group（力导向图谱）
  await page.evaluate((idx) => {
    window.__neo.scene.children[idx].visible = false;
  }, bigGroup.i);
  await scrollAndMeasure(page, `C 隐藏最大 group[${bigGroup.i}] (${bigGroup.n}个对象)`);
  await page.evaluate((idx) => {
    window.__neo.scene.children[idx].visible = true;
  }, bigGroup.i);

  // 逐个隐藏其余 group
  for (const g of groups) {
    if (g.n <= 3 || g.i === bigGroup.i) continue;
    await page.evaluate((idx) => {
      window.__neo.scene.children[idx].visible = false;
    }, g.i);
    await scrollAndMeasure(page, `D 隐藏 group[${g.i}] ${g.type}(${g.n}个)`);
    await page.evaluate((idx) => {
      window.__neo.scene.children[idx].visible = true;
    }, g.i);
  }

  // 全部隐藏
  await page.evaluate(() => {
    window.__neo.scene.children.forEach((o, i) => {
      if (i > 0) o.visible = false;
    });
  });
  await scrollAndMeasure(page, "E 隐藏全部 3D 内容（空场景）");
  await page.evaluate(() => {
    window.__neo.scene.children.forEach((o) => (o.visible = true));
  });

  // 降低像素比
  await page.evaluate(() => window.__neo.gl.setPixelRatio(0.5));
  await scrollAndMeasure(page, "F 像素比 0.5（降分辨率渲染）");
  await page.evaluate(() => window.__neo.gl.setPixelRatio(1));

  // 关闭所有透明材质
  await page.evaluate(() => {
    window.__neo.gl.info.autoReset = false;
  });

  await browser.close();
})();
