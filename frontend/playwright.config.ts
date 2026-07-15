import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 1,
  reporter: "list",
  timeout: 60000,
  use: {
    baseURL: "http://localhost:8000",
    trace: "on-first-retry",
  },
  projects: [
    {
      name: "api",
      use: {
        browserName: "chromium",
        headless: true,
        launchOptions: {
          executablePath:
            "C:/Users/15722/AppData/Local/ms-playwright/chromium-1228/chrome-win64/chrome.exe",
        },
      },
    },
  ],
});
