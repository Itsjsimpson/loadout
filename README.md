# Loadout
AI tool directory for vibe coders and builders. Static site.
- Data: edit `gen.py` -> `python3 gen.py` writes `tools.json` (public API).
- Pages: `LOADOUT_BASE_URL=https://yourdomain python3 build.py` (tool/category/use-case pages, sitemap, robots, llms.txt).
- Newsletter draft: `python3 newsletter.py` -> `newsletter/DATE.md` (diffs vs `snapshots/latest.json`).
- Tests: `python3 check.py` (HTML structure, meta, JSON-LD, internal links, external tool URLs).
- Monetization: `featured` and `affiliateUrl` fields per tool (empty; affiliate links get rel="sponsored").
