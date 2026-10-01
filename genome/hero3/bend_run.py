"""Verify the 5 strong-Bend tree reductions (verify_b1 seeds 0-2 on the rope-input programs) and write runs/hero3/bend_verify.json."""
import json, sys
from ..verify import verify_b1
from . import folds as F
from .bend_trees import BEND
from .programs import tree_program

res = {}
for fid in BEND:
    f = F.by_id(fid); tp = tree_program(f, "py")
    res[fid] = {}
    for s in (0, 1, 2):
        r = verify_b1(tp, BEND[fid], s, workers=3)
        res[fid][s] = dict(status=r["status"], reason=r.get("reason"), cex=r.get("counterexample"), metrics=r.get("metrics"))
    print(fid, [res[fid][s]["status"] for s in (0, 1, 2)], flush=True)
json.dump(res, open("runs/hero3/bend_verify.json", "w"), indent=1, default=str)
