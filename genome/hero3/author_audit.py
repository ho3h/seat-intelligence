"""Differential audit against the ORIGINAL nets as authored in the corpus runs (not the generated walker): for the 12 corpus-derived
folds the rewritten tree net is verified with reference = the accepted native net of that corpus program, run on the in-order
leaves, seeds 100-102. Also checks the authored net itself against the corpus program (seed 0). -> runs/hero3/author_audit.json"""
import json
from concurrent.futures import ThreadPoolExecutor
from ..exp12.evaluate import native_nets
from ..verify import verify
from . import folds as F
from .nets import tree_net
from .programs import tree_program, list_program


def one(f):
    net = open(native_nets()[f.corpus]).read()
    lp = list_program(f)
    orig = verify(lp, net, 0, workers=2)["status"]
    tp = tree_program(f, "net", net)
    st = [verify(tp, tree_net(f), s, workers=2)["status"] for s in (100, 101, 102)]
    return dict(fold=f.id, corpus=f.corpus, authored_net_seed0=orig, tree_vs_authored=st)


if __name__ == "__main__":
    fs = [f for f in F.assoc() if f.corpus]
    out = []
    with ThreadPoolExecutor(2) as ex:
        for r in ex.map(one, fs):
            print(r, flush=True); out.append(r)
    json.dump(out, open("runs/hero3/author_audit.json", "w"), indent=1)
