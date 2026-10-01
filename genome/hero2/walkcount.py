"""The one inlining the exp3 search accepted on seed 0 and had to roll back on seeds 1-2 (t3_walk_count, operator inline_call):
apply exp3's inline_call operator at every site, one site at a time, and ask (a) does the executor separate it from the original,
(b) does the normalizer prove it?"""
import json
from genome.netast import parse_book, print_book
from genome.corpus import load_all
from genome.exp3 import mut as M
from genome.hero2.corpus import Case
from genome.hero2.harness import sample_pair
from genome.hero2.prove import Prover
from genome.verify import lint_net

R = load_all(); p = R["t3_walk_count"]
text = open("runs/exp3/base/t3_walk_count.native.hvm").read()
defs, order = parse_book(text)
sites = M.call_sites(defs)
print("inline_call sites:", len(sites))
rows = []
for i, s in enumerate(sites):
    nd = M.call_apply(defs, s)
    if nd is None: continue
    ct = print_book(nd, list(nd))
    if lint_net(ct): continue
    v = Prover(text, ct).prove()
    c = Case(f"walk{i}", "S", "?", text, ct, prog=p)
    smp = sample_pair(c, 250, seed=31000, workers=3, timeout=8.0)
    rows.append({"site": repr(s)[:80], "proved": v.equal, "tier": v.tier, "disagree": smp["disagree"], "n": smp["n"]})
    print(rows[-1], flush=True)
# all sites at once (what the search's accepted candidate was)
nd, k = M.apply_all(defs, "inline_call")
ct = print_book(nd, list(nd))
v = Prover(text, ct).prove()
c = Case("walk_all", "S", "?", text, ct, prog=p)
smp = sample_pair(c, 250, seed=31000, workers=3, timeout=8.0)
rows.append({"site": f"apply_all ({k} sites)", "proved": v.equal, "tier": v.tier, "reason": v.reason, "disagree": smp["disagree"], "n": smp["n"]})
print(rows[-1])
json.dump(rows, open("runs/hero2/walkcount.json", "w"), indent=1)
