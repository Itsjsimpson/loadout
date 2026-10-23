# Loadout
AI tool directory for vibe coders and builders. Static site.
- Data: edit `gen.py` -> `python3 gen.py` writes `tools.json` (public API).
- Pages: `LOADOUT_BASE_URL=https://yourdomain python3 build.py` (tool/category/use-case/compare pages, sitemap, robots, llms.txt).
- Newsletter draft: `python3 newsletter.py` -> `newsletter/DATE.md` (diffs vs `snapshots/latest.json`).
- Tests: `python3 check.py` (HTML structure, meta, JSON-LD, internal links, external tool URLs).
- Monetization: `featured` and `affiliateUrl` fields per tool (empty; affiliate links get rel="sponsored").
- Search/AI crawl (2026-10-23): every page gets a summary, a visible "Last updated" date + "By Loadout Team", JSON-LD `dateModified`/`author`, and a "Related on Loadout" block. Dates come from git history (`seo.py`): the commit date of the last change to the page's visible text, or today if the text differs from HEAD. Build from a full (non-shallow) clone and commit the rebuilt pages.
- IndexNow: key file `d0a1f2fcfe3b5c756dde5aa5e6742ac3.txt` at the root. `python3 indexnow.py` is a dry run; `python3 indexnow.py --send` pings once (re-runs `check.py --live` first).
- Bing / Google ownership meta tags: paste the code into `BING_SITE_VERIFY` / `GOOGLE_SITE_VERIFY` in `build.py`, rebuild, ship via PR.
