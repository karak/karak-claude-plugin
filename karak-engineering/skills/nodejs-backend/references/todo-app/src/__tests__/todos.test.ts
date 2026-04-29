import { describe, it, expect, beforeEach } from 'vitest'
import request from 'supertest'
import { db } from '../db/client.ts'
import { todos } from '../db/schema.ts'
import { app } from '../app.ts'

beforeEach(() => {
  db.delete(todos).run()
})

describe('GET /todos', () => {
  it('returns empty array initially', async () => {
    const res = await request(app).get('/todos').expect(200)
    expect(res.body).toEqual([])
  })
})

describe('POST /todos', () => {
  it('creates a todo and returns 201', async () => {
    const res = await request(app).post('/todos').send({ title: 'buy milk' }).expect(201)
    expect(res.body.title).toBe('buy milk')
    expect(res.body.done).toBe(false)
    expect(res.body.id).toBeTypeOf('number')
  })
})

describe('PATCH /todos/:id', () => {
  it('updates done status', async () => {
    const created = await request(app).post('/todos').send({ title: 'test' })
    const res = await request(app)
      .patch(`/todos/${created.body.id}`)
      .send({ done: true })
      .expect(200)
    expect(res.body.done).toBe(true)
  })

  it('returns 404 for unknown id', async () => {
    await request(app).patch('/todos/9999').send({ done: true }).expect(404)
  })
})

describe('DELETE /todos/:id', () => {
  it('deletes and returns 204', async () => {
    const created = await request(app).post('/todos').send({ title: 'delete me' })
    await request(app).delete(`/todos/${created.body.id}`).expect(204)
    const list = await request(app).get('/todos')
    expect(list.body).toHaveLength(0)
  })

  it('returns 404 for unknown id', async () => {
    await request(app).delete('/todos/9999').expect(404)
  })
})
