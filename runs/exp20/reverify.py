"""Full re-verification (unmodified genome.verify, seed 0, 60 s per case, 2 workers) of attempts whose recorded failure
was a timeout but which ran correctly under recheck_timeouts.py. -> runs/exp20/reverify.json"""
import sys, os, json, fcntl
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(os.path.dirname(D)))
from genome.corpus import load_all
from genome.verify import verify, feedback_text
ps = load_all(); out = {}
for key in sys.argv[1:]:
    c, p, a = key.split("/")
    book = open(os.path.join(D, c, p, f"attempt{a}.hvm")).read()
    with open(os.path.join(D, ".verify.lock"), "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        r = verify(ps[p], book, 0, 60.0, 2)
    out[key] = {"status": r["status"], "feedback": feedback_text(ps[p], r)[:400], "metrics": r.get("metrics")}
    print(key, r["status"], feedback_text(ps[p], r)[:200].replace("\n", " | "), flush=True)
json.dump(out, open(os.path.join(D, "reverify.json"), "w"), indent=1, default=str)
