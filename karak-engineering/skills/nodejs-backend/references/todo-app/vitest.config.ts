import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    pool: 'forks',
    environment: 'node',
    env: { DB_FILE: ':memory:' },
    setupFiles: ['./src/__tests__/setup.ts'],
  },
})
