// Cloudflare Pages Function: POST /api/subscribe {email, website(honeypot)}
// Env (Pages → Settings → Environment variables): BEEHIIV_API_KEY, BEEHIIV_PUBLICATION_ID (optional)
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
  // Signups go to Beehiiv (no longer Resend). With BEEHIIV_API_KEY set, subscribe via API;
  // otherwise hand back the hosted Beehiiv subscribe URL.
  const pub = env.BEEHIIV_PUBLICATION_ID || "pub_49a39894-0d05-4c27-a465-26fe564c839e";
  const hosted = "https://jojos-newsletter-38aad3.beehiiv.com/subscribe?utm_source=loadoutweekly&utm_medium=website&utm_campaign=home&email=" + encodeURIComponent(email);
  const key = env.BEEHIIV_API_KEY;
  if (!key) return Response.json({ ok: false, redirect: hosted, error: "Continue on our Beehiiv signup page." });
  const r = await fetch(`https://api.beehiiv.com/v2/publications/${pub}/subscriptions`, {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
    body: JSON.stringify({ email, reactivate_existing: false, send_welcome_email: true,
      utm_source: "loadoutweekly", utm_medium: "website", utm_campaign: "home", referring_site: "https://loadoutweekly.com" }),
  });
  if (r.ok) return Response.json({ ok: true });
  console.error("beehiiv", r.status, await r.text());
  return Response.json({ ok: false, redirect: hosted, error: "Continue on our Beehiiv signup page." });
}

export async function onRequest(context) {
  if (context.request.method === "POST") return onRequestPost(context);
  return new Response(JSON.stringify({ ok: false, error: "Method not allowed" }), {
    status: 405,
    headers: { "Content-Type": "application/json", Allow: "POST" },
  });
}
