// Cloudflare Pages Function: POST /api/subscribe {email, website(honeypot)}
// Env (Pages → Settings → Environment variables):
//   BEEHIIV_API_KEY + BEEHIIV_PUBLICATION_ID (primary, if set)
//   RESEND_API_KEY, RESEND_SEGMENT_ID (fallback / mirror)
const EMAIL = /^[^\s@]{1,64}@[^\s@]{1,255}\.[a-z]{2,}$/i;

export async function onRequestPost(context) {
  const { request, env } = context;
  let body = {};
  const ct = request.headers.get("content-type") || "";
  try {
    if (ct.includes("application/json")) body = await request.json();
    else {
      const text = await request.text();
      try { body = JSON.parse(text); } catch { body = Object.fromEntries(new URLSearchParams(text)); }
    }
  } catch {
    return Response.json({ ok: false, error: "Invalid body." }, { status: 400 });
  }
  if (body.website) return Response.json({ ok: true });
  const email = String(body.email || "").trim().toLowerCase();
  if (!EMAIL.test(email) || email.length > 254) {
    return Response.json({ ok: false, error: "Please enter a valid email." }, { status: 400 });
  }
  const bk = env.BEEHIIV_API_KEY, pub = env.BEEHIIV_PUBLICATION_ID;
  if (bk && pub) {
    const b = await fetch(`https://api.beehiiv.com/v2/publications/${pub}/subscriptions`, {
      method: "POST",
      headers: { Authorization: `Bearer ${bk}`, "Content-Type": "application/json" },
      body: JSON.stringify({ email, reactivate_existing: false, send_welcome_email: true,
        utm_source: "loadoutweekly.com", referring_site: request.headers.get("referer") || "loadoutweekly.com" }),
    });
    if (b.ok) return Response.json({ ok: true });
    console.error("beehiiv", b.status, await b.text());
    if (!env.RESEND_API_KEY) return Response.json({ ok: false, error: "Could not subscribe right now. Try again later." }, { status: 502 });
  }
  const key = env.RESEND_API_KEY, seg = env.RESEND_SEGMENT_ID;
  if (!key) return Response.json({ ok: false, error: "Signup not configured yet." }, { status: 503 });
  const payload = { email, unsubscribed: false };
  if (seg) payload.segments = [{ id: seg }];
  const r = await fetch("https://api.resend.com/contacts", {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (r.ok || r.status === 409) return Response.json({ ok: true });
  console.error("resend", r.status, await r.text());
  return Response.json({ ok: false, error: "Could not subscribe right now. Try again later." }, { status: 502 });
}

export async function onRequest(context) {
  if (context.request.method === "POST") return onRequestPost(context);
  return new Response(JSON.stringify({ ok: false, error: "Method not allowed" }), {
    status: 405,
    headers: { "Content-Type": "application/json", Allow: "POST" },
  });
}
