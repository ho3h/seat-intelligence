"""Rebuild every exp19 net, verify on seeds 0,1,2 (2 workers), and record the Bend B1 baseline (runs/g1*/b1 state
'best', with its accepted/audit flags). Writes runs/exp19/results.json."""
import sys, os, json, glob
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
os.chdir(ROOT)
from build import NETS
from genome.corpus import load_all
from genome.verify import verify
P = load_all(); res = {}
for prog in (sys.argv[1:] or sorted(NETS)):
    net = NETS[prog](16); open(os.path.join(D, prog + ".hvm"), "w").write(net)
    r = {"seeds": {}, "bend": []}
    for s in (0, 1, 2):
        v = verify(P[prog.split("__")[0]], net, s, timeout=60, workers=2)
        r["seeds"][s] = {"status": v["status"], **(v.get("metrics") or {})}
        print(prog, s, v["status"], v.get("metrics"), v.get("counterexample") or "", flush=True)
    for f in sorted(glob.glob(f"runs/g1*/b1/seed0/{prog.split('__')[0]}/state.json")):
        st = json.load(open(f))
        if st.get("best"): r["bend"].append({"state": f, "accepted": st.get("accepted"), "audit": st.get("audit"), **st["best"]})
    res[prog] = r
old = json.load(open(os.path.join(D, "results.json"))) if os.path.exists(os.path.join(D, "results.json")) else {}
old.update(res); json.dump(old, open(os.path.join(D, "results.json"), "w"), indent=1)
