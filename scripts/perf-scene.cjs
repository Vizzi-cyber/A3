/**
 * 探查 live three.js 场景：统计对象数量、绘制调用、以及分组的渲染代价
 * 用法: node scripts/perf-scene.cjs [url]
 */
const { chromium } = require("playwright");
const URL = process.argv[2] || "http://localhost:5173/";

const ONSTATS = `() => {
  const keys = Object.keys(document.querySelector('canvas'));
  return keys;
}`;

(async () => {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(4500);

  // 找 canvas 上的 r3f 句柄
  const probe = await page.evaluate(() => {
    const c = document.querySelector("canvas");
    const own = Object.keys(c).filter((k) => k.startsWith("__"));
    // r3f v8 会把 root 存在 canvas 的 __r3f 或 __reactFiber
    return {
      ownKeys: own,
      hasR3F: !!c.__r3f,
      r3fKeys: c.__r3f ? Object.keys(c.__r3f) : null,
      // 全局线索
      globalR3F: Object.keys(window).filter(
        (k) => /r3f|three|fiber/i.test(k),
      ),
    };
  });
  console.log("canvas 上的 r3f 线索:", JSON.stringify(probe, null, 2));

  // 尝试通过 __r3f.store.getState().scene 拿到场景
  const stats = await page.evaluate(() => {
    const c = document.querySelector("canvas");
    let scene = null;
    try {
      const r3f = c.__r3f;
      if (r3f) {
        // v8: store 在 r3f.store 或 r3f.root.getState()
        const st =
          (r3f.store && r3f.store.getState && r3f.store.getState()) ||
          (r3f.root && r3f.root.getState && r3f.root.getState()) ||
          null;
        scene = st && st.scene;
      }
    } catch (e) {}
    if (!scene) return { ok: false };

    const byType = {};
    let total = 0;
    scene.traverse((o) => {
      total++;
      byType[o.type] = (byType[o.type] || 0) + 1;
    });

    // 按顶层子节点统计
    const groups = scene.children.map((c) => {
      let n = 0;
      c.traverse(() => n++);
      return { type: c.type, name: c.name || "", children: n };
    });

    return { ok: true, total, byType, groups };
  });
  console.log("\n场景统计:", JSON.stringify(stats, null, 2));

  if (!stats.ok) {
    console.log("拿不到场景句柄，改用 CSS 级消融");
    await browser.close();
    return;
  }

  // 分组消融：轮流隐藏顶层 group，测 loop 耗时
  const measure = async (hideIndex) => {
    await page.evaluate((idx) => {
      const c = document.querySelector("canvas");
      const r3f = c.__r3f;
      const st =
        (r3f.store && r3f.store.getState()) || (r3f.root && r3f.root.getState());
      st.scene.children.forEach((o, i) => {
        if (i === 0) return; // background color 不动
        o.visible = idx === null || i !== idx;
      });
    }, hideIndex);

    await page.evaluate(() => window.scrollTo(0, 1400));
    await page.waitForTimeout(500);

    const r = await page.evaluate(
      () =>
        new Promise((res) => {
          const f = [];
          let last = performance.now();
          let n = 0;
          const tick = () => {
            const now = performance.now();
            f.push(now - last);
            last = now;
            if (++n < 90) requestAnimationFrame(tick);
            else {
              f.sort((a, b) => a - b);
              res({
                median: +f[45].toFixed(1),
                p90: +f[Math.floor(f.length * 0.9)].toFixed(1),
              });
            }
          };
          requestAnimationFrame(tick);
        }),
    );
    return r;
  };

  console.log("\n=== 顶层节点消融（scrollY=1400，仅 3D 在视口）===");
  const base = await measure(null);
  console.log(`全部显示`.padEnd(28) + ` 中位 ${base.median}ms  P90 ${base.p90}ms`);
  for (let i = 1; i < stats.groups.length; i++) {
    const g = stats.groups[i];
    if (g.children <= 1) continue;
    const r = await measure(i);
    console.log(
      `隐藏[${i}] ${g.type}/${g.name || "-"}(${g.children}个对象)`.padEnd(28) +
        ` 中位 ${r.median}ms  P90 ${r.p90}ms`,
    );
  }
  await measure(null);

  await browser.close();
})();
