import { test, expect } from "@playwright/test";

const BASE_URL = "http://localhost:5173";

async function login(page: any) {
  await page.goto(`${BASE_URL}/login`);
  // 登录页有轮询请求，networkidle 不会触发；等 load 后直接等输入框可见
  await page.waitForLoadState("load");
  await page
    .getByPlaceholder("学号 / 工号")
    .waitFor({ state: "visible", timeout: 30000 });
  await page.getByPlaceholder("学号 / 工号").fill("student_001");
  await page.getByPlaceholder("输入密码").fill("123456");
  await page.locator(".ant-btn-primary").click();
  // Wait for dashboard layout to appear (more reliable than URL change for SPA navigation)
  await page.waitForSelector(".ant-layout", { timeout: 30000 });
}

test("Resource detail renders markdown without console errors", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (err) => errors.push(err.message));
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(msg.text());
  });

  await login(page);

  // Directly navigate to a chapter that has markdown content
  await page.goto(`${BASE_URL}/resource/kp_c09`);
  await page.waitForLoadState("networkidle");

  // Wait for markdown body to appear
  await page.waitForSelector(".markdown-body", { timeout: 15000 });

  // 验证 markdown 确实渲染出内容（不写死具体知识点，避免随课程内容变动而误报）
  const bodyText = await page.locator(".markdown-body").innerText();
  expect(bodyText.trim().length).toBeGreaterThan(50);
  // 渲染出中文内容（说明讲义已加载并解析）
  expect(/[一-龥]{4,}/.test(bodyText)).toBeTruthy();

  // Check no remark / markdown related errors
  const remarkErrors = errors.filter(
    (e) =>
      e.includes("remark") ||
      e.includes("data") ||
      e.includes("react-markdown"),
  );
  expect(remarkErrors).toEqual([]);

  // Check code block rendered
  const codeBlocks = await page.locator(".code-block-wrapper").count();
  expect(codeBlocks).toBeGreaterThan(0);
});
