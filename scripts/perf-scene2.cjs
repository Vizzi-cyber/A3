/**
 * 场景分析 v2：用 __neo 句柄统计 draw call / 三角形 / 各物件，并做分组消融
 * 用法: node scripts/perf-scene2.cjs [url]
 */
const { chromium } = require("playwright");
const URL = process.argv[2] || "http://localhost:5173/";

async function frameStat(page, n = 90) {
  return page.evaluate(
    (cnt) =>
      new Promise((res) => {
        const f = [];
        let last = performance.now();
        let i = 0;
        const tick = () => {
          const now = performance.now();
          f.push(now - last);
          last = now;
          if (++i < cnt) requestAnimationFrame(tick);
          else {
            f.sort((a, b) => a - b);
            res({
              median: +f[Math.floor(cnt / 2)].toFixed(1),
              p90: +f[Math.floor(cnt * 0.9)].toFixed(1),
              max: +f[cnt - 1].toFixed(1),
            });
          }
        };
        requestAnimationFrame(tick);
      }),
    n,
  );
}

(async () => {
  const browser = await chromium.launch({
    channel: "chrome",
    headless: false,
    args: ["--window-position=3000,3000", "--use-angle=default"],
  });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  page.on("console", (m) => {
    if (m.type() === "error") console.log("[err]", m.text().slice(0, 200));
  });
  await page.goto(URL, { waitUntil: "networkidle" });
  await page.waitForTimeout(5000);

  const ok = await page.evaluate(() => !!(window).__neo);
  console.log("__neo 句柄可用:", ok);
  if (!ok) {
    await browser.close();
    return;
  }

  // 1) 渲染统计
  const stats = await page.evaluate(() => {
    const { scene, gl } = window.__neo;
    const info = gl.info;
    const byType = {};
    let total = 0;
    scene.traverse((o) => {
      total++;
      byType[o.type] = (byType[o.type] || 0) + 1;
    });
    const groups = scene.children.map((c) => {
      let n = 0;
      c.traverse(() => n++);
      return { type: c.type, name: c.name || "(无名)", children: n };
    });
    // 统计光栅化开销
    let transparentBig = 0;
    scene.traverse((o) => {
      if (o.isMesh && o.material && o.material.transparent) transparentBig++;
    });
    return {
      render: { calls: info.render.calls, triangles: info.render.triangles, points: info.render.points },
      memory: info.memory,
      total,
      byType,
      groups,
      transparentMeshes: transparentBig,
      pixelRatio: gl.getPixelRatio(),
      canvasSize: [gl.domElement.width, gl.domElement.height],
    };
  });
  console.log("\n=== 渲染统计 ===");
  console.log("  draw calls:", stats.render.calls, "| 三角形:", stats.render.triangles, "| 点:", stats.render.points);
  console.log("  geometry:", JSON.stringify(stats.memory.geometries), "texture:", JSON.stringify(stats.memory.textures));
  console.log("  像素比:", stats.pixelRatio, "| canvas 实际分辨率:", stats.canvasSize.join("×"), "| 透明mesh:", stats.transparentMeshes);
  console.log("\n  场景对象类型:", JSON.stringify(stats.byType));
  console.log("\n  顶层节点:");
  stats.groups.forEach((g, i) => console.log(`   [${i}] ${g.type} ${g.name} (${g.children} 对象)`));

  // 2) 可见性消融
  const setVisible = (pred) =>
    page.evaluate((p) => {
      const { scene } = window.__neo;
      const fn = new Function("i", "o", "return (" + p + ")(i,o)");
      scene.children.forEach((o, i) => {
        if (i === 0) return;
        o.visible = fn(i, o.type);
      });
    }, pred.toString());

  console.log("\n=== 顶层节点消融（scrollY=1400）===");
  const measure = async () => {
    await page.evaluate(() => window.scrollTo(0, 1400));
    await page.waitForTimeout(500);
    return frameStat(page);
  };

  await setVisible(() => true);
  let r = await measure();
  console.log(`  全部显示                     中位 ${r.median}  P90 ${r.p90}  最大 ${r.max}`);

  for (let i = 1; i < stats.groups.length; i++) {
    const g = stats.groups[i];
    if (g.children <= 1) continue;
    await setVisible((idx) => idx !== i);
    r = await measure();
    console.log(
      `  隐藏[${i}] ${g.type}${g.name !== "(无名)" ? "/" + g.name : ""}(${g.children}个)  中位 ${r.median}  P90 ${r.p90}  最大 ${r.max}`,
    );
  }

  // 3) 全部只留 canvas 背景
  await setVisible(() => false);
  r = await measure();
  console.log(`  全部隐藏（空场景）            中位 ${r.median}  P90 ${r.p90}  最大 ${r.max}`);

  await setVisible(() => true);

  // 4) 逐步降级 gl 设置看看
  await page.evaluate(() => {
    const { gl } = window.__neo;
    gl.setPixelRatio(1);
  });
  r = await measure();
  console.log(`\n  像素比降到 1                 中位 ${r.median}  P90 ${r.p90}  最大 ${r.max}`);
  await page.evaluate(() => {
    const { gl } = window.__neo;
    gl.setPixelRatio(Math.min(2, window.devicePixelRatio));
  });

  await browser.close();
})();
