/**
 * CDP 追踪 v2：抓出滚动时的具体 JS 函数名 + 每帧耗时分布
 * 用法: node scripts/perf-trace2.cjs [url]
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
  const events = [];
  cdp.on("Tracing.dataCollected", ({ value }) => events.push(...value));

  await cdp.send("Tracing.start", {
    categories:
      "devtools.timeline,v8,blink,cc,gpu,disabled-by-default-devtools.timeline,disabled-by-default-devtools.timeline.frame",
    transferMode: "ReportEvents",
  });

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

  // 1) 具体函数名
  const fn = {};
  for (const e of events) {
    if (e.name === "FunctionCall" || e.name === "EvaluateScript") {
      const name =
        (e.args && e.args.data && (e.args.data.functionName || e.args.data.url)) ||
        "(anonymous)";
      const dur = (e.dur || e.tdur || 0) / 1000;
      fn[name] = fn[name] || { n: 0, total: 0, max: 0 };
      fn[name].n++;
      fn[name].total += dur;
      fn[name].max = Math.max(fn[name].max, dur);
    }
  }
  console.log("=== 滚动期间执行的 JS 函数（按累计耗时）===");
  Object.entries(fn)
    .sort((a, b) => b[1].total - a[1].total)
    .slice(0, 20)
    .forEach(([k, v]) =>
      console.log(
        `  ${k.slice(0, 48).padEnd(50)} 次数 ${String(v.n).padStart(5)} 累计 ${v.total.toFixed(1).padStart(7)}ms 最大 ${v.max.toFixed(1).padStart(6)}ms`,
      ),
    );

  // 2) 每帧主线程总耗时
  const frames = events
    .filter((e) => e.name === "ProxyMain::BeginMainFrame" || e.name === "WebFrameWidgetImpl::BeginMainFrame")
    .map((e) => ({ dur: (e.dur || 0) / 1000, ts: e.ts }));
  const durs = frames.map((f) => f.dur).sort((a, b) => a - b);
  const q = (p) => (durs.length ? durs[Math.floor(durs.length * p)] : NaN);
  console.log(`\n=== 主线程每帧耗时（共 ${durs.length} 帧）===`);
  console.log(
    `  中位 ${q(0.5).toFixed(1)}ms | P90 ${q(0.9).toFixed(1)}ms | 最大 ${durs[durs.length - 1].toFixed(1)}ms | >16ms 的帧 ${durs.filter((d) => d > 16).length} 个`,
  );

  // 3) Animate / 样式 / 布局 细分
  const stages = {};
  for (const e of events) {
    const D = (e.dur || 0) / 1000;
    if (!D) continue;
    if (
      [
        "Blink.Animate.UpdateTime",
        "UpdateLayoutTree",
        "Layout",
        "RecalcStyle",
        "Paint",
        "RasterTask",
        "GPUTask",
        "PageAnimator::serviceScriptedAnimations",
        "Commit",
        "Layerize",
        "UpdateLayer",
      ].includes(e.name)
    ) {
      stages[e.name] = stages[e.name] || { n: 0, total: 0, max: 0 };
      stages[e.name].n++;
      stages[e.name].total += D;
      stages[e.name].max = Math.max(stages[e.name].max, D);
    }
  }
  console.log("\n=== 关键阶段（滚动期间累计）===");
  Object.entries(stages)
    .sort((a, b) => b[1].total - a[1].total)
    .forEach(([k, v]) =>
      console.log(
        `  ${k.padEnd(38)} 次数 ${String(v.n).padStart(5)} 累计 ${v.total.toFixed(0).padStart(6)}ms 单次最大 ${v.max.toFixed(1).padStart(6)}ms`,
      ),
    );

  await browser.close();
})();
