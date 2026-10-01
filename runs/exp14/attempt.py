"""exp14 attempt counter: the ONLY way a weak author may test a net. Verifies seed 0 with the unmodified
genome.verify.verify (3 workers; one verification at a time machine-wide via a lock file), logs every attempt, keeps a
copy of each net, and refuses a 7th attempt.
usage: python3 runs/exp14/attempt.py <checked|unchecked> <prog> <net.hvm>"""
import sys, os, json, time, fcntl, shutil
D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(D)))
from genome.corpus import load_all
from genome.verify import verify, feedback_text

MAX = 6
cond, prog, net = sys.argv[1], sys.argv[2], sys.argv[3]
assert cond in ("checked", "unchecked", "checked_sonnet", "unchecked_sonnet"), cond
wd = os.path.join(D, cond, prog); os.makedirs(wd, exist_ok=True)
log = os.path.join(wd, "attempts.jsonl")
prev = [json.loads(l) for l in open(log)] if os.path.exists(log) else []
if any(r["status"] == "pass" for r in prev):
    print("Already PASSED; no more attempts needed."); sys.exit(0)
if len(prev) >= MAX:
    print(f"REFUSED: all {MAX} attempts used."); sys.exit(2)
k = len(prev) + 1
book = open(net).read()
shutil.copy(net, os.path.join(wd, f"attempt{k}.hvm"))
with open(os.path.join(D, ".verify.lock"), "w") as lk:
    fcntl.flock(lk, fcntl.LOCK_EX)
    t = time.time(); res = verify(load_all()[prog], book, 0, 60.0, 3); secs = time.time() - t
fb = feedback_text(load_all()[prog], res)
rec = {"attempt": k, "time": time.strftime("%H:%M:%S"), "status": res["status"], "secs": round(secs, 1),
       "feedback": fb, "metrics": res.get("metrics")}
with open(log, "a") as f: f.write(json.dumps(rec, default=str) + "\n")
print(f"ATTEMPT {k} of {MAX}: {fb}")
sys.exit(0 if res["status"] == "pass" else 1)
