"""Executor-guided search over verified nets (exp3). Keep-if-better (Pareto on median big-case interactions and parallel depth),
judged by the hidden-suite verifier. Per (program, arm): baseline verify -> phase 1 targeted peepholes (greedy) -> phase 2
(1+1) evolution with random targeted/structural mutations -> final re-verification on seeds 1 and 2 (walk back the
accepted chain on failure). Budget = number of candidates that reach the executor, identical for both arms.

usage: python3 -m genome.exp3.search --budget 200 --procs 16 [--pids a,b] [--tag main]
"""
from __future__ import annotations
import argparse, json, os, random, sys, time, traceback
from concurrent.futures import ProcessPoolExecutor, as_completed
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from genome import bend_io as B
from genome.corpus import load_all
from genome.executor import run_net
from genome.netast import parse_book, print_book
from genome.types import decode
from genome.verify import verify, verify_b1, build_cases, assemble, check_book
from genome.exp3 import mut as M

R = None


def prog(pid):
    global R
    if R is None: R = load_all()
    return R[pid]


# ------------------------------------------------------------------ evaluation
def asm(p, arm, book, x):
    return assemble(p, book, x) if arm == "native" else B.assemble_bend(p, book, x, digest=False)


def dec(p, arm, text):
    return decode(text, p.out) if arm == "native" else B.decode_bend(text, p.out)


class Probe:
    """Cheap pre-screen: 4 small cases for correctness (fast fail) + 1 large case under the depth oracle (correctness + metrics)."""

    def __init__(self, p, arm):
        cases = build_cases(p, 0)
        sm = sorted([c for c in cases if c[0] == "small"], key=lambda c: -(c[1] or 0))
        small = [c for c in cases if c[0] == "edge"][:2] + sm[:4]
        bigs = [c for c in cases if c[0] == "big"]
        self.small = [(c[2], p.ref(c[2])) for c in small]
        big = bigs[1] if len(bigs) > 1 else bigs[0]
        self.big = (big[2], p.ref(big[2]))
        self.p, self.arm = p, arm

    def run(self, book, timeout):
        p, arm = self.p, self.arm
        for x, e in self.small:
            r = run_net(asm(p, arm, book, x), "run", min(timeout, 10))
            if not r.ok: return None
            try:
                if dec(p, arm, r.result) != e: return None
            except Exception: return None
        x, e = self.big
        r = run_net(asm(p, arm, book, x), "depth", timeout)  # the depth oracle does not print the result; metrics only
        if not r.ok: return None
        return (r.itrs, r.depth)


def full(p, arm, book, seed, timeout, workers=3):
    if arm == "native":
        return verify(p, book, seed=seed, timeout=timeout, workers=workers)
    return verify_b1(p, "", seed=seed, timeout=timeout, workers=workers, hvm_book=book)


def key(m):
    return (m["itrs_median_big"], m["depth_median_big"])


def better(a, b):
    """a Pareto-better than b (tuples)."""
    return a[0] <= b[0] and a[1] <= b[1] and (a[0] < b[0] or a[1] < b[1])


# ------------------------------------------------------------------ one (program, arm)
def search(pid, arm, budget, seed=0, outdir="runs/exp3/out"):
    t0 = time.time()
    p = prog(pid)
    base_txt = open(os.path.join(ROOT, f"runs/exp3/base/{pid}.{arm}.hvm")).read()
    defs, order = parse_book(base_txt)
    rng = random.Random(f"{pid}|{arm}|{seed}")
    log = {"pid": pid, "arm": arm, "budget": budget, "accepted": [], "ops_tried": {}, "ops_prescreen_pass": {}}
    b0 = full(p, arm, base_txt, 0, 60)
    if b0["status"] != "pass":
        log["error"] = "baseline failed seed0"; return log
    probe = Probe(p, arm)
    ts = time.time(); pr0 = probe.run(base_txt, 120); tprobe = time.time() - ts
    if pr0 is None:
        log["error"] = "baseline probe failed"; return log
    ptimeout = max(4.0, 15 * tprobe); vtimeout = max(8.0, 15 * tprobe)
    base_size = M.total_size(defs)
    cur = {"defs": defs, "order": order, "txt": base_txt, "m": b0["metrics"], "probe": pr0}
    chain = [(base_txt, b0["metrics"], "base")]
    log["base"] = b0["metrics"]; log["base_probe"] = pr0
    used = 0

    def text_of(d, o):
        o2 = [n for n in o if n in d] + [n for n in d if n not in o]
        return print_book(d, o2), o2

    def attempt(new_defs, opname):
        """Evaluate a candidate; accept into cur if Pareto-better. Returns True if accepted."""
        nonlocal used, cur
        if new_defs is None or used >= budget: return False
        if new_defs is cur["defs"]: return False
        new_defs, _o = M.prune(new_defs, list(cur["order"]) + [n for n in new_defs if n not in cur["order"]])
        if M.lint(new_defs, arm == "native"): return False
        if M.total_size(new_defs) > 4 * base_size + 200: return False
        txt, o2 = text_of(new_defs, cur["order"])
        if txt == cur["txt"]: return False
        if arm == "native" and check_book(txt): return False
        used += 1
        log["ops_tried"][opname] = log["ops_tried"].get(opname, 0) + 1
        pr = probe.run(txt, ptimeout)
        if pr is None or not better(pr, cur["probe"]) and pr != cur["probe"]:
            return False
        if pr == cur["probe"]: return False
        log["ops_prescreen_pass"][opname] = log["ops_prescreen_pass"].get(opname, 0) + 1
        r = full(p, arm, txt, 0, vtimeout)
        if r["status"] != "pass" or not better(key(r["metrics"]), key(cur["m"])): return False
        cur = {"defs": new_defs, "order": o2, "txt": txt, "m": r["metrics"], "probe": pr}
        chain.append((txt, r["metrics"], opname))
        log["accepted"].append({"op": opname, "metrics": r["metrics"], "used": used})
        return True

    # ---------------- phase 1: targeted peepholes, greedy
    try:
        attempt(M.opt_apply(cur["defs"], cur["order"]), "opt40")
        attempt(M.opt_apply(cur["defs"], cur["order"], max_size=400), "opt400")
        for op in ("numopr", "preset", "litfirst", "eqz", "eqzi", "duperase"):
            nd, k = M.apply_all(cur["defs"], op)
            if k: attempt(nd, op + "_all")
        # per-site: inline calls (incl. one unrolling of recursive calls), inline tree-only leaves, and the peepholes singly
        for op in ("inline_call", "inline_leaf", "eqz", "eqzi", "numopr", "preset", "duperase"):
            sf, af = M.TARGETED[op]
            tried = set()
            for _ in range(40):
                if used >= budget * 0.5: break
                st = [s for s in sf(cur["defs"]) if repr(s) not in tried]
                if not st: break
                s = st[0]; tried.add(repr(s))
                try: nd = af(cur["defs"], s)
                except Exception: nd = None
                if attempt(nd, op):
                    tried = set()
        log["phase1_used"] = used; log["phase1_m"] = cur["m"]
        # ---------------- phase 2: (1+1) evolution, random targeted + structural mutations
        ops = list(M.TARGETED) + list(M.RANDOM)
        stall = 0
        while used < budget and stall < 20 * budget:
            stall += 1
            nd = cur["defs"]; names = []
            for _ in range(1 if rng.random() < .7 else 2):
                op = rng.choice(ops); names.append(op)
                try:
                    if op in M.TARGETED:
                        st = M.TARGETED[op][0](nd)
                        if not st: nd = None; break
                        nd = M.TARGETED[op][1](nd, rng.choice(st))
                    else:
                        nd = M.RANDOM[op](nd, rng)
                except Exception:
                    nd = None
                if nd is None: break
            if nd is not None: attempt(nd, "+".join(names))
    except Exception:
        log["exc"] = traceback.format_exc()[-800:]
    log["used"] = used
    # ---------------- final: independent re-verification on seeds 1 and 2; walk back on failure
    final = None
    for txt, m, op in reversed(chain):
        if op == "base": final = (txt, m, op); break
        ok = all(full(p, arm, txt, s, max(vtimeout, 30))["status"] == "pass" for s in (1, 2))
        if ok: final = (txt, m, op); break
        log.setdefault("rejected_on_reseed", []).append(op)
    txt, m, op = final
    os.makedirs(os.path.join(ROOT, outdir, arm), exist_ok=True)
    open(os.path.join(ROOT, outdir, arm, f"{pid}.hvm"), "w").write(txt)
    log["final"] = m; log["final_idx"] = [c[0] for c in chain].index(txt); log["chain_ops"] = [c[2] for c in chain]
    log["secs"] = round(time.time() - t0, 1)
    return log


def _job(a):
    pid, arm, budget, outdir = a
    try: return search(pid, arm, budget, outdir=outdir)
    except Exception: return {"pid": pid, "arm": arm, "error": traceback.format_exc()[-800:]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=int, default=200); ap.add_argument("--procs", type=int, default=16)
    ap.add_argument("--pids", default=""); ap.add_argument("--tag", default="main"); ap.add_argument("--arms", default="native,bend")
    a = ap.parse_args()
    os.chdir(ROOT)
    pids = a.pids.split(",") if a.pids else json.load(open("runs/exp3/sample.json"))["sample"]
    outdir = f"runs/exp3/{a.tag}"
    os.makedirs(outdir, exist_ok=True)
    jobs = [(pid, arm, a.budget, outdir) for pid in pids for arm in a.arms.split(",")]
    res_path = f"{outdir}/results.jsonl"
    done = set()
    if os.path.exists(res_path):
        for line in open(res_path): r = json.loads(line); done.add((r["pid"], r["arm"]))
    jobs = [j for j in jobs if (j[0], j[1]) not in done]
    print(f"{len(jobs)} jobs", flush=True)
    with ProcessPoolExecutor(a.procs) as ex:
        futs = [ex.submit(_job, j) for j in jobs]
        for f in as_completed(futs):
            r = f.result()
            with open(res_path, "a") as fh: fh.write(json.dumps(r, default=str) + "\n")
            b, fn = r.get("base"), r.get("final")
            print(r["pid"], r["arm"], "ERR " + r.get("error", "")[:200] if "error" in r else f"{key(b)} -> {key(fn)} used={r.get('used')} {r.get('secs')}s acc={[x['op'] for x in r['accepted']]}", flush=True)
