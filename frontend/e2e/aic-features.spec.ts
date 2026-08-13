/**
 * AIC 新功能 E2E 验证（需本地前后端已启动：8000/5173）
 * 覆盖：跨学科学习链路 / 试点数据分析 / 电路故障实验 / STM32 AI分析
 */
import { test, expect } from "@playwright/test";

const BASE = "http://localhost:5173";

/** 页面存在覆盖层吞点击事件，统一用 focus + Enter 触发按钮 */
async function pressClick(
  page: import("@playwright/test").Page,
  locator: import("@playwright/test").Locator,
) {
  await locator.waitFor({ state: "visible", timeout: 10000 });
  await locator.scrollIntoViewIfNeeded().catch(() => {});
  await locator.focus();
  await page.keyboard.press("Enter");
}

async function studentLogin(page: import("@playwright/test").Page) {
  await page.goto(`${BASE}/login`);
  await page.getByPlaceholder("学号 / 工号").fill("student_001");
  await page.getByPlaceholder("输入密码").fill("123456");
  await page
    .getByRole("button", { name: /登\s*录/ })
    .first()
    .click();
  // 登录成功后会离开 /login（跳转首页或 dashboard）
  await page.waitForURL((url) => url.pathname !== "/login", {
    timeout: 15000,
  });
  await page.waitForTimeout(1500);
}

test.describe("AIC 新功能验证", () => {
  test("学生登录后进入学习路径页，跨学科学习链路正常渲染", async ({ page }) => {
    await studentLogin(page);
    await page.goto(`${BASE}/learning-path`, { waitUntil: "domcontentloaded" });
    // 等待页面加载
    await page.waitForTimeout(3000);
    // 展开"跨学科学习链路"折叠卡片（页面有覆盖层吞点击事件，用键盘触发）
    const crossLabel = page.getByText(/跨学科学习链路/).first();
    await crossLabel.waitFor({ state: "visible", timeout: 10000 });
    await crossLabel.scrollIntoViewIfNeeded();
    await crossLabel.locator("xpath=..").focus();
    await page.keyboard.press("Enter");
    await page.waitForTimeout(2500);
    // 学科卡片渲染（3门课）
    await expect(page.getByText("计算机科学与技术").first()).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByText("电子信息工程").first()).toBeVisible();
    // 目标选择下拉存在
    await expect(page.getByText("选择跨学科学习目标：")).toBeVisible();
    // 依赖图渲染（SVG + 课程图例）
    await expect(page.locator("svg").first()).toBeVisible();
    await expect(
      page.getByText("C语言", { exact: true }).first(),
    ).toBeVisible();
  });

  test("电路仿真故障实验完整流程", async ({ page }) => {
    await studentLogin(page);
    // 错误诊断页，学科=电路分析（仿真器）
    await page.goto(`${BASE}/error-diagnosis`, {
      waitUntil: "domcontentloaded",
    });
    await page.waitForTimeout(2500);
    // 切换到电路分析学科（AppHeader 顶部 pill）
    const circuitPill = page.getByRole("button", { name: "电路分析" }).first();
    if (await circuitPill.isVisible().catch(() => false)) {
      await pressClick(page, circuitPill);
      await page.waitForTimeout(2000);
    }
    // 故障实验按钮
    const faultBtn = page.getByRole("button", { name: /故障实验/ }).first();
    await pressClick(page, faultBtn);
    // 弹窗出现，选择故障实验
    await expect(page.getByText("故障诊断实验")).toBeVisible({ timeout: 8000 });
    await page.getByText("分压电路 · R2 断路").first().click();
    // 实验任务描述出现
    await expect(page.getByText(/请选择故障原因/)).toBeVisible({
      timeout: 8000,
    });
    // 选择答案并提交
    await page.getByText("A. R2 断路", { exact: true }).click();
    await pressClick(page, page.getByRole("button", { name: /提交诊断/ }));
    await expect(page.getByText("诊断正确")).toBeVisible({ timeout: 5000 });
    // 截图留证
    await page.screenshot({
      path: "test-screenshots/aic-fault-diagnosis.png",
      fullPage: false,
    });
  });

  test("STM32 仿真器包含 AI 分析按钮", async ({ page }) => {
    await studentLogin(page);
    await page.goto(`${BASE}/error-diagnosis`, {
      waitUntil: "domcontentloaded",
    });
    await page.waitForTimeout(2500);
    // 切换到 STM32 学科
    const stm32Pill = page.getByRole("button", { name: "STM32嵌入式" }).first();
    if (await stm32Pill.isVisible().catch(() => false)) {
      await pressClick(page, stm32Pill);
      await page.waitForTimeout(2000);
    }
    // STM32 仿真器 AI 分析按钮
    const aiBtn = page.getByRole("button", { name: /AI 分析/ }).first();
    await aiBtn.waitFor({ state: "visible", timeout: 10000 });
    await expect(aiBtn).toBeVisible();
    await page.screenshot({
      path: "test-screenshots/aic-stm32-ai.png",
      fullPage: false,
    });
  });

  test("教师登录后试点数据分析页面正常渲染", async ({ page }) => {
    await page.goto(`${BASE}/login`);
    await page.getByPlaceholder("学号 / 工号").fill("T001");
    await page.getByPlaceholder("输入密码").fill("Teacher123");
    await page
      .getByRole("button", { name: /登\s*录/ })
      .first()
      .click();
    await page.waitForURL((url) => url.pathname !== "/login", {
      timeout: 15000,
    });
    await page.waitForTimeout(1500);
    // 直接访问试点数据分析页
    await page.goto(`${BASE}/teacher/pilot-report`, {
      waitUntil: "domcontentloaded",
    });
    // 统计卡片渲染
    await expect(page.getByText("试点数据分析")).toBeVisible({
      timeout: 10000,
    });
    await expect(page.getByText("活跃学生")).toBeVisible({ timeout: 8000 });
    await expect(page.getByText("总学习时长(h)")).toBeVisible();
    await expect(page.getByText("实验次数")).toBeVisible();
    // 截图留证
    await page.screenshot({
      path: "test-screenshots/aic-pilot-report.png",
      fullPage: true,
    });
  });
});
