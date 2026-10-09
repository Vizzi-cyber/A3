/** 关键页面截图（提交前目视检查用） */
import { test, Page } from "@playwright/test";

const BASE = process.env.E2E_BASE_URL || "http://localhost:5180";
const OUT = process.env.SHOT_DIR || "shots";

const PAGES: [string, string][] = [
  ["01-home", "/"],
  ["02-path", "/learning-path"],
  ["03-center", "/resources"],
  ["04-challenge", "/challenges"],
  ["05-error", "/error-diagnosis"],
  ["06-project", "/project-collaboration"],
  ["07-personal", "/personal"],
  ["08-kb", "/knowledge-base"],
  ["09-leaderboard", "/leaderboard"],
  ["10-tutor", "/tutor"],
];

async function login(page: Page, sid: string, pwd: string) {
  await page.goto(`${BASE}/login`);
  const resp = await page.request.post(`${BASE}/api/v1/auth/login`, {
    data: { student_id: sid, password: pwd },
  });
  const token = (await resp.json()).access_token;
  await page.evaluate(
    ({ t, s }) => {
      localStorage.setItem(
        "learnlab-storage",
        JSON.stringify({
          state: { token: t, studentId: s, isLoggedIn: true },
          version: 0,
        }),
      );
    },
    { t: token, s: sid },
  );
}

test("关键页面截图", async ({ page }) => {
  test.setTimeout(600000);
  await page.setViewportSize({ width: 1600, height: 950 });
  await login(page, "student_001", "123456");
  for (const [name, path] of PAGES) {
    await page.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
    await page.waitForTimeout(3000);
    await page.screenshot({ path: `${OUT}/${name}.png`, fullPage: false });
  }
});
