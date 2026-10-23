"""Search / AI-crawl helpers (AI-search cleanup, 2026-10-23).
Page dates come from git history, never invented: a page's date is the commit date of the last commit that
changed its visible main text. Navigation-only blocks (pagemeta, relnav, newsletter card) are ignored, so a
site-wide nav tweak doesn't mark every page as updated. A page whose text differs from HEAD (an uncommitted
change about to ship) gets today's date, the day it's being committed."""
import re,html,hashlib,subprocess,datetime
def content_key(h):
    m=re.search(r'<main\b[^>]*>(.*)</main>',h,re.S);s=m.group(1) if m else h
    s=re.sub(r'<div class="pagemeta">.*?</div><!--/pagemeta-->','',s,flags=re.S)
    s=re.sub(r'<nav class="relnav.*?</nav><!--/relnav-->','',s,flags=re.S)
    s=re.sub(r'<aside\b.*?</aside>',lambda m:'' if 'nlcard' in m.group(0) or 'beehiiv.com' in m.group(0) else m.group(0),s,flags=re.S)  # newsletter CTAs
    s=re.sub(r'<(script|style)\b.*?</\1>','',s,flags=re.S)
    s=html.unescape(re.sub(r'<[^>]+>',' ',s))
    return hashlib.sha1(" ".join(s.split()).encode()).hexdigest()
def _git(*a,inp=None):
    return subprocess.run(["git",*a],input=inp,capture_output=True,text=True).stdout
def page_dates(paths,today,fallback):
    """{path: YYYY-MM-DD} from git history of each built file (see module doc)."""
    out={p:fallback for p in paths}
    try:
        if _git("rev-parse","--is-inside-work-tree").strip()!="true" or _git("rev-parse","--is-shallow-repository").strip()=="true":return out
        hist={};sha=None;date=None
        for line in _git("log","--format=C %H %cI","--name-only","--",*paths).splitlines():
            if line.startswith("C "):_,sha,date=line.split(" ");continue
            if line in out:hist.setdefault(line,[]).append((sha,date[:10]))
        specs=[f"{s}:{p}" for p,v in hist.items() for s,_ in v]
        raw=subprocess.run(["git","cat-file","--batch"],input=("\n".join(specs)+"\n").encode(),capture_output=True).stdout
        blobs={};i=0
        for spec in specs:
            nl=raw.index(b"\n",i);hdr=raw[i:nl].split()
            if hdr[-1]==b"missing":blobs[spec]=None;i=nl+1;continue
            n=int(hdr[2]);blobs[spec]=raw[nl+1:nl+1+n].decode("utf-8","replace");i=nl+1+n+1
        for p in paths:
            cur=content_key(open(p).read());d=today
            for s,dt in hist.get(p,[]):  # newest first
                b=blobs.get(f"{s}:{p}")
                if b is None or content_key(b)!=cur:break
                d=dt
            out[p]=d
    except Exception as e:print("WARN page_dates fallback:",e)
    return out
def human(d):return datetime.date.fromisoformat(d).strftime("%b %-d, %Y")
