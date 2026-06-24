#!/usr/bin/env python3
"""USAVX junior engineer candidate scoring — reproducible & re-weightable.
Ratings are 0-5 per category, grounded in resume-summary + About-Me evidence.
Change WEIGHTS and re-run to see ranking shift instantly."""

# Category weights (must sum to 100). Tuned to the JD: hands-on building is the core
# of this role; credentials are deliberately NOT a category.
WEIGHTS = {
    "CAD":          18,   # CAD modeling proficiency (SolidWorks/Fusion/Creo/ANSYS)
    "Fabrication":  22,   # hands-on building: 3D printing, CNC, machining, prototyping
    "MechDesign":   15,   # mechanical design aptitude / FEA / GD&T / tolerancing
    "Domain":       15,   # robotics / UAV / aero / automotive / Baja / FSAE experience
    "Electronics":   8,   # electronics + mechanical integration
    "Initiative":   12,   # self-directed learning, ownership, building things unprompted
    "English":      10,   # English communication evidence
}

# conf: H/M/L = how much evidence backs the scores (resume present, About Me depth)
# c = dict of category->0-5 ; school ; flag notes
C = [
 dict(name="Leon Aillaud Chavez", school="CETYS Mexicali", conf="H",
   c=dict(CAD=5,Fabrication=5,MechDesign=5,Domain=5,Electronics=3,Initiative=5,English=5),
   note="Built inspection fixtures on his OWN 3D printer until employer saw value & bought one; co-founded CADIS; CSU 3D-printed fixed-wing aircraft comp (empennage); MATE ROV submarine + ANSYS FEA. Textbook fit."),
 dict(name="Yixin Zhou", school="Olin College", conf="H",
   c=dict(CAD=5,Fabrication=5,MechDesign=5,Domain=5,Electronics=3,Initiative=4,English=5),
   note="Formula SAE powertrain — hand calcs + FEA, CAD, 3D printing, CNC. Olin = elite hands-on program. Native-level English."),
 dict(name="Jackson Martin", school="San Diego State", conf="M",
   c=dict(CAD=4,Fabrication=4,MechDesign=4,Domain=5,Electronics=4,Initiative=5,English=5),
   note="Autonomous-drone software w/ Dr. Machuca; built a quadcopter biplane senior project (direct UAV); CAD internship; led 8-person team. Strongest pure-UAV signal in the pool."),
 dict(name="Sofia Valdez Lau", school="CETYS", conf="M",
   c=dict(CAD=5,Fabrication=4,MechDesign=5,Domain=4,Electronics=2,Initiative=5,English=4),
   note="President of university racing team (automotive/SAE-adjacent); advanced parametric SolidWorks; real-time troubleshooting under pressure; manufacturing internship."),
 dict(name="Diego Mendoza Madrid", school="CETYS", conf="H",
   c=dict(CAD=5,Fabrication=4,MechDesign=5,Domain=2,Electronics=3,Initiative=5,English=4),
   note="Össur internship: precision fixtures, tooling, parametric test setups in SolidWorks; CNC + laser cutting; GD&T; Manufacturing Team Lead. Strong hardware, no UAV/SAE."),
 dict(name="Antonio Quezada Figueroa", school="CETYS Tijuana", conf="M",
   c=dict(CAD=4,Fabrication=3,MechDesign=4,Domain=5,Electronics=2,Initiative=5,English=4),
   note="Led the only Mexican team at CSULA 3D-printed aircraft comp; president of student eng group; JAE automotive internship (injection molding). Aero passion + leadership; only 6th semester."),
 dict(name="Roberto Monroy Amador", school="CETYS", conf="H",
   c=dict(CAD=4,Fabrication=4,MechDesign=4,Domain=1,Electronics=2,Initiative=5,English=5),
   note="~1yr pro manufacturing eng: led plant transfer & global standardization; fixture design; Lean/Six Sigma. Strong but more PROCESS/manufacturing than rapid prototyping. No robotics/UAV/SAE."),
 dict(name="Leila Sigala", school="CETYS", conf="M",
   c=dict(CAD=4,Fabrication=3,MechDesign=4,Domain=3,Electronics=2,Initiative=4,English=5),
   note="ME w/ explicit aerospace interest; SolidWorks/Inventor/AutoCAD, CNC machining, automation. Domain evidence is mostly coursework + a furniture-design project lead. Excellent English."),
 dict(name="Jake Rufino", school="UT Tijuana", conf="M",
   c=dict(CAD=4,Fabrication=4,MechDesign=4,Domain=2,Electronics=3,Initiative=4,English=2),
   note="~2.5yr mechanical design + automation; SolidWorks, FEA, PLC; fixture/tooling; supervised interns. RED FLAG: resume summary explicitly notes ENGLISH IS INTERMEDIATE — verify."),
 dict(name="Vania Leal Espinoza", school="CETYS", conf="M",
   c=dict(CAD=2,Fabrication=3,MechDesign=2,Domain=4,Electronics=5,Initiative=5,English=4),
   note="Electronics lead for university rocketry team; embedded/robotics/vision; hackathons; taught robotics. Excellent for electronics integration, light on CAD/mechanical."),
 dict(name="Daniel Lopez Moreno", school="CETYS", conf="M",
   c=dict(CAD=3,Fabrication=3,MechDesign=3,Domain=3,Electronics=4,Initiative=4,English=3),
   note="Mechatronics student; built a robotic car and a robotic arm; basic CNC/lathe/milling + PLC. Early but genuine hands-on trajectory."),
 dict(name="Melanie Picen", school="CETYS", conf="M",
   c=dict(CAD=2,Fabrication=2,MechDesign=2,Domain=3,Electronics=5,Initiative=5,English=3),
   note="Cybernetics: FPGA/Verilog, embedded, ML. Strong electronics + initiative, but little CAD/fabrication evidence. Discipline tilts away from this role's core."),
 dict(name="Alfonso Gonzalez Villalobos", school="CETYS", conf="L",
   c=dict(CAD=3,Fabrication=3,MechDesign=3,Domain=2,Electronics=2,Initiative=3,English=3),
   note="ME w/ SolidWorks/AutoCAD + process-improvement internship. Generic mid profile; NO 'About Me' so motivation/English are unverified."),
 dict(name="Kevin Osorio Franco", school="CETYS", conf="L",
   c=dict(CAD=2,Fabrication=2,MechDesign=2,Domain=3,Electronics=4,Initiative=3,English=3),
   note="RESUME MISSING (no summary in Airtable). About Me shows AOI/ABB robotics, STM32, PLC. Tagged 'Not Relevant'. Cannot assess until resume obtained."),
 dict(name="Diego Romero Bassoco", school="CETYS", conf="L",
   c=dict(CAD=3,Fabrication=2,MechDesign=3,Domain=2,Electronics=2,Initiative=3,English=2),
   note="Last-year ME, CNC operator, ANSYS. Very thin/generic record and a one-line About Me with weak written English. Eager but unproven."),
 dict(name="Esau Colloy Alvarez", school="CETYS Tijuana", conf="L",
   c=dict(CAD=3,Fabrication=2,MechDesign=2,Domain=1,Electronics=2,Initiative=3,English=3),
   note="CAD-assistant / technical-drawing background (AutoCAD/Revit/SolidWorks). Best fit for the eng-documentation slice, not fabrication. No LinkedIn."),
 dict(name="Marco Rangel", school="CETYS", conf="L",
   c=dict(CAD=2,Fabrication=2,MechDesign=2,Domain=1,Electronics=1,Initiative=3,English=5),
   note="ME grad met at job fair; 3D printing; quad-lingual (En/Es/It/basic German); production-supervision internship. Thin technical depth; strong communicator."),
 # --- domain mismatch: capable but not a mechanical/CAD/fab fit ---
 dict(name="Jonayet Lavin", school="Caltech", conf="H",
   c=dict(CAD=0,Fabrication=1,MechDesign=0,Domain=1,Electronics=2,Initiative=5,English=5),
   note="MISMATCH: ML/software engineer, co-founded a GenAI startup. Exceptional — but no mechanical/CAD/fabrication. Redirect to a software/autonomy req, not this hardware role."),
 dict(name="Felipe Fluck", school="ORT Argentina", conf="H",
   c=dict(CAD=0,Fabrication=1,MechDesign=0,Domain=1,Electronics=2,Initiative=4,English=5),
   note="MISMATCH: full-stack / Web3 software developer. Capable, wrong discipline for a CAD/fab role. Redirect to software."),
 dict(name="Camila Lewis", school="CETYS", conf="H",
   c=dict(CAD=0,Fabrication=0,MechDesign=0,Domain=0,Electronics=0,Initiative=3,English=4),
   note="WRONG FIELD: marketing student (social media, Canva, branding). 'Highly Relevant' tag is mis-set. Not an engineering candidate."),
 dict(name="Lauren Hagen", school="San Diego State", conf="H",
   c=dict(CAD=0,Fabrication=0,MechDesign=0,Domain=1,Electronics=0,Initiative=5,English=5),
   note="WRONG FIELD for this role: B.S. Business Admin / Management. Strong operations & leadership — possible ops/PM fit elsewhere, not mechanical engineering."),
]

def score(cat):
    return round(sum(cat[k]/5*WEIGHTS[k] for k in WEIGHTS), 1)

ranked = sorted(C, key=lambda x: score(x["c"]), reverse=True)
print(f"{'#':>2}  {'Score':>5}  {'Cf':>2}  {'Name':28}  {'School':16}")
print("-"*95)
for i,r in enumerate(ranked,1):
    print(f"{i:>2}  {score(r['c']):>5}  {r['conf']:>2}  {r['name']:28}  {r['school']:16}")

import csv
with open("scores.csv","w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["Rank","Name","School","Confidence","Weighted"]+list(WEIGHTS))
    for i,r in enumerate(ranked,1):
        w.writerow([i,r["name"],r["school"],r["conf"],score(r["c"])]+[r["c"][k] for k in WEIGHTS])
print("\nWrote scores.csv")
