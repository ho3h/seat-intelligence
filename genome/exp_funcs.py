"""How much of each verified net is a helper procedure that recurs (modulo naming) in OTHER programs?"""
import glob, json, os, sys, collections, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from genome.netast import parse_book, size
KIDS = ("con", "dup", "opr", "swi")
ABSTRACT = os.environ.get("ABSTRACT") == "1"  # numbers and operator symbols become holes (parametric templates)

def _num(v): return v if not ABSTRACT else ("OP" if v.startswith("[") else "N")

def norm_def(root, reds, refmap):
    """canonical string of one def: vars alpha-renamed by first occurrence (redexes sorted by var-blind shape), refs via refmap"""
    def shape(t):
        k = t[0]
        if k in KIDS: return {"con": "(", "dup": "{", "opr": "$(", "swi": "?("}[k] + shape(t[1]) + " " + shape(t[2]) + ")"
        if k == "var": return "_"
        if k == "ref": return "@" + refmap(t[1])
        if k == "era": return "*"
        return _num(t[1])
    rs = sorted(reds, key=lambda r: min(shape(r[1]), shape(r[2])) + "~" + max(shape(r[1]), shape(r[2])))
    names = {}
    def show(t):
        k = t[0]
        if k in KIDS: return {"con": "(", "dup": "{", "opr": "$(", "swi": "?("}[k] + show(t[1]) + " " + show(t[2]) + ")"
        if k == "var": return "v" + str(names.setdefault(t[1], len(names)))
        if k == "ref": return "@" + refmap(t[1])
        if k == "era": return "*"
        return _num(t[1])
    body = show(root)
    body += "".join("&" + "~".join(sorted([show(a), show(b)], key=len)) for _, a, b in rs)
    return body

def cluster_key(name, defs):
    """canonical string for def `name` plus everything it (transitively) calls; refs numbered in discovery order"""
    order = []; seen = {}
    def visit(n):
        if n in seen or n not in defs: return
        seen[n] = len(order); order.append(n)
        root, reds = defs[n]
        def refs(t):
            if t[0] == "ref": visit(t[1])
            elif t[0] in KIDS: refs(t[1]); refs(t[2])
        refs(root)
        for _, a, b in reds: refs(a); refs(b)
    visit(name)
    refmap = lambda r: str(seen.get(r, "ext:" + r if not r.startswith("__") else r))
    return "|".join(norm_def(*defs[n], refmap) for n in order), sum(size(defs[n][0]) + sum(size(a) + size(b) for _, a, b in defs[n][1]) for n in order)

ok = lambda s: s["accepted"] and s.get("audit") == ["pass", "pass"]
nets = {}
for pat in ("runs/datagen/native/seed0/*/state.json", "runs/g1/native/seed0/*/state.json", "runs/g1r1/native/seed0/*/state.json", "runs/g1esc/native/seed0/*/state.json"):
    for f in glob.glob(pat):
        s = json.load(open(f)); b = os.path.join(os.path.dirname(f), "best.hvm")
        if ok(s) and os.path.exists(b) and s["pid"] not in nets: nets[s["pid"]] = open(b).read()
table = collections.defaultdict(set); mass = {}; per = {}
for pid, txt in nets.items():
    try: defs, order = parse_book(txt)
    except Exception: continue
    for n in order:
        if n == "prog": continue
        key, sz = cluster_key(n, defs)
        table[key].add(pid); mass[key] = sz; per.setdefault(pid, []).append((n, key, sz))
tot = sum(sz for v in per.values() for _, _, sz in v)
shared = sum(sz for v in per.values() for _, k, sz in v if len(table[k]) >= 2)
big_shared = sum(sz for v in per.values() for _, k, sz in v if len(table[k]) >= 3 and mass[k] >= 12)
print(f"{len(nets)} nets; helper-procedure mass {tot} nodes")
print(f"  in a procedure identical (mod names) in >=2 programs: {100*shared/tot:.1f}%")
print(f"  in a procedure of size>=12 identical in >=3 programs: {100*big_shared/tot:.1f}%")
top = sorted(((len(v), mass[k], k) for k, v in table.items() if len(v) >= 3 and mass[k] >= 12), reverse=True)[:8]
print("most reused procedures (programs, nodes):", [(a, b) for a, b, _ in top])
if top: print("example:", top[0][2][:400])
