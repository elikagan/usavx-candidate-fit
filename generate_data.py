#!/usr/bin/env python3
"""Build candidates.json — per-ROLE rankings. Each candidate is scored against
the rubric for the job they applied to (see score.py). Pulls live from Airtable
if AIRTABLE_TOKEN is set, else falls back to local candidates_raw.json.

New applicants (not yet in score.py) are emitted unscored as "needs review"."""
import json, re, os, urllib.request
from score import C, RUBRICS, ROLE_RUBRIC

BASE = "app3Xl5G65tJGxKGQ"
TABLE = "tblUzb0LiqEpfVS33"
SEG_TABLE = "tbln455HEK0nvZPue"   # Roles / Segments (job descriptions)

def airtable(table):
    tok = os.environ["AIRTABLE_TOKEN"]
    recs, offset = [], None
    while True:
        url = f"https://api.airtable.com/v0/{BASE}/{table}?pageSize=100" + (f"&offset={offset}" if offset else "")
        d = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"})))
        recs += d["records"]; offset = d.get("offset")
        if not offset: break
    return recs

def load_raw():
    if os.environ.get("AIRTABLE_TOKEN"):
        recs = airtable(TABLE)
        json.dump({"records": recs}, open("candidates_raw.json", "w"))
        # also cache role JDs/meta
        segs = {}
        for r in airtable(SEG_TABLE):
            f = r["fields"]; nm = f.get("Role Name")
            if nm: segs[nm] = {"jd": f.get("Job Description",""), "seniority": f.get("Seniority Level",""), "status": f.get("Status","")}
        json.dump(segs, open("roles_raw.json", "w"))
        return recs
    return json.load(open("candidates_raw.json"))["records"]

raw = load_raw()
try: ROLE_META = json.load(open("roles_raw.json"))
except Exception: ROLE_META = {}
def field(f, k):
    v = f.get(k, "")
    if isinstance(v, dict): v = v.get("value", "")
    return v or ""
def norm(s): return re.sub(r"\s+", " ", (s or "").strip().lower())

by_name, roles_by_name = {}, {}
for r in raw:
    f = r["fields"]; nm = norm(f.get("Name", ""))
    if not nm: continue
    w = len(field(f, "About Me")) + len(field(f, "Resume Summary"))
    if nm not in by_name or w > by_name[nm][1]:
        by_name[nm] = (f, w)
    for rl in (f.get("Role Name (from Roles)") or []):
        roles_by_name.setdefault(nm, [])
        if rl not in roles_by_name[nm]: roles_by_name[nm].append(rl)

def match_key(name):
    n = norm(name); toks = set(n.split())
    if n in by_name: return n
    for k in by_name:
        kt = set(k.split())
        if toks <= kt or kt <= toks: return k
        nl, kl = n.split(), k.split()
        if nl and kl and nl[0]==kl[0] and nl[-1]==kl[-1]: return k
    return None

def total(cand):
    return round(sum(cand["c"][k]/5*w for k,_,w in RUBRICS[cand["rubric"]]), 1)

def rec(score):
    if score>=80: return ("Strong interview","strong")
    if score>=65: return ("Interview","interview")
    if score>=50: return ("Maybe","maybe")
    return ("Hold","hold")

# tailored intro email for the strongest candidate(s); first-name keyed
EMAILS = {
 "Leon Aillaud Chavez": ("Leon","your 3D-printed aircraft and in-house fixture work",
   "What stood out to us was that you built inspection fixtures on your own 3D printer until the value was proven — that build-it-and-show-it instinct is exactly how we operate. Your CADIS aircraft project and ROV/FEA work line up closely with the flight hardware we prototype."),
 "Yixin Zhou": ("Yixin","your Formula SAE powertrain work",
   "Your Formula SAE powertrain work — pairing hand calculations with FEA and then actually fabricating the parts — is the exact loop our junior engineers run every week. Olin's hands-on reputation and your CNC/3D-printing experience are a strong match."),
 "Jackson Martin": ("Jackson","your autonomous drone and quadcopter biplane work",
   "You're the rare candidate whose hands-on work is literally UAVs — autonomous drone software with Dr. Machuca and a quadcopter biplane you built end to end. That's directly on-mission for our airframe team."),
 "Sofia Valdez Lau": ("Sofia","leading your university racing team",
   "Running a competitive racing team — designing and optimizing components, then troubleshooting them in real time under pressure — maps almost exactly onto our prototype-and-test cycle. Your advanced SolidWorks work and ownership mindset are what we look for."),
 "Diego Mendoza Madrid": ("Diego","your fixture and tooling work at Össur",
   "Your work at Össur — precision fixtures, tooling, parametric test setups, GD&T, and a revalidation that measurably cut scrap — shows the careful, hands-on mechanical design we rely on."),
 "Vania Leal Espinoza": ("Vania","your embedded and rocketry electronics work",
   "Your embedded systems background — Linux, sensor and vision integration, and leading electronics for a rocketry team — is almost a one-to-one match for bringing up and testing our Delta AI hardware. This role is hands-on bench work, exactly where you've thrived."),
 "Jonayet Lavin": ("Jonayet","your ML engineering and GenAI startup work",
   "Your ML engineering depth — PyTorch, RAG, fine-tuning, and co-founding a GenAI platform as backend lead — lines up closely with the onboard AI agents we're building. We'd love to talk about edge inference and real-time autonomy with you."),
 "Lauren Hagen": ("Lauren","your operations and organizational leadership",
   "Running large campus organizations, managing budgets, and keeping complex logistics on track is exactly the operational backbone we need as we scale. Your organization and communication strengths fit this role closely."),
 "Camila Lewis": ("Camila","your marketing and event-coordination work",
   "Your marketing strategy, content, and event-coordination experience map directly onto the Strategic Projects role — helping leadership keep initiatives, marketing, and communications organized in a fast-moving startup."),
}
def email_for(name):
    if name not in EMAILS: return None
    first, hook, body = EMAILS[name]
    return {"to_first": first,
      "subject": "USAVX — we were impressed by your application",
      "body": (f"Hi {first},\n\nI'm reaching out from USAVX — we design autonomous unmanned aircraft systems, and your "
        f"application stood out while we were reviewing candidates.\n\n{body}\n\nWould you be open to a short call this "
        f"week or next so we can tell you more about the role and hear what you're looking for?\n\nBest,\n[Your name]\nUSAVX")}

out = []
scored_keys = set()
for r in C:
    mk = match_key(r["name"]); scored_keys.add(mk)
    f = by_name.get(mk, ({},0))[0] if mk else {}
    sc = total(r); label, key = rec(sc)
    out.append({
      "name": r["name"], "school": r["school"], "score": sc,
      "confidence": {"H":"High","M":"Medium","L":"Low"}[r["conf"]],
      "rubric": r["rubric"], "rec": label, "recKey": key,
      "roles": roles_by_name.get(mk, []) if mk else [],
      "categories": [{"label":lbl,"score":r["c"][k],"weight":w} for k,lbl,w in RUBRICS[r["rubric"]]],
      "note": r["note"], "email": field(f,"Email"), "linkedin": f.get("LinkedIn",""),
      "about": field(f,"About Me"), "summary": field(f,"Resume Summary"),
      "intro_email": email_for(r["name"]),
    })

new_count = 0
for nm,(f,_) in by_name.items():
    if nm in scored_keys: continue
    new_count += 1
    out.append({
      "name": f.get("Name",""), "school": "", "score": None, "confidence": "—",
      "rubric": None, "rec": "New", "recKey": "new",
      "roles": roles_by_name.get(nm, []),
      "categories": [], "note": "New application — not yet reviewed.",
      "email": field(f,"Email"), "linkedin": f.get("LinkedIn",""),
      "about": field(f,"About Me"), "summary": field(f,"Resume Summary"), "intro_email": None,
    })

# role catalogue (for the page's role picker) — every role that has candidates
role_counts = {}
for c in out:
    for rl in c["roles"]: role_counts[rl] = role_counts.get(rl,0)+1

# role detail (JD + seniority) for each role that has candidates
role_info = {}
for rl in role_counts:
    m = ROLE_META.get(rl, {})
    role_info[rl] = {"count": role_counts[rl], "jd": m.get("jd",""), "seniority": m.get("seniority","")}

json.dump({"candidates": out, "rubrics": RUBRICS, "roles": role_counts,
           "role_info": role_info, "new_count": new_count},
          open("candidates.json","w"), indent=1, ensure_ascii=False)
print(f"Wrote candidates.json — {len(out)} candidates across {len(role_counts)} roles ({new_count} new)")
for rl,n in sorted(role_counts.items(), key=lambda x:-x[1]): print(f"  {n:2}  {rl}")
