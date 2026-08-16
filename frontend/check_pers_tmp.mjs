import { chromium } from "playwright-core";
const browser = await chromium.launch({
  executablePath: "C:/Users/Cypress/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe",
  headless: true,
});
const page = await browser.newPage({ viewport: { width: 1400, height: 900 } });
await page.goto("http://localhost:5173/login", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(1500);
const inputs = page.locator("input");
await inputs.nth(0).fill("student_001");
await inputs.nth(1).fill("123456");
await page.locator("button:has-text('登 录')").last().click();
await page.waitForTimeout(4000);
await page.evaluate(() => localStorage.setItem("onboarding_completed_C语言", "true"));
await page.goto("http://localhost:5173/personal", { waitUntil: "domcontentloaded" });
await page.waitForTimeout(8000);
const t = await page.evaluate(() => document.body.innerText);
console.log("URL:", await page.evaluate(() => location.pathname));
console.log("六维画像雷达:", t.includes("六维画像雷达") ? "✅" : "❌");
console.log("个人空间内容:", t.slice(0, 120).replace(/\n/g, "|"));
await browser.close();
