import express from 'express'
import { todosRouter } from './routes/todos.ts'

export const app = express()
app.use(express.json())
app.use('/todos', todosRouter)
