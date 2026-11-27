import { defineConfig, devices } from "@playwright/test";

// O E2E roda contra a stack completa (db + api + frontend). `make e2e` sobe
// uma cópia isolada (projeto estoque-e2e) e passa a URL em E2E_BASE_URL.
export default defineConfig({
  testDir: "./tests/e2e",
  retries: process.env.CI ? 1 : 0,
  use: { baseURL: process.env.E2E_BASE_URL ?? "http://localhost:5173" },
  projects: [
    { name: "desktop", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
  ],
});
