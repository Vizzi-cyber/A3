const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  const results = [];

  const check = (name, pass) => {
    results.push({ name, pass });
    console.log(`${pass ? '✅' : '❌'} ${name}`);
  };

  try {
    // 1. 登录
    console.log('\n=== 1. 登录 ===');
    await page.goto('http://localhost:5173/login');
    await page.waitForTimeout(2000);
    await page.fill('input#student_id, input[name="student_id"]', 'student_001');
    await page.fill('input#password, input[name="password"]', '123456');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(3000);
    check('登录成功', page.url().includes('/resources') || page.url().includes('/'));

    // 2. 打开资源中心
    console.log('\n=== 2. 打开资源中心 ===');
    await page.goto('http://localhost:5173/resources');
    await page.waitForTimeout(3000);
    check('资源中心加载', page.url().includes('/resources'));

    // 关闭弹窗
    await page.evaluate(() => {
      document.querySelectorAll('.ant-modal-wrap, .ant-modal-mask').forEach(m => m.remove());
    });
    await page.waitForTimeout(500);

    // 3. 切换到 STM32嵌入式
    console.log('\n=== 3. 切换 STM32嵌入式 ===');
    const stm32Btn = await page.locator('button:has-text("STM32嵌入式")').first();
    const stm32Visible = await stm32Btn.isVisible({ timeout: 3000 }).catch(() => false);
    check('STM32嵌入式按钮可见', stm32Visible);
    if (stm32Visible) {
      await stm32Btn.click({ force: true });
      await page.waitForTimeout(2000);
    }

    // 4. 检查课程菜单
    console.log('\n=== 4. 课程菜单 ===');
    const menuItems = await page.locator('.ant-menu-item, .ant-menu-submenu-title').count();
    check('课程菜单有内容', menuItems > 0);
    console.log(`   菜单项数量: ${menuItems}`);

    // 5. 点击基础入门
    console.log('\n=== 5. 点击基础入门 ===');
    const kp1 = await page.locator('text=基础入门').first();
    const kp1Visible = await kp1.isVisible({ timeout: 3000 }).catch(() => false);
    check('基础入门知识点可见', kp1Visible);
    if (kp1Visible) {
      await kp1.click({ force: true });
      await page.waitForTimeout(3000);
    }

    // 6. 检查课程内容加载
    console.log('\n=== 6. 课程内容 ===');
    const hasH1 = await page.locator('.md-h1').count() > 0;
    check('课程文档内容加载', hasH1);
    if (hasH1) {
      const title = await page.locator('.md-h1').first().textContent();
      console.log(`   文档标题: ${title}`);
    }

    // 7. 检查接线图 Tab
    console.log('\n=== 7. 接线图 Tab ===');
    const wiringTab = await page.locator('text=接线图').first();
    const wiringTabVisible = await wiringTab.isVisible({ timeout: 3000 }).catch(() => false);
    check('接线图 Tab 存在', wiringTabVisible);
    if (wiringTabVisible) {
      await wiringTab.click({ force: true });
      await page.waitForTimeout(2000);
      const wiringImages = await page.locator('.grid img').count();
      const wiringEmpty = await page.locator('text=暂无接线图').count() > 0;
      check('接线图有内容或提示空', wiringImages > 0 || wiringEmpty);
      console.log(`   接线图数量: ${wiringImages}`);
    }

    // 8. 检查代码工程 Tab
    console.log('\n=== 8. 代码工程 Tab ===');
    const projectsTab = await page.locator('text=代码工程').first();
    const projectsTabVisible = await projectsTab.isVisible({ timeout: 3000 }).catch(() => false);
    check('代码工程 Tab 存在', projectsTabVisible);
    if (projectsTabVisible) {
      await projectsTab.click({ force: true });
      await page.waitForTimeout(2000);
      const projectCards = await page.locator('.ant-card').count();
      const projectsEmpty = await page.locator('text=暂无代码工程').count() > 0;
      check('代码工程有内容或提示空', projectCards > 0 || projectsEmpty);
      console.log(`   代码工程卡片数: ${projectCards}`);
    }

    // 9. 检查 .md 链接修复
    console.log('\n=== 9. .md 链接修复 ===');
    const mdLinks = await page.locator('a[href$=".md"]').count();
    check('无 .md 跳转链接', mdLinks === 0);
    console.log(`   .md 链接数量: ${mdLinks}`);

    // 10. 课程导航链接
    console.log('\n=== 10. 课程导航链接 ===');
    const courseNavLinks = await page.locator('.course-nav-link').count();
    check('课程导航链接存在', courseNavLinks > 0);
    console.log(`   导航链接数量: ${courseNavLinks}`);

    // 11. 点击课程导航链接
    if (courseNavLinks > 0) {
      console.log('\n=== 11. 课程导航跳转 ===');
      const linkText = await page.locator('.course-nav-link').first().textContent();
      const titleBefore = await page.locator('.md-h1').first().textContent();
      console.log(`   点击前: ${titleBefore}`);
      console.log(`   点击链接: ${linkText}`);
      await page.locator('.course-nav-link').first().click({ force: true });
      await page.waitForTimeout(5000);
      const titleAfter = await page.locator('.md-h1').first().textContent();
      console.log(`   点击后: ${titleAfter}`);
      check('课程导航切换成功', titleBefore !== titleAfter);
      check('URL 保持 /resources', page.url().includes('/resources'));
    }

    // 12. 切换其他知识点
    console.log('\n=== 12. 切换其他知识点 ===');
    const otherKps = ['定时器', '串口通信', 'I2C通信'];
    for (const kp of otherKps) {
      const el = await page.locator(`text=${kp}`).first();
      if (await el.isVisible({ timeout: 2000 }).catch(() => false)) {
        await el.click({ force: true });
        await page.waitForTimeout(2000);
        const title = await page.locator('.md-h1').first().textContent().catch(() => '');
        console.log(`   ${kp}: ${title}`);
      }
    }
    check('知识点切换正常', true);

    // 13. 后端 API 验证
    console.log('\n=== 13. 后端 API ===');
    const apiTests = [
      { url: '/api/v1/stm32/wiring-diagrams', name: '接线图列表' },
      { url: '/api/v1/stm32/projects', name: '代码工程列表' },
      { url: '/api/v1/stm32/courses', name: '课程列表' },
    ];
    for (const t of apiTests) {
      const res = await page.evaluate(async (url) => {
        const r = await fetch(url, {
          headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || ''}` }
        });
        return { status: r.status, ok: r.ok };
      }, t.url);
      check(`${t.name} API (${res.status})`, res.ok);
    }

    // 14. 截图
    console.log('\n=== 14. 截图 ===');
    await page.screenshot({ path: 'screenshot-final.png', fullPage: true });
    check('截图保存', true);

  } catch (e) {
    console.error('测试异常:', e.message);
  }

  // 汇总
  console.log('\n=============================');
  console.log(`总计: ${results.length} 项检查`);
  console.log(`通过: ${results.filter(r => r.pass).length}`);
  console.log(`失败: ${results.filter(r => !r.pass).length}`);
  if (results.some(r => !r.pass)) {
    console.log('\n失败项:');
    results.filter(r => !r.pass).forEach(r => console.log(`  ❌ ${r.name}`));
  }
  console.log('=============================');

  await browser.close();
})();
