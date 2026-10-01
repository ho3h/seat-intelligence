"""Fill the placeholders of docs/HERO-4.md from the scored samples."""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, os
from genome.hero4 import report
from genome.hero4.report import load, fam_table, NEW_WORDS, FAMS_BASE, paired, md_newtable
R = report.R

def pooled(t, fams):
    ok = sum(t[f]["pass_samples"] for f in fams); n = sum(t[f]["samples"] for f in fams); return ok, n

def table_a():
    A = [("A. base-only block", "main_without"), ("B. + own word", "main_own"), ("C. + all ten", "main_all"),
         ("G. ablation: constant names, + own", "const_own"), ("E. untuned 4B-Instruct, all 15", "zs4b_all"), ("F. retrained 1.7B, all 15", "retrain_all")]
    cols = [(l, fam_table(load(k), NEW_WORDS) if load(k) else None) for l, k in A]
    t = md_newtable(cols)
    ci = fam_table(load("main_own"), NEW_WORDS)
    t += "\n\nArm B 95% CIs: " + ", ".join(f"{f} [{ci[f]['ci'][0]}, {ci[f]['ci'][1]}]" for f in NEW_WORDS) + "."
    return t

def ctl(k, label):
    s = load(k)
    if not s: return "not run"
    t = fam_table(s, NEW_WORDS); ok, n = pooled(t, NEW_WORDS); ok2 = sum(t[f]["pass1"] >= 70 for f in NEW_WORDS)
    base = fam_table(s, FAMS_BASE); bok, bn = pooled(base, FAMS_BASE)
    return (f"pooled {100*ok/n:.1f}% ({ok}/{n}), {ok2} of 10 families >= 70; per family " + ", ".join(f"{f} {t[f]['pass1']}" for f in NEW_WORDS)
            + f". Its base-family pass@1 in the same run: {100*bok/bn:.1f}% ({bok}/{bn}) over the 150 base tasks.")

def table_b():
    B = [("base-only", "tv2_without"), ("own, r1 entries", "tv2_r1_own"), ("all ten, r1", "tv2_r1_all"), ("own, r2 entries", "tv2_r2_own"), ("all ten, r2", "tv2_r2_all")]
    cols = [(l, fam_table(load(k), NEW_WORDS)) for l, k in B]
    return ("**Table B. Fresh test v2** (new wording writers, new parameters; r1 = round-1 entries, r2 = revised entries frozen after the dev round). "
            "pass@1 % (passing/samples), 30 tasks x 4 per family.\n\n" + md_newtable(cols))

def base_reg():
    rows = [("test v1, 150 base tasks (independent wording)", [("base-only", "main_without"), ("+ all ten (r1)", "main_all")]),
            ("test v1, held-out training templates (iid)", [("base-only", "main_iid_without"), ("+ all ten", "main_iid_all")]),
            ("test v2, 150 base tasks (fresh wording)", [("base-only", "btv2_without"), ("+ one rotating word (r1)", "btv2_r1_one"), ("+ one rotating word (r2)", "btv2_r2_one"),
                                                          ("+ all ten (r1)", "btv2_r1_all"), ("+ all ten (r2)", "btv2_r2_all")])]
    out = ["| base set | block | group | spread | order | sections | captains | pooled (samples) | paired delta vs base-only, points [95% CI] |", "|---|---|---|---|---|---|---|---|---|"]
    for name, arms in rows:
        base = load(arms[0][1])
        for l, k in arms:
            s = load(k)
            if not s: continue
            t = fam_table(s, FAMS_BASE); ok, n = pooled(t, FAMS_BASE)
            d = "-" if k == arms[0][1] else (lambda p: f"{p['delta_pts']:+.1f} [{p['ci'][0]:+.1f}, {p['ci'][1]:+.1f}]")(paired(base, s, FAMS_BASE))
            out.append(f"| {name} | {l} | " + " | ".join(str(t[f]["pass1"]) for f in FAMS_BASE) + f" | {100*ok/n:.1f} ({ok}/{n}) | {d} |")
    return "\n".join(out)

def authoring_table():
    a = report.authoring(); sz = json.load(open(f"{R}/authoring_sizes.json"))
    sec = {"limit": 35, "pair": 42, "headseat": 15, "bigfirst": 23, "waitlist": 23, "snake": 28, "sectionlead": 37}
    out = ["| # | word | verifier attempts (seeds 0-2) | tool-clock s, start to end | reference lines | net lines | entry chars | est. tokens (reference + net + entry) | new fragment |", "|---|---|---|---|---|---|---|---|---|"]
    for i, w in enumerate(NEW_WORDS, 1):
        s = sz[w]; t = str(sec.get(w, "27 (batch of 3: 82 s)"))
        frag = "two-pass aggregate (first use)" if w == "headseat" else ("two-pass (reused)" if w in ("bigfirst", "sectionlead") else "-")
        out.append(f"| {i} | {w} | 1 | {t} | {s['ref_lines']} | {s['net_lines']} | {s['entry_chars']} | {s['total_tokens_est']} | {frag} |")
    mean_tok = sum(sz[w]["total_tokens_est"] for w in NEW_WORDS) / 10
    out.append(f"| | **mean** | **1.0** | **28.5** | {sum(sz[w]['ref_lines'] for w in NEW_WORDS)/10:.1f} | {sum(sz[w]['net_lines'] for w in NEW_WORDS)/10:.1f} | {sum(sz[w]['entry_chars'] for w in NEW_WORDS)/10:.0f} | {mean_tok:.0f} | |")
    return "\n".join(out)

if __name__ == "__main__":
    p = _REPO + "/docs/HERO-4.md"; s = open(p).read()
    s = s.replace("RESULTS_TABLE_A", table_a()).replace("TABLE_B", table_b()).replace("BASE_REG_TABLE", base_reg()).replace("AUTHORING_TABLE", authoring_table())
    s = s.replace("CONTROL_E", ctl("zs4b_all", "E")).replace("CONTROL_F", ctl("retrain_all", "F"))
    open(p, "w").write(s)
    print("filled; remaining placeholders:", [x for x in ["RESULTS_TABLE_A", "TABLE_B", "BASE_REG_TABLE", "AUTHORING_TABLE", "CONTROL_E", "CONTROL_F"] if x in s])
