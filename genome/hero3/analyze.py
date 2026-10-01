"""Assemble the HERO-3 result tables from runs/hero3/*.json(l). Prints markdown and writes runs/hero3/summary.json."""
from __future__ import annotations
import json, math, os, statistics as S
from . import folds as F

R = "runs/hero3"


def load_jsonl(kind):
    p = f"{R}/scale_{kind}.jsonl"; d = {}
    if os.path.exists(p):
        for l in open(p):
            j = json.loads(l)
            if j.get("ok"): d[(j["fold"], j["n"])] = j
    return d


def slope(xs, ys):
    lx = [math.log(x) for x in xs]; ly = [math.log(y) for y in ys]
    mx, my = S.mean(lx), S.mean(ly)
    return sum((a - mx) * (b - my) for a, b in zip(lx, ly)) / sum((a - mx) ** 2 for a in lx)


def fit(d, fold, key, sizes=(1000, 10000, 100000)):
    pts = [(n, d[(fold, n)][key]) for n in sizes if (fold, n) in d and d[(fold, n)][key] > 0]
    if len(pts) < 3: return None
    return slope([p[0] for p in pts], [p[1] for p in pts])


def main():
    t1 = json.load(open(f"{R}/stage1_tester.json"))
    v2 = json.load(open(f"{R}/stage2_verify.json"))
    K = ["tree", "seq_list", "seq_la", "seq_tree", "ingest"]
    D = {k: load_jsonl(k) for k in K}
    summ = {}
    # ---- (a)
    acc = {f.id: all(r["accept"] for r in t1[f.id]) for f in F.FOLDS}
    a_assoc = [f.id for f in F.assoc() if acc[f.id]]
    a_non = [f.id for f in F.nonassoc() if acc[f.id]]
    summ["a"] = dict(assoc_total=len(F.assoc()), assoc_accepted=len(a_assoc), nonassoc_total=len(F.nonassoc()), nonassoc_accepted=a_non,
                     adversarial_accepted={f.id: acc[f.id] for f in F.adversarial()},
                     audit_stable=all(len({r["accept"] for r in t1[f.id]}) == 1 for f in F.FOLDS))
    comm_ok = {f.id: (t1[f.id][0]["commutative"] == f.comm) for f in F.assoc()}
    summ["comm_label_agreement"] = f"{sum(comm_ok.values())}/{len(comm_ok)}"
    # ---- (b)
    accepted = [f.id for f in F.FOLDS if acc[f.id]]
    def passed(fid):
        r = v2[fid]
        return all(v["status"] == "pass" for v in r["seeds"].values()) and all(v["status"] == "pass" for v in r["audit"].values()) and len(r["audit"]) == 3
    b_pass = [i for i in accepted if passed(i)]
    summ["b"] = dict(accepted=len(accepted), passed=len(b_pass), failed=[i for i in accepted if not passed(i)])
    # forced rewrites of rejected
    forced = {}
    for f in F.FOLDS:
        if not acc[f.id]:
            r = v2[f.id]["seeds"]
            forced[f.id] = dict(statuses=[r[s]["status"] for s in ("0", "1", "2")], cex=(r["0"].get("cex") or {}))
    summ["forced_rewrites_of_rejected"] = {k: v["statuses"] for k, v in forced.items()}
    # ---- (c)
    rows = []
    for f in F.assoc():
        i = f.id
        row = dict(fold=i, verified=(i in b_pass))
        for k in K:
            row[k] = {n: D[k].get((i, n)) for n in (1000, 10000, 100000)}
            row[k + "_dexp"] = fit(D[k], i, "depth"); row[k + "_iexp"] = fit(D[k], i, "itrs")
        rows.append(row)
    ver = [r for r in rows if r["verified"] and r["tree_dexp"] is not None]
    dex = [r["tree_dexp"] for r in ver]
    summ["c"] = dict(n=len(ver), median_exp=S.median(dex), max_exp=max(dex), share_le_0_4=sum(e <= 0.4 for e in dex) / len(dex),
                     itrs_median_exp=S.median([r["tree_iexp"] for r in ver]),
                     seq_median_exp=S.median([r["seq_list_dexp"] for r in ver if r["seq_list_dexp"] is not None]),
                     seq_la_median_exp=S.median([r["seq_la_dexp"] for r in ver if r["seq_la_dexp"] is not None] or [float('nan')]),
                     seqtree_median_exp=S.median([r["seq_tree_dexp"] for r in ver if r["seq_tree_dexp"] is not None] or [float('nan')]),
                     ingest_median_exp=S.median([r["ingest_dexp"] for r in ver if r["ingest_dexp"] is not None] or [float('nan')]))
    json.dump(dict(summary=summ, rows=rows), open(f"{R}/summary.json", "w"), indent=1, default=str)
    print(json.dumps(summ, indent=1, default=str))
    # ---- table
    def d(r, k, n):
        x = r[k][n]; return "-" if not x else f"{x['depth']:,}"
    print("\n| fold | tree d 1k | 10k | 100k | exp | seq d 100k | exp | seq/tree d @100k | itrs ratio tree/seq @100k |")
    print("|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        t, s = r["tree"][100000], r["seq_list"][100000]
        rat = f"{s['depth'] / t['depth']:.0f}x" if s and t else "-"
        ir = f"{t['itrs'] / s['itrs']:.2f}" if s and t else "-"
        e1 = f"{r['tree_dexp']:.2f}" if r["tree_dexp"] is not None else "-"; e2 = f"{r['seq_list_dexp']:.2f}" if r["seq_list_dexp"] is not None else "-"
        print(f"| {r['fold']} | {d(r,'tree',1000)} | {d(r,'tree',10000)} | {d(r,'tree',100000)} | {e1} | {d(r,'seq_list',100000)} | {e2} | {rat} | {ir} |")


if __name__ == "__main__":
    main()
