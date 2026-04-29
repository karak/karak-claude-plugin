import { Router } from 'express'
import { eq } from 'drizzle-orm'
import { db } from '../db/client.ts'
import { todos } from '../db/schema.ts'

export const todosRouter = Router()

todosRouter.get('/', (_req, res) => {
  const all = db.select().from(todos).all()
  res.json(all)
})

todosRouter.post('/', (req, res) => {
  const { title } = req.body as { title: string }
  const inserted = db.insert(todos).values({ title }).returning().get()
  res.status(201).json(inserted)
})

todosRouter.patch('/:id', (req, res) => {
  const id = Number(req.params['id'])
  const updated = db
    .update(todos)
    .set(req.body as Partial<typeof todos.$inferInsert>)
    .where(eq(todos.id, id))
    .returning()
    .get()
  if (!updated) return res.status(404).json({ error: 'not found' })
  res.json(updated)
})

todosRouter.delete('/:id', (req, res) => {
  const id = Number(req.params['id'])
  const deleted = db.delete(todos).where(eq(todos.id, id)).returning().get()
  if (!deleted) return res.status(404).json({ error: 'not found' })
  res.status(204).end()
})
