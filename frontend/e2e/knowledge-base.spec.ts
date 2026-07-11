import { test, expect } from "@playwright/test";

test.describe.configure({ mode: "serial" });

// Helper: authenticate
async function authenticateViaApi(page: any) {
  const response = await page.request.post(
    "http://localhost:8000/api/v1/auth/login",
    {
      data: { student_id: "student_001", password: "123456" },
    },
  );
  const { access_token } = await response.json();

  await page.goto("http://localhost:5173/login");
  await page.waitForLoadState("networkidle");

  await page.evaluate((token: string) => {
    const state = {
      state: { token, studentId: "student_001" },
      version: 0,
    };
    localStorage.setItem("learnlab-storage", JSON.stringify(state));
  }, access_token);

  await page.reload();
  await page.waitForLoadState("networkidle");
  await expect(page.locator(".ant-layout").first()).toBeVisible({
    timeout: 15000,
  });
}

test.describe("Knowledge Base Tests", () => {
  test("Knowledge Base page loads", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://localhost:5173/knowledge-base");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    // Should show the three-panel layout
    await expect(page.locator("text=文件夹").first()).toBeVisible({
      timeout: 15000,
    });
  });

  test("Create a new note", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://localhost:5173/knowledge-base");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    // Click "新建" button in note list
    const newBtn = page.locator("button:has-text('新建')").first();
    await expect(newBtn).toBeVisible({ timeout: 10000 });
    await newBtn.click();

    // Wait for the note to be created and editor to appear
    await page.waitForTimeout(2000);

    // Check if any editor is visible
    const hasEditor = await page
      .locator(".monaco-editor, input[placeholder='笔记标题']")
      .first()
      .isVisible()
      .catch(() => false);
    expect(hasEditor).toBeTruthy();
  });

  test("Split view mode works", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://localhost:5173/knowledge-base");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    // Create a note
    const newBtn = page.locator("button:has-text('新建')").first();
    await newBtn.click();
    await page.waitForTimeout(3000);

    // Check if Monaco editor is present
    const editor = page.locator(".monaco-editor").first();
    const hasEditor = await editor.isVisible().catch(() => false);

    // Also check for the resize panels (split view)
    const hasPanels = (await page.locator("[data-panel]").count()) > 0;

    expect(hasEditor || hasPanels).toBeTruthy();
  });

  test("Right panel shows when note selected", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://localhost:5173/knowledge-base");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    // Create a note to select it
    const newBtn = page.locator("button:has-text('新建')").first();
    await newBtn.click();
    await page.waitForTimeout(2000);

    // Right panel should show backlinks tab
    const backlinksTab = page
      .locator("[role='tab']:has-text('反向链接')")
      .first();
    const hasBacklinks = await backlinksTab.isVisible().catch(() => false);
    expect(hasBacklinks).toBeTruthy();
  });

  test("Graph tab is accessible and shows graph content", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://localhost:5173/knowledge-base");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    // Create a note
    const newBtn = page.locator("button:has-text('新建')").first();
    await newBtn.click();
    await page.waitForTimeout(2000);

    // Graph tab should be visible
    const graphTab = page.locator("[role='tab']:has-text('图谱')").first();
    const hasGraphTab = await graphTab.isVisible().catch(() => false);
    expect(hasGraphTab).toBeTruthy();

    // Click graph tab
    if (hasGraphTab) {
      await graphTab.click();
      await page.waitForTimeout(2000);

      // Graph should show nodes - check for graph content
      const graphPanel = page
        .locator("[role='tabpanel']:has-text('知识图谱')")
        .first();
      const hasGraphContent = await graphPanel.isVisible().catch(() => false);
      expect(hasGraphContent).toBeTruthy();

      // SVG should exist and have content
      const svg = page.locator("svg").first();
      const hasSvg = await svg.isVisible().catch(() => false);
      expect(hasSvg).toBeTruthy();
    }
  });

  test("Search panel works", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://localhost:5173/knowledge-base");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    // Click search tab in left panel
    const searchTab = page.locator("button:has-text('搜索')").first();
    const hasSearchTab = await searchTab.isVisible().catch(() => false);

    if (hasSearchTab) {
      await searchTab.click();
      await page.waitForTimeout(1000);

      // Search input should be visible - use Ant Design input
      const searchInput = page
        .locator(".ant-input, input")
        .filter({ hasText: /搜索/ })
        .first();
      const searchInputAlt = page.locator("input[placeholder*='搜索']").first();
      const hasSearchInput =
        (await searchInput.isVisible().catch(() => false)) ||
        (await searchInputAlt.isVisible().catch(() => false));
      expect(hasSearchInput).toBeTruthy();
    }
  });

  test("File tree shows folders", async ({ page }) => {
    await authenticateViaApi(page);
    await page.goto("http://localhost:5173/knowledge-base");
    await page.waitForLoadState("networkidle");
    await page.waitForTimeout(2000);

    // Should show file tree with at least the tree structure
    const hasTree = await page
      .locator(".ant-tree, [class*='tree']")
      .first()
      .isVisible()
      .catch(() => false);
    expect(hasTree).toBeTruthy();
  });
});
