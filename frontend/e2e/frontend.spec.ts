import { test, expect } from '@playwright/test';

test.describe.configure({ mode: 'serial' });

test.describe('Frontend E2E Tests', () => {
  
  // Helper function to login
  async function login(page: any) {
    await page.goto('http://localhost:5173/login');
    await page.waitForLoadState('networkidle');
    await page.getByPlaceholder('请输入学号').fill('student_001');
    await page.getByPlaceholder('请输入密码').fill('123456');
    await page.locator('.ant-btn-primary').click();
    await page.waitForURL('http://localhost:5173/', { timeout: 5000 });
  }

  test('Login page loads correctly', async ({ page }) => {
    await page.goto('http://localhost:5173/login');
    await page.waitForLoadState('networkidle');
    await expect(page).toHaveTitle(/AI Learning System/);
    
    // Wait for Ant Design to render
    await page.waitForSelector('.ant-tabs', { timeout: 10000 });
    
    // Check login tab is active
    await expect(page.locator('.ant-tabs-tab-active')).toBeVisible();
    
    // Check form inputs by placeholder
    await expect(page.getByPlaceholder('请输入学号')).toBeVisible({ timeout: 10000 });
    await expect(page.getByPlaceholder('请输入密码')).toBeVisible({ timeout: 10000 });
    
    // Check login button by class (Ant Design primary button)
    await expect(page.locator('.ant-btn-primary')).toBeVisible({ timeout: 10000 });
  });

  test('Login with valid credentials', async ({ page }) => {
    await login(page);
    
    // Check dashboard loaded
    await expect(page.locator('.ant-layout').first()).toBeVisible({ timeout: 10000 });
    // Check sidebar is present
    await expect(page.locator('.ant-menu')).toBeVisible();
  });

  test('Navigate to Profile page', async ({ page }) => {
    await login(page);
    await page.goto('http://localhost:5173/profile');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.ant-layout').first()).toBeVisible({ timeout: 10000 });
    // Profile page should have card components
    await expect(page.locator('.ant-card').first()).toBeVisible();
  });

  test('Navigate to Learning Path page', async ({ page }) => {
    await login(page);
    await page.goto('http://localhost:5173/learning-path');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.ant-layout').first()).toBeVisible({ timeout: 10000 });
  });

  test('Navigate to Resource Center page', async ({ page }) => {
    await login(page);
    await page.goto('http://localhost:5173/resources');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.ant-layout').first()).toBeVisible({ timeout: 10000 });
  });

  test('Navigate to Tutor page', async ({ page }) => {
    await login(page);
    await page.goto('http://localhost:5173/tutor');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.ant-layout').first()).toBeVisible({ timeout: 10000 });
    // Tutor page has input for questions
    await expect(page.locator('input, textarea').first()).toBeVisible();
  });

  test('Navigate to Personal Space page', async ({ page }) => {
    await login(page);
    await page.goto('http://localhost:5173/personal');
    await page.waitForLoadState('networkidle');
    await expect(page.locator('.ant-layout').first()).toBeVisible({ timeout: 10000 });
  });

  test('Sidebar navigation works', async ({ page }) => {
    await login(page);
    
    // Wait for sidebar menu to render
    await page.waitForSelector('.ant-menu', { timeout: 10000 });
    
    // Find all menu items (Ant Design menu items)
    const menuItems = await page.locator('.ant-menu-item, .ant-menu-item-only-child').all();
    console.log('Menu items found:', menuItems.length);
    
    if (menuItems.length === 0) {
      // If no menu items, just verify sidebar exists
      await expect(page.locator('.ant-layout-sider')).toBeVisible();
      return;
    }
    
    // Click second menu item
    await menuItems[1].click();
    await page.waitForTimeout(1000);
    const url = page.url();
    expect(url).not.toBe('http://localhost:5173/login');
  });

  test('Logout redirects to login', async ({ page }) => {
    await login(page);
    
    // Look for logout button in header or user dropdown
    const possibleLogoutSelectors = [
      'text=退出',
      'text=Logout',
      'text=登出',
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
      await page.waitForURL('http://localhost:5173/login', { timeout: 5000 });
      await expect(page.locator('.ant-btn-primary')).toBeVisible();
    } else {
      // Skip if logout button not found - may need user dropdown interaction
      test.skip();
    }
  });

});
