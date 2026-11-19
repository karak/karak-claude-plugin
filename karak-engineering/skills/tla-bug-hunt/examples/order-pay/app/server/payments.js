// Express handler: pay for an order.
const express = require('express');
const db = require('./db'); // pg Pool wrapper, autocommit per query
const gateway = require('./gateway');

const router = express.Router();

router.post('/orders/:id/pay', async (req, res) => {
  const orderId = req.params.id;
  const { rows } = await db.query('SELECT status, amount FROM orders WHERE id = $1', [orderId]);
  const order = rows[0];
  if (!order) return res.status(404).end();
  if (order.status === 'paid') return res.status(409).json({ error: 'already paid' });

  const charge = await gateway.charge(order.amount); // external card charge
  await db.query('INSERT INTO charges (order_id, gateway_ref) VALUES ($1, $2)', [orderId, charge.ref]);
  await db.query("UPDATE orders SET status = 'paid' WHERE id = $1", [orderId]);
  res.json({ ok: true });
});

module.exports = router;
