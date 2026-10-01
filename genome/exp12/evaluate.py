"""Swing 18 evaluation: apply the lookahead transformer with K in {2,4,8,16} to accepted audit-clean native nets
(T1, T2, T4 as genome/opt_eval.py finds them; T3 = runs/exp5 hand nets, both as shipped (K=16 stream) and rebuilt with
the one-cell stream K=1), verify every result on seeds 0,1,2 (at most 3 processes), write runs/exp12/results.jsonl.
usage: python -m genome.exp12.evaluate [tier ...]"""
import glob, json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
os.chdir(ROOT)
from genome.corpus import load_all
from genome.verify import verify
from genome.exp12.lookahead import transform, Fail, net_size

R = load_all()
OUT = "runs/exp12"
ok = lambda s: s["accepted"] and s.get("audit") == ["pass", "pass"]


def native_nets():
    out = {}
    for pat in ["runs/g1/native/seed0/*/state.json", "runs/g1r1/native/seed0/*/state.json",
                "runs/probe2/dsv4/native/seed0/*/state.json", "runs/g1esc/native/seed0/*/state.json"]:
        for f in glob.glob(pat):
            s = json.load(open(f)); d = os.path.dirname(f)
            if not ok(s) or not os.path.exists(os.path.join(d, "best.hvm")): continue
            if s["pid"] not in out: out[s["pid"]] = os.path.join(d, "best.hvm")
    return out


def sets(tiers):
    nn = native_nets(); items = []
    for pid in sorted(nn):
        if pid[:2] in tiers and pid[:2] != "t3": items.append((pid[:2], pid, nn[pid]))
        if pid[:2] == "t3" and "t3n" in tiers: items.append(("t3n", pid, nn[pid]))
    if "t3" in tiers:
        for f in sorted(glob.glob("runs/exp5/t3_*.hvm")):
            b = os.path.basename(f)[:-4]
            if "__" in b: continue
            items.append(("t3x16", b, f))
        for f in sorted(glob.glob("runs/exp12/exp5_k1/t3_*.hvm")):
            items.append(("t3x1", os.path.basename(f)[:-4], f))
    return items


def slim(r):
    return {"status": r["status"], "metrics": r.get("metrics"), "cex": r.get("counterexample"), "reason": (r.get("reason") or "")[:300]}


def main(tiers):
    done = set()
    res_path = os.path.join(OUT, "results.jsonl")
    if os.path.exists(res_path):
        for line in open(res_path): j = json.loads(line); done.add((j["set"], j["pid"]))
    for st, pid, path in sets(tiers):
        if (st, pid) in done: continue
        t0 = time.time()
        text = open(path).read(); p = R[pid]
        rec = {"set": st, "pid": pid, "path": path, "size": net_size(text), "orig": slim(verify(p, text, 0, workers=3)), "K": {}}
        for K in (2, 4, 8, 16):
            try:
                new, info = transform(text, K)
            except Fail as e:
                rec["applies"] = False; rec["why"] = str(e)[:300]; break
            except Exception as e:  # transformer crash counts as not applicable, recorded
                rec["applies"] = False; rec["why"] = f"transformer error: {type(e).__name__}: {e}"[:300]; break
            rec["applies"] = True; rec["chains"] = info["chains"]; rec["log"] = info["log"][:6]
            d = os.path.join(OUT, "nets", st); os.makedirs(d, exist_ok=True)
            fp = os.path.join(d, f"{pid}.K{K}.hvm"); open(fp, "w").write(new)
            kr = {"size": net_size(new), "seeds": {}}
            for seed in (0, 1, 2):
                r = verify(p, new, seed, workers=3)
                kr["seeds"][seed] = slim(r)
                if r["status"] != "pass": break
            kr["pass"] = all(v["status"] == "pass" for v in kr["seeds"].values()) and len(kr["seeds"]) == 3
            rec["K"][K] = kr
        rec["secs"] = round(time.time() - t0, 1)
        with open(res_path, "a") as f: f.write(json.dumps(rec, default=str) + "\n")
        print(st, pid, rec.get("applies"), {k: (v["pass"], (v["seeds"][0]["metrics"] or {}).get("depth_median_big")) for k, v in rec["K"].items()},
              (rec["orig"]["metrics"] or {}).get("depth_median_big"), rec["secs"], flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or ["t1", "t2", "t3", "t4"])
