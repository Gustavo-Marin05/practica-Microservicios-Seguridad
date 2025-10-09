// src/middlewares/auth.js
const jwt = require('jsonwebtoken');
const jwksRsa = require('jwks-rsa');

const method = (process.env.AUTH_METHOD || 'hs256').toLowerCase();

// Preferimos JWT_* si están definidos, si no, caemos a AUTH_*
const JWT_SECRET = process.env.JWT_SECRET || process.env.AUTH_SECRET;
const JWT_ALGORITHM = process.env.JWT_ALGORITHM || 'HS256';

function verifyHS256(req, res, next) {
	const header = req.headers.authorization;
	if (!header) return res.status(401).json({ error: 'Token requerido' });

	const token = header.split(' ')[1];
	try {
		const opts = {
			algorithms: [JWT_ALGORITHM],
		};
		// Opcionales: audiencia / issuer si las usas
		if (process.env.JWT_AUDIENCE) opts.audience = process.env.JWT_AUDIENCE;
		if (process.env.JWT_ISSUER) opts.issuer = process.env.JWT_ISSUER;

		const payload = jwt.verify(token, JWT_SECRET, opts);
		req.user = payload;
		next();
	} catch (err) {
		return res.status(401).json({ error: 'Token inválido', details: err.message });
	}
}

// JWKS / RS256 (igual que antes, pero usando posibles env names JWT_* o AUTH_*)
const jwksClient = jwksRsa({
	cache: true,
	rateLimit: true,
	jwksRequestsPerMinute: 10,
	jwksUri: process.env.JWKS_URI || '',
});

function getKey(header, callback) {
	jwksClient.getSigningKey(header.kid, (err, key) => {
		if (err) return callback(err);
		callback(null, key.getPublicKey());
	});
}

function verifyJWKS(req, res, next) {
	const header = req.headers.authorization;
	if (!header) return res.status(401).json({ error: 'Token requerido' });

	const token = header.split(' ')[1];

	jwt.verify(
		token,
		getKey,
		{
			algorithms: ['RS256'],
			audience: process.env.JWT_AUDIENCE || process.env.AUTH_AUDIENCE,
			issuer: process.env.JWT_ISSUER || process.env.AUTH_ISSUER,
		},
		(err, payload) => {
			if (err) return res.status(401).json({ error: 'Token inválido', details: err.message });
			req.user = payload;
			next();
		}
	);
}

function requireAuth(req, res, next) {
	return method === 'jwks' ? verifyJWKS(req, res, next) : verifyHS256(req, res, next);
}

function requireAdmin(req, res, next) {
	const role = req.user?.role || req.user?.roles || req.user?.isAdmin;
	if (role === 'admin' || role === true || (Array.isArray(role) && role.includes('admin'))) return next();
	return res.status(403).json({ error: 'Solo administradores' });
}

module.exports = {
	requireAuth,
	requireAdmin,
};
