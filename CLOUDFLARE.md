# Cloudflare Pages (branch: cloudflare-pages)

Local-only prep for migrating Loadout off Vercel Hobby.

- `_headers` — replaces `vercel.json` security header (`X-Content-Type-Options: nosniff`).
- `functions/api/subscribe.js` — Cloudflare Pages Function replacing `api/subscribe.js` (Vercel serverless). Needs env vars `RESEND_API_KEY` and optional `RESEND_SEGMENT_ID`.
- Static HTML/CSS/JS and Whop checkout links need no change.
- Do not merge until a `*.pages.dev` preview is verified and Jojo approves cutover.
- Full cutover steps: `/workspace/launch/cloudflare-migration.md`
