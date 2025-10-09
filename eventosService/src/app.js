const express = require('express');
const cors = require('cors');
const morgan = require('morgan');

const eventsRoutes = require('./routes/events');

const app = express();
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

// Rutas
app.use('/events', eventsRoutes);

// Healthcheck
app.get('/health', (req, res) => res.json({ ok: true }));

module.exports = app;
