"""Build static SEO pages from tools.json. Run: python3 gen.py && python3 build.py"""
import json,os,html,shutil,datetime
BASE_URL=os.environ.get("LOADOUT_BASE_URL","https://loadoutweekly.com")  # Vercel production
D=json.load(open("tools.json"));E=html.escape
cat={c["id"]:c["name"] for c in D["categories"]};by={t["id"]:t for t in D["tools"]}
def slug(s):return "".join(ch if ch.isalnum() else "-" for ch in s.lower()).strip("-").replace("--","-")
pages=[]
# Editorial comparisons. Sentences are assembled only from tools.json fields.
COMPARES=[{"a":"cursor","b":"devin-desktop-formerly-windsurf","year":"2026","kind":"AI IDE","use_case":"I code daily and want an AI editor"}]
COMP_OUT=[]
def short_name(t):
    n=t["name"];i=n.find(" (");return n[:i] if i!=-1 else n
def lower_first(s):return (s[:1].lower()+s[1:]) if s else s
def compare_slug(c):return f"{slug(short_name(by[c['a']]))}-vs-{slug(short_name(by[c['b']]))}"
def compare_label(c):return f"Compare {short_name(by[c['a']])} vs {short_name(by[c['b']])}"
def tool_compare_link(tid):
    return "".join(f'<p><a href="../compare/{compare_slug(c)}.html">{E(compare_label(c))} →</a></p>' for c in COMPARES if tid in (c["a"],c["b"]))
def cat_compare_links(cid):
    return "".join(f'<p><a href="../compare/{compare_slug(c)}.html">{E(compare_label(c))} →</a></p>' for c in COMPARES if by[c["a"]]["category"]==cid and by[c["b"]]["category"]==cid)
def compare_card(t):
    return (f'<article class="card"><h3><a href="../tools/{t["id"]}.html">{E(t["name"])}</a></h3>'
     f'<span class="tag">{E(cat[t["category"]])}</span><span class="tag {t["pricing"]}">{t["pricing"]}</span>'
     f'<p>{E(t["description"])}</p><p class="muted">Best for: {E(t["bestFor"])}</p>'
     f'<p class="muted">Last verified: {E(t["verified"] or "not yet verified")}</p>'
     f'<p><a class="btn" href="{E(t["url"])}" rel="noopener">Visit {E(t["name"])} →</a></p></article>')
def emit_compares():
    for c in COMPARES:
        a,b=by[c["a"]],by[c["b"]]
        sa,sb=short_name(a),short_name(b)
        h1=f"{sa} vs {sb} ({c['year']})"
        uc=next((u for u in D["useCases"] if u["question"]==c["use_case"]),None)
        if not uc or "slug" not in uc:raise SystemExit(f"compare {compare_slug(c)}: use case missing")
        same=a["pricing"]==b["pricing"]
        desc=(f"Both {a['pricing']}. {sa}: {lower_first(a['bestFor'])}. {sb}: {lower_first(b['bestFor'])}." if same
              else f"{sa} ({a['pricing']}): {lower_first(a['bestFor'])}. {sb} ({b['pricing']}): {lower_first(b['bestFor'])}.")
        if len(desc)>155:raise SystemExit(f"compare {compare_slug(c)}: meta description is {len(desc)} chars")
        title=f"{h1}: which {c['kind']}? | Loadout"
        lead=f"{E(a['name'])} is for {E(lower_first(a['bestFor']))}. {E(b['name'])} is for {E(lower_first(b['bestFor']))}."
        rules=[f"Choose {E(sa)} for {E(lower_first(a['bestFor']))}. {E(a['name'])}: {E(a['description'])}",
               f"Choose {E(sb)} for {E(lower_first(b['bestFor']))}. {E(b['name'])}: {E(b['description'])}"]
        rules.append(f"Both are {E(a['pricing'])}. Pick the best-for line that matches the work. This page does not score either tool." if same
                     else f"{E(sa)} is {E(a['pricing'])}. {E(sb)} is {E(b['pricing'])}. Pick the best-for line that matches the work. This page does not score either tool.")
        faqs=[(f"What is {a['name']} best for?", a["bestFor"] if a["bestFor"].endswith(".") else a["bestFor"]+"."),
              (f"What is {b['name']} best for?", b["bestFor"] if b["bestFor"].endswith(".") else b["bestFor"]+"."),
              (f"What is {a['name']}?", a["description"]),
              (f"What is {b['name']}?", b["description"]),
              (f"What pricing does Loadout list for {sa} and {sb}?", f"Both are {a['pricing']}." if same else f"{a['name']} is {a['pricing']}. {b['name']} is {b['pricing']}.")]
        ctx=""
        if "devin-desktop-formerly-windsurf" in (a["id"],b["id"]) and "devin" in by:
            desk=a if a["id"]=="devin-desktop-formerly-windsurf" else b
            note=f"No. {short_name(desk)} is {desk['description']} Devin is the separate cloud agent product."
            ctx=f'<p>{E(short_name(desk))} is {E(desk["description"])} <a href="../tools/devin.html">{E(by["devin"]["name"])}</a> is the separate cloud agent product.</p>'
            faqs.append(("Is Devin Desktop the same product as Devin?", note))
        path=f"compare/{compare_slug(c)}.html"
        url=f"{BASE_URL}/{path}"
        ld={"@context":"https://schema.org","@graph":[
            {"@type":"WebPage","name":h1,"description":meta_desc(desc),"url":url},
            {"@type":"ItemList","name":h1,"itemListElement":[{"@type":"ListItem","position":i+1,"name":t["name"],"url":f"{BASE_URL}/tools/{t['id']}.html"} for i,t in enumerate((a,b))]},
            {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":ans}} for q,ans in faqs]}]}
        faq_html="".join(f"<h3>{E(q)}</h3><p>{E(ans)}</p>" for q,ans in faqs)
        body=(f'<h1>{E(h1)}</h1><p class="lead">{lead}</p>'
              f'<section><h2>Side by side</h2><div class="grid">{compare_card(a)}{compare_card(b)}</div></section>'
              f'<section><h2>Which should you pick?</h2><ul>{"".join(f"<li>{r}</li>" for r in rules)}</ul>{ctx}'
              f'<p class="muted">Editorial comparison. Rankings and picks on Loadout are never sold.</p></section>'
              f'<section><h2>Questions</h2>{faq_html}</section>'
              f'<p>See <a href="../categories/{a["category"]}.html">{E(cat[a["category"]])}</a> and the use case <a href="../use-cases/{uc["slug"]}.html">{E(uc["question"])}</a>.</p>')
        page(path,title,desc,body,ld,1,bc=[(cat[a["category"]],f"../categories/{a['category']}.html"),(h1,None)])
        COMP_OUT.append((h1,path,f"{a['name']} ({a['pricing']}) — {a['description']} Best for: {a['bestFor']}. {b['name']} ({b['pricing']}) — {b['description']} Best for: {b['bestFor']}. Editorial comparison; rankings and picks are never sold."))
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
    return f'<article class="card{" sponsor" if sp else ""}">{badge}<h3><a href="{r}tools/{t["id"]}.html">{E(t["name"])}</a></h3>{aff}<span class="tag">{E(cat[t["category"]])}</span><span class="tag {t["pricing"]}">{t["pricing"]}</span>'+(f'<p class="tagline"><strong>{E(t["tagline"])}</strong></p>' if t.get("tagline") else '')+f'<p>{E(t["description"])}</p><p class="muted">Best for: {E(t["bestFor"])}</p>'+(f'<p class="muted"><strong>Pricing:</strong> {E(t["priceNote"])} <a href="{E(t["pricingSource"])}" rel="noopener">Source</a></p>' if t.get("priceNote") else '')+(f'<p><a href="{E(t["affiliateUrl"])}" rel="sponsored noopener">Visit {E(t["name"])} →</a> <span class="muted">(affiliate link)</span></p>' if t.get("affiliateUrl") else '')+'</article>'
AGENT_TOP=('<aside class="card callout disclosure" role="note" aria-label="Affiliate disclosure"><div><strong>Disclosure</strong><p>Rankings and listings on Loadout are editorial and <strong>never sold</strong>. This page contains one affiliate link: <strong>Postiz</strong>. If you sign up through it, Loadout may earn a commission at no extra cost to you. It does not affect the order or rankings on this page. The affiliate link is labelled &quot;Affiliate&quot; right next to it.</p></div></aside>'
 +'<p class="lead">The tools AI agents use to act in the real world: post to social, send and receive email, take payments, make phone calls and browse the web. Pricing is taken from each tool\'s official pricing page (checked Oct 17, 2026).</p>')
JOBS=[("Posting","Social posting"),("Email","Email"),("Payments","Payments"),("Phone","Phone and voice"),("Browsing","Browsing and web data")]
def agent_sections(ts):
    return "".join(f'<section><h2 id="{j.lower()}">{E(n)}</h2><div class="grid">{"".join(card(t) for t in ts if t.get("job")==j)}</div></section>' for j,n in JOBS if any(t.get("job")==j for t in ts))
for d in("tools","categories","use-cases","compare"):shutil.rmtree(d,ignore_errors=True)
for t in D["tools"]:
    rel=t.get("affiliateUrl") and ' rel="sponsored noopener"' or ' rel="noopener"'
    ld={"@context":"https://schema.org","@type":"SoftwareApplication","name":t["name"],"description":t["description"],"applicationCategory":"DeveloperApplication","url":t["url"],"offers":{"@type":"Offer","description":t["pricing"]}}
    page(f"tools/{t['id']}.html",f"{t['name']} — {cat[t['category']]} | Loadout",f"{t['name']}: {t['description']} Best for: {t['bestFor']}. Pricing: {t['pricing']}.",
     f'<article class="detail card">{'<span class="tag sponsored">Featured · Sponsored</span>' if is_featured(t) else ''}<h1>{E(t["name"])}</h1>{'<span class="tag sponsored">Affiliate</span>' if t.get("affiliateUrl") else ''}{('<p class="tagline"><strong>'+E(t["tagline"])+'</strong></p>') if t.get("tagline") else ""}<p class="lead">{E(t["description"])}</p><dl><dt>Category</dt><dd><a href="../categories/{t["category"]}.html">{E(cat[t["category"]])}</a></dd><dt>Best for</dt><dd>{E(t["bestFor"])}</dd><dt>Pricing</dt><dd>{t["pricing"]}{(" · "+E(t["priceNote"])+f' (<a href="{E(t["pricingSource"])}" rel="noopener">official pricing</a>)') if t.get("priceNote") else ""}</dd><dt>Last verified</dt><dd>{t["verified"] or "not yet verified"}</dd></dl><p><a class="btn" href="{E(t["affiliateUrl"] or t["url"])}"{rel}>Visit {E(t["name"])} →</a></p>{tool_compare_link(t["id"])}</article>'+related(t),ld,1,bc=[(cat[t["category"]],f"../categories/{t['category']}.html"),(t["name"],None)])
for cid,cn in cat.items():
    ts=sorted([t for t in D["tools"] if t["category"]==cid],key=lambda t:not is_featured(t))
    ld={"@context":"https://schema.org","@type":"ItemList","name":cn,"itemListElement":[{"@type":"ListItem","position":i+1,"name":t["name"],"url":f"{BASE_URL}/tools/{t['id']}.html"} for i,t in enumerate(ts)]}
    page(f"categories/{cid}.html",f"Best {cn} for vibe coders (2026) | Loadout",f"{len(ts)} {cn.lower()} for vibe coders and builders, with pricing and what each is best for.",f'<h1>{E(cn)}</h1>'+(AGENT_TOP if cid=="agent-tools" else f'<p class="lead">{len(ts)} tools, with pricing and what each is best for.</p>')+cat_compare_links(cid)+chips(cid)+(PSCALL.replace("{r}","../") if cid=="sports" else "")+f'<div class="filterbar"><label class="sr" for="cf">Filter tools in this category</label><input id="cf" type="search" data-filter=".grid > article" placeholder="Filter {len(ts)} tools…"><span class="muted" data-count></span></div>'+(agent_sections(ts) if cid=="agent-tools" else f'<section class="grid">{"".join(card(t) for t in ts)}</section>')+'',ld,1,bc=[("Categories","../index.html#categories"),(cn,None)])
for u in D["useCases"]:
    s=slug(u["question"]);u["slug"]=s;ts=[by[p] for p in u["picks"]]
    ld={"@context":"https://schema.org","@type":"ItemList","name":u["question"],"itemListOrder":"https://schema.org/ItemListOrderAscending","itemListElement":[{"@type":"ListItem","position":i+1,"name":t["name"],"url":f"{BASE_URL}/tools/{t['id']}.html"} for i,t in enumerate(ts)]}
    page(f"use-cases/{s}.html",f"{u['question']} — top picks | Loadout",f"Ranked picks for \"{u['question']}\": "+", ".join(t["name"] for t in ts)+".",f'<h1>{E(u["question"])}</h1><ol class="ranked">'+"".join(f'<li>{card(dict(t,featured=False))}</li>' for t in ts)+'</ol>'+'<p class="muted">Rankings are editorial and never sold. <a href="../index.html#picks">See all use cases →</a></p>',ld,1,bc=[("Use cases","../index.html#picks"),(u["question"],None)])
emit_compares()
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
 +f'<h2>Founding member presale: $9</h2><article class="card sponsor"><p><strong>$9 one-time</strong> covers your first month once PrepSheet launches.</p><ul><li>Launch date: not set yet. PrepSheet launches once 10 founding members join.</li><li>We only build PrepSheet if at least 10 founding members join.</li><li><strong>Refund promise:</strong> if PrepSheet doesn\'t launch, you get a full refund of your $9.</li></ul><p><a class="btn" href="{E(PS_URL)}" rel="noopener">Become a founding member, $9 →</a></p><p class="muted">Checkout is handled by Whop. At checkout you tell us your podcast and the teams you cover.</p></article>'
 +'<h2>Sample brief</h2><p class="muted"><strong>EXAMPLE ONLY.</strong> The teams, players, numbers and sources below are made up to show the format. They are not real data.</p>'
 +'<article class="card"><span class="tag">Example · fictional data</span><h3>PrepSheet: Riverton Hawks vs. Lakeside Comets (example)</h3>'
 +'<p><strong>Key stats</strong></p><ul><li>Hawks have won 4 of their last 5 (example figure) [source link]</li><li>Comets\' starting guard is averaging 22.0 points over his last 3 games (example figure) [source link]</li></ul>'
 +'<p><strong>Injuries</strong></p><ul><li>Hawks forward J. Example: questionable, ankle (example) [source link]</li></ul>'
 +'<p><strong>Odds moves</strong></p><ul><li>Line moved from Hawks −3.5 to −2 since yesterday (example) [source link]</li></ul>'
 +'<p><strong>Talking points</strong></p><ul><li>Is the Hawks\' win streak real or a soft schedule?</li><li>What the questionable tag means for the rotation tonight.</li></ul></article>'
 +'<h2>Questions</h2><p>Email <a href="mailto:loadout@loadoutweekly.com?subject=PrepSheet">loadout@loadoutweekly.com</a>. PrepSheet is a project from Loadout.</p>')
page("prepsheet/index.html","PrepSheet: daily show prep for sports podcasters | Loadout","PrepSheet presale: a daily one-page brief for sports podcasters with sourced stats, injuries, odds moves and talking points. $9 founding member, full refund if it doesn't launch.",PS,None,1,bc=[("Sports AI Tools","../categories/sports.html"),("PrepSheet",None)])
# Guide: Best AI coding tool for your first SaaS. Prices only from official pricing pages, checked Oct 17, 2026.
# Public X replies are paraphrased without handles or names. Body internal links are clean (no .html).
GCHK="checked Oct 17, 2026"
GSRC={"codex":"https://learn.chatgpt.com/docs/pricing","claude":"https://claude.com/pricing","cursor":"https://cursor.com/pricing","lovable":"https://lovable.dev/pricing","bolt":"https://bolt.new/pricing","replit":"https://replit.com/pricing","v0":"https://v0.app/pricing"}
GSUB="https://jojos-newsletter-38aad3.beehiiv.com/subscribe?utm_source=loadoutweekly&utm_medium=website&utm_campaign=first-saas-page"
def gsrc(k,label="official pricing"):return f'<a href="{GSRC[k]}" rel="noopener">{label}</a>'
def gtool(tid,label=None):return f'<a href="../tools/{tid}">{E(label or by[tid]["name"])}</a>'
GROWS=[  # tool, what it is, free option, entry paid, next step, source key
 (gtool("openai-codex","Codex")+" (OpenAI)","Coding agent. On Plus: on the web, in the terminal (CLI), in your editor (IDE extension) and on iOS","Yes. Free plan includes Codex, $0/month","Go $8/month; Plus $20/month","Pro from $100/month (plans at $100, $200 or $500)","codex"),
 (gtool("claude-code","Claude Code")+" (Anthropic)","Coding agent, included with Claude paid plans","No. Claude Code isn't on the Free plan","Pro $20/month billed monthly ($17/month with annual billing, $200 up front)","Max from $100/month","claude"),
 (gtool("cursor","Cursor"),"Code editor with an AI agent","Free $0/month (limited agent requests)","Plus $8/month (only Grok models on this plan)","Premium $30/month; Super $100/month; Ultra $200/month. Third-party models billed separately by usage","cursor"),
 (gtool("lovable","Lovable"),"Chat-to-app builder with hosting","Free $0/month: 5 daily build credits (up to 30 a month) plus 20 monthly Cloud credits","Pro $25/month (100 monthly credits, billed monthly)","Business $50/month (100 monthly credits)","lovable"),
 (gtool("bolt-new","Bolt"),"Chat-to-app builder with hosting","Free $0: 300K tokens daily limit, 1M tokens a month","Pro $25/month billed monthly (starts at 10M tokens a month). Yearly price: check pricing page","Teams $30 per member/month billed monthly","bolt"),
 (gtool("replit","Replit"),"Browser workspace with an AI agent, database and hosting","Check pricing page","Core $20/month ($18/month billed annually)","Pro $100/month ($90/month billed annually)","replit"),
 (gtool("v0","v0")+" (Vercel)","AI front-end and app builder that deploys to Vercel","Free $0/month, 7 messages a day","Plus $30/user/month (shown next to a crossed-out $90)","Business $100/user/month","v0"),
]
GFAQ=[
 ("Do I need to pay for another tool if I already have ChatGPT?",f"Not to start. OpenAI says Codex is included in ChatGPT Free, Go, Plus, Pro, Business, Edu and Enterprise plans. Try it before you buy anything else.","codex"),
 ("Is Claude Code free?","No. Claude Code is included in Claude's paid plans (Pro and up) and isn't on the Free plan.","claude"),
 ("Can I start in Lovable or Bolt and switch later?","Yes. Several builders suggested exactly that: build a clickable version first, then move the code to GitHub and keep going in a code tool when you need login, payments and a database. Moving takes work, so do it once, on purpose.",None),
 ("What's the one habit that saves beginners the most pain?","Save your work with git after every step that works. When the AI breaks something, you can go back in seconds.",None),
 ("Which tech stack should I pick?","One builder's advice: pick a boring, popular stack such as Next.js with Postgres, because the AI has lots of examples of it to learn from.",None),
 ("How often do these prices change?","Often. Every price on this page links to the official pricing page and shows the date we checked it (Oct 17, 2026).",None),
 ("Does Loadout get paid to rank tools?","No. Loadout rankings are never for sale. This page contains no affiliate links.",None),
]
GUIDE=('<article class="guide"><h1>Best AI coding tool for your first SaaS</h1>'
 +f'<p class="muted">By Loadout Team · Prices {GCHK} from official pricing pages</p>'
 +'<aside class="card callout disclosure" role="note" aria-label="Affiliate disclosure"><div><strong>Disclosure</strong><p>Rankings and picks on Loadout are editorial and <strong>never sold</strong>. <strong>This page contains no affiliate links</strong> and no paid placements. No tool on this page paid to be included or to be placed. If that ever changes, the link will be labelled &quot;Affiliate&quot; or &quot;Sponsored&quot; right next to it.</p></div></aside>'
 +'<p class="lead">A plain-English guide to Codex, Claude Code, Cursor, Lovable, Bolt, Replit and v0 for first-time builders, using official prices and advice from builders who have shipped.</p>'
 +'<h2 id="quick-answer">Quick answer</h2>'
 +f'<p><strong>Already paying for ChatGPT? Start with Codex. It&#39;s already in your plan.</strong> OpenAI says Codex is included in ChatGPT Free, Go, Plus, Pro, Business, Edu and Enterprise. On Plus ($20/month) you get it on the web, in the terminal (CLI), in your code editor (IDE extension) and on iOS ({gsrc("codex","OpenAI pricing")}, {GCHK}).</p>'
 +'<ul><li><strong>Want to read and own your code?</strong> Codex, Claude Code or Cursor.</li><li><strong>Can&#39;t code at all and want a clickable app fast?</strong> Lovable or Bolt. Plan to move to a code tool once you add login, payments and a database.</li><li><strong>The most repeated tip from builders:</strong> pick one tool, save your work with git often, and don&#39;t switch until version 1 ships.</li></ul>'
 +'<p>That last tip came up again and again when a first-time builder asked this exact question on X. He already paid for ChatGPT, kept seeing Cursor, Claude Code, Lovable, Bolt and Replit everywhere, and was building by pasting code from ChatGPT into VS Code by hand. If that sounds like you, the biggest step up is a tool that edits the files for you, so you stop copying and pasting.</p>'
 +'<h2 id="by-situation">Pick by situation</h2>'
 +f'<section class="grid">'
 +f'<article class="card"><h3>&quot;I already pay for ChatGPT and I&#39;m on a budget.&quot;</h3><p><strong>Codex.</strong> It&#39;s in your plan already, so you pay nothing extra to start. Plus is $20/month. If you hit limits, Pro starts at $100/month.</p><p class="muted">{gsrc("codex")} · {GCHK}</p></article>'
 +f'<article class="card"><h3>&quot;I want to understand and own every line of code.&quot;</h3><p><strong>Claude Code or Cursor.</strong> Claude Code comes with Claude Pro ($20/month billed monthly, or $17/month with annual billing at $200 up front). It isn&#39;t on the Free plan. Cursor is a code editor with an AI agent built in; read the Cursor pricing note below before you pick a plan.</p><p class="muted">{gsrc("claude","Claude pricing")} · {gsrc("cursor","Cursor pricing")} · {GCHK}</p></article>'
 +f'<article class="card"><h3>&quot;I can&#39;t code. I want to see my idea working this weekend.&quot;</h3><p><strong>Lovable or Bolt.</strong> You describe the app in chat and it gets built and hosted for you. Lovable Pro is $25/month (100 monthly credits, custom domains). Bolt Pro is $25/month billed monthly and includes custom domain support.</p><p class="muted">{gsrc("lovable","Lovable pricing")} · {gsrc("bolt","Bolt pricing")} · {GCHK}</p></article>'
 +f'<article class="card"><h3>&quot;I want everything in the browser: code, database, hosting.&quot;</h3><p><strong>Replit.</strong> Core is $20/month ($18/month billed annually) and Pro is $100/month ($90/month billed annually).</p><p class="muted">{gsrc("replit")} · {GCHK}</p></article>'
 +f'<article class="card"><h3>&quot;I mostly need a good-looking front end I can deploy to Vercel.&quot;</h3><p><strong>v0.</strong> The free plan has a 7-message-a-day limit, deploys to Vercel and syncs with GitHub. Plus is $30/user/month and Business is $100/user/month.</p><p class="muted">{gsrc("v0")} · {GCHK}</p></article>'
 +'</section>'
 +f'<h2 id="compare">Comparison table</h2><p class="muted">Official pricing pages only, {GCHK}. Prices exclude tax and can change. Always confirm on the official page before you buy.</p>'
 +'<div class="tablewrap"><table class="cmp"><caption class="sr">AI coding tools for a first SaaS: free option, entry plan and next plan, from official pricing pages</caption><thead><tr><th scope="col">Tool</th><th scope="col">What it is</th><th scope="col">Free option</th><th scope="col">Entry paid plan</th><th scope="col">Next step up</th><th scope="col">Source</th></tr></thead><tbody>'
 +"".join(f'<tr><th scope="row">{a}</th><td>{E(b)}</td><td>{E(c)}</td><td>{E(d)}</td><td>{E(e)}</td><td>{gsrc(k)}<br><span class="muted">{GCHK}</span></td></tr>' for a,b,c,d,e,k in GROWS)
 +'</tbody></table></div>'
 +f'<p class="muted"><strong>Cursor pricing note:</strong> Cursor&#39;s official pricing page currently lists Free, Plus, Premium, Super and Ultra plans bundled with Grok and X features, says only Grok models are available on Plus, bills third-party models (such as Claude) separately by usage on paid plans, and says subscriptions are sold through X Subscription Corp. Check {gsrc("cursor","cursor.com/pricing")} before you buy.</p>'
 +'<h2 id="pains">The real pains, from builders who answered</h2><p class="muted">Paraphrased from public replies on X. We left out replies from people who run tool-directory or ranking sites.</p>'
 +'<ol><li><strong>AI &quot;fixes&quot; one thing and breaks three others.</strong> Commit to git before every big AI change, and after every step that works, so you can roll back in seconds when it goes sideways.</li>'
 +'<li><strong>App builders feel fast until you need to change something.</strong> Several builders said Lovable or Bolt can get you a clickable demo by the weekend, but login, billing, webhooks, database changes and the first strange bug are where you want your own code files.</li>'
 +'<li><strong>&quot;It works on my computer&quot; but breaks when it goes live.</strong> One builder said most of that pain comes from setup like the site URL, secret keys and database access rules, not from the tool. Fix those before you spend money on ads.</li>'
 +'<li><strong>Tool-hopping.</strong> Switching tools mid-build costs more than any difference between them, and whichever one you pick, you&#39;ll be tempted to switch again in two weeks.</li>'
 +'<li><strong>Picking for day 1 instead of month 3.</strong> Choose the tool you can still live with once the app is real. One builder uses Lovable to get the first screen live and connected to a database, then moves to Cursor from day 2.</li></ol>'
 +'<p>A solo builder said they would pick Claude Code again if they had to start over, because most of their small apps are built in it.</p>'
 +'<h2 id="faq">FAQ</h2>'
 +"".join(f'<h3>{E(q)}</h3><p>{E(a)}'+(f' ({gsrc(k,"source")}, {GCHK})' if k else '')+'</p>' for q,a,k in GFAQ)
 +f'<aside class="card callout"><div><strong>Get the weekly version</strong><p>Tools and prices change every week. Loadout Weekly is a free email with the AI coding tools worth using right now, in plain English, ranked honestly and never for sale.</p></div><div><a class="btn" href="{E(GSUB)}" rel="noopener">Subscribe free →</a></div></aside>'
 +f'<p class="muted">By Loadout Team. Prices from official pricing pages, {GCHK}. Builder advice is paraphrased from public replies on X. More picks: <a href="../categories/editors">AI editors</a> · <a href="../categories/builders">app builders</a> · <a href="../categories/agents">coding agents</a>.</p></article>')
GURL=f"{BASE_URL}/best-ai-coding-tool-first-saas/"
GLD={"@context":"https://schema.org","@graph":[
 {"@type":"Article","headline":"Best AI coding tool for your first SaaS","description":"A plain-English guide to Codex, Claude Code, Cursor, Lovable, Bolt, Replit and v0 for first-time builders, using official prices checked Oct 17, 2026.","datePublished":"2026-10-17","dateModified":"2026-10-17","author":{"@type":"Organization","name":"Loadout Team","url":BASE_URL+"/"},"publisher":{"@type":"Organization","name":"Loadout","url":BASE_URL+"/"},"mainEntityOfPage":GURL,"about":[{"@type":"SoftwareApplication","name":n,"applicationCategory":"DeveloperApplication","url":GSRC[k]} for n,k in [("Codex","codex"),("Claude Code","claude"),("Cursor","cursor"),("Lovable","lovable"),("Bolt","bolt"),("Replit","replit"),("v0","v0")]]},
 {"@type":"FAQPage","mainEntity":[{"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a,k in GFAQ]},
 {"@type":"BreadcrumbList","itemListElement":[{"@type":"ListItem","position":1,"name":"Home","item":BASE_URL+"/"},{"@type":"ListItem","position":2,"name":"Best AI coding tool for your first SaaS","item":GURL}]}]}
page("best-ai-coding-tool-first-saas/index.html","Best AI coding tool for your first SaaS (2026) | Loadout","Building your first SaaS? A plain-English guide to Codex, Claude Code, Cursor, Lovable, Bolt, Replit and v0, with official prices and real builder advice.",GUIDE,GLD,1,bc=[("Best AI coding tool for your first SaaS",None)])
GUIDES=[("Best AI coding tool for your first SaaS","best-ai-coding-tool-first-saas/","Codex, Claude Code, Cursor, Lovable, Bolt, Replit and v0 compared for first-time builders, with official prices checked Oct 17, 2026.")]
# homepage static fallback list for crawlers + sitemap/llms
FEAT_HTML='<section id="featured" class="wrap" aria-label="Featured"><h2 class="h3">Featured</h2><div class="grid">'+"".join(card(t,"") for t in FEAT)+'</div></section>' if FEAT else None
tpl=open("index.tpl.html").read()
if FEAT_HTML:
    a=tpl.index('<section id="featured"');b=tpl.index('</section>',a)+10;tpl=tpl[:a]+FEAT_HTML+tpl[b:]
BLURB={'editors': 'Editors and IDEs with built-in AI and agents.', 'builders': 'Describe an app and get a working one.', 'agents': 'Agents that take on multi-step tasks in your repo.', 'frameworks': 'Libraries for building your own agents.', 'backend': 'Hosting, databases and serverless.', 'design': 'Turn designs into front-end code.', 'models': 'Model APIs to power your app.', 'sports': 'Data, clipping and editing tools for sports shows.', 'agent-tools': 'Posting, email, payments, phone and browsing for AI agents.'}
tpl=tpl.replace("<!--PSCALL-->",PSCALL.replace("{r}","")).replace("<!--HEADER-->",nav("")).replace("<!--FOOTER-->",footer("")).replace("<!--CATGRID-->","".join(f'<a class="catcard" href="categories/{c}.html"><strong>{E(n)}</strong><span class="muted">{E(BLURB.get(c,""))}</span><span class="count">{sum(t["category"]==c for t in D["tools"])} tools →</span></a>' for c,n in cat.items()))
# Homepage JSON-LD (daily ship 2026-10-22): WebSite + Organization + ItemList of categories, all from existing data.
HLD={"@context":"https://schema.org","@graph":[
 {"@type":"WebSite","@id":BASE_URL+"/#website","name":"Loadout","url":BASE_URL+"/","description":"Loadout ranks AI tools for vibe coders and builders by use case.","publisher":{"@id":BASE_URL+"/#org"}},
 {"@type":"Organization","@id":BASE_URL+"/#org","name":"Loadout","url":BASE_URL+"/","sameAs":["https://x.com/loadout_toolsAI"]},
 {"@type":"ItemList","name":"Loadout categories","itemListElement":[{"@type":"ListItem","position":i+1,"name":n,"url":f"{BASE_URL}/categories/{c}.html"} for i,(c,n) in enumerate(cat.items())]}]}
tpl=tpl.replace("</head>",'<script type="application/ld+json">'+json.dumps(HLD)+"</script></head>",1)
open("index.html","w").write(tpl.replace("<!--STATIC-->","".join(f'<li><a href="tools/{t["id"]}.html">{E(t["name"])}</a> — {E(t["description"])}</li>' for t in D["tools"])).replace("<!--UCLINKS-->","".join(f'<li><a href="use-cases/{u["slug"]}.html">{E(u["question"])}</a></li>' for u in D["useCases"])).replace("<!--CATLINKS-->","".join(f'<li><a href="categories/{c}.html">{E(n)}</a></li>' for c,n in cat.items())))
pages.append("index.html")
open("sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+"".join(f'<url><loc>{BASE_URL}/{p.replace("index.html","")}</loc><lastmod>{D["updated"]}</lastmod></url>' for p in pages)+"</urlset>\n")
open("robots.txt","w").write("User-agent: *\nAllow: /\n\n# AI crawlers welcome\n"+"".join(f"User-agent: {b}\nAllow: /\n" for b in["GPTBot","OAI-SearchBot","ChatGPT-User","ClaudeBot","Claude-User","PerplexityBot","Google-Extended","Applebot-Extended","CCBot"])+f"\nSitemap: {BASE_URL}/sitemap.xml\n")
L=[f"# Loadout\n\n> Directory of AI tools for vibe coders and builders, ranked by use case. Updated {D['updated']}. Machine-readable data: {BASE_URL}/tools.json (public, free to use with attribution).\n"]
L.append("## Categories\n"+"".join(f"- [{n}]({BASE_URL}/categories/{c}.html)\n" for c,n in cat.items()))
L.append("\n## Use cases\n"+"".join(f"- [{u['question']}]({BASE_URL}/use-cases/{u['slug']}.html)\n" for u in D["useCases"]))
L.append("\n## Guides\n"+"".join(f"- [{n}]({BASE_URL}/{p}): {d}\n" for n,p,d in GUIDES))
if COMP_OUT:L.append("\n## Comparisons\n"+"".join(f"- [{h}]({BASE_URL}/{p})\n" for h,p,_ in COMP_OUT))
L.append("\n## Data\n- [tools.json]("+BASE_URL+"/tools.json): categories, tools (id, name, category, description, bestFor, pricing, url, verified), useCases, newReleases\n- [llms-full.txt]("+BASE_URL+"/llms-full.txt): full content in one file\n")
open("llms.txt","w").write("".join(L))
F=["# Loadout — full content\n"]
for cid,cn in cat.items():
    F.append(f"\n## {cn}\n");F+= [f"- **{t['name']}** ({t['pricing']}) — {t['description']} Best for: {t['bestFor']}. {t['url']} (verified: {t['verified'] or 'no'})\n" for t in D["tools"] if t["category"]==cid]
F.append("\n## Which tool should I use\n");F+=[f"- {u['question']}: "+" > ".join(by[p]["name"] for p in u["picks"])+"\n" for u in D["useCases"]]
F.append("\n## Guides\n");F+=[f"- [{n}]({BASE_URL}/{p}): {d}\n" for n,p,d in GUIDES]
if COMP_OUT:
    F.append("\n## Comparisons\n");F+=[f"- **{h}** — {s} {BASE_URL}/{p}\n" for h,p,s in COMP_OUT]
F.append("\n## New releases\n");F+=[f"- {r['date']} **{r['name']}** — {r['summary']} Source: {r['source']}\n" for r in D["newReleases"]]
open("llms-full.txt","w").write("".join(F))
# Cloudflare Pages 308-redirects /x.html to /x, so absolute URLs (canonical, og:url, JSON-LD, sitemap, llms) use the clean form.
import re as _re
_rx=_re.compile(_re.escape(BASE_URL)+r'/([A-Za-z0-9_./-]*?)\.html\b')
for _f in pages+["sitemap.xml","llms.txt","llms-full.txt"]:
    _s=open(_f).read();_n=_rx.sub(lambda m:BASE_URL+"/"+m.group(1),_s)
    if _n!=_s:open(_f,"w").write(_n)
print(len(pages),"pages")
# Internal relative links use clean URLs too (audit fix 4): Cloudflare Pages 308s every /x.html, so a nav link to
# x.html costs every click a redirect. Rewrite href="x.html#f" -> "x#f", "dir/index.html" -> "dir/", "index.html" -> "./".
_href=_re.compile(r'href="(?!https?:|mailto:|#|data:|//)([^"#?]*?)(index)?\.html([#?][^"]*)?"')
def _clean(m):
    path,idx,frag=m.group(1),m.group(2),m.group(3) or ""
    if idx is not None and (path=="" or path.endswith("/")): out=path or "./"
    else: out=path+(idx or "")
    return f'href="{out}{frag}"'
for _f in pages:
    _s=open(_f).read();_n=_href.sub(_clean,_s)
    if _n!=_s:open(_f,"w").write(_n)
# Real 404 page (soft-404 fix). Cloudflare Pages serves /404.html with a 404 status for any missing path once it
# exists at the output root; without it Pages falls back to SPA mode and serves index.html with 200.
# Root-relative links so it works at any depth. noindex, no canonical, and kept out of sitemap.xml / llms.txt.
NF_SUB="https://jojos-newsletter-38aad3.beehiiv.com/subscribe?utm_source=loadoutweekly&utm_medium=website&utm_campaign=404"
NF=f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Page not found | Loadout</title><meta name="description" content="This page doesn&#x27;t exist on Loadout. Try the homepage, the tools directory or the free newsletter."><meta name="robots" content="noindex">
<link rel="icon" href="data:,"><link rel="stylesheet" href="/style.css"></head><body>
{nav("/")}
<main id="main" class="wrap page"><article class="card"><h1>Page not found</h1><p class="lead">We couldn&#39;t find that page. It may have moved, or the link may be wrong.</p>
<ul><li><a href="/">Go to the Loadout homepage</a></li><li><a href="/#tools">Browse the tools directory</a></li><li><a href="{E(NF_SUB)}" rel="noopener">Get Loadout Weekly, the free newsletter</a></li></ul>
<p><a class="btn" href="/">Back to home →</a></p></article></main>
{footer("/")}<script src="/app.js" defer></script></body></html>"""
open("404.html","w").write(_href.sub(_clean,NF))
