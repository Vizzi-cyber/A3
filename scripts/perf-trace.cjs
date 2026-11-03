/**
 * CDP 性能追踪：滚动 3D 区间时，统计各阶段耗时（Scripting / Style / Layout / Raster / GPU）
 * 用法: node scripts/perf-trace.cjs [url]
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

  const cdp = await page.context().newCDPSession(page);
  await cdp.send("Performance.enable");

  const cats = {};
  const events = [];
  cdp.on("Tracing.dataCollected", ({ value }) => {
    for (const e of value) {
      if (e.ph !== "X" && e.ph !== "B" && e.ph !== "E") continue;
      const cat = e.cat || "";
      const name = e.name || "";
      const dur = e.dur ? e.dur / 1000 : 0;
      if (!dur) continue;
      events.push({ cat, name, dur });
    }
  });

  await cdp.send("Tracing.start", {
    categories:
      "devtools.timeline,v8,blink,cc,gpu,disabled-by-default-devtools.timeline,disabled-by-default-devtools.timeline.frame",
    transferMode: "ReportEvents",
  });

  // 滚过 3D 区间
  await page.evaluate(() => window.scrollTo(0, 800));
  await page.waitForTimeout(400);
  for (let y = 800; y < 2600; y += 120) {
    await page.mouse.wheel(0, 120);
    await page.waitForTimeout(60);
  }
  await page.waitForTimeout(300);

  const done = new Promise((r) => cdp.once("Tracing.tracingComplete", r));
  await cdp.send("Tracing.end");
  await done;

  // 归类
  const bucket = (e) => {
    const n = e.name;
    if (/^(GPUTask|RasterTask|Paint|Compositor|UpdateLayer|ActivateLayer|DrawLazyPixelRef|ImageDecodeTask|Tile)/.test(n))
      return "GPU/光栅/合成";
    if (/^(UpdateLayoutTree|Layout|RecalcStyle|ParseHTML|InvalidateLayout)/.test(n)) return "样式/布局";
    if (/^(FunctionCall|EvaluateScript|TimerFire|EventDispatch|RunMicrotasks|v8|MajorGC|MinorGC)/.test(n)) return "脚本/GC";
    if (/^HitTest|^Commit|^BeginFrame|^DrawFrame|^ProxyMain/.test(n)) return "主线程帧调度";
    return "其他";
  };

  const agg = {};
  let total = 0;
  for (const e of events) {
    const b = bucket(e);
    agg[b] = (agg[b] || 0) + e.dur;
    total += e.dur;
  }

  console.log("=== 滚动 800→2600px（3D 区间）期间各阶段 CPU 耗时 ===");
  Object.entries(agg)
    .sort((a, b) => b[1] - a[1])
    .forEach(([k, v]) => {
      console.log(
        `  ${k.padEnd(14)} ${v.toFixed(0).padStart(7)} ms   (${((v / total) * 100).toFixed(1)}%)`,
      );
    });

  // top 单个事件
  console.log("\n=== 耗时最长的 15 类事件 ===");
  const byName = {};
  for (const e of events) {
    const k = e.name;
    byName[k] = byName[k] || { n: 0, total: 0, max: 0 };
    byName[k].n++;
    byName[k].total += e.dur;
    byName[k].max = Math.max(byName[k].max, e.dur);
  }
  Object.entries(byName)
    .sort((a, b) => b[1].total - a[1].total)
    .slice(0, 15)
    .forEach(([k, v]) => {
      console.log(
        `  ${k.padEnd(34)} 次数 ${String(v.n).padStart(5)} 累计 ${v.total.toFixed(0).padStart(7)}ms 单次最大 ${v.max.toFixed(1).padStart(7)}ms`,
      );
    });

  console.log("\n=== 总录制时长内的帧 ===");
  const frames = events.filter((e) => e.name === "DrawFrame" || e.name === "BeginFrame");
  console.log(`  ${frames.length} 个帧事件`);

  await browser.close();
})();
