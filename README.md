# practica-Microservicios-Seguridad



PUNTO 3 
## Endpoints

- `GET /health` - Health check
- `GET /compras` - Obtener compras del usuario
- `POST /compras` - Crear nueva compra
- `GET /compras/{id}` - Obtener compra específica
- `POST /compras/{id}/pagar` - Procesar pago de compra


## Puerto

El servicio corre en el puerto **5002**



PUNTO 4

## Servicio: Notificaciones (Node.js)
- Carpeta: `servicio-notificaciones/`
- Rol: consumir `payment.confirmed` desde RabbitMQ y enviar correos por SMTP (MailHog en laboratorio).
- Levantar solo este servicio:
  ```bash
  cd servicio-notificaciones
  docker compose up --build
