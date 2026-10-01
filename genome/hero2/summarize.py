"""Tables for docs/HERO-2.md from the run artifacts. usage: python3 -m genome.hero2.summarize"""
import json, glob, collections, statistics
run = json.load(open("runs/hero2/run1.json"))["results"]
snd = json.load(open("runs/hero2/soundness1.json"))
scope = json.load(open("runs/hero2/scope.json"))

print("== coverage by class and tier (known-equal, denominators as in s.1.3)")
byc = collections.defaultdict(lambda: collections.Counter())
for cid, r in run.items():
    if r["expect"] != "equal" or not r["denom"]: continue
    byc[r["cls"]]["n"] += 1
    if r["equal"]: byc[r["cls"]][r["tier"]] += 1
tot = collections.Counter()
for c in sorted(byc):
    v = byc[c]; tot.update(v)
    print(f"{c}: {sum(v[t] for t in ('S','S~a','U','U~a','D'))}/{v['n']}  " + " ".join(f"{t}={v[t]}" for t in ('S', 'S~a', 'U', 'U~a', 'D') if v[t]))
for grp, cls in (("synthetic", "F"), ("real", "R")):
    n = sum(byc[c]["n"] for c in byc if c[0] == cls)
    ps = {t: sum(byc[c][t] for c in byc if c[0] == cls) for t in ('S', 'S~a', 'U', 'U~a', 'D')}
    print(f"{grp}: proved {sum(ps.values())}/{n}  by first tier {ps}; S only {ps['S']}/{n}")
allp = sum(tot[t] for t in ('S', 'S~a', 'U', 'U~a', 'D'))
print(f"ALL: proved {allp}/{tot['n']} ({100*allp/tot['n']:.1f}%), S-only {tot['S']}/{tot['n']} ({100*tot['S']/tot['n']:.1f}%)")
print("unproved known-equal:", [c for c, r in run.items() if r["expect"] == "equal" and r["denom"] and not r["equal"]])
un = [r for r in run.values() if r["expect"] == "unequal"]
print(f"== known-unequal: proved {sum(1 for r in un if r['equal'])}/{len(un)}")
x1 = [(c, r["equal"]) for c, r in run.items() if r["cls"] == "X1"]
print("== X1 (informational):", x1)
print("== soundness sampling:", len(snd), "proved pairs; inputs per pair min/median/max", min(v["n"] for v in snd.values()),
      statistics.median(v["n"] for v in snd.values()), max(v["n"] for v in snd.values()), "; total executions (x2 nets):",
      2 * sum(v["n"] for v in snd.values()), "; disagreements:", sum(v["disagree"] for v in snd.values()))
print("== normalizer time (s): total", round(sum(r["secs"] for r in run.values()), 1), "max", max(r["secs"] for r in run.values()))
for kind in ("primitives", "recipes"):
    print(f"== scope {kind}")
    for reg in ("open", "shape", "spine"):
        c = collections.Counter(v[reg]["class"][:1] + " " + v[reg]["class"][2:] for v in scope[kind].values())
        print(f"  {reg}:", dict(c), "terminates:", sum(v[reg]["terminates"] for v in scope[kind].values()), "/", len(scope[kind]))
