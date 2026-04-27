import { test, expect } from '@playwright/test';

const BASE_URL = 'http://localhost:5174';

async function login(page: any) {
  await page.goto(`${BASE_URL}/login`);
  await page.waitForLoadState('networkidle');
  await page.getByPlaceholder('请输入学号').fill('student_001');
  await page.getByPlaceholder('请输入密码').fill('123456');
  await page.locator('.ant-btn-primary').click();
  await page.waitForURL(`${BASE_URL}/`, { timeout: 5000 });
}

test('Resource detail renders markdown without console errors', async ({ page }) => {
  const errors: string[] = [];
  page.on('pageerror', (err) => errors.push(err.message));
  page.on('console', (msg) => {
    if (msg.type() === 'error') errors.push(msg.text());
  });

  await login(page);

  // Directly navigate to a chapter that has markdown content
  await page.goto(`${BASE_URL}/resource/kp_c09`);
  await page.waitForLoadState('networkidle');

  // Wait for markdown body to appear
  await page.waitForSelector('.markdown-body', { timeout: 15000 });

  // Verify Chinese text is rendered (not blank)
  const bodyText = await page.locator('.markdown-body').innerText();
  expect(bodyText).toContain('地址和指针');
  expect(bodyText).toContain('9.1');

  // Check no remark / markdown related errors
  const remarkErrors = errors.filter(e => e.includes('remark') || e.includes('data') || e.includes('react-markdown'));
  expect(remarkErrors).toEqual([]);

  // Check code block rendered
  const codeBlocks = await page.locator('.code-block-wrapper').count();
  expect(codeBlocks).toBeGreaterThan(0);
});
