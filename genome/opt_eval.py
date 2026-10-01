"""Recompute the G1 seed-0 native-vs-Bend comparison with the optimizer applied to the Bend arm (and the native arm, for symmetry)."""
import glob, json, os, sys, statistics as S
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from genome import bend_io as B
from genome.opt import optimize
from genome.corpus import load_all
from genome.verify import verify, verify_b1

R = load_all()
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

def one(pid):
    sb, db = BB[pid]
    if not ok(sb) or not os.path.exists(os.path.join(db, "best.bend")): return pid, None
    code = open(os.path.join(db, "best.bend")).read()
    book, err = B.compile_bend(B.bend_source(R[pid], code))
    if err: return pid, None
    opt, st = optimize(book)
    r = verify_b1(R[pid], "", hvm_book=opt, workers=4)
    if r["status"] != "pass": return pid, {"failed": True, "stats": st}
    return pid, {"metrics": r["metrics"], "stats": st}

with ThreadPoolExecutor(4) as ex: res = dict(ex.map(one, [p for p in BB if ok(BB[p][0])]))
json.dump(res, open("runs/opt_eval_bend.json", "w"))
broke = [p for p, v in res.items() if v and v.get("failed")]
print("optimized bend nets:", len(res), "| broke on re-verify:", len(broke), broke[:5])
rows = []
for p, v in res.items():
    if not v or v.get("failed"): continue
    sn = NB.get(p)
    if not sn or not ok(sn[0]) or not sn[0].get("best"): continue
    n = sn[0]["best"]; b0 = BB[p][0]["best"]; b1 = v["metrics"]
    g0 = max(1 - n["itrs_median_big"] / b0["itrs_median_big"], 1 - n["depth_median_big"] / b0["depth_median_big"])
    g1 = max(1 - n["itrs_median_big"] / b1["itrs_median_big"], 1 - n["depth_median_big"] / b1["depth_median_big"])
    rows.append((p, g0, g1, 1 - b1["itrs_median_big"] / b0["itrs_median_big"]))
print(f"programs solved by both: {len(rows)}")
print(f"native wins vs plain Bend: {sum(r[1] > 0 for r in rows)} ({100 * sum(r[1] > 0 for r in rows) / len(rows):.0f}%), median gain {100 * S.median(r[1] for r in rows):.0f}%")
print(f"native wins vs optimized Bend: {sum(r[2] > 0 for r in rows)} ({100 * sum(r[2] > 0 for r in rows) / len(rows):.0f}%), median gain {100 * S.median(r[2] for r in rows):.0f}%")
print(f"optimizer's own median interaction reduction on Bend nets: {100 * S.median(r[3] for r in rows):.1f}%")
