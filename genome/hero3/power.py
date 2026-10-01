"""EXTRA (not in the kill rule): detection power of the tester and of the hidden verify suite against a merge bug that fires with
tunable rarity. Fold = sum with comb(a,b) = 0 when (a & MA) == MA and (b & MB) == MB, with popcount(MA)+popcount(MB) = k, so the bug
fires on about 2^-k of random pairs. Tester seeds 0..9; verify seeds 0..2 on the FORCED tree rewrite (py reference)."""
from __future__ import annotations
import json, sys
from concurrent.futures import ThreadPoolExecutor
from ..verify import verify
from . import folds as F
from .netbuild import build, sel, eq, C
from .tester import test_fold
from .nets import tree_net
from .programs import tree_program


def glitch_fold(k):
    ka = k // 2; kb = k - ka
    MA, MB = (1 << ka) - 1, (1 << kb) - 1
    f = F.Fold(id=f"glitch_k{k}", label="nonassoc", desc=f"sum with merge bug firing on ~2^-{k} of pairs", elem_ar=1, state_ar=1, unit=0,
               lift_txt=build("lift", [1], lambda x: x),
               comb_txt=build("comb", [1, 1], lambda a, b: sel(eq(a & MA, MA) & eq(b & MB, MB), C(0), a + b)),
               py_lift=lambda x: x, py_comb=lambda a, b: 0 if (a & MA) == MA and (b & MB) == MB else (a + b) & F.M,
               gen=F.g_mix, enum=F.ENUM3)
    return f


def one(k):
    f = glitch_fold(k)
    det = []
    for s in range(10):
        r = test_fold(f, 100 + s)
        det.append(not r["accept"])
    tp = tree_program(f, "py")
    vs = [verify(tp, tree_net(f), s, workers=2)["status"] for s in (0, 1, 2)]
    return dict(k=k, tester_detect=sum(det), tester_runs=len(det), verify=vs)


if __name__ == "__main__":
    ks = [int(x) for x in sys.argv[1:]] or [4, 6, 8, 10, 12, 14, 16, 20, 24]
    out = []
    with ThreadPoolExecutor(2) as ex:
        for r in ex.map(one, ks):
            print(r, flush=True); out.append(r)
    json.dump(out, open("runs/hero3/power.json", "w"), indent=1)
