#!/usr/bin/env python3
"""Per-ROLE candidate scoring. Each candidate is judged against the rubric for
the job THEY applied to — a hardware rubric for airframe roles, an embedded
rubric for the embedded intern, an ML rubric for AI Engineer, etc.

Credentials/GPA are never a dimension — demonstrated capability is.
Scores are hand-authored 0-5, grounded in resume + the role's real JD."""

# ---- Rubrics: dimension key -> (label, weight). Weights sum to 100 per rubric. ----
RUBRICS = {
 "hardware": [   # Mechanical Eng Intern + Aerospace Mechanical Engineer
   ("Fabrication","Fabrication & Prototyping",22),
   ("CAD","CAD Proficiency",18),
   ("MechDesign","Mechanical Design",15),
   ("Domain","Domain (UAV / robotics / SAE)",15),
   ("Initiative","Initiative",12),
   ("English","English",10),
   ("Electronics","Electronics Integration",8)],
 "embedded": [   # Hardware / Embedded Systems Intern – AI Test & Integration
   ("Bringup","HW/Embedded Bring-up (RPi, sensors, MCU)",25),
   ("Electronics","Electronics & Integration",18),
   ("Software","Software / Linux / Python",15),
   ("Testing","Test & Debug",15),
   ("Initiative","Initiative",12),
   ("English","English & Documentation",15)],
 "ai": [         # AI Engineer – Edge Autonomy (LLM)
   ("ML","ML / LLM depth (PyTorch, RAG, fine-tuning)",30),
   ("SWE","Software Engineering / Production",20),
   ("Edge","Edge / Real-time Systems",15),
   ("Initiative","Initiative / Research-to-product",15),
   ("Domain","Autonomy / Robotics domain",10),
   ("English","Communication",10)],
 "strategic": [  # Strategic Projects Intern
   ("Org","Project Coordination & Organization",25),
   ("Comms","Communication & Writing",20),
   ("Initiative","Initiative / Ownership",20),
   ("Marketing","Marketing & Comms Support",15),
   ("Range","Adaptability / Generalist Range",10),
   ("English","English",10)],
 "ops": [        # Operations Intern
   ("OpsLog","Operations / Logistics / Supply Chain",25),
   ("Org","Organization & Time Management",20),
   ("Tools","Spreadsheets / Scheduling / Automation",15),
   ("Comms","Communication",15),
   ("Initiative","Self-starter / Initiative",15),
   ("English","English",10)],
}

# Airtable role name -> rubric key
ROLE_RUBRIC = {
 "Mechanical Engineering Intern – Prototyping & Test Systems": "hardware",
 "Aerospace Mechanical Engineer": "hardware",
 "Hardware / Embedded Systems Intern – AI Test & Integration": "embedded",
 "AI Engineer": "ai",
 "Strategic Projects Intern": "strategic",
 "Operations Intern": "ops",
}

# ---- Candidates: scored on the rubric for their applied role ----
C = [
 # ===== HARDWARE (Mechanical Eng Intern + Aerospace Mechanical Engineer) =====
 dict(name="Leon Aillaud Chavez", school="CETYS Mexicali", conf="H", rubric="hardware",
   c=dict(CAD=5,Fabrication=5,MechDesign=5,Domain=5,Electronics=3,Initiative=5,English=5),
   note="Built inspection fixtures on his OWN 3D printer until the employer funded one; co-founded CADIS; CSU 3D-printed fixed-wing aircraft comp (empennage); MATE ROV submarine + ANSYS FEA. Textbook fit."),
 dict(name="Yixin Zhou", school="Olin College", conf="H", rubric="hardware",
   c=dict(CAD=5,Fabrication=5,MechDesign=5,Domain=5,Electronics=3,Initiative=4,English=5),
   note="Formula SAE powertrain — hand calcs + FEA, CAD, 3D printing, CNC. Olin = elite hands-on program. Native-level English."),
 dict(name="Jackson Martin", school="San Diego State", conf="M", rubric="hardware",
   c=dict(CAD=4,Fabrication=4,MechDesign=4,Domain=5,Electronics=4,Initiative=5,English=5),
   note="Autonomous-drone software w/ Dr. Machuca; built a quadcopter biplane senior project (direct UAV); CAD internship; led 8-person team. Strongest pure-UAV signal in the pool."),
 dict(name="Sofia Valdez Lau", school="CETYS", conf="M", rubric="hardware",
   c=dict(CAD=5,Fabrication=4,MechDesign=5,Domain=4,Electronics=2,Initiative=5,English=4),
   note="President of university racing team (automotive/SAE-adjacent); advanced parametric SolidWorks; real-time troubleshooting under pressure; manufacturing internship."),
 dict(name="Diego Mendoza Madrid", school="CETYS", conf="H", rubric="hardware",
   c=dict(CAD=5,Fabrication=4,MechDesign=5,Domain=2,Electronics=3,Initiative=5,English=4),
   note="Össur internship: precision fixtures, tooling, parametric test setups in SolidWorks; CNC + laser cutting; GD&T; Manufacturing Team Lead. Strong hardware, no UAV/SAE."),
 dict(name="Antonio Quezada Figueroa", school="CETYS Tijuana", conf="M", rubric="hardware",
   c=dict(CAD=4,Fabrication=3,MechDesign=4,Domain=5,Electronics=2,Initiative=5,English=4),
   note="Led the only Mexican team at CSULA 3D-printed aircraft comp; president of student eng group; JAE automotive internship (injection molding). Aero passion + leadership; only 6th semester."),
 dict(name="Roberto Monroy Amador", school="CETYS", conf="H", rubric="hardware",
   c=dict(CAD=4,Fabrication=4,MechDesign=4,Domain=1,Electronics=2,Initiative=5,English=5),
   note="~1yr pro manufacturing eng: led plant transfer & global standardization; fixture design; Lean/Six Sigma. Strong but more PROCESS/manufacturing than rapid prototyping. No robotics/UAV/SAE."),
 dict(name="Leila Sigala", school="CETYS", conf="M", rubric="hardware",
   c=dict(CAD=4,Fabrication=3,MechDesign=4,Domain=3,Electronics=2,Initiative=4,English=5),
   note="ME w/ explicit aerospace interest; SolidWorks/Inventor/AutoCAD, CNC machining, automation. Domain evidence is mostly coursework + a furniture-design project lead. Excellent English."),
 dict(name="Jake Rufino", school="UT Tijuana", conf="M", rubric="hardware",
   c=dict(CAD=4,Fabrication=4,MechDesign=4,Domain=2,Electronics=3,Initiative=4,English=2),
   note="~2.5yr mechanical design + automation; SolidWorks, FEA, PLC; fixture/tooling; supervised interns. RED FLAG: resume notes ENGLISH IS INTERMEDIATE — verify."),
 dict(name="Daniel Lopez Moreno", school="CETYS", conf="M", rubric="hardware",
   c=dict(CAD=3,Fabrication=3,MechDesign=3,Domain=3,Electronics=4,Initiative=4,English=3),
   note="Mechatronics student; built a robotic car and a robotic arm; basic CNC/lathe/milling + PLC. Early but genuine hands-on trajectory."),
 dict(name="Alfonso Gonzalez Villalobos", school="CETYS", conf="L", rubric="hardware",
   c=dict(CAD=3,Fabrication=3,MechDesign=3,Domain=2,Electronics=2,Initiative=3,English=3),
   note="ME w/ SolidWorks/AutoCAD + process-improvement internship. Generic mid profile; NO 'About Me' so motivation/English are unverified."),
 dict(name="Diego Romero Bassoco", school="CETYS", conf="L", rubric="hardware",
   c=dict(CAD=3,Fabrication=2,MechDesign=3,Domain=2,Electronics=2,Initiative=3,English=2),
   note="Last-year ME, CNC operator, ANSYS. Very thin/generic record and a one-line About Me with weak written English. Eager but unproven."),
 dict(name="Esau Colloy Alvarez", school="CETYS Tijuana", conf="L", rubric="hardware",
   c=dict(CAD=3,Fabrication=2,MechDesign=2,Domain=1,Electronics=2,Initiative=3,English=3),
   note="CAD-assistant / technical-drawing background (AutoCAD/Revit/SolidWorks). Best fit for the eng-documentation slice, not fabrication. No LinkedIn."),
 dict(name="Marco Rangel", school="CETYS", conf="L", rubric="hardware",
   c=dict(CAD=2,Fabrication=2,MechDesign=2,Domain=1,Electronics=1,Initiative=3,English=5),
   note="ME grad met at job fair; 3D printing; quad-lingual (En/Es/It/basic German); production-supervision internship. Thin technical depth; strong communicator."),

 # ===== EMBEDDED (Hardware / Embedded Systems Intern – AI Test & Integration) =====
 dict(name="Vania Leal Espinoza", school="CETYS", conf="M", rubric="embedded",
   c=dict(Bringup=5,Electronics=5,Software=5,Testing=4,Initiative=5,English=4),
   note="Near-ideal for this role: embedded systems, hardware-software integration, Linux, vision systems, sensor integration. Led electronics for a rocketry team; hackathons; taught robotics."),
 dict(name="Melanie Picen", school="CETYS", conf="M", rubric="embedded",
   c=dict(Bringup=4,Electronics=5,Software=4,Testing=4,Initiative=5,English=3),
   note="Cybernetics: FPGA/Verilog, embedded systems, ML, system validation, Python/C++. Strong embedded/test fit; written English brief but technical depth is high."),
 dict(name="Kevin Osorio Franco", school="CETYS", conf="L", rubric="embedded",
   c=dict(Bringup=4,Electronics=4,Software=2,Testing=3,Initiative=3,English=3),
   note="Mechatronics: AOI systems, ABB robotics, STM32 embedded, PLC — relevant to bring-up/test. RESUME MISSING in Airtable, so scores are provisional; get the resume to confirm."),

 # ===== AI ENGINEER =====
 dict(name="Jonayet Lavin", school="Caltech", conf="H", rubric="ai",
   c=dict(ML=5,SWE=5,Edge=3,Initiative=5,Domain=2,English=5),
   note="Strong fit for this role: ML eng (PyTorch, GenAI, RAG, fine-tuning), co-founded a GenAI startup as backend lead, model deployment (Docker/FastAPI). Edge-inference & autonomy domain are the gaps to probe."),

 # ===== STRATEGIC PROJECTS INTERN =====
 dict(name="Felipe Fluck", school="ORT Argentina", conf="H", rubric="strategic",
   c=dict(Org=3,Comms=4,Initiative=5,Marketing=2,Range=4,English=5),
   note="Full-stack/Web3 builder with strong initiative (founded projects, DAOs), logistics coordination and customer-facing experience. Broad generalist; lighter on pure marketing/comms."),
 dict(name="Camila Lewis", school="CETYS", conf="M", rubric="strategic",
   c=dict(Org=4,Comms=4,Initiative=3,Marketing=5,Range=3,English=4),
   note="Directly relevant for this role: marketing strategy, social media/content, event coordination, market research, bilingual. The marketing-coordination core of Strategic Projects is her strength."),

 # ===== OPERATIONS INTERN =====
 dict(name="Lauren Hagen", school="San Diego State", conf="H", rubric="ops",
   c=dict(OpsLog=4,Org=5,Tools=3,Comms=5,Initiative=5,English=5),
   note="Strong Operations fit: ran large campus organizations, managed budgets, event logistics, compliance & program administration. Supply-chain specifics are lighter, but the operational backbone is all there."),
]

if __name__ == "__main__":
    def total(cand):
        dims = RUBRICS[cand["rubric"]]
        return round(sum(cand["c"][k]/5*w for k,_,w in dims), 1)
    by_rub = {}
    for cand in C: by_rub.setdefault(cand["rubric"], []).append(cand)
    for rub, cands in by_rub.items():
        print(f"\n=== {rub.upper()} ===")
        for c in sorted(cands, key=total, reverse=True):
            print(f"  {total(c):5}  {c['conf']}  {c['name']}")
