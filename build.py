"""Build static SEO pages from tools.json. Run: python3 gen.py && python3 build.py"""
import json,os,html,shutil,datetime
BASE_URL=os.environ.get("LOADOUT_BASE_URL","https://loadoutweekly.com")  # Vercel production
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
def meta_desc(s,n=155):
    s=" ".join((s or "").split())
    if len(s)<=n:return s
    cut=s[:n-1].rsplit(" ",1)[0].rstrip(" ,.;:")
    return (cut or s[:n-1])+"…"
def nav(r):
    cl="".join(f'<a href="{r}categories/{c}.html">{E(n)}</a>' for c,n in cat.items())
    return (f'<a class="skip" href="#main">Skip to content</a><div class="psbanner"><div class="wrap"><strong>PrepSheet founding presale: $9.</strong> Daily show-prep brief for sports podcasters. Full refund if it doesn\'t launch. <a href="{r}prepsheet/">See PrepSheet →</a></div></div><header class="top"><div class="wrap bar"><a class="logo" href="{r}index.html"><span class="mark">L</span>Loadout</a>'
     f'<div class="mnav"><input type="checkbox" id="navt" class="sr navt"><label for="navt" class="burger" aria-label="Menu"><span></span><span></span><span></span></label><nav aria-label="Main">'
     f'<details class="dd"><summary>Categories</summary><div class="ddm">{cl}</div></details>'
     f'<a href="{r}index.html#picks">Use cases</a><a href="{r}categories/sports.html">Sports AI</a><a href="{r}index.html#new">New</a><a href="{r}index.html#tools">Directory</a><a href="{r}prepsheet/">PrepSheet</a>'
     f'<a class="btn btn-sm" href="{r}advertise.html">Advertise</a></nav></div></div></header>')
def crumbs(r,items):
    if not items:return ""
    li=f'<li><a href="{r}index.html">Home</a></li>'+"".join(f'<li><a href="{h}">{E(n)}</a></li>' if h else f'<li aria-current="page">{E(n)}</li>' for n,h in items)
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{li}</ol></nav>'
def footer(r,extra=""):
    cl="".join(f'<li><a href="{r}categories/{c}.html">{E(n)}</a></li>' for c,n in cat.items())
    ul="".join(f'<li><a href="{r}use-cases/{slug(u["question"])}.html">{E(u["question"])}</a></li>' for u in D["useCases"][:6])
    return (f'<footer class="foot"><div class="wrap fcols"><div><a class="logo" href="{r}index.html"><span class="mark">L</span>Loadout</a><p class="muted">AI tools for vibe coders and builders, ranked by what you are trying to ship.</p></div>'
     f'<div><h4>Categories</h4><ul>{cl}</ul></div><div><h4>Popular use cases</h4><ul>{ul}</ul></div>'
     f'<div><h4>Loadout</h4><ul><li><a href="{r}index.html#tools">Full directory</a></li><li><a href="{r}prepsheet/">PrepSheet</a></li><li><a href="{r}advertise.html">Advertise</a></li><li><a href="{r}tools.json">tools.json</a></li><li><a href="{r}llms.txt">llms.txt</a></li><li><a href="mailto:loadout@loadoutweekly.com">loadout@loadoutweekly.com</a></li></ul></div></div>'
     f'<div class="wrap fbase muted">Loadout · data updated {D["updated"]}{extra}</div></footer>')
def page(path,title,desc,body,ld=None,depth=0,foot="",bc=None):
    r="../"*depth;url=f"{BASE_URL}/{path}".replace("index.html","")
    h=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(title)}</title><meta name="description" content="{E(meta_desc(desc))}"><link rel="canonical" href="{url}">
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(meta_desc(desc))}"><meta property="og:url" content="{url}"><meta property="og:site_name" content="Loadout"><meta name="twitter:card" content="summary">
<link rel="icon" href="data:,"><link rel="stylesheet" href="{r}style.css">{'<script type="application/ld+json">'+json.dumps(ld)+'</script>' if ld else ''}</head><body>
{nav(r)}
<main id="main" class="wrap page">{crumbs(r,bc)}{body}</main>
{footer(r,foot)}<script src="{r}app.js" defer></script></body></html>"""
    os.makedirs(os.path.dirname(path) or ".",exist_ok=True);open(path,"w").write(h);pages.append(path)
PSCALL='<aside class="card callout"><div><span class="tag sponsored">Presale</span><strong>PrepSheet: daily show-prep brief for sports podcasters</strong><p>A one-page brief every morning before you record: stats, injuries, odds moves and talking points for the teams you cover, every item sourced. $9 founding member presale; full refund if it doesn\'t launch.</p></div><div class="psbtns"><a class="btn" href="'+os.environ.get("PREPSHEET_CHECKOUT","https://whop.com/checkout/plan_HesQSWaUF81Cq")+'" rel="noopener">Join for $9 →</a> <a href="{r}prepsheet/">See PrepSheet</a></div></aside>'
def chips(cur,r="../"):
    return '<nav class="chips" aria-label="Categories">'+"".join(f'<a class="chip{" on" if c==cur else ""}" href="{r}categories/{c}.html"{" aria-current=page" if c==cur else ""}>{E(n)} <span>{sum(t["category"]==c for t in D["tools"])}</span></a>' for c,n in cat.items())+'</nav>'
def related(t):
    o=[x for x in D["tools"] if x["category"]==t["category"] and x["id"]!=t["id"]][:6]
    return f'<section><h2>More in {E(cat[t["category"]])}</h2><div class="grid">{"".join(card(x) for x in o)}</div><p><a href="../categories/{t["category"]}.html">All {E(cat[t["category"]])} →</a></p></section>' if o else ''
def card(t,r="../"):
    v=t["verified"] or "unverified";u=t["affiliateUrl"] or t["url"]
    sp=is_featured(t);badge='<span class="tag sponsored">Featured · Sponsored</span>' if sp else ''
    aff='<span class="tag sponsored">Affiliate</span>' if t.get("affiliateUrl") else ''
    return f'<article class="card{" sponsor" if sp else ""}">{badge}<h3><a href="{r}tools/{t["id"]}.html">{E(t["name"])}</a></h3>{aff}<span class="tag">{E(cat[t["category"]])}</span><span class="tag {t["pricing"]}">{t["pricing"]}</span><p>{E(t["description"])}</p><p class="muted">Best for: {E(t["bestFor"])}</p>'+(f'<p class="muted"><strong>Pricing:</strong> {E(t["priceNote"])} <a href="{E(t["pricingSource"])}" rel="noopener">Source</a></p>' if t.get("priceNote") else '')+(f'<p><a href="{E(t["affiliateUrl"])}" rel="sponsored noopener">Visit {E(t["name"])} →</a> <span class="muted">(affiliate link)</span></p>' if t.get("affiliateUrl") else '')+'</article>'
AGENT_TOP=('<aside class="card callout disclosure" role="note" aria-label="Affiliate disclosure"><div><strong>Disclosure</strong><p>Rankings and listings on Loadout are editorial and <strong>never sold</strong>. This page contains one affiliate link: <strong>Postiz</strong>. If you sign up through it, Loadout may earn a commission at no extra cost to you. It does not affect the order or rankings on this page. The affiliate link is labelled &quot;Affiliate&quot; right next to it.</p></div></aside>'
 +'<p class="lead">The tools AI agents use to act in the real world: post to social, send and receive email, take payments, make phone calls and browse the web. Pricing is taken from each tool\'s official pricing page (checked Oct 17, 2026).</p>')
JOBS=[("Posting","Social posting"),("Email","Email"),("Payments","Payments"),("Phone","Phone and voice"),("Browsing","Browsing and web data")]
def agent_sections(ts):
    return "".join(f'<section><h2 id="{j.lower()}">{E(n)}</h2><div class="grid">{"".join(card(t) for t in ts if t.get("job")==j)}</div></section>' for j,n in JOBS if any(t.get("job")==j for t in ts))
for d in("tools","categories","use-cases"):shutil.rmtree(d,ignore_errors=True)
for t in D["tools"]:
    rel=t.get("affiliateUrl") and ' rel="sponsored noopener"' or ' rel="noopener"'
    ld={"@context":"https://schema.org","@type":"SoftwareApplication","name":t["name"],"description":t["description"],"applicationCategory":"DeveloperApplication","url":t["url"],"offers":{"@type":"Offer","description":t["pricing"]}}
    page(f"tools/{t['id']}.html",f"{t['name']} — {cat[t['category']]} | Loadout",f"{t['name']}: {t['description']} Best for: {t['bestFor']}. Pricing: {t['pricing']}.",
     f'<article class="detail card">{'<span class="tag sponsored">Featured · Sponsored</span>' if is_featured(t) else ''}<h1>{E(t["name"])}</h1>{'<span class="tag sponsored">Affiliate</span>' if t.get("affiliateUrl") else ''}<p class="lead">{E(t["description"])}</p><dl><dt>Category</dt><dd><a href="../categories/{t["category"]}.html">{E(cat[t["category"]])}</a></dd><dt>Best for</dt><dd>{E(t["bestFor"])}</dd><dt>Pricing</dt><dd>{t["pricing"]}{(" · "+E(t["priceNote"])+f' (<a href="{E(t["pricingSource"])}" rel="noopener">official pricing</a>)') if t.get("priceNote") else ""}</dd><dt>Last verified</dt><dd>{t["verified"] or "not yet verified"}</dd></dl><p><a class="btn" href="{E(t["affiliateUrl"] or t["url"])}"{rel}>Visit {E(t["name"])} →</a></p></article>'+related(t),ld,1,bc=[(cat[t["category"]],f"../categories/{t['category']}.html"),(t["name"],None)])
for cid,cn in cat.items():
    ts=sorted([t for t in D["tools"] if t["category"]==cid],key=lambda t:not is_featured(t))
    ld={"@context":"https://schema.org","@type":"ItemList","name":cn,"itemListElement":[{"@type":"ListItem","position":i+1,"name":t["name"],"url":f"{BASE_URL}/tools/{t['id']}.html"} for i,t in enumerate(ts)]}
    page(f"categories/{cid}.html",f"Best {cn} for vibe coders (2026) | Loadout",f"{len(ts)} {cn.lower()} for vibe coders and builders, with pricing and what each is best for.",f'<h1>{E(cn)}</h1>'+(AGENT_TOP if cid=="agent-tools" else f'<p class="lead">{len(ts)} tools, with pricing and what each is best for.</p>')+chips(cid)+(PSCALL.replace("{r}","../") if cid=="sports" else "")+f'<div class="filterbar"><label class="sr" for="cf">Filter tools in this category</label><input id="cf" type="search" data-filter=".grid > article" placeholder="Filter {len(ts)} tools…"><span class="muted" data-count></span></div>'+(agent_sections(ts) if cid=="agent-tools" else f'<section class="grid">{"".join(card(t) for t in ts)}</section>')+'',ld,1,bc=[("Categories","../index.html#categories"),(cn,None)])
for u in D["useCases"]:
    s=slug(u["question"]);u["slug"]=s;ts=[by[p] for p in u["picks"]]
    ld={"@context":"https://schema.org","@type":"ItemList","name":u["question"],"itemListOrder":"https://schema.org/ItemListOrderAscending","itemListElement":[{"@type":"ListItem","position":i+1,"name":t["name"],"url":f"{BASE_URL}/tools/{t['id']}.html"} for i,t in enumerate(ts)]}
    page(f"use-cases/{s}.html",f"{u['question']} — top picks | Loadout",f"Ranked picks for \"{u['question']}\": "+", ".join(t["name"] for t in ts)+".",f'<h1>{E(u["question"])}</h1><ol class="ranked">'+"".join(f'<li>{card(dict(t,featured=False))}</li>' for t in ts)+'</ol>'+'<p class="muted">Rankings are editorial and never sold. <a href="../index.html#picks">See all use cases →</a></p>',ld,1,bc=[("Use cases","../index.html#picks"),(u["question"],None)])
HUB_CHECKOUT=[("Standard hub",os.environ.get("HUB_STANDARD_CHECKOUT","https://whop.com/checkout/plan_wnhElC4Sjff7d")),("Coding Agents hub",os.environ.get("HUB_CODING_CHECKOUT","https://whop.com/checkout/plan_3SUe1fdbB7mQ4")),("Deploy & Backend hub",os.environ.get("HUB_DEPLOY_CHECKOUT","https://whop.com/checkout/plan_SkJgqwSdHPqUT"))]
ADV=('<h1>Advertise on Loadout</h1><p class="lead">Put your tool in front of vibe coders and builders. Launch pricing while we grow; early sponsors keep their rate.</p><section class="grid">'
 +f'<article class="card sponsor"><span class="tag">Featured</span><h3>Featured listing</h3><p>30 days in the homepage Featured slot, pinned to the top of your category page with a Featured badge. Always labelled as sponsored.</p><p><strong>{PRICE["featured"]}</strong> · launch pricing</p>'+(f'<p><a class="btn" href="{E(CHECKOUT["featured"])}" rel="noopener">Buy now →</a></p>' if CHECKOUT["featured"] else '<p class="muted">Checkout opening soon</p>')+'</article>'
 +f'<article class="card sponsor"><span class="tag">Sponsored</span><h3>Newsletter sponsor</h3><p>The single sponsor slot in one weekly Loadout issue: logo, up to 80 words and one link, plus a click report afterwards.</p><p><strong>{PRICE["newsletter"]}</strong> · launch pricing</p>'+(f'<p><a class="btn" href="{E(CHECKOUT["newsletter"])}" rel="noopener">Buy now →</a></p>' if CHECKOUT["newsletter"] else '<p class="muted">Checkout opening soon</p>')+'</article>'
 +'</section><p>Questions? Email <a href="mailto:loadout@loadoutweekly.com?subject=Loadout%20sponsorship">loadout@loadoutweekly.com</a></p>'
 +'<h2>More ways to sponsor</h2><section class="grid">'
 +'<article class="card sponsor"><span class="tag">Sponsored</span><h3>Category hub sponsorship</h3><p>A clearly labelled &quot;Sponsored by&quot; unit on one category hub page, shown alongside, never inside, the editorial rankings. One sponsor per hub, month to month, one-month minimum. Live within 2 business days of payment and assets.</p><ul><li><strong>$99 / month</strong> · standard hubs</li><li><strong>$149 / month</strong> · Coding Agents</li><li><strong>$199 / month</strong> · Deploy, Hosting &amp; Backend</li></ul>'+"".join(f'<p><a class="btn" href="{E(u)}" rel="noopener">{l} →</a></p>' if u.startswith("http") else f'<p class="muted">{l}: checkout opening soon</p>' for l,u in HUB_CHECKOUT)+'<p class="muted">Cancel before renewal; no partial-month refunds.</p></article>'
 +'<article class="card sponsor"><span class="tag">Featured (paid) + Spotlight (paid)</span><h3>Featured + Spotlight bundle</h3><p>The 30-day Featured listing plus a labelled &quot;Spotlight&quot; mention in the monthly New Launches roundup on the Loadout blog.</p><p><strong>$49</strong> · launch pricing</p><p class="muted"><strong>Available when the Loadout blog launches.</strong></p><p><a class="btn btn-sm" href="mailto:loadout@loadoutweekly.com?subject=Waitlist%3A%20Featured%20%2B%20Spotlight%20bundle">Join the waitlist →</a></p></article>'
 +'<article class="card sponsor"><span class="tag">Sponsored</span><h3>Sponsored review</h3><p>A hands-on review on the Loadout blog, labelled &quot;Sponsored&quot;, with a newsletter slot included. You buy coverage, not conclusions: one factual-accuracy check before publishing, no editorial approval. Published within 10 business days of product access.</p><p><strong>$79</strong> launch · <strong>$99</strong> standard</p><p class="muted"><strong>Available when the Loadout blog launches.</strong></p><p><a class="btn btn-sm" href="mailto:loadout@loadoutweekly.com?subject=Waitlist%3A%20Sponsored%20review">Join the waitlist →</a></p></article>'
 +'</section><h2>Disclosure</h2><p>Following the FTC Endorsement Guides, every paid placement on Loadout carries a clear label right next to it, such as &quot;Sponsored&quot;, &quot;Featured (paid)&quot; or &quot;Spotlight (paid)&quot;, not just a footer note. Newsletter slots are headed &quot;Sponsor&quot;. Sponsored reviews say &quot;Sponsored&quot; in the title and open with: <em>&quot;Sponsored: [Company] paid for this review. Our verdict is our own, and Loadout&#39;s editorial rankings are never sold.&quot;</em></p><p><strong>Editorial rankings are never sold.</strong> Sponsors cannot buy or move a &quot;Which tool should I use&quot; pick.</p><p class="muted">Payment is 100% upfront. Full refund if we decline or cancel before a placement runs, or if you cancel more than 5 days before the start. No traffic guarantees.</p><h2>Ground rules</h2><ul><li>Rankings in &quot;Which tool should I use&quot; are editorial and never sold. Sponsored tools are not boosted there.</li><li>Every paid placement is clearly labelled.</li><li>We may decline tools that are unsafe, misleading or off-topic for builders, and refund in full.</li></ul>')
page("advertise.html","Advertise on Loadout","Featured listings and newsletter sponsorships on Loadout, the AI tool directory for vibe coders and builders.",ADV,None,0,bc=[("Advertise",None)],foot=' · Sponsor contact: <a href="mailto:loadout@loadoutweekly.com">loadout@loadoutweekly.com</a>')
PS_URL=os.environ.get("PREPSHEET_CHECKOUT","https://whop.com/checkout/plan_HesQSWaUF81Cq")
PS=('<h1>PrepSheet: show prep for sports podcasters</h1><p class="lead">A one-page brief in your inbox every morning before you record: the stats, injuries, odds moves and talking points for the teams you cover. Every item links to its source.</p>'
 +'<p><span class="tag sponsored">Presale · not built yet</span></p>'
 +'<h2>Why</h2><ul><li>Cut the hour of tab-hopping before every episode down to a single page.</li><li>Only the teams and leagues you cover.</li><li>Every item is sourced, so you can check it before you say it on air.</li></ul>'
 +f'<h2>Founding member presale: $9</h2><article class="card sponsor"><p><strong>$9 one-time</strong> covers your first month once PrepSheet launches.</p><ul><li>Target launch: about 2 weeks from now. That is an estimate, not a promise.</li><li>We only build PrepSheet if at least 10 founding members join.</li><li><strong>Refund promise:</strong> if PrepSheet doesn\'t launch, you get a full refund of your $9.</li></ul><p><a class="btn" href="{E(PS_URL)}" rel="noopener">Become a founding member, $9 →</a></p><p class="muted">Checkout is handled by Whop. At checkout you tell us your podcast and the teams you cover.</p></article>'
 +'<h2>Sample brief</h2><p class="muted"><strong>EXAMPLE ONLY.</strong> The teams, players, numbers and sources below are made up to show the format. They are not real data.</p>'
 +'<article class="card"><span class="tag">Example · fictional data</span><h3>PrepSheet: Riverton Hawks vs. Lakeside Comets (example)</h3>'
 +'<p><strong>Key stats</strong></p><ul><li>Hawks have won 4 of their last 5 (example figure) [source link]</li><li>Comets\' starting guard is averaging 22.0 points over his last 3 games (example figure) [source link]</li></ul>'
 +'<p><strong>Injuries</strong></p><ul><li>Hawks forward J. Example: questionable, ankle (example) [source link]</li></ul>'
 +'<p><strong>Odds moves</strong></p><ul><li>Line moved from Hawks −3.5 to −2 since yesterday (example) [source link]</li></ul>'
 +'<p><strong>Talking points</strong></p><ul><li>Is the Hawks\' win streak real or a soft schedule?</li><li>What the questionable tag means for the rotation tonight.</li></ul></article>'
 +'<h2>Questions</h2><p>Email <a href="mailto:loadout@loadoutweekly.com?subject=PrepSheet">loadout@loadoutweekly.com</a>. PrepSheet is a project from Loadout.</p>')
page("prepsheet/index.html","PrepSheet: daily show prep for sports podcasters | Loadout","PrepSheet presale: a daily one-page brief for sports podcasters with sourced stats, injuries, odds moves and talking points. $9 founding member, full refund if it doesn't launch.",PS,None,1,bc=[("Sports AI Tools","../categories/sports.html"),("PrepSheet",None)])
# homepage static fallback list for crawlers + sitemap/llms
FEAT_HTML='<section id="featured" class="wrap" aria-label="Featured"><h2 class="h3">Featured</h2><div class="grid">'+"".join(card(t,"") for t in FEAT)+'</div></section>' if FEAT else None
tpl=open("index.tpl.html").read()
if FEAT_HTML:
    a=tpl.index('<section id="featured"');b=tpl.index('</section>',a)+10;tpl=tpl[:a]+FEAT_HTML+tpl[b:]
BLURB={'editors': 'Editors and IDEs with built-in AI and agents.', 'builders': 'Describe an app and get a working one.', 'agents': 'Agents that take on multi-step tasks in your repo.', 'frameworks': 'Libraries for building your own agents.', 'backend': 'Hosting, databases and serverless.', 'design': 'Turn designs into front-end code.', 'models': 'Model APIs to power your app.', 'sports': 'Data, clipping and editing tools for sports shows.', 'agent-tools': 'Posting, email, payments, phone and browsing for AI agents.'}
tpl=tpl.replace("<!--PSCALL-->",PSCALL.replace("{r}","")).replace("<!--HEADER-->",nav("")).replace("<!--FOOTER-->",footer("")).replace("<!--CATGRID-->","".join(f'<a class="catcard" href="categories/{c}.html"><strong>{E(n)}</strong><span class="muted">{E(BLURB.get(c,""))}</span><span class="count">{sum(t["category"]==c for t in D["tools"])} tools →</span></a>' for c,n in cat.items()))
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
# Cloudflare Pages 308-redirects /x.html to /x, so absolute URLs (canonical, og:url, JSON-LD, sitemap, llms) use the clean form.
import re as _re
_rx=_re.compile(_re.escape(BASE_URL)+r'/([A-Za-z0-9_./-]*?)\.html\b')
for _f in pages+["sitemap.xml","llms.txt","llms-full.txt"]:
    _s=open(_f).read();_n=_rx.sub(lambda m:BASE_URL+"/"+m.group(1),_s)
    if _n!=_s:open(_f,"w").write(_n)
print(len(pages),"pages")
