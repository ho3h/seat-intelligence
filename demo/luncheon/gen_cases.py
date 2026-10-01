"""Dump random cases from the Python reference for test_seating.js: 400 cases of the six HERO-1 words (genome/hero1/lang.py,
unchanged), then 600 cases with the named words `avoid` and `pair` (genome/hero6/lang6.py)."""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, random, sys
sys.path.insert(0, _REPO)
from genome.hero1 import lang
random.seed(20260930)
ORGS = {c: [f"{lang.CATS[c][:3]}{k}" for k in range(3)] for c in range(len(lang.CATS))}
def rand_guests(n):
    gs = []
    for _ in range(n):
        c = random.randrange(7)
        org = random.choice(ORGS[c]) if c not in (5, 6) or random.random() < 0.3 else None
        gs.append((org, c))
    return gs
def rand_prog():
    L = []
    if random.random() < .7: L.append(f"size {random.randint(1, 6)}")
    if random.random() < .4: L.append("together company")
    if random.random() < .2: L.append(f"together {random.choice(lang.CATS)}")
    for _ in range(random.randint(0, 2)):
        L.append("limit " + " ".join(random.sample(lang.CATS, random.randint(1, 3))) + f" {random.randint(1, 4)}")
    for _ in range(random.randint(0, 2)):
        a, b = random.sample(lang.CATS, 2); L.append(f"apart {a} {b}")
    if random.random() < .5: L.append("order " + " ".join(random.sample(lang.CATS, random.randint(1, 4))))
    return "\n".join(L) or "none"
cases = []
for _ in range(400):
    n = random.choice([6, 12, 34, 34, 60])
    g = rand_guests(n); prog = rand_prog()
    try: pol = lang.parse(prog)
    except lang.ParseError: continue
    a = lang.assign_ref(g, pol); v = lang.violations(g, pol, a)
    cases.append({"guests": [{"org": o, "cat": c} for o, c in g], "prog": prog, "assign": a, "seq": lang.seat_order(g, pol),
                  "v": v, "canon": lang.to_text(pol), "posted": lang.posted_assignment(n, pol.cap) if n % 2 == 0 else None})
# ---- HERO-6: named words (avoid, pair) from genome/hero6/lang6.py, guests with names; the old cases above are unchanged
from genome.hero6 import lang6
r6 = random.Random(6)
NAMES = ["Ada Lovelace", "Grace Hopper", "Alan Turing", "Elon Musk", "Mark Zuckerberg", "Kofi Mensah", "Jean-Luc Picard", "Ana María López",
         "Li Wei", "O'Brien", "Zoë Grünewald", "Sam", "Secretary Lutnick"]
ORGS6 = {c: [f"{lang.CATS[c][:3]} co {k}" for k in range(3)] + ({0: ["OpenAI"], 1: ["X, Tesla, Space X"]}.get(c, [])) for c in range(7)}
def rand_guests6(n):
    gs = []
    for i in range(n):
        c = r6.randrange(7)
        org = r6.choice(ORGS6[c]) if c not in (5, 6) or r6.random() < 0.3 else None
        name = r6.choice(NAMES) if r6.random() < 0.5 else (f"Guest {i}" if r6.random() < 0.8 else None)
        gs.append((org, c, name))
    return gs
def rand_prog6(g):
    pool = [lang6.key(x[2]) for x in g if x[2]] + [lang6.key(x[0]) for x in g if x[0]] + ["Nobody"]
    L = [x for x in rand_prog_r6().split("\n") if x != "none"]
    for w in ("avoid", "pair"):
        for _ in range(r6.choice([0, 1, 1, 2, 3] if w == "avoid" else [0, 1, 1, 2])):
            a, b = r6.choice(pool), r6.choice(pool)
            if a != b: L.append(f"{w} {a} {b}")
    r6.shuffle(L)
    return "\n".join(L) or "none"
def rand_prog_r6():
    global random
    st = random.getstate(); random.seed(r6.random()); t = rand_prog(); random.setstate(st); return t
n6 = 0
while n6 < 600:
    n = r6.choice([2, 6, 12, 34, 34, 60])
    g = rand_guests6(n); prog = rand_prog6(g)
    try: pol = lang6.parse(prog)
    except lang6.ParseError: continue
    a = lang6.assign_ref(g, pol); v = lang6.violations(g, pol, a)
    cases.append({"guests": [{"org": o, "cat": c, "name": nm} for o, c, nm in g], "prog": prog, "assign": a, "seq": lang6.seat_order(g, pol),
                  "v": v, "canon": lang6.to_text(pol), "posted": lang6.posted_assignment(n, pol.cap) if n % 2 == 0 else None, "named": True})
    n6 += 1
json.dump(cases, open(_REPO + "/demo/luncheon/cases.json", "w"))
print(len(cases))
