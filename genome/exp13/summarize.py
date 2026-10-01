"""Summarise runs/exp13/{heldout,llmcmp}.json -> runs/exp13/SUMMARY.txt (python -m genome.exp13.summarize)."""
from __future__ import annotations
import json, math, os
from collections import Counter, defaultdict

KS = ["3", "4", "5", "6", "8", "10"]


def pct(a, b): return f"{a}/{b} ({100 * a / b:.0f}%)" if b else f"{a}/0"


def med(v):
    v = sorted(v); return v[len(v) // 2] if v else None


def gmean(v): return math.exp(sum(math.log(x) for x in v) / len(v)) if v else float("nan")


def main():
    L = []
    rows = json.load(open("runs/exp13/heldout.json"))
    n = len(rows); fam = lambda r: r["id"].split("_")[1]
    L.append(f"exp13 word filling, held-out generated tasks (indices >= 20000, not in any taskset): {n} tasks")
    L.append(f"  by family: {dict(Counter(fam(r) for r in rows))}")
    L.append("")
    L.append("COVERAGE (ground-truth shape parsed from the description; the search never sees it)")
    L.append(f"  core library (words named in the brief): {pct(sum(r['core'] for r in rows), n)}")
    L.append(f"  extended library (+ runmax runmin runxor diff ind-map idxfirst idxlast idxsum argmax cntgtfirst): {pct(sum(r['in_space'] for r in rows), n)} inside the search space")
    nc = Counter(r["shape"] for r in rows if not r["core"])
    L.append(f"  shapes outside the core library: {dict(nc)}")
    shapes = Counter(r["shape"] for r in rows)
    L.append(f"  distinct task shapes: {len(shapes)} (core covers {sum(1 for s in shapes if all(r['core'] for r in rows if r['shape'] == s))})")
    L.append("")
    cov = [r for r in rows if r["in_space"]]
    found = [r for r in cov if r["found"]]
    npass = [r for r in cov if r.get("net_pass")]
    L.append("SOLVE RATE, k=3 examples (net composed from word templates passes genome.verify seeds 0,1,2)")
    L.append(f"  covered tasks solved: {pct(len(npass), len(cov))}; search found a consistent program: {pct(len(found), len(cov))}")
    for f in ["pipeline", "reduce", "scan", "position"]:
        c = [r for r in cov if fam(r) == f]; L.append(f"    {f:9s} {pct(sum(1 for r in c if r.get('net_pass')), len(c))}")
    corec = [r for r in cov if r["core"]]
    L.append(f"  core-covered subset: {pct(sum(1 for r in corec if r.get('net_pass')), len(corec))}")
    sp = [r for r in found if not r.get("py_hidden_ok")]
    L.append(f"  spurious fits (fit the examples, fail the hidden suite): {pct(len(sp), len(found))}")
    mism = [r for r in found if r.get("py_hidden_ok") and not r.get("net_pass")]
    L.append(f"  lowering failures (program right in Python, net fails verify): {len(mism)} {[r['id'] for r in mism]}")
    by_n = defaultdict(list)
    for r in cov: by_n[len(r["truth"])].append(r)
    L.append("  by ground-truth size (words incl. reducer): " + ", ".join(f"{k}: {pct(sum(1 for r in v if r.get('net_pass')), len(v))}" for k, v in sorted(by_n.items())))
    L.append("  spurious examples (found program vs truth):")
    for r in sp[:12]: L.append(f"    {r['id']}: found {r['prog']}  truth {r['truth']}")
    L.append("")
    L.append("EXAMPLES NEEDED (Python-level check of the found program on the hidden suites, seeds 0,1,2; nested example sets)")
    for k in KS:
        ok = sum(1 for r in cov if r["by_k"][k]["ok"]); L.append(f"  k={k:>2}: {pct(ok, len(cov))}  median search {1e6 * med([r['by_k'][k]['sec'] for r in cov]):.0f} us, max {max(r['by_k'][k]['sec'] for r in cov):.2f} s")
    never = [r for r in cov if not r["by_k"]["10"]["ok"]]
    L.append(f"  still wrong at k=10: {len(never)}: " + "; ".join(f"{r['id']} found {r['by_k']['10']['prog']} truth {r['truth']}" for r in never[:10]))
    L.append("")
    ss = [r["search_sec"] for r in cov]; vs = [r["verify_sec"] for r in cov if r.get("verify_sec")]
    L.append(f"TIME PER TASK (k=3): search median {1e6 * med(ss):.0f} us, mean {1000 * sum(ss) / len(ss):.1f} ms, max {max(ss):.2f} s, timeouts {sum(r['timeout'] for r in cov)}; "
             f"lowering < 1 ms; verify (3 seeds, ~95 HVM runs each) median {med(vs):.1f} s")
    st = [r["states"] for r in cov]
    L.append(f"  OE classes built per task: median {med(st)}, max {max(st)}")
    if os.path.exists("runs/exp13/cegis.json"):
        c = json.load(open("runs/exp13/cegis.json")); L.append("")
        L.append("WITH COUNTEREXAMPLE FEEDBACK (the LLM authors' loop: on failure add the smallest failing seed-0 input + expected, re-search; <= 8 rounds; final net judged on seeds 0,1,2)")
        L.append(f"  solved {pct(sum(1 for r in c if r.get('net_pass')), len(c))}; rounds used by solved tasks {dict(sorted(Counter(r['rounds'] for r in c if r.get('net_pass')).items()))}")
        L.append(f"  net passed seed 0 but failed seed 1/2: {sum(1 for r in c if r.get('found') and not r.get('net_pass'))}; unsolved: " + "; ".join(f"{r['id']} last {r['hist'][-1:]}" for r in c if not r.get('net_pass')))
        L.append(f"  wall-clock per task incl. feedback rounds (search only): median {1000 * med([r['sec'] for r in c]):.2f} ms, max {max(r['sec'] for r in c):.2f} s")
    if os.path.exists("runs/exp13/llmcmp.json"):
        L.append("")
        c = json.load(open("runs/exp13/llmcmp.json"))
        both = [r for r in c if r.get("net_pass")]
        fails = [r for r in c if not r.get("net_pass")]
        L.append("  failures: " + "; ".join(f"{r['id']} {r.get('prog')} ({'spurious' if r.get('found') and not r.get('py_hidden_ok') else 'other'})" for r in fails[:25]))
        L.append(f"VS LLM-AUTHORED NATIVE NETS (training tasks with an accepted, audited Luna Pro net; k=6 examples; seed-0 metrics)")
        L.append(f"  word filling solves {pct(len(both), len(c))} of these tasks (Luna Pro: all by selection; its overall train rate 785/824 = 95%)")
        for key, nm in (("itrs_median_big", "interactions (median, largest inputs)"), ("depth_median_big", "depth (median, largest inputs)")):
            rat = [r["verify"][0]["metrics"][key] / r["llm"][key] for r in both if r["llm"].get(key) and r["verify"][0]["metrics"].get(key)]
            if rat:
                L.append(f"  {nm}: ours/LLM geomean {gmean(rat):.2f}x, median {med(rat):.2f}x, ours better on {sum(1 for x in rat if x < 1)}/{len(rat)}, "
                         f"range {min(rat):.2f}-{max(rat):.2f}")
        byf = defaultdict(list)
        for r in both:
            m, l = r["verify"][0]["metrics"], r["llm"]
            if l.get("depth_median_big") and m.get("depth_median_big"): byf[r["id"].split("_")[1]].append((m["itrs_median_big"] / l["itrs_median_big"], m["depth_median_big"] / l["depth_median_big"]))
        for f, v in byf.items(): L.append(f"    {f:9s} n={len(v)} itrs {gmean([a for a, _ in v]):.2f}x depth {gmean([b for _, b in v]):.2f}x")
        worst = sorted(both, key=lambda r: -r["verify"][0]["metrics"]["depth_median_big"] / max(1, r["llm"]["depth_median_big"] or 1))[:5]
        L.append("  largest depth ratios: " + "; ".join(f"{r['id']} {r['prog']} {r['verify'][0]['metrics']['depth_median_big']} vs {r['llm']['depth_median_big']}" for r in worst))
    open("runs/exp13/SUMMARY.txt", "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
