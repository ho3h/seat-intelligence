"""Ground-truth validation of the corpus labels using ONLY the real executor (the normalizer is not involved).
usage: python3 -m genome.hero2.gt_check [n_syn] [n_real]"""
import json, sys, time
from genome.hero2 import corpus as C
from genome.hero2.harness import sample_pair
from genome.verify import lint_net


def main():
    n_syn = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    n_real = int(sys.argv[2]) if len(sys.argv) > 2 else 220
    cases = C.all_cases()
    out = {}
    t0 = time.time()
    for c in cases:
        lint = [lint_net(c.A), lint_net(c.B)] if c.cls[0] != "R" and c.cls != "X1" else [None, None]
        # HVM-level lint of real nets was done by their own authors; synthetic ones are linted here
        s = sample_pair(c, n_real if c.prog is not None else n_syn, seed=5000, workers=4)
        ok = (s["disagree"] == 0) if c.expect == "equal" else (s["disagree"] > 0)
        out[c.id] = {"cls": c.cls, "expect": c.expect, "lint": lint, "sample": s, "label_confirmed": ok}
        print(f"{c.id:45s} {c.expect:8s} n={s['n']:3d} disagree={s['disagree']:3d} lint={'ok' if not any(lint) else lint} {'OK' if ok else 'LABEL?'}", flush=True)
    json.dump(out, open("runs/hero2/groundtruth.json", "w"), indent=1)
    bad = [k for k, v in out.items() if not v["label_confirmed"] or any(v["lint"])]
    print("problems:", bad, "secs", round(time.time() - t0))

main()
