"""Quick experiments Q1 (anchoring / structural distance) and Q2 (where does the medium win) from data we already have."""
import glob, json, os, random, statistics as S, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from genome.netast import parse_book, size
from genome import bend_io as B
from genome.corpus import load_all
R = load_all()
ok = lambda s: s["accepted"] and s.get("audit") == ["pass", "pass"]
KIDS = ("con", "dup", "opr", "swi")

def layers(pats):
    out = {}
    for pat in pats:
        for f in glob.glob(pat):
            s = json.load(open(f))
            if s["pid"] not in out or (not ok(out[s["pid"]][0]) and ok(s)): out[s["pid"]] = (s, os.path.dirname(f))
    return out
NB = layers(["runs/g1/native/seed0/*/state.json", "runs/g1r1/native/seed0/*/state.json", "runs/probe2/dsv4/native/seed0/*/state.json", "runs/g1esc/native/seed0/*/state.json"])
BB = layers(["runs/g1/b1/seed0/*/state.json", "runs/g1r1/b1/seed0/*/state.json", "runs/g1esc/b1/seed0/*/state.json"])
both = [p for p in NB if p in BB and ok(NB[p][0]) and ok(BB[p][0]) and NB[p][0].get("best") and BB[p][0].get("best")]

# ---------------- Q2: where does the medium win?
by = collections.defaultdict(list)
for p in both:
    n, b = NB[p][0]["best"], BB[p][0]["best"]
    gi = 1 - n["itrs_median_big"] / b["itrs_median_big"]; gd = 1 - n["depth_median_big"] / b["depth_median_big"]
    by[p.split("_")[0]].append((gi, gd, max(gi, gd)))
print("Q2  tier | n | native wins (int or depth) | median interaction gain | median depth gain")
for t in sorted(by):
    v = by[t]; print(f"    {t} | {len(v):3d} | {100*sum(x[2]>0 for x in v)/len(v):3.0f}% | {100*S.median(x[0] for x in v):+4.0f}% | {100*S.median(x[1] for x in v):+4.0f}%")
allv = [x for v in by.values() for x in v]
print(f"    all | {len(allv)} | {100*sum(x[2]>0 for x in allv)/len(allv):.0f}% | {100*S.median(x[0] for x in allv):+.0f}% | {100*S.median(x[1] for x in allv):+.0f}%")

# ---------------- Q1: anchoring. Do native nets look like compiled Bend nets?
def shapes(book, lo=3, hi=7):
    defs, _ = parse_book(book); out = collections.Counter()
    def canon(t):
        k = t[0]
        if k in KIDS: return {"con": "(", "dup": "{", "opr": "$(", "swi": "?("}[k] + canon(t[1]) + " " + canon(t[2]) + ")"
        if k == "num": return "N" if not t[1].startswith("[") else t[1]
        return {"var": "v", "ref": "@", "era": "*"}[k]
    def walk(t):
        if t[0] in KIDS:
            if lo <= size(t) <= hi: out[canon(t)] += 1
            walk(t[1]); walk(t[2])
    for n, (root, reds) in defs.items():
        walk(root)
        for _, a, b in reds: walk(a); walk(b)
    return out
def jac(a, b):
    ka, kb = set(a), set(b); return len(ka & kb) / max(1, len(ka | kb))
random.seed(0); sims, base, sizes = [], [], []
pool = {}
for p in both:
    sn, dn = NB[p]; sb, db = BB[p]
    nf = os.path.join(dn, "best.hvm"); bf = os.path.join(db, "best.bend")
    if not (os.path.exists(nf) and os.path.exists(bf)): continue
    book, err = B.compile_bend(B.bend_source(R[p], open(bf).read()))
    if err: continue
    pool[p] = (shapes(open(nf).read()), shapes(book), size(parse_book(open(nf).read())[0]["prog"][0]) if "prog" in parse_book(open(nf).read())[0] else 0, len(open(nf).read()), len(book))
keys = list(pool)
for p in keys:
    sims.append(jac(pool[p][0], pool[p][1]))
    q = random.choice([k for k in keys if k != p and k.split("_")[0] == p.split("_")[0]] or keys)
    base.append(jac(pool[p][0], pool[q][1]))
    sizes.append(pool[p][3] / pool[p][4])
print(f"\nQ1  native net vs Bend-compiled net of the SAME program: median shape overlap (Jaccard) {S.median(sims):.3f}")
print(f"    vs Bend net of a DIFFERENT program in the same tier:  median {S.median(base):.3f}   (n={len(keys)})")
print(f"    ratio same/different = {S.median(sims)/max(1e-9,S.median(base)):.2f}  (near 1.0 means native nets are NOT transcriptions of the Bend route)")
print(f"    text size native/Bend-compiled: median {S.median(sizes):.2f}")
