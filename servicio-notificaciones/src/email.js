import nodemailer from "nodemailer";

export function buildTransport() {
  const port = Number(process.env.EMAIL_PORT || 587);
  const secure = port === 465;
  return nodemailer.createTransport({
    host: process.env.EMAIL_HOST,
    port,
    secure,
    auth: (process.env.EMAIL_USER || process.env.EMAIL_PASS) ? {
      user: process.env.EMAIL_USER,
      pass: process.env.EMAIL_PASS
    } : undefined
  });
}

export async function sendPurchaseEmail({ to, name, event, quantity, total }) {
  const transporter = buildTransport();
  const subject = `Confirmación de compra: ${event.name}`;
  const text =
`Hola ${name || "cliente"}, tu compra fue confirmada.

Evento: ${event.name}
Fecha: ${event.date || "-"}
Entradas: ${quantity ?? "-"}
Total: ${total ?? "-"}

¡Gracias por tu compra!`;

  await transporter.sendMail({
    from: process.env.EMAIL_FROM || "no-reply@lab.local",
    to,
    subject,
    text
  });
}
