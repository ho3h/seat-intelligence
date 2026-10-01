"""Stage 2: explanations for every frozen decision by every method, classified by counterfactual reruns through the net.
usage: python3 -m genome.hero5.run_eval <set.json> <tracedir> <out.jsonl> [workers]"""
import sys, os, json, time
from concurrent.futures import ProcessPoolExecutor
from .core import Problem
from .evalx import *

METHODS = ["T-D", "T-F", "T-F+G", "T-F+DD", "T-F+DDc", "DD", "DDc", "LOO", "G-full"]


def load_problem(o, tag):
    pd = o["problems"][tag]
    pr = Problem(n=pd["n"], cap=pd["cap"], mnl=[tuple(m) for m in pd["mnl"]], edges=[tuple(e) for e in pd["edges"]], name=pd["name"])
    pr.names = pd.get("names", {})
    return pr


def explain(pr, dec, tr, method, sample=False):
    """-> (E fact set, cost dict, sentence, extra)"""
    a, b = str(dec["a"]), str(dec["b"])
    allf = set(range(pr.F)) - ({dec["subject"]} if dec["subject"] is not None else set())
    orc = Oracle(pr, dec, use_net=False)     # search by reference (identical answers, checked on every classification call)
    t0 = time.time()
    Call = set(tr["mode2"]["sets"][a]) | set(tr["mode2"]["sets"][b])
    if method == "T-D":
        E = set(tr["mode1"]["sets"][a]) | set(tr["mode1"]["sets"][b]); roles = None
    elif method == "T-F":
        E = set(tr["mode2"]["sets"][a]) | set(tr["mode2"]["sets"][b]); roles = None
    elif method == "T-F+G":
        C = set(tr["mode2"]["sets"][a]) | set(tr["mode2"]["sets"][b])
        E, why, roles = extract(pr, dec, C)
    elif method == "LOO":
        # leave-one-out: rerun with each single fact removed from the full input; keep the facts whose removal flips D
        base = orc(allf)
        E = {f for f in sorted(allf) if orc(allf - {f}) != base}; roles = None
    elif method == "G-full":
        E, why, roles = extract(pr, dec, allf)
    elif method == "T-F+DD":
        C = sorted((set(tr["mode2"]["sets"][a]) | set(tr["mode2"]["sets"][b])) - ({dec["subject"]} if dec["subject"] is not None else set()))
        E = ddmin(C, orc); roles = None
        if E is None: E = set(C)
        E = set(E)
    elif method == "DD":
        E = ddmin(sorted(allf), orc); roles = None
        if E is None: E = set(allf)
        E = set(E)
    elif method in ("DDc", "T-F+DDc"):
        # context-preserving delta debugging: for a MERGE decision the blocking clauses (all MNL rows and the cap) stay in every
        # test world and only the edge rows are minimised; for a refusal the blockers are part of the answer, so it is plain DD.
        U = sorted(allf) if method == "DDc" else sorted((set(tr["mode2"]["sets"][a]) | set(tr["mode2"]["sets"][b])) - ({dec["subject"]} if dec["subject"] is not None else set()))
        if dec["polarity"] == "same":
            fixed = set(range(pr.E, pr.E + pr.M + 1))
            U = [k for k in U if k < pr.E]
            E = ddmin(U, lambda S: orc(set(S) | fixed)); roles = None
        else:
            E = ddmin(U, orc); roles = None
        if E is None: E = set(U)
        E = set(E)
    E = set(E) - ({dec["subject"]} if dec["subject"] is not None else set())
    cost = dict(net_calls=len(orc.log), ref_wall=time.time() - t0, mismatch=orc.mismatch)
    if sample and orc.log and method != "LOO":
        n, secs = orc.replay_on_net(); cost.update(net_replay_calls=n, net_replay_secs=secs)
    return E, cost, roles


def one(args):
    setpath, tracedir, did = args
    o = json.load(open(setpath))
    dec = next(d for d in o["decisions"] if d["id"] == did)
    pr = load_problem(o, dec["src"])
    tr = json.load(open(os.path.join(tracedir, dec["src"] + ".json")))
    rows = []
    memo = {}
    subj = {dec["subject"]} if dec["subject"] is not None else set()
    allf = set(range(pr.F)) - subj
    Cf = (set(tr["mode2"]["sets"][str(dec["a"])]) | set(tr["mode2"]["sets"][str(dec["b"])])) - subj
    order = ["T-D", "T-F", "T-F+G", "DD", "DDc", "LOO", "T-F+DD", "T-F+DDc", "G-full"]
    for m in order:
        if m in ("T-F+DD", "T-F+DDc") and Cf == allf:
            E, cost, roles = memo[m[4:]]                       # causal set == all facts: identical run, reuse
            cost = dict(cost, reused_from=m[4:])
        else:
            E, cost, roles = explain(pr, dec, tr, m, sample=(did % 5 == 0))
        memo[m] = (E, cost, roles)
        # classification uses a fresh oracle so the cost above is the method's own
        corc = Oracle(pr, dec, use_net=True)
        c = classify(pr, dec, E, corc)
        if len(E) <= 40:
            full = set(range(pr.F)); base = corc.ref(full)      # D in the untouched input (must be True)
            tot = sum(1 for f in E if corc.ref(full - {f}) != base)   # facts whose deletion from the FULL input flips D
            c["N_full"] = [tot, len(E)]; c["D_full"] = bool(base)
        c.update(id=did, method=m, kind=dec["kind"], src=dec["src"], polarity=dec["polarity"], truth=truth_reason(dec), cost=cost,
                 check_calls=corc.calls_net, check_mismatch=corc.mismatch)
        if m in ("T-F+G", "G-full") and len(E) <= 25:
            c["sentence"] = render(pr, dec, E, roles) if roles else None
            c["E"] = sorted(E)
        elif len(E) <= 25: c["E"] = sorted(E)
        rows.append(c)
    return rows


if __name__ == "__main__":
    setpath, tracedir, outp = sys.argv[1:4]
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 4
    o = json.load(open(setpath))
    ids = [d["id"] for d in o["decisions"]]
    done = set()
    if os.path.exists(outp):
        for line in open(outp):
            done.add(json.loads(line)["id"])
    lo, hi = (int(x) for x in os.environ.get("HERO5_IDS", f"0-{len(ids) - 1}").split("-"))
    todo = [i for i in ids if i not in done and lo <= i <= hi and os.path.exists(os.path.join(tracedir, next(d for d in o["decisions"] if d["id"] == i)["src"] + ".json"))]
    with ProcessPoolExecutor(workers) as ex, open(outp, "a") as f:
        for rows in ex.map(one, [(setpath, tracedir, i) for i in todo]):
            for r in rows: f.write(json.dumps(r) + "\n")
            f.flush()
            print(rows[0]["id"], [(r["method"], r["cls"]) for r in rows], flush=True)
