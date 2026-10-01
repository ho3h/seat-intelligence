"""Score sampled programs: parse -> compare with the gold program (exact, or equal semantics on probe inputs) -> ONE net assembled from
the verified word templates -> genome.verify (seed 0) against the GOLD reference. Cached per (gold, program).
   python -m genome.hero4.score samples.json [...]      python -m genome.hero4.score --gold sets.json   (verifies every gold program)
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import hashlib, json, os, random, sys, threading, time
from concurrent.futures import ThreadPoolExecutor
from genome.corpus import Program as CP
from genome.types import u24, list_of
from genome.verify import verify
from genome.hero4 import lang, refs, tasks as T
from genome.hero4.wordtests import edges

CACHE = _REPO + "/runs/hero4/vcache.json"
_lock = threading.Lock(); L_ = list_of(u24)


def _load():
    try: return json.load(open(CACHE))
    except Exception: return {}


def _save(c):
    tmp = CACHE + ".tmp"; json.dump(c, open(tmp, "w")); os.replace(tmp, CACHE)


def probes():
    r = random.Random(123); xs = []
    for n in list(range(0, 8)) + [10, 14, 20, 27, 34, 34, 40] * 3:
        xs.append(refs.gen_guests(r, n, skew=(n % 2 == 0)))
    return xs + edges()


PROBES = probes()


def program_for(gold_words):
    text = lang.to_text(gold_words)
    pid = "h4p_" + hashlib.sha1(text.encode()).hexdigest()[:10]
    return CP(pid, "H4", text, L_, L_, lambda xs, g=list(gold_words): refs.run_program(g, list(xs)),
              lambda rng, n: refs.gen_guests(rng, n), [0, 1, 2, 3, 5, 8, 12, 20], [34, 48], edges(), None)


def refute(gold, prog):
    for x in PROBES:
        try:
            if refs.run_program(prog, list(x)) != refs.run_program(gold, list(x)): return x
        except Exception: return x
    return None


def verify_prog(gold, prog, cache, seed=0):
    key = lang.to_text(gold) + "||" + lang.to_text(prog) + f"||{seed}"
    with _lock:
        if key in cache: return cache[key]
    cx = refute(gold, prog)
    if cx is not None:
        v = {"status": "fail", "why": "semantics differ from gold on a probe input", "refuted": True}
    else:
        try:
            net = lang.assemble(prog); r = verify(program_for(gold), net, seed=seed, timeout=20.0, workers=1)
            v = {"status": r["status"], "why": (r.get("reason") or (r.get("counterexample") or {}).get("why") or "")[:160],
                 "itrs": (r.get("metrics") or {}).get("itrs_median_big"), "depth": (r.get("metrics") or {}).get("depth_median_big")}
        except Exception as e:
            v = {"status": "error", "why": repr(e)[:160]}
    with _lock: cache[key] = v
    return v


def score_file(path, threads=4):
    d = json.load(open(path)); cache = _load(); tasks = {t["id"]: t for t in d["tasks"]}; t0 = time.time()
    jobs = [(pid, j, txt) for pid, tx in d["samples"].items() for j, txt in enumerate(tx)]
    def one(job):
        pid, j, txt = job; t = tasks[pid]; gold = T.gold(t)
        try: prog = lang.parse(txt)
        except lang.ParseError as e: return pid, j, {"status": "parse", "why": str(e)[:100], "text": txt[:160]}
        v = verify_prog(gold, prog, cache)
        return pid, j, {"status": v["status"], "prog": lang.to_text(prog), "exact": prog == gold, "why": v.get("why", "")[:100]}
    res = {pid: [None] * len(v) for pid, v in d["samples"].items()}
    with ThreadPoolExecutor(threads) as ex:
        for pid, j, r in ex.map(one, jobs): res[pid][j] = r
    _save(cache)
    meta = dict(d["meta"]); meta["score_seconds"] = round(time.time() - t0, 1)
    out = {"meta": meta, "tasks": d["tasks"], "scored": res, "gold": {pid: lang.to_text(T.gold(t)) for pid, t in tasks.items()}}
    sp = path.replace(".json", ".scored.json"); json.dump(out, open(sp, "w"))
    return sp


def score_gold(set_path, threads=4):
    tasks = json.load(open(set_path)); cache = _load(); seen = {}
    for t in tasks: seen.setdefault(lang.to_text(T.gold(t)), T.gold(t))
    t0 = time.time(); items = list(seen.items())
    def one(kv):
        g = kv[1]; return kv[0], verify_prog(g, g, cache)
    with ThreadPoolExecutor(threads) as ex: rows = list(ex.map(one, items))
    _save(cache)
    bad = [(k, v) for k, v in rows if v["status"] != "pass"]
    print(json.dumps({"set": set_path, "tasks": len(tasks), "distinct_gold": len(items), "pass": len(items) - len(bad), "secs": round(time.time() - t0)}), bad[:3])
    return rows


def repair_file(path, threads=4):
    """DIAGNOSTIC (never the headline): a sample that fails ONLY because it has no closing word gets the GOLD closing line appended and is
    re-scored. Measures whether the arrangement part (the new word) was right."""
    d = json.load(open(path)); cache = _load(); tasks = {t["id"]: t for t in d["tasks"]}; t0 = time.time()
    jobs = [(pid, j, txt) for pid, tx in d["samples"].items() for j, txt in enumerate(tx)]
    def one(job):
        pid, j, txt = job; t = tasks[pid]; gold = T.gold(t)
        try: prog = lang.parse(txt); rep = False
        except lang.ParseError as e:
            if "closing" not in str(e): return pid, j, {"status": "parse", "prog": None}
            try: prog = lang.parse(txt.rstrip() + "\n" + lang.fmt_word(gold[-1])); rep = True
            except lang.ParseError as e2: return pid, j, {"status": "parse", "prog": None}
        v = verify_prog(gold, prog, cache)
        return pid, j, {"status": v["status"], "prog": lang.to_text(prog), "repaired": rep}
    res = {pid: [None] * len(v) for pid, v in d["samples"].items()}
    with ThreadPoolExecutor(threads) as ex:
        for pid, j, r in ex.map(one, jobs): res[pid][j] = r
    _save(cache)
    out = {"meta": d["meta"], "tasks": d["tasks"], "scored": res, "gold": {pid: lang.to_text(T.gold(t)) for pid, t in tasks.items()}}
    sp = path.replace(".json", ".repaired.json"); json.dump(out, open(sp, "w"))
    return sp


if __name__ == "__main__":
    if sys.argv[1] == "--repair":
        for p in sys.argv[2:]: print(repair_file(p))
    elif sys.argv[1] == "--gold":
        for s in sys.argv[2:]: score_gold(s)
    else:
        for p in sys.argv[1:]: print(score_file(p))


