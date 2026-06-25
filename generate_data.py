#!/usr/bin/env python3
"""Build candidates.json. Pulls LIVE from Airtable if AIRTABLE_TOKEN is set
(GitHub Action), else falls back to local candidates_raw.json.

Candidates already rated in score.py keep their careful, hand-authored scores.
Anyone new in Airtable is emitted as tier 0 = "New - needs review" (unscored),
so new applicants surface immediately without faking a score."""
import json, re, os, urllib.request
from score import C, WEIGHTS

BASE = "app3Xl5G65tJGxKGQ"
TABLE = "tblUzb0LiqEpfVS33"

def load_raw():
    tok = os.environ.get("AIRTABLE_TOKEN")
    if tok:
        recs, offset = [], None
        while True:
            url = f"https://api.airtable.com/v0/{BASE}/{TABLE}?pageSize=100" + (f"&offset={offset}" if offset else "")
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {tok}"})
            d = json.load(urllib.request.urlopen(req))
            recs += d["records"]
            offset = d.get("offset")
            if not offset: break
        json.dump({"records": recs}, open("candidates_raw.json", "w"))  # cache
        return recs
    return json.load(open("candidates_raw.json"))["records"]

raw = load_raw()

def field(f, k):
    v = f.get(k, "")
    if isinstance(v, dict): v = v.get("value", "")
    return v or ""
def norm(s): return re.sub(r"\s+", " ", (s or "").strip().lower())

# richest record per unique person (dedupe; prefer one with most text)
# also collect ALL roles a person is linked to across their records
by_name = {}
roles_by_name = {}
for r in raw:
    f = r["fields"]
    nm = norm(f.get("Name", ""))
    if not nm: continue
    weight = len(field(f, "About Me")) + len(field(f, "Resume Summary"))
    if nm not in by_name or weight > by_name[nm][1]:
        by_name[nm] = (f, weight)
    for rl in (f.get("Role Name (from Roles)") or []):
        roles_by_name.setdefault(nm, [])
        if rl not in roles_by_name[nm]:
            roles_by_name[nm].append(rl)

def match_key(name):
    """Find the raw record key for a scored name, tolerating middle names."""
    n = norm(name); toks = set(n.split())
    if n in by_name: return n
    best = None
    for k in by_name:
        kt = set(k.split())
        if toks <= kt or kt <= toks:  # one name is subset of the other
            best = k; break
        # else require first + last token both present
        nl = n.split(); kl = k.split()
        if nl and kl and nl[0]==kl[0] and nl[-1]==kl[-1]:
            best = k; break
    return best

scored_keys = {}
for c in C:
    mk = match_key(c["name"])
    if mk: scored_keys[mk] = c["name"]

def total(c): return round(sum(c[k]/5*WEIGHTS[k] for k in WEIGHTS), 1)

T1 = {"Leon Aillaud Chavez","Yixin Zhou","Jackson Martin","Sofia Valdez Lau","Diego Mendoza Madrid"}
OTHER_ROLE = {"Jonayet Lavin","Felipe Fluck","Lauren Hagen","Camila Lewis"}  # applied to non-hardware reqs
def tier(name, sc):
    if name in OTHER_ROLE: return 5   # "Other roles" — not ranked vs hardware rubric
    if name in T1: return 1
    return 2 if sc >= 64 else 3

EMAILS = {
 "Leon Aillaud Chavez": ("Leon", "your 3D-printed aircraft and in-house fixture work",
   "What stood out to us was that you built inspection fixtures on your own 3D printer until the value was proven — that build-it-and-show-it instinct is exactly how we operate. Your CADIS aircraft project and ROV/FEA work line up closely with the flight hardware we prototype."),
 "Yixin Zhou": ("Yixin", "your Formula SAE powertrain work",
   "Your Formula SAE powertrain work — pairing hand calculations with FEA and then actually fabricating the parts — is the exact loop our junior engineers run every week. Olin's hands-on engineering reputation and your CNC/3D-printing experience are a strong match for how we build."),
 "Jackson Martin": ("Jackson", "your autonomous drone and quadcopter biplane work",
   "You're the rare candidate whose hands-on work is literally UAVs — autonomous drone software with Dr. Machuca and a quadcopter biplane you built end to end. That's directly on-mission for what we're developing, and your team-leadership experience is a bonus."),
 "Sofia Valdez Lau": ("Sofia", "leading your university racing team",
   "Running a competitive racing team — designing and optimizing components, then troubleshooting them in real time under pressure — maps almost exactly onto our prototype-and-test cycle. Your advanced SolidWorks work and ownership mindset are what we look for."),
 "Diego Mendoza Madrid": ("Diego", "your fixture and tooling work at Össur",
   "Your work at Össur — precision fixtures, tooling, parametric test setups, GD&T, and a process revalidation that measurably cut scrap — shows the kind of careful, hands-on mechanical design we rely on. We think you'd ramp quickly on our prototype hardware."),
}
def email_for(name):
    if name not in EMAILS: return None
    first, hook, body = EMAILS[name]
    return {"to_first": first,
      "subject": "USAVX — junior engineering role (we were impressed by your work)",
      "body": (f"Hi {first},\n\nI'm reaching out from USAVX — we design unmanned aircraft systems and autonomy "
        f"technology, and we came across your profile while hiring for a junior engineering role on our small hardware team.\n\n"
        f"{body}\n\nThe role is hands-on: CAD modeling, prototype fabrication, assembly and testing, and working directly "
        f"with our senior engineers across several early-stage projects. It's the kind of build–test–iterate environment "
        f"where {hook} would translate directly.\n\nWould you be open to a short call this week or next to tell you more and "
        f"hear about what you're looking for?\n\nBest,\n[Your name]\nUSAVX")}

CATLABELS = [("Fabrication","Fabrication & Prototyping"),("CAD","CAD Proficiency"),
  ("MechDesign","Mechanical Design"),("Domain","Domain (UAV/robotics/SAE)"),
  ("Initiative","Initiative"),("English","English"),("Electronics","Electronics Integration")]

out = []

# 1) scored candidates (hand-authored ratings)
for r in sorted(C, key=lambda x: total(x["c"]), reverse=True):
    mk = match_key(r["name"])
    f = by_name.get(mk, ({},0))[0] if mk else {}
    c = r["c"]
    out.append({
      "name": r["name"], "school": r["school"], "score": total(c),
      "confidence": {"H":"High","M":"Medium","L":"Low"}[r["conf"]],
      "tier": tier(r["name"], total(c)),
      "roles": roles_by_name.get(mk, []) if mk else [],
      "categories": [{"key":k,"label":lbl,"score":c[k],"weight":WEIGHTS[k]} for k,lbl in CATLABELS],
      "note": r["note"], "email": field(f,"Email"), "linkedin": f.get("LinkedIn",""),
      "about": field(f,"About Me"), "summary": field(f,"Resume Summary"),
      "intro_email": email_for(r["name"]),
    })

# 2) NEW candidates in Airtable not yet scored -> tier 0, needs review
new_count = 0
for nm,(f,_) in by_name.items():
    if nm in scored_keys: continue
    new_count += 1
    out.append({
      "name": f.get("Name",""), "school": field(f,"Resume-Role Relevance Category") or "",
      "score": None, "confidence": "—", "tier": 0,
      "roles": roles_by_name.get(nm, []),
      "categories": [], "note": "New application — not yet reviewed.",
      "email": field(f,"Email"), "linkedin": f.get("LinkedIn",""),
      "about": field(f,"About Me"), "summary": field(f,"Resume Summary"), "intro_email": None,
    })

json.dump({"candidates": out, "weights": WEIGHTS, "new_count": new_count},
          open("candidates.json","w"), indent=1, ensure_ascii=False)
print(f"Wrote candidates.json — {len(out)} total ({new_count} new, unscored)")
