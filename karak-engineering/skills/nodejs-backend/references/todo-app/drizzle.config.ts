import { defineConfig } from 'drizzle-kit'

export default defineConfig({
  // drizzle-kit compiles this config with esbuild (CJS), so import.meta is unavailable.
  // Use relative paths from the project root (where drizzle-kit is invoked).
  schema: './src/db/schema.ts',
  out: './drizzle',
  dialect: 'sqlite',
  dbCredentials: { url: process.env.DB_FILE ?? './dev.db' },
})
