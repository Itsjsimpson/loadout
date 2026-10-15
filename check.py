"""Automated checks: python3 check.py [--no-external]. Exits 1 on failure."""
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
        if not getattr(x,k):fails.append(f"{p}: missing {k}")
    if p!="index.html" and x.h1!=1:fails.append(f"{p}: {x.h1} h1")
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>',h,re.S):
        try:json.loads(m)
        except Exception as e:fails.append(f"{p}: bad JSON-LD {e}")
    for l in x.links:
        if l.startswith(("http","mailto:","#","${","data:")):continue
        tgt=os.path.normpath(os.path.join(os.path.dirname(p),urllib.parse.urlparse(l).path))
        if not os.path.exists(tgt):fails.append(f"{p}: broken link {l}")
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
print(f"{len(pages)} pages checked");[print("WARN",w) for w in warn];[print("FAIL",f) for f in fails]
print("PASS" if not fails else f"{len(fails)} failures");sys.exit(1 if fails else 0)
