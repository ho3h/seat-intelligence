"""The 5 inline_call candidates that only tier S~a proves (they flip a definition's DUP-free flag): do they ever abort? Sample many more inputs
(edge + small + exhaustive sweep at 12 fresh seeds, and the 'big' sizes without the digest wrapper)."""
import json, glob
from genome.netast import parse_book, print_book
from genome.corpus import load_all
from genome.exp3 import mut as M
from genome.hero2.corpus import Case
from genome.hero2.harness import sample_pair
from genome.hero2.prove import Prover
from genome.verify import build_cases
from genome import hero2

R = load_all()
out = {}
for pid in ("t3_wsp_all_from", "t5_cluster_count", "t5_rewrite_sameas_roots", "t3_bipartite_comps", "t3_cc_largest"):
    text = open(f"runs/exp3/base/{pid}.native.hvm").read()
    defs, order = parse_book(text)
    nd, k = M.apply_all(defs, "inline_call")
    ct = print_book(nd, list(nd))
    v = Prover(text, ct).prove()
    # which defs flipped safety?
    pr = Prover(text, ct)
    flipped = sorted(n[2:] for n, d in pr.reg.defs.items() if n.startswith("A:") and ("B:" + n[2:]) in pr.reg.defs and d.safe != pr.reg.defs["B:" + n[2:]].safe)
    case = Case(pid, "S", "?", text, ct, prog=R[pid])
    s = sample_pair(case, 2000, seed=40000, workers=2, timeout=8.0)
    out[pid] = {"tier": v.tier, "flipped_safe_flags": flipped, "n": s["n"], "disagree": s["disagree"], "w": s["witnesses"][:1]}
    print(pid, out[pid], flush=True)
json.dump(out, open("runs/hero2/sa_probe.json", "w"), indent=1)
