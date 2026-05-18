import Database from 'better-sqlite3'
import { drizzle } from 'drizzle-orm/better-sqlite3'
import * as schema from './schema.ts'

const sqlite = new Database(process.env.DB_FILE ?? ':memory:')
export const db = drizzle(sqlite, { schema })
