const { chromium } = require("playwright");
const BASE = "https://www.dreamlast.cn";
const OUT = "E:/开发/learnlabAI教学平台/交付材料/_assets";
const fs = require("fs");
fs.mkdirSync(OUT, { recursive: true });
(async () => {
  const browser = await chromium.launch({ channel: "chrome" });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await ctx.newPage();
  const shot = async (name) => {
    await page.waitForTimeout(3200);
    await page.screenshot({ path: `${OUT}/${name}.png` });
    console.log("shot", name);
  };
  // 登录页
  await page.goto(BASE + "/login", { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1500);
  await page.evaluate(() => localStorage.clear());
  await page.reload();
  await page.waitForTimeout(2000);
  await shot("01-登录页");
  // 学生
  await page.fill('input[placeholder*="学号"]', "student_001");
  await page.fill('input[type=password]', "123456");
  await page.click('button[type=submit]');
  await page.waitForTimeout(3500);
  const studentPages = [
    ["02-学生仪表盘", "/"],
    ["03-学习路径", "/learning-path"],
    ["04-学习中心", "/resources"],
    ["05-知识冒险", "/challenges"],
    ["06-排行榜", "/leaderboard"],
    ["07-AI智能辅导", "/tutor"],
    ["08-错误诊断", "/error-diagnosis"],
    ["09-个人空间", "/personal"],
  ];
  for (const [n, p] of studentPages) {
    await page.goto(BASE + p, { waitUntil: "domcontentloaded" });
    await shot(n);
  }
  // 教师
  await page.evaluate(() => localStorage.clear());
  await page.goto(BASE + "/login", { waitUntil: "domcontentloaded" });
  await page.waitForTimeout(1200);
  await page.fill('input[placeholder*="学号"]', "T001");
  await page.fill('input[type=password]', "Teacher123");
  await page.click('button[type=submit]');
  await page.waitForTimeout(3500);
  const teacherPages = [
    ["10-教师工作台", "/teacher"],
    ["11-学情分析", "/teacher/analytics"],
    ["12-试点数据分析", "/teacher/pilot-report"],
    ["13-AI智能组卷", "/teacher/smart-quiz"],
  ];
  for (const [n, p] of teacherPages) {
    await page.goto(BASE + p, { waitUntil: "domcontentloaded" });
    await shot(n);
  }
  console.log("ALL_DONE");
  await browser.close();
})().catch((e) => { console.error("FATAL:", String(e).slice(0, 200)); process.exit(1); });
