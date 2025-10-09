# Notifications Service (Node.js) — LAB

Microservicio backend que **escucha** `payment.confirmed` en **RabbitMQ** y **envía correos** usando SMTP de laboratorio (**MailHog**). Sin frontend.

## Endpoints
- `GET /health` → estado del servicio.
- `POST /notify/test` (JWT) → prueba manual de envío.
  ```json
  {
    "to": "alguien@mail.com",
    "name": "Alguien",
    "event": { "name": "Rock Fest", "date": "2025-11-12" },
    "quantity": 2,
    "total": 120
  }
