# Cloudflare Pages (branch: cloudflare-pages)

Local-only prep for migrating Loadout off Vercel Hobby.

- `_headers` — replaces `vercel.json` security header (`X-Content-Type-Options: nosniff`).
- `functions/api/subscribe.js` — Cloudflare Pages Function replacing `api/subscribe.js` (Vercel serverless). Writes to Beehiiv when `BEEHIIV_API_KEY` + `BEEHIIV_PUBLICATION_ID` are set; otherwise falls back to Resend (`RESEND_API_KEY`, optional `RESEND_SEGMENT_ID`).
- Static HTML/CSS/JS and Whop checkout links need no change.
- Do not merge until a `*.pages.dev` preview is verified and Jojo approves cutover.
- Full cutover steps: `/workspace/launch/cloudflare-migration.md`
