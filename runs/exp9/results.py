"""Rebuild every exp9 net, verify on seeds 0,1,2 (3 workers), and tabulate against the frozen author's native and
Bend states (combined exactly as genome/exp_quick.py does). Writes runs/exp9/results.json and prints a markdown table."""
import sys, os, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
os.chdir(ROOT)
from build import NETS
from genome.corpus import load_all
from genome.verify import verify
ok = lambda s: s["accepted"] and s.get("audit") == ["pass", "pass"]
def layers(pats):
    out = {}
    for pat in pats:
        for f in glob.glob(pat):
            s = json.load(open(f))
            if s["pid"] not in out or (not ok(out[s["pid"]][0]) and ok(s)): out[s["pid"]] = (s, os.path.dirname(f))
    return out
NB = layers(["runs/g1/native/seed0/*/state.json", "runs/g1r1/native/seed0/*/state.json", "runs/probe2/dsv4/native/seed0/*/state.json", "runs/g1esc/native/seed0/*/state.json"])
BB = layers(["runs/g1/b1/seed0/*/state.json", "runs/g1r1/b1/seed0/*/state.json", "runs/g1esc/b1/seed0/*/state.json"])
def prev(Dd, p):
    if p not in Dd or not ok(Dd[p][0]) or not Dd[p][0].get("best"): return None
    b = Dd[p][0]["best"]; return {"depth": b["depth_median_big"], "itrs": b["itrs_median_big"], "depth_max": b.get("depth_max"), "itrs_max": b.get("itrs_max")}
P = load_all(); res = {}
progs = sys.argv[1:] or sorted(NETS)
for prog in progs:
    net = NETS[prog](16); open(os.path.join(D, prog + ".hvm"), "w").write(net)
    r = {"seeds": {}}
    for s in (0, 1, 2):
        v = verify(P[prog], net, s, timeout=60, workers=3)
        r["seeds"][s] = {"status": v["status"], **(v.get("metrics") or {})}
        print(prog, s, v["status"], v.get("metrics"), v.get("counterexample") or "", flush=True)
    r["native_prev"] = prev(NB, prog); r["bend"] = prev(BB, prog); res[prog] = r
old = json.load(open(os.path.join(D, "results.json"))) if os.path.exists(os.path.join(D, "results.json")) else {}
old.update(res); json.dump(old, open(os.path.join(D, "results.json"), "w"), indent=1)
