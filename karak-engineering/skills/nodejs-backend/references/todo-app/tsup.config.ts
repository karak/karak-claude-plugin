import { defineConfig } from 'tsup'

export default defineConfig({
  entry: ['src/server.ts'],
  format: ['esm'],
  target: 'node24',
  external: ['better-sqlite3', 'drizzle-orm'],
  clean: true,
})
