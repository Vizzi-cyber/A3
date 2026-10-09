/** 教师端关键页面截图 */
import { test, Page } from "@playwright/test";

const BASE = process.env.E2E_BASE_URL || "http://localhost:5180";
const OUT = process.env.SHOT_DIR || "shots_teacher";

const PAGES: [string, string][] = [
  ["t01-home", "/teacher"],
  ["t02-analytics", "/teacher/analytics"],
  ["t03-class", "/teacher/class-analytics"],
  ["t04-compare", "/teacher/class-comparison"],
  ["t05-pilot", "/teacher/pilot-report"],
  ["t06-lesson", "/teacher/lesson-plan"],
  ["t07-insights", "/teacher/insights"],
  ["t08-quiz", "/teacher/smart-quiz"],
  ["t09-students", "/teacher/students"],
  ["t10-assign", "/teacher/assignments"],
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

test("教师端截图", async ({ page }) => {
  test.setTimeout(600000);
  await page.setViewportSize({ width: 1600, height: 950 });
  await login(page, "T001", "Teacher123");
  for (const [name, path] of PAGES) {
    await page.goto(`${BASE}${path}`, { waitUntil: "networkidle" });
    await page.waitForTimeout(3000);
    await page.screenshot({ path: `${OUT}/${name}.png` });
  }
});
