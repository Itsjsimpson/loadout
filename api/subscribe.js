// Vercel serverless function: POST /api/subscribe {email, website(honeypot)}
// Env: RESEND_API_KEY (required), RESEND_SEGMENT_ID (id of the "Loadout Newsletter" segment)
const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,255}\.[a-z]{2,}$/i;
module.exports = async (req, res) => {
  if (req.method !== "POST") { res.setHeader("Allow", "POST"); return res.status(405).json({ ok: false, error: "Method not allowed" }); }
  let body = req.body || {};
  if (typeof body === "string") { try { body = JSON.parse(body); } catch { body = Object.fromEntries(new URLSearchParams(body)); } }
  if (body.website) return res.status(200).json({ ok: true }); // honeypot: pretend success for bots
  const email = String(body.email || "").trim().toLowerCase();
  if (!EMAIL.test(email) || email.length > 254) return res.status(400).json({ ok: false, error: "Please enter a valid email." });
  const key = process.env.RESEND_API_KEY, seg = process.env.RESEND_SEGMENT_ID;
  if (!key) return res.status(503).json({ ok: false, error: "Signup not configured yet." });
  const payload = { email, unsubscribed: false };
  if (seg) payload.segments = [{ id: seg }];
  const r = await fetch("https://api.resend.com/contacts", { method: "POST", headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (r.ok || r.status === 409) return res.status(200).json({ ok: true });
  console.error("resend", r.status, await r.text());
  return res.status(502).json({ ok: false, error: "Could not subscribe right now. Try again later." });
};
