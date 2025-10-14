const { Router } = require('express');
const { PrismaClient } = require('@prisma/client');
const { body, validationResult } = require('express-validator');
const { requireAuth, requireAdmin } = require('../middlewares/auth');

const prisma = new PrismaClient();
const router = Router();

// GET /events
router.get('/', async (req, res) => {
	const events = await prisma.event.findMany({ orderBy: { date: 'asc' } });
	res.json(events);
});

// GET /events/:id
router.get('/:id', async (req, res) => {
	const id = parseInt(req.params.id);
	const event = await prisma.event.findUnique({ where: { id } });
	if (!event) return res.status(404).json({ error: 'Evento no encontrado' });
	res.json(event);
});

// POST /events (admin)
router.post(
	'/',
	requireAuth,
	requireAdmin,
	[
		body('name').isString().notEmpty(),
		body('date').isISO8601(),
		body('location').isString().notEmpty(),
		body('capacity').isInt({ min: 1 }),
		body('price').isFloat({ min: 0 }),
	],
	async (req, res) => {
		const errors = validationResult(req);
		if (!errors.isEmpty()) return res.status(422).json({ errors: errors.array() });

		const { name, date, location, capacity, price } = req.body;
		try {
			const newEvent = await prisma.event.create({
				data: {
					name,
					date: new Date(date),
					location,
					capacity: parseInt(capacity),
					price: parseFloat(price),
				},
			});
			res.status(201).json(newEvent);
		} catch (err) {
			res.status(500).json({ error: err.message });
		}
	}
);

// PUT /events/:id (admin)
router.put(
	'/:id',
	requireAuth,
	requireAdmin,
	[
		body('name').optional().isString(),
		body('date').optional().isISO8601(),
		body('location').optional().isString(),
		body('capacity').optional().isInt({ min: 1 }),
		body('price').optional().isFloat({ min: 0 }),
	],
	async (req, res) => {
		const id = parseInt(req.params.id);
		const errors = validationResult(req);
		if (!errors.isEmpty()) return res.status(422).json({ errors: errors.array() });

		const payload = {};
		for (const key of ['name', 'date', 'location', 'capacity', 'price']) {
			if (req.body[key] !== undefined) {
				payload[key] = key === 'date' ? new Date(req.body[key]) : req.body[key];
			}
		}

		try {
			const updated = await prisma.event.update({ where: { id }, data: payload });
			res.json(updated);
		} catch (err) {
			res.status(500).json({ error: err.message });
		}
	}
);

// DELETE /events/:id (admin)
router.delete('/:id', requireAuth, requireAdmin, async (req, res) => {
	const id = parseInt(req.params.id);
	try {
		await prisma.event.delete({ where: { id } });
		res.status(204).send();
	} catch (err) {
		res.status(500).json({ error: err.message });
	}
});

module.exports = router;
