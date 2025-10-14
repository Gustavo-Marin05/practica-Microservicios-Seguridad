import amqp from "amqplib";
import { sendPurchaseEmail } from "./email.js";

async function connectAndConsume() {
  const url = process.env.RABBITMQ_URL;
  const exchange = process.env.RABBITMQ_EXCHANGE || "payments";
  const routingKey = process.env.RABBITMQ_ROUTING_KEY || "payment.confirmed";
  const queue = process.env.RABBITMQ_QUEUE || "notifications.payment.confirmed";

  const conn = await amqp.connect(url);
  const ch = await conn.createChannel();

  await ch.assertExchange(exchange, "topic", { durable: true });
  await ch.assertQueue(queue, { durable: true });
  await ch.bindQueue(queue, exchange, routingKey);

  console.log(`[rabbitmq] escuchando ${exchange}:${routingKey} -> ${queue}`);

  ch.consume(queue, async (msg) => {
    if (!msg) return;
    try {
      const payload = JSON.parse(msg.content.toString());
      if (payload?.type === "payment.confirmed") {
        const { user, event, quantity, total } = payload.data || {};
        if (!user?.email || !event?.name) {
          throw new Error("mensaje incompleto: user.email y event.name son requeridos");
        }
        await sendPurchaseEmail({ to: user.email, name: user.name, event, quantity, total });
        console.log(`[email] enviado a ${user.email}`);
      } else {
        console.log("[consumer] type no manejado:", payload?.type);
      }
      ch.ack(msg);
    } catch (err) {
      console.error("[consumer] error:", err.message);
      ch.nack(msg, false, false);
    }
  }, { noAck: false });
}

export async function startConsumerWithRetry() {
  let attempt = 0;
  while (true) {
    try {
      await connectAndConsume();
      return;
    } catch (e) {
      attempt++;
      const delay = Math.min(30000, 2000 * 2 ** (attempt - 1));
      console.error(`[consumer] fallo conexión a RabbitMQ (intento ${attempt}): ${e.message}. Reintentando en ${Math.round(delay/1000)}s`);
      await new Promise(r => setTimeout(r, delay));
    }
  }
}
