"""Re-run every attempt whose failure was a timeout / 'did not run', with generous timeouts, to separate genuine hangs
from harness artifacts (short per-case timeouts, machine load, another agent's `pkill -f hvm` at ~05:00).
Result -> runs/exp20/recheck_timeouts.json"""
import sys, os, json, fcntl
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(os.path.dirname(D)))
from genome.corpus import load_all
from genome.verify import verify, assemble
from genome.executor import run_net
from genome.types import decode
ps = load_all(); out = {}
for c in ("A", "B"):
    for p in sorted(os.listdir(os.path.join(D, c))):
        log = os.path.join(D, c, p, "attempts.jsonl")
        if not os.path.exists(log): continue
        for l in open(log):
            r = json.loads(l)
            if r["status"] == "pass" or not ("did not run" in r["feedback"] or "timeout" in r["feedback"]): continue
            book = open(os.path.join(D, c, p, f"attempt{r['attempt']}.hvm")).read()
            prog = ps[p]; edge = []
            with open(os.path.join(D, ".verify.lock"), "w") as lk:
                fcntl.flock(lk, fcntl.LOCK_EX)
                for x in sorted(prog.edges, key=lambda v: len(repr(v)))[:1]:
                    rr = run_net(assemble(prog, book, x), "run", 120.0)
                    ok = rr.ok and decode(rr.result, prog.out) == prog.ref(x) if rr.ok else False
                    edge.append({"input": repr(x)[:60], "ran": rr.ok, "correct": ok, "secs": rr.secs,
                                 "err": None if rr.ok else str(rr.error)[:80]})
            key = f"{c}/{p}/{r['attempt']}"
            out[key] = {"orig": r["feedback"][:200], "recheck_edges_120s": edge,
                        "verdict": "genuine hang/crash" if not all(e["ran"] for e in edge) else
                                   ("ran but wrong" if not all(e["correct"] for e in edge) else "ran and correct on edges: RE-VERIFY")}
            print(key, out[key]["verdict"], [(e["ran"], e["correct"], round(e["secs"] or 0, 1)) for e in edge], flush=True)
json.dump(out, open(os.path.join(D, "recheck_timeouts.json"), "w"), indent=1)
