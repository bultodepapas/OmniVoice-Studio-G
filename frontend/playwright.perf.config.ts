import { defineConfig, devices } from '@playwright/test';
import { existsSync } from 'node:fs';

// Opt-in production-bundle responsiveness benchmark. Keep it separate from
// playwright.prod.config.ts: the smoke suite is a CI correctness gate, while
// this harness records machine-dependent timing diagnostics for local review.
const PORT = Number(process.env.E2E_PERF_PORT || 4174);

// An explicit browser wins; Linux CI/dev containers commonly provide a system
// Chromium; contributors on Windows/macOS fall back to Playwright's bundle.
const SYSTEM_CHROMIUM = '/usr/bin/chromium';
const browserPath =
  process.env.PLAYWRIGHT_CHROMIUM || (existsSync(SYSTEM_CHROMIUM) ? SYSTEM_CHROMIUM : undefined);

export default defineConfig({
  testDir: './e2e-perf',
  testMatch: 'responsiveness.spec.ts',
  timeout: 120_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  retries: 0,
  reporter: [['list']],
  outputDir: 'test-results/responsiveness',
  use: {
    baseURL: `http://localhost:${PORT}`,
    headless: true,
    trace: 'retain-on-failure',
    ...(browserPath ? { launchOptions: { executablePath: browserPath } } : {}),
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    // Playwright launches through the platform shell. Invoke the repo-pinned
    // Vite binary directly so Windows does not depend on whichever global Bun
    // shim happens to precede the checked-in toolchain on PATH.
    command: `node ./node_modules/vite/bin/vite.js build && node ./node_modules/vite/bin/vite.js preview --port ${PORT} --strictPort`,
    url: `http://localhost:${PORT}`,
    reuseExistingServer: !process.env.CI,
    timeout: 180_000,
  },
});
