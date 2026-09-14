import { expect, test } from "@playwright/test";

const BASE_URL = process.env.E2E_BASE_URL || "http://127.0.0.1:5180";

test("student quick login opens the student application", async ({ page }) => {
  await page.goto(`${BASE_URL}/login`);

  const loginResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/v1/auth/login") &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "学生一键登录" }).click();

  expect((await loginResponse).ok()).toBe(true);
  await page.waitForURL((url) => url.pathname !== "/login");
  await expect(page).not.toHaveURL(/\/login$/);
  await expect(page.getByText(/欢迎回来/).first()).toBeVisible();
  await page.screenshot({ path: "test-results/quick-login-student.png" });

  await page.goto(`${BASE_URL}/teacher`);
  await expect(page).toHaveURL(`${BASE_URL}/`);
  await expect(page.getByRole("heading", { name: "教师工作台" })).toHaveCount(
    0,
  );
});

test("teacher quick login opens the teacher application", async ({ page }) => {
  await page.goto(`${BASE_URL}/login`);

  const loginResponse = page.waitForResponse(
    (response) =>
      response.url().endsWith("/api/v1/auth/login") &&
      response.request().method() === "POST",
  );
  await page.getByRole("button", { name: "教师一键登录" }).click();

  expect((await loginResponse).ok()).toBe(true);
  await page.waitForURL((url) => url.pathname.startsWith("/teacher"));
  await expect(page).toHaveURL(/\/teacher/);
  await expect(page.getByRole("heading", { name: "教师工作台" })).toBeVisible();
  await page.screenshot({ path: "test-results/quick-login-teacher.png" });

  await page.getByRole("button", { name: "用户菜单" }).click();
  await page.getByRole("menuitem", { name: "个人中心" }).click();
  await expect(page).toHaveURL(`${BASE_URL}/teacher/personal`);
});
