"""Metrics over scored sample files: unbiased pass@k, static-filtered best-of-n, Wilson and task-bootstrap intervals."""
import json, math, random, collections
from math import comb


def pass_at_k(n, c, k):
    if n - c < k: return 1.0
    return 1.0 - comb(n - c, k) / comb(n, k)


def wilson(x, n, z=1.96):
    if n == 0: return (0.0, 0.0)
    p = x / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den; h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (round(max(0, c - h), 3), round(min(1, c + h), 3))


def boot_ci(vals, iters=4000, seed=0):
    """95% CI of the mean of per-task values, resampling tasks (samples within a task are correlated)."""
    r = random.Random(seed); n = len(vals); ms = sorted(sum(vals[r.randrange(n)] for _ in range(n)) / n for _ in range(iters))
    return (round(ms[int(.025 * iters)], 3), round(ms[int(.975 * iters)], 3))


def fam_of(pid): return pid[4:].rsplit("_", 1)[0] if pid.startswith("gen_") else pid


def summarize(path):
    d = json.load(open(path)); S = d["scored"]; n = len(next(iter(S.values())))
    tot = collections.Counter(s["status"] for v in S.values() for s in v)
    cls = collections.Counter(s.get("cls") for v in S.values() for s in v if s["status"] == "static")
    per_task_p1 = [sum(s["status"] == "pass" for s in v) / len(v) for v in S.values()]
    N = sum(tot.values())
    out = {"file": path, "tasks": len(S), "n": n, "samples": N, "outcomes": dict(tot), "static_classes": dict(cls),
           "pass@1": round(sum(per_task_p1) / len(S), 4), "pass@1_task_boot95": boot_ci(per_task_p1),
           "pass@1_wilson95_samples(naive)": wilson(tot["pass"], N)}
    for k in (2, 4, 8):
        if k <= n: out[f"pass@{k}"] = round(sum(pass_at_k(len(v), sum(s["status"] == "pass" for s in v), k) for v in S.values()) / len(S), 4)
    # static-filtered best-of-n: take the FIRST sample (in sampling order) that parses and passes the free static check, run only that one.
    first_clean = []
    for v in S.values():
        c = next((s for s in v if s["status"] in ("pass", "fail")), None)
        first_clean.append(1 if c and c["status"] == "pass" else 0)
    out[f"static_filter_best_of_{n}"] = round(sum(first_clean) / len(S), 4)
    out["static_filter_best_of_n_wilson95"] = wilson(sum(first_clean), len(S))
    clean = tot["pass"] + tot["fail"]
    out["pass_given_static_clean"] = round(tot["pass"] / clean, 4) if clean else None
    out["static_clean_rate"] = round(clean / N, 4)
    fam = collections.defaultdict(list)
    for pid, v in S.items(): fam[fam_of(pid)].append(sum(s["status"] == "pass" for s in v) / len(v))
    out["per_family_pass@1"] = {f: round(sum(x) / len(x), 3) for f, x in sorted(fam.items())}
    return out


def paired(path_a, path_b, iters=4000, seed=0):
    """Difference in pass@1 (b - a) over the tasks common to both files, task-bootstrap 95% CI."""
    A = json.load(open(path_a))["scored"]; B = json.load(open(path_b))["scored"]
    ks = sorted(set(A) & set(B)); p = lambda v: sum(s["status"] == "pass" for s in v) / len(v)
    diffs = [p(B[k]) - p(A[k]) for k in ks]
    return {"tasks": len(ks), "delta_pass@1": round(sum(diffs) / len(ks), 4), "boot95": boot_ci(diffs, iters, seed)}
