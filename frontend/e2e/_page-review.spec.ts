/**
 * 全站页面复查（提交前排查用）
 * 目的：访问所有页面，抓控制台错误 / 失败请求 / 敏感文案，输出问题清单。
 * 运行：npx playwright test e2e/_page-review.spec.ts --reporter=list
 */
import { test, Page } from "@playwright/test";

// 注意：本机 Vite 只监听 IPv6 [::1]，用 127.0.0.1 会 ERR_CONNECTION_REFUSED
const BASE = process.env.E2E_BASE_URL || "http://localhost:5180";

const IGNORE_CONSOLE = [
  "WebSocket is closed before the connection is established",
  "Unable to preventDefault inside passive event listener",
  "antd: Modal",
  "antd: message",
  "antd: notification",
  "[antd",
  "Download the React DevTools",
  "Warning: ReactDOM.render",
];

// 提交材料红线：赛事名 / 学校 / 指导教师 / 内部信息
const RED_FLAGS = [
  /软件杯/,
  /中国软件杯/,
  /A3\s*赛题/,
  /大学/,
  /学院/,
  /指导教师/,
  /指导老师/,
  /校徽/,
  /TODO/,
  /FIXME/,
  /undefined/,
  /NaN/,
  /\bnull\b/,
  /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}/i, // UUID 泄漏
];

const STUDENT_PAGES = [
  ["仪表盘", "/"],
  ["学习路径", "/learning-path"],
  ["学习中心", "/resources"],
  ["知识冒险", "/challenges"],
  ["错误诊断", "/error-diagnosis"],
  ["项目协作", "/project-collaboration"],
  ["个人空间", "/personal"],
  ["知识库", "/knowledge-base"],
  ["排行榜", "/leaderboard"],
  ["智能辅导", "/tutor"],
];

const TEACHER_PAGES = [
  ["教师首页", "/teacher"],
  ["教师主页", "/teacher/home"],
  ["作业管理", "/teacher/assignments"],
  ["学生管理", "/teacher/students"],
  ["备课资源", "/teacher/resources"],
  ["学情分析", "/teacher/analytics"],
  ["班级分析", "/teacher/class-analytics"],
  ["班级对比", "/teacher/class-comparison"],
  ["报告导出", "/teacher/reports"],
  ["试点数据分析", "/teacher/pilot-report"],
  ["AI智能备课", "/teacher/lesson-plan"],
  ["学情洞察", "/teacher/insights"],
  ["智能组卷", "/teacher/smart-quiz"],
  ["系统设置", "/teacher/settings"],
  ["教师个人空间", "/teacher/personal"],
];

type Issue = { page: string; kind: string; detail: string };
const ISSUES: Issue[] = [];

function attachListeners(page: Page, label: string) {
  page.on("console", (msg) => {
    if (msg.type() !== "error" && msg.type() !== "warning") return;
    const text = msg.text();
    if (IGNORE_CONSOLE.some((s) => text.includes(s))) return;
    if (msg.type() === "error") {
      ISSUES.push({
        page: label,
        kind: "console.error",
        detail: text.slice(0, 300),
      });
    }
  });
  page.on("pageerror", (err) => {
    ISSUES.push({
      page: label,
      kind: "pageerror",
      detail: String(err).slice(0, 300),
    });
  });
  page.on("response", async (resp) => {
    const status = resp.status();
    if (status < 400) return;
    const url = resp.url();
    if (!url.includes("/api/")) return;
    ISSUES.push({
      page: label,
      kind: `HTTP ${status}`,
      detail: url.replace(BASE, "").slice(0, 200),
    });
  });
}

async function loginAs(page: Page, sid: string, pwd: string) {
  await page.goto(`${BASE}/login`);
  await page.waitForLoadState("networkidle");
  const resp = await page.request.post(`${BASE}/api/v1/auth/login`, {
    data: { student_id: sid, password: pwd },
  });
  const json = await resp.json();
  const token = json.access_token;
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
  return token;
}

async function visit(page: Page, label: string, path: string) {
  try {
    await page.goto(`${BASE}${path}`, {
      waitUntil: "networkidle",
      timeout: 30000,
    });
  } catch {
    ISSUES.push({ page: label, kind: "导航超时", detail: path });
    return;
  }
  await page.waitForTimeout(2500);

  // 检查红线文案
  const bodyText =
    (await page
      .locator("body")
      .innerText()
      .catch(() => "")) || "";
  for (const re of RED_FLAGS) {
    const m = bodyText.match(re);
    if (m) {
      const idx = bodyText.indexOf(m[0]);
      const ctx = bodyText
        .slice(Math.max(0, idx - 30), idx + 40)
        .replace(/\s+/g, " ");
      ISSUES.push({ page: label, kind: `红线文案 ${re}`, detail: ctx });
    }
  }

  // 空状态提示（可能是数据没到位）
  const emptyHints = ["暂无数据", "暂无记录", "加载失败", "出错了", "获取失败"];
  for (const h of emptyHints) {
    if (bodyText.includes(h)) {
      ISSUES.push({ page: label, kind: "空态", detail: h });
    }
  }
}

test.describe.configure({ mode: "serial" });

test("学生端全页复查", async ({ page }) => {
  test.setTimeout(600000);
  await loginAs(page, "student_001", "123456");
  for (const [label, path] of STUDENT_PAGES) {
    attachListeners(page, `[学生]${label}`);
    await visit(page, `[学生]${label}`, path);
  }
});

test("教师端全页复查", async ({ page }) => {
  test.setTimeout(600000);
  await loginAs(page, "T001", "Teacher123");
  for (const [label, path] of TEACHER_PAGES) {
    attachListeners(page, `[教师]${label}`);
    await visit(page, `[教师]${label}`, path);
  }
});

test.afterAll(async () => {
  console.log("\n\n========== 页面复查问题清单 ==========");
  if (!ISSUES.length) {
    console.log("未发现问题 ✅");
    return;
  }
  const byPage = new Map<string, Issue[]>();
  for (const it of ISSUES) {
    if (!byPage.has(it.page)) byPage.set(it.page, []);
    byPage.get(it.page)!.push(it);
  }
  for (const [pg, list] of byPage) {
    console.log(`\n### ${pg}`);
    const seen = new Set<string>();
    for (const it of list) {
      const key = `${it.kind}|${it.detail}`;
      if (seen.has(key)) continue;
      seen.add(key);
      console.log(`  - [${it.kind}] ${it.detail}`);
    }
  }
  console.log(`\n合计 ${ISSUES.length} 条（去重后见上）`);
});
