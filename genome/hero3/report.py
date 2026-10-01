"""Print the extra HERO-3 tables (Bend comparison, controls and ingest, authored originals, power, shape) as markdown."""
import json, statistics as S, os
from .analyze import load_jsonl, fit
from . import folds as F

R = "runs/hero3"
N = (1000, 10000, 100000)
tree = load_jsonl("tree"); seq = load_jsonl("seq_list"); la = load_jsonl("seq_la"); st = load_jsonl("seq_tree")
ing = load_jsonl("ingest"); ingla = load_jsonl("ingest_la"); bend = load_jsonl("bend"); auth = load_jsonl("seq_author")
A = [f.id for f in F.assoc()]


def med(d, key, n, ids=A): return S.median([d[(i, n)][key] for i in ids if (i, n) in d])


print("### Bend vs machine-rewritten native (same balanced rope, depth oracle)")
print("| fold | n | native depth | Bend depth | Bend/native depth | native itrs | Bend itrs | Bend/native itrs |\n|---|---|---|---|---|---|---|---|")
rd, ri = [], []
for i in ["sum", "max", "argmax_first", "category_counts", "first_violation"]:
    for n in N:
        t, b = tree[(i, n)], bend[(i, n)]
        rd.append(b["depth"] / t["depth"]); ri.append(b["itrs"] / t["itrs"])
        print(f"| {i} | {n:,} | {t['depth']:,} | {b['depth']:,} | {b['depth']/t['depth']:.2f} | {t['itrs']:,} | {b['itrs']:,} | {b['itrs']/t['itrs']:.2f} |")
import math
gm = lambda v: math.exp(sum(math.log(x) for x in v) / len(v))
print(f"geomean Bend/native depth {gm(rd):.3f} (range {min(rd):.2f}-{max(rd):.2f}); interactions {gm(ri):.3f} (range {min(ri):.2f}-{max(ri):.2f}); Bend depth exponents:",
      {i: round(fit(bend, i, 'depth'), 3) for i in ["sum", "max", "argmax_first", "category_counts", "first_violation"]})

print("\n### Median over the 31 associative folds (rounds / interactions)")
print("| variant | depth 1k | 10k | 100k | depth exponent (median) | itrs 100k | itrs exponent (median) |\n|---|---|---|---|---|---|---|")
for name, d in [("tree fold on rope (rewrite)", tree), ("original list walker", seq), ("original + K=16 lookahead", la), ("in-order sequential fold on the rope (control)", st),
                ("list -> rope -> tree fold (ingest)", ing), ("ingest after K=16 lookahead", ingla)]:
    if not d: continue
    ex = [fit(d, i, "depth") for i in A]; ex = [e for e in ex if e is not None]
    ix = [fit(d, i, "itrs") for i in A]; ix = [e for e in ix if e is not None]
    print(f"| {name} | {med(d,'depth',1000):,.0f} | {med(d,'depth',10000):,.0f} | {med(d,'depth',100000):,.0f} | {S.median(ex):.3f} | {med(d,'itrs',100000):,.0f} | {S.median(ix):.3f} |")

print("\nPer-element rounds at n=100k (median over folds): tree", f"{med(tree,'depth',100000)/1e5:.4f}", "seq", f"{med(seq,'depth',100000)/1e5:.2f}", "seq+K16", f"{med(la,'depth',100000)/1e5:.2f}",
      "ingest", f"{med(ing,'depth',100000)/1e5:.2f}", "ingest+K16", f"{med(ingla,'depth',100000)/1e5:.2f}" if ingla else "-")
if ingla:
    win = [i for i in A if (i, 100000) in ingla and ingla[(i, 100000)]["depth"] < seq[(i, 100000)]["depth"]]
    print(f"ingest+K16 shallower than the original list walker at 100k on {len(win)}/{len(A)} folds; vs original+K16 walker: "
          f"{sum(ingla[(i,100000)]['depth'] < la[(i,100000)]['depth'] for i in A)}/{len(A)}")
    print("ingest+K16 / original ratio at 100k: median", f"{S.median(seq[(i,100000)]['depth']/ingla[(i,100000)]['depth'] for i in A):.2f}",
          "min", f"{min(seq[(i,100000)]['depth']/ingla[(i,100000)]['depth'] for i in A):.2f}", "max", f"{max(seq[(i,100000)]['depth']/ingla[(i,100000)]['depth'] for i in A):.2f}")

print("\n### Authored originals (accepted corpus nets from the G1 runs) vs the rewrite, 12 corpus folds")
print("| fold | authored depth 1k | 100k | exp | rewrite depth 100k | authored/rewrite |\n|---|---|---|---|---|---|")
for f in F.assoc():
    if not f.corpus: continue
    i = f.id; e = fit(auth, i, "depth")
    print(f"| {i} | {auth[(i,1000)]['depth']:,} | {auth[(i,100000)]['depth']:,} | {e:.2f} | {tree[(i,100000)]['depth']:,} | {auth[(i,100000)]['depth']/tree[(i,100000)]['depth']:.0f}x |")

if os.path.exists(f"{R}/power.json"):
    print("\n### Detection power vs nominal violation rate 2^-k (tester: 10 seeds; verify on the forced tree: seeds 0-2)")
    for r in json.load(open(f"{R}/power.json")): print(r)
if os.path.exists(f"{R}/shape_sensitivity.json"):
    print("\n### Shape sensitivity (sum)"); [print(r) for r in json.load(open(f"{R}/shape_sensitivity.json"))]
