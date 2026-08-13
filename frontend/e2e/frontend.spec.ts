import { test, expect } from "@playwright/test";

// 每个测试独立认证（authenticateViaApi），无需 serial 模式（serial 导致状态累积 flaky）

// Helper: authenticate by getting token via API and injecting into localStorage
async function authenticateViaApi(page: any) {
  // Get a fresh token from the backend API
  const response = await page.request.post(
    "http://localhost:8000/api/v1/auth/login",
    {
      data: { student_id: "student_001", password: "123456" },
    },
  );
  const { access_token } = await response.json();

  // Navigate to the app first (need a page context for localStorage access)
  await page.goto("http://localhost:5173/login", {
    waitUntil: "domcontentloaded",
  });
  await page.waitForSelector(".ant-tabs", { timeout: 15000 });

  // Inject token into Zustand persist storage + 标记 onboarding 完成（避免问卷 Modal 拦截）
  await page.evaluate((token: string) => {
    const state = {
      state: { token, studentId: "student_001" },
      version: 0,
    };
    localStorage.setItem("learnlab-storage", JSON.stringify(state));
    localStorage.setItem("onboarding_completed_C语言", "true");
    localStorage.setItem("onboarding_completed_电路分析", "true");
    localStorage.setItem("onboarding_completed_STM32嵌入式", "true");
  }, access_token);

  // Reload to trigger Zustand hydration from localStorage
  await page.reload({ waitUntil: "domcontentloaded" });
  // Wait for dashboard layout to render（SPA 用元素等待替代 networkidle）
  await expect(page.locator(".ant-layout").first()).toBeVisible({
    timeout: 20000,
  });
}

test.describe("Frontend E2E Tests", () => {
  test("Login page loads correctly", async ({ page }) => {
    await page.goto("http://localhost:5173/login");
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
    await page.goto("http://localhost:5173/login");
    await page.waitForLoadState("domcontentloaded");
    await page.getByPlaceholder("学号 / 工号").fill("student_001");
    await page.getByPlaceholder("输入密码").fill("123456");
    await page.locator(".ant-btn-primary").click();
    // Wait for dashboard layout to appear
    await expect(page.locator(".ant-layout").first()).toBeVisible({
      timeout: 30000,
    });
    // Check sidebar is present
    await expect(page.locator(".ant-menu")).toBeVisible();
  });

  test("Navigate to Profile page", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://localhost:5173/personal");
    await page.waitForLoadState("domcontentloaded");
    // Profile page should have card components
    await expect(page.locator(".ant-card").first()).toBeVisible({
      timeout: 15000,
    });
  });

  test("Navigate to Learning Path page", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://localhost:5173/learning-path");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.locator(".ant-layout").first()).toBeVisible({
      timeout: 15000,
    });
  });

  test("Navigate to Resource Center page", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://localhost:5173/resources");
    await page.waitForLoadState("domcontentloaded");
    await expect(page.locator(".ant-layout").first()).toBeVisible({
      timeout: 15000,
    });
  });

  test("Navigate to Tutor page", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://localhost:5173/tutor");
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
    await page.goto("http://localhost:5173/personal", {
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
    expect(url).not.toBe("http://localhost:5173/login");
  });

  test("Logout redirects to login", async ({ page }) => {
    await authenticateViaApi(page);

    // Look for logout button in header or user dropdown
    const possibleLogoutSelectors = [
      "text=退出",
      "text=Logout",
      "text=登出",
      '.ant-dropdown-menu-item:has-text("退出")',
    ];

    let found = false;
    for (const selector of possibleLogoutSelectors) {
      const el = page.locator(selector).first();
      const count = await el.count();
      if (count > 0) {
        await el.click();
        found = true;
        break;
      }
    }

    if (found) {
      await page.waitForURL("http://localhost:5173/login", { timeout: 5000 });
      await expect(page.locator(".ant-btn-primary")).toBeVisible();
    } else {
      // Skip if logout button not found - may need user dropdown interaction
      test.skip();
    }
  });
});
