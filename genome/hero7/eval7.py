"""HERO-7 grid evaluation of one model+adapter: sets 7, 1, 2, 6 x {T=0.7 n=5, greedy} x {plain, cons}; scores with score7.py.
  python -m genome.hero7.eval7 <model> <adapter|-> <tag> [modes=plain,cons]   -> runs/hero7/samples/<tag>/..., runs/hero7/grid/<tag>.json"""
import json, os, sys, time
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
sys.path.insert(0, _REPO)
from genome.hero7.score7 import SETS, score
from genome.hero7.sample7 import run, request_guests


def main(model_id, adapter, tag, modes="plain,cons", sets="7,1,2,6"):
    from mlx_lm import load
    model, tok = load(model_id, adapter_path=None if adapter == "-" else adapter)
    od = f"{_REPO}/runs/hero7/samples/{tag}"; os.makedirs(od, exist_ok=True)
    grid = {}
    gp = f"{_REPO}/runs/hero7/grid/{tag}.json"; os.makedirs(os.path.dirname(gp), exist_ok=True)
    if os.path.exists(gp): grid = json.load(open(gp))
    for mode in modes.split(","):
        for s in sets.split(","):
            d = json.load(open(SETS[s])); pols = [p for p in (d["policies"] if isinstance(d, dict) else d) if p.get("scope", "in") == "in"]
            for kind, n, temp in (("t07", 5, 0.7), ("greedy", 1, 0.0)):
                key = f"{mode}/{s}/{kind}"
                if key in grid: continue
                t0 = time.time()
                out, raw, scans = run(model, tok, [p["text"] for p in pols], request_guests(SETS[s]), n, temp, 0.95 if temp else 1.0, mode)
                secs = time.time() - t0
                path = f"{od}/{mode}_set{s}_{kind}.json"
                json.dump(dict(meta=dict(model=model_id, adapter=adapter, mode=mode, set=s, n=n, temp=temp, seconds=round(secs, 1), full_scans=scans),
                               samples={p["id"]: o for p, o in zip(pols, out)}, raw={p["id"]: r for p, r in zip(pols, raw)}), open(path, "w"))
                r = score(s, path); r["seconds"] = round(secs, 1); r["full_scans"] = scans
                grid[key] = r
                json.dump(grid, open(gp, "w"), indent=1)
                print(tag, key, f"pass1={r['pass1']} strict={r['pass1_strict']} vote={r['vote_strict']}/{r['policies']} {secs:.0f}s", flush=True)


if __name__ == "__main__": main(*sys.argv[1:])
