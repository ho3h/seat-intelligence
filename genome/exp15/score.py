"""exp15 scoring: parse each sampled stage program, assemble ONE net from the verified word templates with the fixed
genome/compose.py glue, and verify it with genome.verify (seed 0, unchanged semantics). Nothing is trusted: a sample passes
only if its assembled net passes the verifier. Verdicts are cached per (task id, program text) in runs/exp15/vcache.json.

  python3 -m genome.exp15.score runs/exp15/samples/X.json [...]     -> X.scored.json + printed summary
  python3 -m genome.exp15.score --gold runs/exp15/sets/iid.json      -> verifies the gold program of every task (coverage)
At most 3 verifier processes run at once (3 threads x workers=1).
"""
from __future__ import annotations
import json, os, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from genome.verify import verify
from genome.exp15.lang import parse, assemble, to_text, ParseError
from genome.exp15.data import load_task, gold, depth, OUT

CACHE_PATH = os.path.join(OUT, "vcache.json")
_lock = threading.Lock()


def _load_cache():
    try: return json.load(open(CACHE_PATH))
    except Exception: return {}


def _save_cache(c):
    tmp = CACHE_PATH + ".tmp"; json.dump(c, open(tmp, "w")); os.replace(tmp, CACHE_PATH)


def refute_py(p, stages, red, n=40):
    """cheap sound-for-FAIL prefilter: the words' Python semantics (exp13, unit-tested equal to the templates, 65/65) disagree
    with the task reference on an edge or random input -> the program is wrong. A PASS always needs genome.verify."""
    import random
    from genome.exp13.words import program_py
    from genome.taskgen import EDGE_L
    f = program_py(stages, red); rng = random.Random(0)
    for x in list(EDGE_L) + [[rng.randrange(hi) for _ in range(rng.randrange(0, 17))] for hi in (10, 100, 1000) for _ in range(n)]:
        try:
            if f(list(x)) != p.ref(list(x)): return x
        except Exception: return x
    return None


def verify_prog(p, stages, red, cache):
    key = p.id + "|" + to_text(stages, red)
    with _lock:
        if key in cache: return cache[key]
    cx = refute_py(p, stages, red)
    if cx is not None:
        v = {"status": "fail", "why": f"refuted by word semantics on {str(cx)[:80]}", "refuted_py": True}
        with _lock: cache[key] = v
        return v
    try:
        net = assemble(stages, red)
        r = verify(p, net, seed=0, timeout=10.0, workers=1)
        v = {"status": r["status"], "itrs": (r.get("metrics") or {}).get("itrs_median_big"),
             "depth_big": (r.get("metrics") or {}).get("depth_median_big"),
             "why": (r.get("reason") or (r.get("counterexample") or {}).get("why") or "")[:160]}
    except Exception as e:
        v = {"status": "error", "why": repr(e)[:160]}
    with _lock: cache[key] = v
    return v


def score_samples(path, threads=3):
    d = json.load(open(path)); cache = _load_cache(); t0 = time.time()
    specs = d["specs"]; tasks = {load_task(s).id: load_task(s) for s in specs}
    jobs = []
    for pid, texts in d["samples"].items():
        for j, txt in enumerate(texts): jobs.append((pid, j, txt))
    def one(job):
        pid, j, txt = job; p = tasks[pid]; g = to_text(*gold(p))
        try: st, rd = parse(txt)
        except ParseError as e: return pid, j, {"status": "parse", "why": str(e)[:120], "text": txt[:200]}
        prog = to_text(st, rd); v = verify_prog(p, st, rd, cache)
        return pid, j, {"status": "pass" if v["status"] == "pass" else ("fail" if v["status"] == "fail" else v["status"]),
                        "prog": prog, "exact": prog == g, "itrs": v.get("itrs"), "why": v.get("why", "")[:120]}
    res = {pid: [None] * len(t) for pid, t in d["samples"].items()}
    with ThreadPoolExecutor(threads) as ex:
        for pid, j, r in ex.map(one, jobs): res[pid][j] = r
    _save_cache(cache)
    meta = dict(d["meta"]); meta["score_seconds"] = round(time.time() - t0, 1)
    out = {"meta": meta, "specs": specs, "scored": res,
           "depth": {pid: depth(*gold(p)) for pid, p in tasks.items()}, "gold": {pid: to_text(*gold(p)) for pid, p in tasks.items()}}
    sp = path.replace(".json", ".scored.json"); json.dump(out, open(sp, "w"), indent=0)
    return sp


def score_gold(set_path, threads=3):
    specs = json.load(open(set_path)); cache = _load_cache(); t0 = time.time()
    def one(s):
        p = load_task(s); st, rd = gold(p); v = verify_prog(p, st, rd, cache)
        return p.id, depth(st, rd), v
    with ThreadPoolExecutor(threads) as ex: rows = list(ex.map(one, specs))
    _save_cache(cache)
    ok = sum(v["status"] == "pass" for _, _, v in rows)
    res = {"set": set_path, "tasks": len(rows), "gold_net_pass": ok, "seconds": round(time.time() - t0, 1),
           "failures": [(pid, v) for pid, _, v in rows if v["status"] != "pass"],
           "itrs_by_depth": {}}
    from collections import defaultdict
    by = defaultdict(list)
    for _, dp, v in rows:
        if v.get("itrs") is not None: by[dp].append(v["itrs"])
    res["itrs_by_depth"] = {k: sorted(x)[len(x) // 2] for k, x in sorted(by.items())}
    name = os.path.basename(set_path).replace(".json", "")
    json.dump(res, open(os.path.join(OUT, f"gold_{name}.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "failures"}), "failures:", res["failures"][:5])


if __name__ == "__main__":
    if sys.argv[1] == "--gold":
        for s in sys.argv[2:]: score_gold(s)
    else:
        from genome.exp15.metrics import summarize
        for pth in sys.argv[1:]:
            sp = score_samples(pth); print(json.dumps(summarize(sp)))
