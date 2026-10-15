"""Draft weekly newsletter markdown. Usage: python3 newsletter.py [prev_tools.json]  -> newsletter/YYYY-MM-DD.md
Compares tools.json with a previous snapshot (default: snapshots/latest.json) to list changes, then snapshots current."""
import json,sys,os,datetime
D=json.load(open("tools.json"));today=datetime.date.today().isoformat()
prev_path=sys.argv[1] if len(sys.argv)>1 else "snapshots/latest.json"
P=json.load(open(prev_path)) if os.path.exists(prev_path) else {"tools":[]}
old={t["id"]:t for t in P["tools"]};new={t["id"]:t for t in D["tools"]}
since=(datetime.date.today()-datetime.timedelta(days=7)).isoformat()
md=[f"# Loadout Weekly — {today}\n","Your weekly AI loadout for vibe coders and builders.\n","## New releases this week\n"]
md+=[f"- **[{r['name']}]({r['url']})** ({r['date']}) — {r['summary']} ([source]({r['source']}))" for r in D["newReleases"] if r["date"]>=since] or ["- Nothing new this week."]
md.append("\n## Directory changes\n")
ch=[f"- Added **{new[i]['name']}** — {new[i]['description']}" for i in new if i not in old]
ch+=[f"- Removed **{old[i]['name']}**" for i in old if i not in new]
ch+=[f"- Updated **{new[i]['name']}**: "+", ".join(k for k in("name","description","pricing","url","bestFor") if new[i][k]!=old[i][k]) for i in new if i in old and any(new[i][k]!=old[i][k] for k in("name","description","pricing","url","bestFor"))]
md+=ch or ["- No changes."]
md+=["\n## Sponsor\n","_[Sponsored slot — contact us]_\n","---\nUnsubscribe link goes here once a newsletter provider is connected."]
os.makedirs("newsletter",exist_ok=True);os.makedirs("snapshots",exist_ok=True)
out=f"newsletter/{today}.md";open(out,"w").write("\n".join(md)+"\n");json.dump(D,open("snapshots/latest.json","w"));print(out)
