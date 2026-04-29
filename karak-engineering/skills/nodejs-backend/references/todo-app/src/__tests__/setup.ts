import { existsSync } from 'node:fs'
import { join } from 'node:path'
import { beforeAll } from 'vitest'
import { migrate } from 'drizzle-orm/better-sqlite3/migrator'
import { db } from '../db/client.ts'

const migrationsFolder = join(import.meta.dirname, '../../drizzle')

beforeAll(() => {
  if (!existsSync(migrationsFolder)) {
    throw new Error('Run `npm run generate` before `npm test`.')
  }
  migrate(db, { migrationsFolder })
})
