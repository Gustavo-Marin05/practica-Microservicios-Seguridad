import "dotenv/config";
import express from "express";
import { verifyJWT } from "./jwt.js";
import { sendPurchaseEmail } from "./email.js";
import { startConsumerWithRetry } from "./consumer.js";

const app = express();
app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({ status: "ok", service: "notifications" });
});

app.post("/notify/test", verifyJWT, async (req, res) => {
  try {
    const { to, name, event, quantity, total } = req.body || {};
    if (!to || !event?.name) {
      return res.status(400).json({ error: "Faltan campos: to, event.name" });
    }
    await sendPurchaseEmail({ to, name, event, quantity, total });
    res.json({ ok: true });
  } catch (err) {
    console.error("[/notify/test] error:", err?.message || err);
    res.status(500).json({ error: "No se pudo enviar el correo" });
  }
});

const port = Number(process.env.PORT || 3002);
app.listen(port, () => {
  console.log(`notifications-service on :${port}`);
});

startConsumerWithRetry();
