"""HERO-4 report: per-family pass@1 with denominators and task-bootstrap CIs, paired deltas, base regression, lexical overlap, authoring cost.
   python -m genome.hero4.report  -> runs/hero4/summary.json  and  runs/hero4/summary.md"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, os, random, re, statistics, sys
from genome.hero4 import lang, refs
from genome.hero4.refs import NEW_WORDS, BASE_WORDS

R = _REPO + "/runs/hero4"
FAMS_BASE = ["group", "spread", "order", "sections", "captains"]
STOP = set("the a an and or of to in on at for with is are be it its that this these those from by as than then there their they them you your our we i my me "
           "should must may would could will can not no all any each every one two three four five six seven eight nine ten per seats seat table section sections "
           "guests guest please want like make sure keep put have has had who which what when where how also just only into over under about more most less "
           "very lowest highest number rank numbers first last other others".split())


def load(name):
    p = f"{R}/samples/{name}.scored.json"
    return json.load(open(p)) if os.path.exists(p) else None


def task_scores(sc):
    """-> {task_id: (family, passes/n, n, parsefail/n, exact/n)}"""
    fam = {t["id"]: t["family"] for t in sc["tasks"]}; out = {}
    for pid, rs in sc["scored"].items():
        n = len(rs); ps = sum(r["status"] == "pass" for r in rs)
        out[pid] = (fam[pid], ps / n, n, sum(r["status"] == "parse" for r in rs) / n, sum(bool(r.get("exact")) and r["status"] == "pass" for r in rs) / n)
    return out


def boot(vals, B=2000, seed=0):
    if not vals: return (float("nan"),) * 3
    r = random.Random(seed); m = statistics.mean(vals); bs = []
    for _ in range(B): bs.append(statistics.mean(r.choice(vals) for _ in vals))
    bs.sort(); return m, bs[int(0.025 * B)], bs[int(0.975 * B) - 1]


def strict_scores(sc, vacuous=()):
    """for NEW families: per task fraction of samples that pass AND use the family's word; vacuous tasks (gold == gold without the word) dropped"""
    fam = {t["id"]: t["family"] for t in sc["tasks"]}; out = {}
    for pid, rs in sc["scored"].items():
        w = fam[pid]
        if w not in NEW_WORDS or pid in vacuous: continue
        ok = 0
        for r in rs:
            lines = (r.get("prog") or "").splitlines()
            if r["status"] == "pass" and any(l.split() and l.split()[0] == w for l in lines): ok += 1
        out[pid] = (w, ok / len(rs), len(rs))
    return out


def strict_table(sc, vacuous=()):
    ts = strict_scores(sc, vacuous); out = {}
    for w in NEW_WORDS:
        v = [x[1] for x in ts.values() if x[0] == w]
        if not v: continue
        m, lo, hi = boot(v)
        out[w] = {"pass1_word_required": round(100 * m, 1), "ci": [round(100 * lo, 1), round(100 * hi, 1)], "tasks": len(v),
                  "samples": sum(x[2] for x in ts.values() if x[0] == w)}
    return out


def fam_table(sc, fams):
    ts = task_scores(sc); out = {}
    for f in fams:
        v = [x[1] for k, x in ts.items() if x[0] == f]
        if not v: continue
        n = sum(x[2] for k, x in ts.items() if x[0] == f); ok = round(sum(v) * (n / len(v)))
        m, lo, hi = boot(v)
        out[f] = {"pass1": round(100 * m, 1), "ci": [round(100 * lo, 1), round(100 * hi, 1)], "tasks": len(v), "samples": n, "pass_samples": ok,
                  "tasks_all4": sum(1 for x in v if x == 1.0), "tasks_any": sum(1 for x in v if x > 0),
                  "parse_fail_pct": round(100 * statistics.mean(x[3] for k, x in ts.items() if x[0] == f), 1)}
    return out


def paired(sc_a, sc_b, fams):
    a, b = task_scores(sc_a), task_scores(sc_b); d = [b[k][1] - a[k][1] for k in a if k in b and a[k][0] in fams]
    m, lo, hi = boot(d); return {"delta_pts": round(100 * m, 1), "ci": [round(100 * lo, 1), round(100 * hi, 1)], "tasks": len(d)}


def content_tokens(s): return {w for w in re.findall(r"[a-z]+", s.lower()) if len(w) >= 4 and w not in STOP}


def overlap(tasks):
    """share of a test text's content words that appear in the family's block entry (gloss + example text) -- per family mean"""
    out = {}
    for w in NEW_WORDS:
        sig, gloss, ex_text, ex_line = lang.ENTRIES[w]; ent = content_tokens(gloss + " " + ex_text)
        vals = []
        for t in tasks:
            if t["family"] != w: continue
            ct = content_tokens(t["text"]); vals.append(len(ct & ent) / max(1, len(ct)))
        out[w] = round(100 * statistics.mean(vals), 1)
    return out


def authoring():
    L = [json.loads(l) for l in open(f"{R}/authoring_log.jsonl")]
    out = {}
    for w in NEW_WORDS:
        ev = [e for e in L if e["word"] == w]
        st = [e for e in ev if e["event"] == "start"]; en = [e for e in ev if e["event"] == "end"]; ve = [e for e in ev if e["event"] == "verify"]
        if not (st and en): continue
        out[w] = {"attempts": len(ve), "first_try_pass": bool(ve and ve[0]["pass"]), "edits": 1 + sum(e["event"] == "edit" for e in ev),
                  "seconds": round(en[-1]["t"] - st[0]["t"]), "lines": en[-1].get("lines"), "chars": en[-1].get("chars"),
                  "tokens_est": round(en[-1].get("chars", 0) / 4)}
    return out


def adoption(sc):
    """per new family: % of samples that use the family's word at all, and % whose line for it equals the gold line"""
    fam = {t["id"]: t["family"] for t in sc["tasks"]}; gold = sc["gold"]; out = {}
    for w in NEW_WORDS:
        n = used = exact = 0
        for pid, rs in sc["scored"].items():
            if fam[pid] != w: continue
            gl = [l for l in gold[pid].splitlines() if l.split()[0] == w][0]
            for r in rs:
                n += 1
                lines = (r.get("prog") or r.get("text") or "").splitlines()
                if any(l.split() and l.split()[0] == w for l in lines): used += 1
                if gl in lines: exact += 1
        out[w] = {"samples": n, "uses_word_pct": round(100 * used / n, 1), "word_line_exact_pct": round(100 * exact / n, 1)}
    return out


def failure_modes(sc, fams):
    """count failing samples by mode"""
    fam = {t["id"]: t["family"] for t in sc["tasks"]}; c = {"pass": 0, "parse": 0, "fail_sem": 0, "other": 0}; ex = []
    for pid, rs in sc["scored"].items():
        if fam[pid] not in fams: continue
        for r in rs:
            s = r["status"]
            if s == "pass": c["pass"] += 1
            elif s == "parse":
                c["parse"] += 1
                if len(ex) < 6: ex.append((pid, r.get("why"), (r.get("text") or "")[:100]))
            elif s == "fail": c["fail_sem"] += 1
            else: c["other"] += 1
    return c, ex


def repaired_table(name, fams):
    p = f"{R}/samples/{name}.repaired.json"
    if not os.path.exists(p): return None
    d = json.load(open(p)); fam = {t["id"]: t["family"] for t in d["tasks"]}; out = {}
    for f in fams:
        n = ok = 0
        for pid, rs in d["scored"].items():
            if fam[pid] != f: continue
            for r in rs: n += 1; ok += r["status"] == "pass"
        if n: out[f] = round(100 * ok / n, 1)
    return out


def cell(t, f):
    v = t.get(f) if t else None
    return "n/a" if not v else f"{v['pass1']} ({v['pass_samples']}/{v['samples']})"


def md_newtable(cols, fams=NEW_WORDS, title=""):
    """cols: list of (label, fam_table dict)"""
    lines = [f"| family | " + " | ".join(l for l, _ in cols) + " |", "|---|" + "---|" * len(cols)]
    for f in fams: lines.append(f"| {f} | " + " | ".join(cell(t, f) for _, t in cols) + " |")
    tot = []
    for _, t in cols:
        if not t: tot.append("n/a"); continue
        ok = sum(t[f]["pass_samples"] for f in fams if f in t); n = sum(t[f]["samples"] for f in fams if f in t)
        tot.append(f"{round(100 * ok / n, 1)} ({ok}/{n}); families >= 70: {sum(t[f]['pass1'] >= 70 for f in fams if f in t)}")
    lines.append("| **all ten pooled** | " + " | ".join(tot) + " |")
    return "\n".join(lines)


def main():
    S = {k: load(k) for k in ["main_without", "main_own", "main_all", "main_iid_without", "main_iid_all", "const_own", "const_without",
                              "retrain_all", "zs4b_all"]}
    out = {"available": [k for k, v in S.items() if v]}
    tasks = json.load(open(f"{R}/sets/FROZEN/test_final.json"))
    out["overlap_pct"] = overlap(tasks)
    out["authoring"] = authoring()
    out["new"] = {}
    for k in ["main_without", "main_own", "main_all", "const_own", "retrain_all", "zs4b_all"]:
        if S[k]: out["new"][k] = fam_table(S[k], NEW_WORDS)
    vac = set(json.load(open(f"{R}/sets/vacuous_test_ids.json")))
    for k in ["main_without", "main_own", "main_all", "const_own", "retrain_all", "zs4b_all"]:
        if S[k]: out.setdefault("strict", {})[k] = strict_table(S[k], vac)
    if S["main_own"]:
        out["adoption_own"] = adoption(S["main_own"])
        out["modes_own"] = failure_modes(S["main_own"], NEW_WORDS)
    if S["main_all"]: out["adoption_all"] = adoption(S["main_all"])
    if S["main_without"] and S["main_own"]: out["paired_own_vs_without"] = paired(S["main_without"], S["main_own"], NEW_WORDS)
    out["base"] = {}
    for k in ["main_without", "main_all", "main_iid_without", "main_iid_all", "const_without", "zs4b_all"]:
        if S[k]: out["base"][k] = fam_table(S[k], FAMS_BASE)
    if S["main_without"] and S["main_all"]: out["paired_base_all_vs_without"] = paired(S["main_without"], S["main_all"], FAMS_BASE)
    if S["main_iid_without"] and S["main_iid_all"]: out["paired_iid_all_vs_without"] = paired(S["main_iid_without"], S["main_iid_all"], FAMS_BASE)
    json.dump(out, open(f"{R}/summary.json", "w"), indent=1)
    print(json.dumps(out, indent=1)[:6000])


if __name__ == "__main__": main()
