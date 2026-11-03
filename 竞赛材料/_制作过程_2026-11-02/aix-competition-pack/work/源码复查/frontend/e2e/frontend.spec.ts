import { test, expect, type Page } from "@playwright/test";

// 每个测试独立认证（authenticateViaApi），无需 serial 模式（serial 导致状态累积 flaky）

let studentToken: string | undefined;

async function authenticateViaApi(page: Page) {
  if (!studentToken) {
    const response = await page.request.post(
      "http://127.0.0.1:8000/api/v1/auth/login",
      { data: { student_id: "student_001", password: "123456" } },
    );
    expect(response.ok()).toBeTruthy();
    studentToken = (await response.json()).access_token;
    expect(studentToken).toBeTruthy();
  }

  await page.addInitScript((token: string) => {
    localStorage.setItem(
      "learnlab-storage",
      JSON.stringify({
        state: {
          token,
          studentId: "student_001",
          userInfo: {
            student_id: "student_001",
            username: "测试学生",
            role: "student",
          },
          currentSubject: "C语言",
        },
        version: 0,
      }),
    );
    localStorage.setItem("onboarding_completed_C语言", "true");
    localStorage.setItem("onboarding_completed_电路分析", "true");
    localStorage.setItem("onboarding_completed_STM32嵌入式", "true");
  }, studentToken);
  await page.goto("http://127.0.0.1:5173/", {
    waitUntil: "domcontentloaded",
  });
  await expect(page.locator(".ant-layout").first()).toBeVisible({
    timeout: 30000,
  });
}

test.describe("Frontend E2E Tests", () => {
  test("Login page loads correctly", async ({ page }) => {
    await page.goto("http://127.0.0.1:5173/login");
    await page.waitForLoadState("domcontentloaded");
    await expect(page).toHaveTitle(/LearnLab/);

    // Wait for Ant Design to render
    await page.waitForSelector(".ant-tabs", { timeout: 10000 });

    // Check login tab is active
    await expect(page.locator(".ant-tabs-tab-active")).toBeVisible();

    // Check form inputs by placeholder（登录 Tab 默认激活）
    await expect(page.getByPlaceholder("学号 / 工号")).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByPlaceholder("输入密码")).toBeVisible({
      timeout: 10000,
    });

    // Check login button by class (Ant Design primary button)
    await expect(page.locator(".ant-btn-primary")).toBeVisible({
      timeout: 10000,
    });
  });

  test("Login with valid credentials", async ({ page }) => {
    await page.goto("http://127.0.0.1:5173/login");
    await page.waitForLoadState("domcontentloaded");
    await page.getByPlaceholder("学号 / 工号").fill("student_001");
    await page.getByPlaceholder("输入密码").fill("123456");
    await Promise.all([
      page.waitForURL((url) => url.pathname !== "/login", {
        timeout: 30000,
      }),
      page.getByRole("button", { name: /登\s*录/ }).click(),
    ]);
    // Wait for dashboard layout to appear
    await expect(page.locator(".ant-layout").first()).toBeVisible({
      timeout: 30000,
    });
    // Check sidebar is present
    await expect(page.locator(".ant-menu")).toBeVisible();
  });

  test("Navigate to Profile page", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://127.0.0.1:5173/personal");
    await page.waitForLoadState("domcontentloaded");
    // Profile page should have card components
    await expect(page.locator(".ant-card").first()).toBeVisible({
      timeout: 15000,
    });
  });

  test("Navigate to Learning Path page", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://127.0.0.1:5173/learning-path");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.locator(".ant-layout").first()).toBeVisible({
      timeout: 15000,
    });
  });

  test("Navigate to Resource Center page", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://127.0.0.1:5173/resources");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.locator(".ant-layout").first()).toBeVisible({
      timeout: 15000,
    });
  });

  test("Navigate to Tutor page", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://127.0.0.1:5173/tutor");
    await page.waitForLoadState("domcontentloaded");
    // 页面框架加载（连跑时后端响应慢，放宽等待）
    await expect(page.locator(".ant-layout").first()).toBeVisible({
      timeout: 30000,
    });
    // Tutor 页有可见输入框（ChatPanel）
    await expect(page.locator("input:visible").first()).toBeVisible({
      timeout: 30000,
    });
  });

  test("Navigate to Personal Space page", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://127.0.0.1:5173/personal", {
      waitUntil: "domcontentloaded",
    });
    // 个人空间加载多个 API（画像/趋势/反思），等待时间放宽
    await expect(page.locator(".ant-layout").first()).toBeVisible({
      timeout: 30000,
    });
  });

  test("Sidebar navigation works", async ({ page }) => {
    await authenticateViaApi(page);

    // Wait for sidebar menu to render
    await page.waitForSelector(".ant-menu", { timeout: 10000 });

    // Find all menu items (Ant Design menu items)
    const menuItems = await page
      .locator(".ant-menu-item, .ant-menu-item-only-child")
      .all();
    console.log("Menu items found:", menuItems.length);

    if (menuItems.length === 0) {
      // If no menu items, just verify sidebar exists
      await expect(page.locator(".ant-layout-sider")).toBeVisible();
      return;
    }

    // Click second menu item
    await menuItems[1].click();
    await page.waitForTimeout(1000);
    const url = page.url();
    expect(url).not.toBe("http://127.0.0.1:5173/login");
  });

  test("Logout redirects to login", async ({ page }) => {
    await authenticateViaApi(page);
    await page.getByRole("button", { name: "用户菜单" }).click();
    await page.getByRole("menuitem", { name: /退出登录/ }).click();

    await expect(page).toHaveURL("http://127.0.0.1:5173/login");
    await expect(page.getByRole("button", { name: /登\s*录/ })).toBeVisible();
  });
});
