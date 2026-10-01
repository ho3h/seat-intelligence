"""exp15 report: tables by model size and composition depth, paired comparison with the plain fine-tuned 4B (native_v1),
error analysis, and an SVG plot of pass@1 vs model size.   python3 -m genome.exp15.report  -> runs/exp15/summary.{json,md}, pass_vs_size.svg
"""
import json, os, collections, math
from genome.exp.metrics import boot_ci
from genome.exp15.metrics import summarize
from genome.exp15.data import OUT, gold, depth
from genome.taskgen import task

RUNS = [("0p6b_lr5e5", "Qwen3-0.6B-4bit, lr 5e-5", 0.6), ("1p7b_lr5e5", "Qwen3-1.7B-4bit, lr 5e-5", 1.7), ("4b_lr5e5", "Qwen3-4B-4bit, lr 5e-5", 4.0),
        ("0p6b", "Qwen3-0.6B-4bit, lr 2e-4 (diverged)", None), ("1p7b", "Qwen3-1.7B-4bit, lr 2e-4", None),
        ("1p7b_aug_lr5e5", "Qwen3-1.7B-4bit, lr 5e-5, 3 wordings in training", None), ("zs4bi", "Qwen3-4B-Instruct-2507, no tuning, vocabulary in prompt", None)]
SIZE_TAGS = {"0p6b_lr5e5": 0.6, "1p7b_lr5e5": 1.7, "4b_lr5e5": 4.0}
SETS = ["iid", "deep", "para", "novel"]


def _f(tag, s): return os.path.join(OUT, "samples", f"{tag}_{s}.scored.json")


def baseline():
    d = json.load(open("runs/exp/A_native_v1_iid.scored.json"))
    per = {}
    for pid, v in d["scored"].items(): per[pid] = sum(s["status"] == "pass" for s in v) / len(v)
    by = collections.defaultdict(list)
    for pid, v in per.items():
        f, i = pid.split("_")[1], int(pid.split("_")[2]); by[depth(*gold(task(f, i)))].append(v)
    return per, {k: {"tasks": len(x), "pass@1": round(sum(x) / len(x), 3), "boot95": boot_ci(x)} for k, x in sorted(by.items())}


def paired(per_a, path_b):
    B = json.load(open(path_b))["scored"]; ks = sorted(set(per_a) & set(B))
    diffs = [sum(s["status"] == "pass" for s in B[k]) / len(B[k]) - per_a[k] for k in ks]
    return {"tasks": len(ks), "delta": round(sum(diffs) / len(ks), 4), "boot95": boot_ci(diffs)}


def errors(path):
    d = json.load(open(path)); G = d["gold"]; c = collections.Counter()
    for pid, v in d["scored"].items():
        g = G[pid].splitlines()
        for s in v:
            if s["status"] == "pass": c["pass_exact" if s.get("exact") else "pass_equivalent_nonexact"] += 1; continue
            if s["status"] == "parse": c["parse_error"] += 1; continue
            p = s["prog"].splitlines()
            if len(p) != len(g): c["wrong_stage_count"] += 1; continue
            diff = [(a, b) for a, b in zip(p, g) if a != b]
            if not diff: c["exact_but_failed(!)"] += 1; continue
            if all(a.split()[0] == b.split()[0] and a.split()[:2] == b.split()[:2] for a, b in diff): c["wrong_parameter"] += 1
            elif all(a.split()[0] == b.split()[0] for a, b in diff): c["wrong_subword"] += 1
            else: c["wrong_word"] += 1
    return dict(c)


def svg(rows, path):
    W, H, l, r, t, b = 560, 340, 60, 150, 20, 45
    xs = SIZE_TAGS; lx = lambda v: l + (math.log(v) - math.log(0.5)) / (math.log(5) - math.log(0.5)) * (W - l - r)
    ly = lambda v: t + (1 - v) * (H - t - b)
    series = [("iid (120)", "iid", "#1f77b4"), ("deep 3 (40)", 3, "#2ca02c"), ("deep 4 (40)", 4, "#9467bd"), ("deep 5 (40)", 5, "#8c564b"),
              ("deep 7-8 (60)", "78", "#e377c2"), ("novel constants (120)", "novel", "#17becf"), ("paraphrase (120)", "para", "#ff7f0e")]
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="11">',
         f'<rect width="{W}" height="{H}" fill="white"/>']
    for g in range(0, 11, 2):
        y = ly(g / 10); o.append(f'<line x1="{l}" y1="{y}" x2="{W - r}" y2="{y}" stroke="#ddd"/><text x="{l - 6}" y="{y + 4}" text-anchor="end">{g * 10}%</text>')
    for tag, v in xs.items():
        o.append(f'<text x="{lx(v)}" y="{H - b + 16}" text-anchor="middle">{v}B</text>')
    o.append(f'<text x="{(l + W - r) / 2}" y="{H - 8}" text-anchor="middle">trained model size (Qwen3, 4-bit, LoRA; log scale)</text>')
    yb = ly(0.144); o.append(f'<line x1="{l}" y1="{yb}" x2="{W - r}" y2="{yb}" stroke="#d62728" stroke-dasharray="5,4"/>')
    o.append(f'<text x="{W - r + 6}" y="{yb + 4}" fill="#d62728">plain 4B net LoRA, iid</text>')
    for i, (name, key, col) in enumerate(series):
        pts = [(lx(xs[tg]), ly(rows[tg][key])) for tg in xs if tg in rows and rows[tg].get(key) is not None]
        if not pts: continue
        o.append(f'<polyline fill="none" stroke="{col}" stroke-width="2" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}"/>')
        o += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="{col}"/>' for x, y in pts]
        o.append(f'<text x="{W - r + 6}" y="{t + 14 + 16 * i}" fill="{col}">{name}</text>')
    o.append("</svg>"); open(path, "w").write("\n".join(o))


def main():
    bper, bdepth = baseline(); res = {"baseline_native_v1_iid_by_depth": bdepth, "models": {}}; plot = {}
    for tag, name, size in RUNS:
        if not os.path.exists(_f(tag, "iid")): continue
        m = {"name": name}
        m.update({s: summarize(_f(tag, s)) for s in SETS if os.path.exists(_f(tag, s))})
        m["paired_vs_native_v1_iid"] = paired(bper, _f(tag, "iid"))
        m["errors"] = {s: errors(_f(tag, s)) for s in SETS if os.path.exists(_f(tag, s))}
        res["models"][tag] = m
        if tag not in SIZE_TAGS: continue
        pr = {"iid": m["iid"]["pass@1"]}
        if "deep" in m:
            bd = m["deep"]["by_depth"]; g = lambda k: bd.get(k) or bd.get(str(k))
            for k in (3, 4, 5): pr[k] = g(k)["pass@1"]
            pr["78"] = (g(7)["pass@1"] * g(7)["tasks"] + g(8)["pass@1"] * g(8)["tasks"]) / (g(7)["tasks"] + g(8)["tasks"])
        for s2 in ("para", "novel"):
            if s2 in m: pr[s2] = m[s2]["pass@1"]
        plot[tag] = pr
    json.dump(res, open(os.path.join(OUT, "summary.json"), "w"), indent=1, default=str)
    svg(plot, os.path.join(OUT, "pass_vs_size.svg"))
    # compact table
    lines = ["| run | iid pass@1 [95% CI] | iid d1/d2/d3 | deep3 | deep4 | deep5 | deep7 | deep8 | novel consts | paraphrase | vs native_v1 (paired) |", "|" + "---|" * 11]
    for tag, m in res["models"].items():
        def c(s, key=None):
            if s not in m: return "-"
            if key is None: return f"{m[s]['pass@1']*100:.1f} [{m[s]['pass@1_boot95'][0]*100:.1f}, {m[s]['pass@1_boot95'][1]*100:.1f}]"
            bd = m[s]["by_depth"]; x = bd.get(key) or bd.get(str(key)); return f"{x['pass@1']*100:.1f}" if x else "-"
        dd = "/".join(c("iid", k) for k in (1, 2, 3))
        pv = m["paired_vs_native_v1_iid"]
        lines.append(f"| {m['name']} | {c('iid')} | {dd} | {c('deep', 3)} | {c('deep', 4)} | {c('deep', 5)} | {c('deep', 7)} | {c('deep', 8)} | {c('novel')} | {c('para')} | {pv['delta']*100:+.1f} [{pv['boot95'][0]*100:+.1f}, {pv['boot95'][1]*100:+.1f}] |")
    open(os.path.join(OUT, "summary.md"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))
    for tag, m in res["models"].items(): print(tag, json.dumps(m["errors"]))


if __name__ == "__main__": main()
