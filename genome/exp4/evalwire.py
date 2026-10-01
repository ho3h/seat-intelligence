"""Step 1 oracle test: predicted wiring in GOLD skeletons of held-out tasks, scored by exact match and by execution.

  <venv python> -m genome.exp4.evalwire --ckpt runs/exp4/wire.pt --out runs/exp4/step1.json
Methods: random (uniform perfect matching), nearest (min token distance, penalise same-statement pairs), lookup (majority
training matching for an identical definition skeleton; random if unseen), model (transformer + Blossom), hybrid (lookup if seen,
else model). Execution: genome.verify.verify seed 0, timeout 10 s per case.
"""
import argparse, collections, json, os, random, sys
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); os.chdir(ROOT)
from genome.netast import parse_book, print_book, show
from genome.exp4.skel import to_skeleton, refill, canon, n_slots
from genome.exp4 import wire as W
import networkx as nx


def def_key(skdef, abstract=False):
    root, reds = skdef
    txt = show(root) + "".join(f"&{'!' if p else ''}{show(a)}~{show(b)}" for p, a, b in reds)
    if abstract:
        import re; txt = re.sub(r"@[\w/]+", "@R", txt)
    return txt


def build_lookup(rows):
    L = [collections.defaultdict(collections.Counter), collections.defaultdict(collections.Counter)]
    for r in rows:
        d, o = parse_book(r["net"]); sk, m = to_skeleton(d, o)
        for n in o:
            for a in (0, 1): L[a][def_key(sk[n], bool(a))][tuple(m[n])] += 1
    return L


def lookup_cands(L, skdef):
    out = []
    for a in (0, 1):
        c = L[a].get(def_key(skdef, bool(a)))
        if c: out += [list(m) for m in c if list(m) not in out]
    return out


def lookup(L, skdef):
    for a in (0, 1):
        c = L[a].get(def_key(skdef, bool(a)))
        if c: return [tuple(p) for p in c.most_common(1)[0][0]]
    return None


def rand_match(k, rng):
    ix = list(range(k)); rng.shuffle(ix); return sorted(tuple(sorted(ix[i:i + 2])) for i in range(0, k, 2))


def slot_meta(skdef):
    """Token position and statement index of each slot (for the nearest heuristic)."""
    root, reds = skdef; out = []; pos = [0]
    def walk(t, st):
        pos[0] += 1
        if t[0] == "var": out.append((pos[0], st))
        elif t[0] in ("con", "dup", "opr", "swi"): walk(t[1], st); walk(t[2], st); pos[0] += 1
    walk(root, 0)
    for s, (_, a, b) in enumerate(reds): pos[0] += 1; walk(a, s + 1); pos[0] += 1; walk(b, s + 1)
    return out


def nearest(skdef):
    m = slot_meta(skdef); k = len(m); G = nx.Graph()
    for i in range(k):
        for j in range(i + 1, k): G.add_edge(i, j, weight=1e5 - abs(m[i][0] - m[j][0]) - 1000 * (m[i][1] == m[j][1]))
    return sorted(tuple(sorted(p)) for p in nx.max_weight_matching(G, maxcardinality=True))


def quick_reject(p, book, k=6, timeout=3.0):
    """Cheap pre-screen (same assembly/decoding as genome.verify): run the first k small cases; True if any is wrong.
    Only used to skip hopeless nets; a PASS always comes from the full genome.verify.verify."""
    from genome.verify import build_cases, assemble, check_book
    from genome.executor import run_net
    from genome.types import decode
    if check_book(book): return True
    cases = [c for c in build_cases(p, 0) if c[0] != "big"][:k]
    for kind, n, x in cases:
        r = run_net(assemble(p, book, x), "run", timeout)
        if not r.ok: return True
        try:
            if decode(r.result, p.out) != p.ref(x): return True
        except Exception: return True
    return False


def prog_of(pid):
    from genome.taskgen import task
    f, i = pid[4:].rsplit("_", 1); return task(f, int(i))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--ckpt", default="runs/exp4/wire.pt"); ap.add_argument("--out", default="runs/exp4/step1.json")
    ap.add_argument("--split", default="test"); a = ap.parse_args()
    D = json.load(open("runs/exp4/dataset.json")); tr = [r for r in D if r["split"] in ("train", "dev")]
    te = [r for r in D if r["split"] == a.split]
    L = build_lookup(tr); rng = random.Random(0)
    model, V, dev = W.load(a.ckpt)
    preds = {m: {} for m in ("random", "nearest", "lookup", "model", "hybrid", "rerank")}
    stats = collections.Counter()
    for r in te:
        d, o = parse_book(r["net"]); sk, gold = to_skeleton(d, o)
        pm, Ws = W.predict_scores(model, V, dev, sk, o)
        for meth in preds:
            M = {}
            for n in o:
                k = n_slots(sk[n])
                if meth == "random": M[n] = rand_match(k, rng)
                elif meth == "nearest": M[n] = nearest(sk[n])
                elif meth == "model": M[n] = pm[n]
                elif meth == "rerank":  # model picks among matchings seen in training for this definition skeleton, else free decode
                    k2 = n_slots(sk[n]); cs = [c for c in lookup_cands(L, sk[n]) if max((max(p) for p in c), default=-1) < k2]
                    M[n] = [tuple(p) for p in max(cs, key=lambda c: sum(Ws[n][i, j] for i, j in c))] if cs else pm[n]
                else:
                    lk = lookup(L, sk[n])
                    if meth == "lookup": M[n] = lk if lk and max(max(p) for p in lk) < k else rand_match(k, rng)
                    else: M[n] = lk if lk and max(max(p) for p in lk) < k else pm[n]
                    if meth == "hybrid": stats["lookup_hit" if lk else "lookup_miss"] += 1
            defs_ok = [M[n] == gold[n] for n in o]
            book = print_book(refill(sk, o, M), o)
            preds[meth][r["task"]] = {"defs_ok": sum(defs_ok), "defs": len(o), "net_exact": all(defs_ok), "book": book}
    # execution
    from genome.verify import verify
    jobs = [(meth, pid) for meth in preds for pid in preds[meth]]
    def run(j):
        meth, pid = j; x = preds[meth][pid]
        if x["net_exact"]: return j, "pass_exact"   # identical modulo names to a verified net
        try:
            p = prog_of(pid)
            if quick_reject(p, x["book"]): return j, "fail_quick"
            return j, verify(p, x["book"], seed=0, timeout=10.0, workers=4)["status"]
        except Exception as e: return j, "error"
    with ThreadPoolExecutor(6) as ex:
        for (meth, pid), st in ex.map(run, jobs): preds[meth][pid]["exec"] = st
    summ = {}
    for meth, P in preds.items():
        n = len(P); dsum = sum(x["defs"] for x in P.values())
        exe = [1 if x["exec"] in ("pass", "pass_exact") else 0 for x in P.values()]
        summ[meth] = {"nets": n, "defs": dsum, "def_exact": round(sum(x["defs_ok"] for x in P.values()) / dsum, 4),
                      "net_exact": round(sum(x["net_exact"] for x in P.values()) / n, 4), "exec_pass": round(sum(exe) / n, 4),
                      "exec_pass_not_exact": sum(1 for x in P.values() if x["exec"] == "pass"),
                      "exec_by_family": {f: f"{sum(1 for r in te if r['fam'] == f and P[r['task']]['exec'] in ('pass','pass_exact'))}/{sum(1 for r in te if r['fam'] == f)}"
                                         for f in sorted({r['fam'] for r in te})}}
    summ["hybrid_lookup_stats"] = dict(stats)
    print(json.dumps(summ, indent=1))
    json.dump({"summary": summ, "preds": {m: {p: {k: v for k, v in x.items() if k != "book"} for p, x in P.items()} for m, P in preds.items()}},
              open(a.out, "w"), indent=0)


if __name__ == "__main__": main()
