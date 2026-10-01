"""exp15 metrics: pass@1 (mean over tasks of the per-task pass fraction), pass@n, task-bootstrap 95% CI, by composition depth
(number of words = list stages + reducer)."""
import json, collections
from genome.exp.metrics import boot_ci, pass_at_k, wilson


def summarize(path):
    d = json.load(open(path)); S = d["scored"]; D = d["depth"]
    n = len(next(iter(S.values())))
    per = {pid: sum(s["status"] == "pass" for s in v) / len(v) for pid, v in S.items()}
    tot = collections.Counter(s["status"] for v in S.values() for s in v)
    out = {"file": path, "model": d["meta"].get("model"), "adapter": d["meta"].get("adapter"), "tasks": len(S), "n": n,
           "outcomes": dict(tot), "pass@1": round(sum(per.values()) / len(per), 4), "pass@1_boot95": boot_ci(list(per.values())),
           f"pass@{n}": round(sum(pass_at_k(len(v), sum(s["status"] == "pass" for s in v), n) for v in S.values()) / len(S), 4),
           "exact_match_rate": round(sum(s.get("exact", False) for v in S.values() for s in v) / sum(tot.values()), 4)}
    by = collections.defaultdict(list)
    for pid, v in per.items(): by[D[pid]].append(v)
    out["by_depth"] = {k: {"tasks": len(x), "pass@1": round(sum(x) / len(x), 3), "boot95": boot_ci(x)} for k, x in sorted(by.items())}
    fam = collections.defaultdict(list)
    for pid, v in per.items(): fam[pid.split("_")[1]].append(v)
    out["by_family"] = {k: round(sum(x) / len(x), 3) for k, x in sorted(fam.items())}
    return out
