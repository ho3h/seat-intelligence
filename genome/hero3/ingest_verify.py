"""Verify the list->rope->tree-fold pipeline nets (plain and after the swing-18 K=16 lookahead transformation) on the LIST
programs, seeds 0-2. -> runs/hero3/ingest_verify.json"""
import json
from concurrent.futures import ThreadPoolExecutor
from ..verify import verify
from ..exp12.lookahead import transform
from . import folds as F
from .nets import ingest_net
from .programs import list_program


def one(f):
    lp = list_program(f); net = ingest_net(f)
    la, _ = transform(net, 16)
    return dict(fold=f.id, plain=[verify(lp, net, s, workers=2)["status"] for s in (0, 1, 2)],
                k16=[verify(lp, la, s, workers=2)["status"] for s in (0, 1, 2)])


if __name__ == "__main__":
    out = []
    with ThreadPoolExecutor(2) as ex:
        for r in ex.map(one, F.assoc()):
            print(r, flush=True); out.append(r)
            json.dump(out, open("runs/hero3/ingest_verify.json", "w"), indent=1)
