"""IndexNow ping for loadoutweekly.com (AI-search cleanup, 2026-10-23). Docs: https://www.indexnow.org/documentation
Default is a DRY RUN: prints the payload and the curl command, sends nothing.
  python3 indexnow.py           # dry run
  python3 indexnow.py --send    # only after the PR is merged AND check.py --live passes on main (re-checked here first)
The key is public by design: the key file /<KEY>.txt sits at the site root and must contain exactly the key."""
import json,re,subprocess,sys,urllib.request
KEY="d0a1f2fcfe3b5c756dde5aa5e6742ac3"
HOST="loadoutweekly.com";KEY_URL=f"https://{HOST}/{KEY}.txt";ENDPOINT="https://api.indexnow.org/indexnow"
urls=re.findall(r"<loc>([^<]+)</loc>",open("sitemap.xml").read())
payload={"host":HOST,"key":KEY,"keyLocation":KEY_URL,"urlList":urls}
if "--payload" in sys.argv:print(json.dumps(payload));sys.exit(0)
if "--send" not in sys.argv:
    print(json.dumps(payload,indent=1));print(f"\n{len(urls)} URLs. DRY RUN, nothing sent. To send (re-checks key file + check.py --live first):\n  python3 indexnow.py --send")
    sys.exit(0)
if open(f"{KEY}.txt").read().strip()!=KEY:sys.exit("key file content mismatch")
live=urllib.request.urlopen(KEY_URL,timeout=20).read().decode().strip()
if live!=KEY:sys.exit(f"live key file {KEY_URL} does not contain the key")
if subprocess.run([sys.executable,"check.py","--live","--no-external"]).returncode:sys.exit("check.py --live failed: not pinging")
req=urllib.request.Request(ENDPOINT,data=json.dumps(payload).encode(),headers={"Content-Type":"application/json; charset=utf-8"},method="POST")
with urllib.request.urlopen(req,timeout=30) as r:print("IndexNow HTTP",r.status,"(200 = received, 202 = key validation pending)")
