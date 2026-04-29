import { int, sqliteTable, text } from 'drizzle-orm/sqlite-core'

export const todos = sqliteTable('todos', {
  id: int('id').primaryKey({ autoIncrement: true }),
  title: text('title').notNull(),
  done: int('done', { mode: 'boolean' }).notNull().default(false),
  createdAt: text('created_at').notNull().$defaultFn(() => new Date().toISOString()),
})

export type Todo = typeof todos.$inferSelect
export type NewTodo = typeof todos.$inferInsert
