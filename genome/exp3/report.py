"""Summarise an exp3 search run: per-arm improvement distributions, operator attribution, native-vs-Bend before/after.
usage: python3 -m genome.exp3.report runs/exp3/main"""
import json, math, os, statistics as S, sys
from collections import Counter, defaultdict

d = sys.argv[1] if len(sys.argv) > 1 else "runs/exp3/main"
rows = [json.loads(l) for l in open(os.path.join(d, "results.jsonl"))]
res = {(r["pid"], r["arm"]): r for r in rows}
out = {}


def k(m): return (m["itrs_median_big"], m["depth_median_big"])


def pct(v): return f"{100 * v:.1f}%"


lines = []
for arm in ("native", "bend"):
    rs = [r for r in rows if r["arm"] == arm and "final" in r]
    errs = [r["pid"] for r in rows if r["arm"] == arm and "final" not in r]
    gi = [1 - k(r["final"])[0] / k(r["base"])[0] for r in rs]
    gd = [1 - k(r["final"])[1] / k(r["base"])[1] for r in rs]
    imp = [r for r in rs if k(r["final"]) != k(r["base"])]
    lines.append(f"== {arm}: n={len(rs)} (errors {len(errs)}: {errs[:6]})")
    lines.append(f"  interactions: median {pct(S.median(gi))}, mean {pct(S.mean(gi))}, max {pct(max(gi))}; depth: median {pct(S.median(gd))}, mean {pct(S.mean(gd))}, max {pct(max(gd))}")
    lines.append(f"  improved (Pareto, seed0 + reseeds 1,2 pass): {len(imp)}/{len(rs)} = {pct(len(imp) / len(rs))}; "
                 f"itrs improved {sum(g > 0 for g in gi)}, depth improved {sum(g > 0 for g in gd)}; reseed rollbacks {sum(1 for r in rs if r.get('rejected_on_reseed'))}")
    best = sorted(rs, key=lambda r: -(1 - k(r['final'])[0] / k(r['base'])[0]))[:5]
    lines.append("  best by interactions: " + "; ".join(f"{r['pid']} {k(r['base'])}->{k(r['final'])}" for r in best))
    # operator attribution along the kept chain (log-ratio of the product itrs*depth)
    att = defaultdict(float); cnt = Counter()
    for r in rs:
        prev = k(r["base"])
        for a in r["accepted"][: r.get("final_idx", 0)]:
            m = k(a["metrics"]); op = a["op"].split("+")[0] if "+" in a["op"] and False else a["op"]
            att[op] += math.log(prev[0] * prev[1]) - math.log(m[0] * m[1]); cnt[op] += 1; prev = m
    tot = sum(att.values()) or 1
    lines.append("  operator share of kept log(itrs*depth) reduction: " + ", ".join(f"{op} {100 * v / tot:.0f}% (x{cnt[op]})" for op, v in sorted(att.items(), key=lambda x: -x[1])))
    tried = Counter(); passed = Counter()
    for r in rs:
        for op, c in r.get("ops_tried", {}).items(): tried[op] += c
        for op, c in r.get("ops_prescreen_pass", {}).items(): passed[op] += c
    rand = [op for op in tried if any(x in op for x in ("rewire", "cutwire", "opsym", "lit", "swapkids", "erasub"))]
    lines.append(f"  random-structural candidates: {sum(tried[o] for o in rand)} evaluated, {sum(passed[o] for o in rand)} passed prescreen, "
                 f"kept {sum(v for o, v in cnt.items() if o in rand)}")
    lines.append(f"  mean candidates used per program: {S.mean(r['used'] for r in rs):.0f}; mean secs {S.mean(r['secs'] for r in rs):.0f}")
    out[arm] = {r["pid"]: r for r in rs}

both = sorted(set(out["native"]) & set(out["bend"]))


def gain(n, b): return max(1 - n[0] / b[0], 1 - n[1] / b[1])


for label, fn, fb in (("before (original nets)", "base", "base"), ("after (both arms searched, same budget)", "final", "final"),
                      ("native searched vs original Bend", "final", "base"), ("original native vs searched Bend", "base", "final")):
    g = [gain(k(out["native"][p][fn]), k(out["bend"][p][fb])) for p in both]
    gi = [1 - k(out["native"][p][fn])[0] / k(out["bend"][p][fb])[0] for p in both]
    gd = [1 - k(out["native"][p][fn])[1] / k(out["bend"][p][fb])[1] for p in both]
    lines.append(f"== native vs Bend, {label}, n={len(both)}: native wins (itrs or depth) {sum(x > 0 for x in g)} ({pct(sum(x > 0 for x in g) / len(both))}), "
                 f"median gain {pct(S.median(g))}; itrs-only wins {pct(sum(x > 0 for x in gi) / len(both))} (median {pct(S.median(gi))}); "
                 f"depth-only wins {pct(sum(x > 0 for x in gd) / len(both))} (median {pct(S.median(gd))})")
txt = "\n".join(lines)
print(txt)
open(os.path.join(d, "report.txt"), "w").write(txt + "\n")
