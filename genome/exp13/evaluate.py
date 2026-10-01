"""exp13 evaluation: LLM-free authoring by word filling on held-out generated tasks.
   python -m genome.exp13.evaluate heldout [n_pipeline n_reduce n_scan n_position]  -> runs/exp13/heldout.json
   python -m genome.exp13.evaluate llmcmp N                                          -> runs/exp13/llmcmp.json
Per task: k examples drawn with the task's own generator (sizes 4..12), OE search on the examples only, the found
program checked in Python on the hidden suites (seeds 0,1,2), lowered to one net by composing word templates, and the
net run through genome.verify on seeds 0,1,2 (stops at the first failing seed).
"""
from __future__ import annotations
import json, os, random, sys, time
from concurrent.futures import ThreadPoolExecutor
from genome.taskgen import task
from genome.verify import verify, build_cases
from genome.exp13.search import search
from genome.exp13.words import program_py, net_program, show
from genome.exp13.truth import coverage

FAMS = ["pipeline", "reduce", "scan", "position"]
KS = [3, 4, 5, 6, 8, 10]


def examples(p, k, salt=0):
    rng = random.Random(f"exp13|{p.id}|{salt}")
    out = []
    for _ in range(k):
        x = p.gen(rng, rng.randint(4, 12)); out.append((x, p.ref(x)))
    return out


def py_hidden_ok(p, stages, red, seeds=(0, 1, 2)):
    f = program_py(stages, red)
    for s in seeds:
        for _, _, x in build_cases(p, s):
            if f(x) != p.ref(x): return False
    return True


def solve(p, k=3, budget=60.0):
    ex = examples(p, k)
    r = search(ex, isinstance(ex[0][1], list), budget=budget)
    rec = {"id": p.id, "k": k, "found": r["found"], "search_sec": r["sec"], "states": r["states"], "timeout": r["timeout"]}
    if r["found"]:
        rec["prog"] = [show(s) for s in r["stages"]] + ([show(r["reducer"])] if r["reducer"] else [])
        rec["stages"], rec["reducer"] = r["stages"], r["reducer"]
        rec["py_hidden_ok"] = py_hidden_ok(p, r["stages"], r["reducer"])
    return rec


def verify_rec(p, rec):
    t0 = time.time()
    net = net_program(rec["stages"], rec["reducer"]); rec["net_chars"] = len(net)
    rec["lower_sec"] = time.time() - t0
    rec["verify"] = []
    for s in (0, 1, 2):
        v = verify(p, net, seed=s, timeout=30.0, workers=1)
        rec["verify"].append({"seed": s, "status": v["status"], "metrics": v.get("metrics"), "cex": v.get("counterexample") or v.get("reason")})
        if v["status"] != "pass": break
    rec["net_pass"] = len(rec["verify"]) == 3 and all(v["status"] == "pass" for v in rec["verify"])
    rec["verify_sec"] = time.time() - t0
    return rec


def excluded():
    ex = set()
    for f in ("train", "iid_test", "indist", "train_probe", "ei_pool"):
        try:
            for fam, i in json.load(open(f"data/tasksets/{f}.json")): ex.add((fam, i))
        except Exception: pass
    return ex


def heldout(ns):
    ex = excluded(); tasks = []
    for fam, n in zip(FAMS, ns):
        i = 20000
        while sum(1 for t in tasks if t.id.startswith(f"gen_{fam}_")) < n:
            if (fam, i) not in ex: tasks.append(task(fam, i))
            i += 1
    rows = []
    t0 = time.time()
    for p in tasks:
        cv = coverage(p)
        rec = solve(p, 3); rec.update(shape=cv["shape"], core=cv["core"], in_space=cv["in_space"],
                                       truth=[show(s) for s in cv["truth"][0]] + ([show(cv["truth"][1])] if cv["truth"][1] else []))
        # how many examples are needed: Python-level hidden check at larger k (nested example sets)
        rec["by_k"] = {}
        for k in KS:
            r = rec if k == 3 else solve(p, k)
            rec["by_k"][k] = {"found": r["found"], "ok": r.get("py_hidden_ok", False), "sec": r["search_sec"],
                              "prog": r.get("prog")}
        rows.append(rec)
    print(f"search done for {len(rows)} tasks in {time.time() - t0:.1f}s", flush=True)
    with ThreadPoolExecutor(3) as exe:
        list(exe.map(lambda pr: verify_rec(*pr) if pr[1]["found"] else None, [(p, r) for p, r in zip(tasks, rows)]))
    os.makedirs("runs/exp13", exist_ok=True)
    json.dump(rows, open("runs/exp13/heldout.json", "w"), indent=1, default=str)
    print(f"total {time.time() - t0:.0f}s")


def llmcmp(n, k=6):
    """Training tasks that have an accepted, audited native LLM net (runs/datagen/native/seed0): same pipeline (k examples),
    then compare the composed net's interactions/depth with the LLM-authored net on the same verify metrics (seed 0)."""
    import glob
    cands = []
    for f in sorted(glob.glob("runs/datagen/native/seed0/gen_*/state.json")):
        s = json.load(open(f)); pid = s["pid"]; fam = pid.split("_")[1]
        if fam not in FAMS or not s.get("accepted") or s.get("audit") != ["pass", "pass"]: continue
        cands.append((fam, int(pid.rsplit("_", 1)[1]), s["best"]))
    rng = random.Random(13); rng.shuffle(cands)
    per = {f: [c for c in cands if c[0] == f] for f in FAMS}
    quota = {"pipeline": n * 4 // 10, "reduce": n * 3 // 10, "scan": n // 10, "position": n - n * 4 // 10 - n * 3 // 10 - n // 10}
    pick = [c for f in FAMS for c in per[f][:quota[f]]]
    rows = []; tasks = []
    for fam, i, best in pick:
        p = task(fam, i); rec = solve(p, k); rec["llm"] = best; rows.append(rec); tasks.append(p)
    with ThreadPoolExecutor(3) as exe:
        list(exe.map(lambda pr: verify_rec(*pr) if pr[1]["found"] else None, list(zip(tasks, rows))))
    json.dump(rows, open("runs/exp13/llmcmp.json", "w"), indent=1, default=str)
    print(f"llmcmp: {sum(1 for r in rows if r.get('net_pass'))}/{len(rows)} pass")


def cegis_one(p, k=3, rounds=8):
    """Same feedback the LLM authors get: on failure, the smallest failing hidden input of seed 0 (with its expected output)
    is added to the examples and the search reruns. The final net is still judged on seeds 0,1,2."""
    ex = examples(p, k); t0 = time.time(); hist = []
    for rd in range(rounds):
        r = search(ex, isinstance(ex[0][1], list), budget=60.0)
        if not r["found"]: return {"id": p.id, "found": False, "rounds": rd + 1, "sec": time.time() - t0, "hist": hist}
        f = program_py(r["stages"], r["reducer"])
        prog = [show(s) for s in r["stages"]] + ([show(r["reducer"])] if r["reducer"] else [])
        hist.append(prog)
        fails = [x for _, _, x in build_cases(p, 0) if f(x) != p.ref(x)]
        if not fails:
            return {"id": p.id, "found": True, "rounds": rd + 1, "stages": r["stages"], "reducer": r["reducer"], "prog": prog,
                    "sec": time.time() - t0, "hist": hist, "n_examples": len(ex)}
        x = min(fails, key=lambda v: len(repr(v))); ex.append((x, p.ref(x)))
    return {"id": p.id, "found": False, "rounds": rounds, "sec": time.time() - t0, "hist": hist}


def cegis():
    rows = json.load(open("runs/exp13/heldout.json"))
    tasks = [task(r["id"].split("_")[1], int(r["id"].rsplit("_", 1)[1])) for r in rows]
    out = [cegis_one(p) for p in tasks]
    with ThreadPoolExecutor(3) as exe:
        list(exe.map(lambda pr: verify_rec(*pr) if pr[1]["found"] else None, list(zip(tasks, out))))
    json.dump(out, open("runs/exp13/cegis.json", "w"), indent=1, default=str)
    from collections import Counter
    print(f"cegis: net pass {sum(1 for r in out if r.get('net_pass'))}/{len(out)}; rounds {dict(Counter(r['rounds'] for r in out if r.get('net_pass')))}")


if __name__ == "__main__":
    if sys.argv[1] == "cegis": cegis()
    if sys.argv[1] == "heldout": heldout([int(a) for a in sys.argv[2:6]] if len(sys.argv) > 2 else [50, 50, 25, 25])
    elif sys.argv[1] == "llmcmp": llmcmp(int(sys.argv[2]) if len(sys.argv) > 2 else 60)
