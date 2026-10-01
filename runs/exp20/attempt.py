"""exp20 attempt counter (copy of runs/exp14/attempt.py, conditions A/B): the ONLY way an author may test a net.
Verifies seed 0 with the unmodified genome.verify.verify (2 workers; one verification at a time machine-wide via a
lock file), logs every attempt, keeps a copy of each net, and refuses a 7th attempt. New vs exp14 (both conditions):
a net.hvm older than the build.py next to it, or identical to the previous attempt, is refused WITHOUT using an
attempt (the exp14 stale-net failure); per-case timeout 10 s (changed from 60 s at 2026-09-30 ~run midpoint, see nudges.log).
usage: python3 runs/exp20/attempt.py <A|B> <prog> <net.hvm>"""
import sys, os, json, time, fcntl, shutil
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(D)))
from genome.corpus import load_all
from genome.verify import verify, feedback_text


def prescreen(p, book):
    """Fast fail (added mid-run, both conditions): run the contract's own edge examples (shown in the brief) first,
    smallest first, 5 s each; the first one that is wrong / does not run is reported in verify's format without
    running the full suite. A net that passes them all goes to the unmodified verify (the only way to PASS)."""
    from genome.verify import assemble, check_book, _short
    from genome.executor import run_net
    from genome.types import decode
    if check_book(book): return None
    for x in sorted(p.edges, key=lambda v: len(repr(v))):
        exp = p.ref(x)
        r = run_net(assemble(p, book, x), "run", 5.0)
        if not r.ok: why, got = "net did not run to a result", r.error
        else:
            try:
                got = decode(r.result, p.out); why = None if got == exp else "wrong answer"
            except Exception as e:
                why, got = f"result is not the canonical encoding: {e}", r.result[:240]
        if why:
            return {"status": "fail", "cases": len(p.edges), "failed": 1, "seed": 0, "suite": "prescreen",
                    "metrics": None, "counterexample": {"why": why, "kind": "edge", "size": None, "input": _short(x),
                                                        "expected": _short(exp), "got": _short(got)}}
    return None

MAX = 6
TIMEOUT = 10.0   # per case; every passing net so far runs a case in < 2 s (exp14 used 60 s; hanging nets held the lock)
cond, prog, net = sys.argv[1], sys.argv[2], sys.argv[3]
assert cond in ("A", "B"), cond
wd = os.path.join(D, cond, prog); os.makedirs(wd, exist_ok=True)
log = os.path.join(wd, "attempts.jsonl")
prev = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
if any(r["status"] == "pass" for r in prev):
    print("Already PASSED; no more attempts needed."); sys.exit(0)
if len(prev) >= MAX:
    print(f"REFUSED: all {MAX} attempts used."); sys.exit(2)
bp = os.path.join(os.path.dirname(os.path.abspath(net)), "build.py")
if os.path.exists(bp) and os.path.getmtime(net) < os.path.getmtime(bp):
    print("NOT SUBMITTED (no attempt used): net.hvm is older than build.py. Run build.py first (fix any GlueError)."); sys.exit(3)
book = open(net).read()
bsrc = open(bp).read() if os.path.exists(bp) else None
with open(os.path.join(D, ".verify.lock"), "w") as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    # re-check under the lock (several calls may have queued while another author's net was running)
    prev = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
    if any(r["status"] == "pass" for r in prev):
        print("Already PASSED; no more attempts needed."); sys.exit(0)
    if len(prev) >= MAX:
        print(f"REFUSED: all {MAX} attempts used."); sys.exit(2)
    k = len(prev) + 1
    if k > 1 and os.path.exists(os.path.join(wd, f"attempt{k-1}.hvm")) and open(os.path.join(wd, f"attempt{k-1}.hvm")).read() == book:
        print(f"NOT SUBMITTED (no attempt used): this net is identical to attempt {k-1}, whose result was:\n"
              + prev[-1]["feedback"]); sys.exit(3)
    open(os.path.join(wd, f"attempt{k}.hvm"), "w").write(book)
    if bsrc is not None: open(os.path.join(wd, f"attempt{k}_build.py"), "w").write(bsrc)
    t = time.time(); res = prescreen(load_all()[prog], book) or verify(load_all()[prog], book, 0, TIMEOUT, 2); secs = time.time() - t
fb = feedback_text(load_all()[prog], res)
rec = {"attempt": k, "time": time.strftime("%H:%M:%S"), "status": res["status"], "secs": round(secs, 1),
       "feedback": fb, "metrics": res.get("metrics")}
with open(log, "a") as f: f.write(json.dumps(rec, default=str) + "\n")
print(f"ATTEMPT {k} of {MAX}: {fb}")
sys.exit(0 if res["status"] == "pass" else 1)
