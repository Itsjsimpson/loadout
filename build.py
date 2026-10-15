"""Build static SEO pages from tools.json. Run: python3 gen.py && python3 build.py"""
import json,os,html,shutil,datetime
BASE_URL=os.environ.get("LOADOUT_BASE_URL","https://loadout-olive.vercel.app")  # Vercel production
D=json.load(open("tools.json"));E=html.escape
cat={c["id"]:c["name"] for c in D["categories"]};by={t["id"]:t for t in D["tools"]}
def slug(s):return "".join(ch if ch.isalnum() else "-" for ch in s.lower()).strip("-").replace("--","-")
pages=[]
TODAY=datetime.date.today().isoformat()
# Paste Whop checkout links here once products are live; empty = "coming soon".
CHECKOUT={"featured":os.environ.get("LOADOUT_CHECKOUT_FEATURED","https://whop.com/checkout/plan_66QiAqtZDPzii"),"newsletter":os.environ.get("LOADOUT_CHECKOUT_NEWSLETTER","https://whop.com/checkout/plan_IgcYDAAIortKU")}
PRICE={"featured":"$29 / 30 days","newsletter":"$25 / issue"}
def is_featured(t):
    f=t.get("featured")
    return bool(f) and (t.get("featuredUntil") or "9999") >= TODAY
FEAT=[t for t in D["tools"] if is_featured(t)]
def page(path,title,desc,body,ld=None,depth=0,foot=""):
    r="../"*depth;url=f"{BASE_URL}/{path}".replace("index.html","")
    h=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(desc)}"><link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Loadout"><meta name="twitter:card" content="summary">
<link rel="icon" href="data:,"><link rel="stylesheet" href="{r}style.css">{'<script type="application/ld+json">'+json.dumps(ld)+'</script>' if ld else ''}</head><body>
<header><div class="wrap"><a class="logo" href="{r}index.html">▣ Loadout</a><nav><a href="{r}index.html#picks">Picks</a><a href="{r}index.html#new">New</a><a href="{r}index.html#tools">Directory</a><a href="{r}advertise.html">Advertise</a></nav></div></header>
<main class="wrap">{body}</main>
<footer class="wrap"><p>Loadout · data updated {D['updated']} · <a href="{r}tools.json">tools.json</a> · <a href="{r}llms.txt">llms.txt</a> · <a href="{r}advertise.html">Advertise</a>{foot}</p></footer></body></html>"""
    os.makedirs(os.path.dirname(path) or ".",exist_ok=True);open(path,"w").write(h);pages.append(path)
def card(t,r="../"):
    v=t["verified"] or "unverified";u=t["affiliateUrl"] or t["url"]
    sp=is_featured(t);badge='<span class="tag sponsored">Featured · Sponsored</span>' if sp else ''
    return f'<article class="card{" sponsor" if sp else ""}">{badge}<h3><a href="{r}tools/{t["id"]}.html">{E(t["name"])}</a></h3><span class="tag">{E(cat[t["category"]])}</span><span class="tag {t["pricing"]}">{t["pricing"]}</span><p>{E(t["description"])}</p><p class="muted">Best for: {E(t["bestFor"])}</p></article>'
for d in("tools","categories","use-cases"):shutil.rmtree(d,ignore_errors=True)
for t in D["tools"]:
    rel=t.get("affiliateUrl") and ' rel="sponsored noopener"' or ' rel="noopener"'
    ld={"@context":"https://schema.org","@type":"SoftwareApplication","name":t["name"],"description":t["description"],"applicationCategory":"DeveloperApplication","url":t["url"],"offers":{"@type":"Offer","description":t["pricing"]}}
    page(f"tools/{t['id']}.html",f"{t['name']} — {cat[t['category']]} | Loadout",f"{t['name']}: {t['description']} Best for: {t['bestFor']}. Pricing: {t['pricing']}.",
     f'<article>{'<span class="tag sponsored">Featured · Sponsored</span>' if is_featured(t) else ''}<h1>{E(t["name"])}</h1><p class="lead">{E(t["description"])}</p><dl><dt>Category</dt><dd><a href="../categories/{t["category"]}.html">{E(cat[t["category"]])}</a></dd><dt>Best for</dt><dd>{E(t["bestFor"])}</dd><dt>Pricing</dt><dd>{t["pricing"]}</dd><dt>Last verified</dt><dd>{t["verified"] or "not yet verified"}</dd></dl><p><a class="btn" href="{E(t["affiliateUrl"] or t["url"])}"{rel}>Visit {E(t["name"])} →</a></p></article>',ld,1)
for cid,cn in cat.items():
    ts=sorted([t for t in D["tools"] if t["category"]==cid],key=lambda t:not is_featured(t))
    ld={"@context":"https://schema.org","@type":"ItemList","name":cn,"itemListElement":[{"@type":"ListItem","position":i+1,"name":t["name"],"url":f"{BASE_URL}/tools/{t['id']}.html"} for i,t in enumerate(ts)]}
    page(f"categories/{cid}.html",f"Best {cn} for vibe coders (2026) | Loadout",f"{len(ts)} {cn.lower()} for vibe coders and builders, with pricing and what each is best for.",f'<h1>{E(cn)}</h1><section class="grid">{"".join(card(t) for t in ts)}</section>',ld,1)
for u in D["useCases"]:
    s=slug(u["question"]);u["slug"]=s;ts=[by[p] for p in u["picks"]]
    ld={"@context":"https://schema.org","@type":"ItemList","name":u["question"],"itemListOrder":"https://schema.org/ItemListOrderAscending","itemListElement":[{"@type":"ListItem","position":i+1,"name":t["name"],"url":f"{BASE_URL}/tools/{t['id']}.html"} for i,t in enumerate(ts)]}
    page(f"use-cases/{s}.html",f"{u['question']} — top picks | Loadout",f"Ranked picks for \"{u['question']}\": "+", ".join(t["name"] for t in ts)+".",f'<h1>{E(u["question"])}</h1><ol class="ranked">'+"".join(f'<li>{card(dict(t,featured=False))}</li>' for t in ts)+'</ol>',ld,1)
ADV=('<h1>Advertise on Loadout</h1><p class="lead">Put your tool in front of vibe coders and builders. Launch pricing while we grow; early sponsors keep their rate.</p><section class="grid">'
 +f'<article class="card sponsor"><span class="tag">Featured</span><h3>Featured listing</h3><p>30 days in the homepage Featured slot, pinned to the top of your category page with a Featured badge. Always labelled as sponsored.</p><p><strong>{PRICE["featured"]}</strong> · launch pricing</p>'+(f'<p><a class="btn" href="{E(CHECKOUT["featured"])}" rel="noopener">Buy now →</a></p>' if CHECKOUT["featured"] else '<p class="muted">Checkout opening soon</p>')+'</article>'
 +f'<article class="card sponsor"><span class="tag">Sponsored</span><h3>Newsletter sponsor</h3><p>The single sponsor slot in one weekly Loadout issue: logo, up to 80 words and one link, plus a click report afterwards.</p><p><strong>{PRICE["newsletter"]}</strong> · launch pricing</p>'+(f'<p><a class="btn" href="{E(CHECKOUT["newsletter"])}" rel="noopener">Buy now →</a></p>' if CHECKOUT["newsletter"] else '<p class="muted">Checkout opening soon</p>')+'</article>'
 +'</section><p>Questions? Email <a href="mailto:loadout@mail.grokbot.com?subject=Loadout%20sponsorship">loadout@mail.grokbot.com</a></p><h2>Ground rules</h2><ul><li>Rankings in &quot;Which tool should I use&quot; are editorial and never sold. Sponsored tools are not boosted there.</li><li>Every paid placement is clearly labelled.</li><li>We may decline tools that are unsafe, misleading or off-topic for builders, and refund in full.</li></ul>')
page("advertise.html","Advertise on Loadout","Featured listings and newsletter sponsorships on Loadout, the AI tool directory for vibe coders and builders.",ADV,None,0,' · Sponsor contact: <a href="mailto:loadout@mail.grokbot.com">loadout@mail.grokbot.com</a>')
# homepage static fallback list for crawlers + sitemap/llms
FEAT_HTML='<section id="featured" class="wrap" aria-label="Featured"><h2 class="h3">Featured</h2><div class="grid">'+"".join(card(t,"") for t in FEAT)+'</div></section>' if FEAT else None
tpl=open("index.tpl.html").read()
if FEAT_HTML:
    a=tpl.index('<section id="featured"');b=tpl.index('</section>',a)+10;tpl=tpl[:a]+FEAT_HTML+tpl[b:]
open("index.html","w").write(tpl.replace("<!--STATIC-->","".join(f'<li><a href="tools/{t["id"]}.html">{E(t["name"])}</a> — {E(t["description"])}</li>' for t in D["tools"])).replace("<!--UCLINKS-->","".join(f'<li><a href="use-cases/{u["slug"]}.html">{E(u["question"])}</a></li>' for u in D["useCases"])).replace("<!--CATLINKS-->","".join(f'<li><a href="categories/{c}.html">{E(n)}</a></li>' for c,n in cat.items())))
pages.append("index.html")
open("sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f'<url><loc>{BASE_URL}/{p.replace("index.html","")}</loc><lastmod>{D["updated"]}</lastmod></url>' for p in pages)+"</urlset>\n")
open("robots.txt","w").write("User-agent: *\nAllow: /\n\n# AI crawlers welcome\n"+"".join(f"User-agent: {b}\nAllow: /\n" for b in["GPTBot","OAI-SearchBot","ChatGPT-User","ClaudeBot","Claude-User","PerplexityBot","Google-Extended","Applebot-Extended","CCBot"])+f"\nSitemap: {BASE_URL}/sitemap.xml\n")
L=[f"# Loadout\n\n> Directory of AI tools for vibe coders and builders, ranked by use case. Updated {D['updated']}. Machine-readable data: {BASE_URL}/tools.json (public, free to use with attribution).\n"]
L.append("## Categories\n"+"".join(f"- [{n}]({BASE_URL}/categories/{c}.html)\n" for c,n in cat.items()))
L.append("\n## Use cases\n"+"".join(f"- [{u['question']}]({BASE_URL}/use-cases/{u['slug']}.html)\n" for u in D["useCases"]))
L.append("\n## Data\n- [tools.json]("+BASE_URL+"/tools.json): categories, tools (id, name, category, description, bestFor, pricing, url, verified), useCases, newReleases\n- [llms-full.txt]("+BASE_URL+"/llms-full.txt): full content in one file\n")
open("llms.txt","w").write("".join(L))
F=["# Loadout — full content\n"]
for cid,cn in cat.items():
    F.append(f"\n## {cn}\n");F+= [f"- **{t['name']}** ({t['pricing']}) — {t['description']} Best for: {t['bestFor']}. {t['url']} (verified: {t['verified'] or 'no'})\n" for t in D["tools"] if t["category"]==cid]
F.append("\n## Which tool should I use\n");F+=[f"- {u['question']}: "+" > ".join(by[p]["name"] for p in u["picks"])+"\n" for u in D["useCases"]]
F.append("\n## New releases\n");F+=[f"- {r['date']} **{r['name']}** — {r['summary']} Source: {r['source']}\n" for r in D["newReleases"]]
open("llms-full.txt","w").write("".join(F))
print(len(pages),"pages")
