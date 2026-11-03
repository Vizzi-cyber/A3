/**
 * 全功能页面测试 + 控制台错误检查
 * 运行：npx playwright test e2e/full-audit.spec.ts --headed
 */
import { test, expect, Page } from "@playwright/test";

const BASE = "http://localhost:5173";
const API = "http://localhost:8000/api/v1";

// 预获取 token
let TOKEN = "";

test.describe.configure({ mode: "serial" });

test.beforeAll(async ({ request }) => {
  const resp = await request.post(`${API}/auth/login`, {
    data: { student_id: "student_001", password: "123456" },
  });
  const json = await resp.json();
  TOKEN = json.access_token;
});

// 登陆辅助函数
async function login(page: Page) {
  await page.goto(`${BASE}/login`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(1000);

  // 注入 token 跳过登录
  await page.evaluate(
    ({ token }) => {
      localStorage.setItem(
        "learnlab-storage",
        JSON.stringify({
          state: { token, studentId: "student_001", isLoggedIn: true },
          version: 0,
        }),
      );
    },
    { token: TOKEN },
  );
  await page.goto(`${BASE}/`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);
}

// 测试页面列表（学生端）
const STUDENT_PAGES = [
  { name: "仪表盘", path: "/" },
  { name: "学习路径", path: "/learning-path" },
  { name: "资源中心", path: "/resources" },
  { name: "智能辅导", path: "/tutor" },
  { name: "知识冒险", path: "/challenges" },
  { name: "错误诊断", path: "/error-diagnosis" },
  { name: "项目协作", path: "/project-collaboration" },
  { name: "个人空间", path: "/personal" },
  { name: "知识库", path: "/knowledge-base" },
  { name: "排行榜", path: "/leaderboard" },
];

// 测试所有学生页面
for (const pageConf of STUDENT_PAGES) {
  test(`学生页面: ${pageConf.name}`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });

    await login(page);
    await page.goto(`${BASE}${pageConf.path}`);
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(3000);

    // 截图
    await page.screenshot({
      path: `test-results/${pageConf.name}.png`,
      fullPage: true,
    });

    // 检查是否有严重错误（忽略已知的 antd 警告）
    const criticalErrors = errors.filter(
      (e) =>
        !e.includes("antd:") &&
        !e.includes("runtime.lastError") &&
        !e.includes("React DevTools") &&
        !e.includes("Download the React DevTools") &&
        !e.includes("unique") &&
        !e.includes("key") &&
        !e.includes("Expected moveto") &&
        !e.includes("attribute d:"),
    );

    // 检查页面是否加载了内容
    const bodyText = await page.locator("body").innerText();

    expect(criticalErrors).toEqual([]);
    expect(bodyText.length).toBeGreaterThan(0);
  });
}

// 登录页测试
test("登录页加载", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (err) => errors.push(err.message));
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });

  await page.goto(`${BASE}/login`);
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(2000);

  await page.screenshot({ path: `test-results/登录页.png`, fullPage: true });

  const criticalErrors = errors.filter(
    (e) =>
      !e.includes("antd:") &&
      !e.includes("runtime.lastError") &&
      !e.includes("React DevTools"),
  );

  // 检查是否有登录表单
  const hasLoginForm =
    (await page.locator("input").count()) > 0 ||
    (await page.locator("button").count()) > 0;

  expect(criticalErrors).toEqual([]);
  expect(hasLoginForm).toBeTruthy();
});

// API 测试
test("核心API可用性", async ({ request }) => {
  const endpoints = [
    { name: "获取画像", path: `/profile/student_001` },
    { name: "仪表盘", path: `/dashboard/student_001/summary` },
    { name: "知识列表", path: `/knowledge/list` },
    { name: "项目列表", path: `/project-decomposer/projects` },
    { name: "知识库文件夹", path: `/kb/folders` },
    { name: "知识库笔记", path: `/kb/notes` },
  ];

  for (const ep of endpoints) {
    const resp = await request.get(`${API}${ep.path}`, {
      headers: { Authorization: `Bearer ${TOKEN}` },
    });
    expect(resp.status(), `${ep.name} 应返回 200`).toBe(200);
  }
});
