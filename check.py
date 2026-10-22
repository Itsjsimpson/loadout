"""Automated checks: python3 check.py [--no-external] [--live]. Exits 1 on failure.
--live (audit fix 4): fetch every sitemap <loc> and each page's canonical on production with redirects OFF;
each must return 200 directly (any 3xx/4xx/5xx fails), canonical must equal its sitemap URL, and
`git ls-remote origin main` must equal local HEAD. Nothing is "deployed" on the board until this passes."""
import json,os,re,sys,glob,subprocess,urllib.parse
from html.parser import HTMLParser
D=json.load(open("tools.json"));fails=[];warn=[]
VOID={"meta","link","br","img","input","hr","source","area","base","col","wbr"}
class P(HTMLParser):
    def __init__(s):super().__init__();s.st=[];s.links=[];s.err=[];s.h1=0;s.title=s.desc=s.canon=False
    def handle_starttag(s,t,a):
        a=dict(a)
        if t=="h1":s.h1+=1
        if t=="title":s.title=True
        if t=="meta" and a.get("name")=="description" and a.get("content"):s.desc=True
        if t=="link" and a.get("rel")=="canonical":s.canon=True
        if t in("a","link","script") and (a.get("href") or a.get("src")):s.links.append(a.get("href") or a.get("src"))
        if t not in VOID:s.st.append(t)
    def handle_endtag(s,t):
        if t in VOID:return
        if not s.st or s.st[-1]!=t:s.err.append(f"unexpected </{t}> (open: {s.st[-3:]})")
        else:s.st.pop()
pages=glob.glob("*.html")+glob.glob("*/*.html");pages.remove("index.tpl.html") if "index.tpl.html" in pages else None
for p in pages:
    h=open(p).read();x=P();x.feed(h)
    if not h.lower().startswith("<!doctype html>"):fails.append(f"{p}: no doctype")
    fails+= [f"{p}: {e}" for e in x.err]
    if x.st:fails.append(f"{p}: unclosed {x.st}")
    for k in("title","desc","canon"):
        if k=="canon" and p=="404.html":continue  # noindex error page: no canonical by design
        if not getattr(x,k):fails.append(f"{p}: missing {k}")
    if p=="404.html":
        if 'name="robots" content="noindex"' not in h:fails.append("404.html: missing noindex")
        if "<title>Page not found | Loadout</title>" not in h:fails.append("404.html: wrong title")
        if "404.html" in open("sitemap.xml").read() or "/404" in open("llms.txt").read():fails.append("404 page listed in sitemap.xml or llms.txt")
    if p!="index.html" and x.h1!=1:fails.append(f"{p}: {x.h1} h1")
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>',h,re.S):
        try:json.loads(m)
        except Exception as e:fails.append(f"{p}: bad JSON-LD {e}")
    for l in x.links:
        if l.startswith(("http","mailto:","#","${","data:","/_vercel")):continue
        lp=urllib.parse.urlparse(l).path
        if lp.endswith(".html"):fails.append(f"{p}: internal link {l} uses .html (production 308-redirects it; use the clean URL)")
        tgt=(os.path.normpath("."+lp) if lp.startswith("/") else os.path.normpath(os.path.join(os.path.dirname(p),lp))) if lp else p
        if lp=="/":tgt="."
        if lp.endswith("/") or lp in("","./","../"):tgt=os.path.join(tgt,"index.html")
        # Clean URLs (no .html) are served by Cloudflare Pages: accept x -> x.html and dir -> dir/index.html
        if not any(os.path.isfile(c) for c in (tgt,tgt+".html",os.path.join(tgt,"index.html"))):fails.append(f"{p}: broken link {l}")
for f in("sitemap.xml","robots.txt","llms.txt","llms-full.txt","tools.json"):
    if not os.path.exists(f):fails.append(f"missing {f}")
ids={t["id"] for t in D["tools"]}
for u in D["useCases"]:fails+=[f"useCase pick {p} unknown" for p in u["picks"] if p not in ids]
for t in D["tools"]:
    for k in("id","name","category","description","bestFor","pricing","url","affiliateUrl","verified"):
        if k not in t:fails.append(f"{t.get('id')}: missing field {k}")
if "--no-external" not in sys.argv:
    urls=[t["url"] for t in D["tools"]]+[r["url"] for r in D["newReleases"]]+[r["source"] for r in D["newReleases"]]
    for u in urls:
        c=subprocess.run(["curl","-sL","-o","/dev/null","-m","20","-A","Mozilla/5.0 (X11; Linux x86_64) Chrome/120","-w","%{http_code}",u],capture_output=True,text=True).stdout
        if c in("403","429","503"):warn.append(f"{u}: {c} (likely bot protection)")
        elif not c.startswith(("2","3")):fails.append(f"{u}: HTTP {c}")
if "--live" in sys.argv:
    from concurrent.futures import ThreadPoolExecutor
    locs=re.findall(r"<loc>([^<]+)</loc>",open("sitemap.xml").read())
    UA="Mozilla/5.0 (X11; Linux x86_64) Chrome/120"
    def get(u):
        r=subprocess.run(["curl","-sS","-m","20","-A",UA,"-o","-","-w","\n%{http_code} %{redirect_url}",u],capture_output=True,text=True)
        body,_,tail=r.stdout.rpartition("\n");code,_,loc=tail.partition(" ")
        return code,loc.strip(),body,r.stderr.strip()
    def live(u):
        out=[];code,loc,body,err=get(u)
        if code!="200":out.append(f"LIVE {u}: HTTP {code or 'no response'}{' -> '+loc if loc else ''}{' '+err if err else ''}");return out
        m=re.search(r'<link rel="canonical" href="([^"]+)"',body)
        if not m:out.append(f"LIVE {u}: no canonical");return out
        c=m.group(1)
        if c!=u:
            out.append(f"LIVE {u}: canonical is {c} (not the sitemap URL)")
            cc,cl,_,_=get(c)
            if cc!="200":out.append(f"LIVE canonical {c}: HTTP {cc}{' -> '+cl if cl else ''}")
        for h in re.findall(r'href="([^"]+)"',body):
            if not h.startswith(("http","mailto:","#","data:","//")) and urllib.parse.urlparse(h).path.endswith(".html"):
                out.append(f"LIVE {u}: internal link {h} uses .html (redirects)");break
        return out
    with ThreadPoolExecutor(8) as ex:
        for r in ex.map(live,locs):fails+=r
    # Soft-404 guard: a random missing path must return a real 404 (not the homepage with 200).
    import uuid
    nf=f"https://loadoutweekly.com/this-page-does-not-exist-{uuid.uuid4().hex[:10]}"
    code,loc,body,err=get(nf)
    if code!="404":fails.append(f"LIVE {nf}: HTTP {code}{' -> '+loc if loc else ''} (expected 404; soft-404?)")
    elif "<title>Page not found | Loadout</title>" not in body:fails.append(f"LIVE {nf}: 404 but not the Loadout not-found page")
    else:print(f"LIVE 404 OK: {nf}")
    try:
        remote=subprocess.run(["git","ls-remote","origin","main"],capture_output=True,text=True,timeout=30).stdout.split()
        head=subprocess.run(["git","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
        if not remote:fails.append("LIVE git ls-remote origin main returned nothing (push unverified)")
        elif remote[0]!=head:fails.append(f"LIVE origin/main {remote[0][:7]} != local HEAD {head[:7]} (local work not on main, or push didn't land)")
        else:print(f"LIVE origin/main == HEAD {head[:7]}")
    except Exception as e:fails.append(f"LIVE git check failed: {e}")
    print(f"LIVE: {len(locs)} sitemap URLs fetched with redirects off")
print(f"{len(pages)} pages checked");[print("WARN",w) for w in warn];[print("FAIL",f) for f in fails]
print("PASS" if not fails else f"{len(fails)} failures");sys.exit(1 if fails else 0)
