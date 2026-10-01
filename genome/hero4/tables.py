"""Print the markdown tables for docs/HERO-4.md from the scored samples (run after all arms exist)."""
import json
from genome.hero4 import report
from genome.hero4.report import load, fam_table, strict_table, NEW_WORDS, FAMS_BASE, paired
R = report.R
vac1 = set(json.load(open(f"{R}/sets/vacuous_test_ids.json"))); vac2 = set(json.load(open(f"{R}/sets/vacuous_testv2_ids.json")))
tasks1 = json.load(open(f"{R}/sets/FROZEN/test_final.json"))

def pooled(t, fams=NEW_WORDS):
    ok = sum(t[f]["pass_samples"] for f in fams); n = sum(t[f]["samples"] for f in fams); return f"{100*ok/n:.1f} ({ok}/{n})"

print("### TABLE A: test v1, round-1 entries (pre-registered), 30 tasks x 4 samples per family")
A = [("A. base-only block", "main_without"), ("B. + own word", "main_own"), ("C. + all ten", "main_all"),
     ("G. ablation, constant names, + own", "const_own"), ("E. untuned 4B-Instruct, all 15", "zs4b_all"), ("F. retrained 1.7B, all 15", "retrain_all")]
cols = [(l, fam_table(load(k), NEW_WORDS) if load(k) else None) for l, k in A]
print(report.md_newtable(cols))
print()
print("CI (95% task bootstrap) for arm B:", {f: v["ci"] for f, v in fam_table(load("main_own"), NEW_WORDS).items()})
print("strict (pass AND uses the word, vacuous tasks dropped), arm B:", {f: v["pass1_word_required"] for f, v in strict_table(load("main_own"), vac1).items()})
print("strict arm C:", {f: v["pass1_word_required"] for f, v in strict_table(load("main_all"), vac1).items()})
print("paired B - A:", paired(load("main_without"), load("main_own"), NEW_WORDS), " C - A:", paired(load("main_without"), load("main_all"), NEW_WORDS))
print()
print("### TABLE B: fresh test v2 (new wording writers, new params), 30 x 4 per family")
B = [("base-only", "tv2_without"), ("own, r1 entries", "tv2_r1_own"), ("all ten, r1", "tv2_r1_all"), ("own, r2 entries", "tv2_r2_own"), ("all ten, r2", "tv2_r2_all")]
cols = [(l, fam_table(load(k), NEW_WORDS) if load(k) else None) for l, k in B]
print(report.md_newtable(cols))
print("strict own r1:", {f: v["pass1_word_required"] for f, v in strict_table(load("tv2_r1_own"), vac2).items()})
print()
print("### TABLE C: base regression (pass@1 of the 5 base families, 30 tasks x 4 each)")
for name, pairs in [("test v1 (n=150 tasks)", [("base-only", "main_without"), ("+ all ten (r1)", "main_all")]),
                    ("test v1 iid templates", [("base-only", "main_iid_without"), ("+ all ten", "main_iid_all")]),
                    ("test v2 (n=150)", [("base-only", "btv2_without"), ("+ one rotating word r1", "btv2_r1_one"), ("+ one rotating word r2", "btv2_r2_one"),
                                         ("+ all ten r1", "btv2_r1_all"), ("+ all ten r2", "btv2_r2_all")])]:
    print("**" + name + "**")
    base = load(pairs[0][1])
    for l, k in pairs:
        s = load(k)
        if not s: print("  ", l, "n/a"); continue
        t = fam_table(s, FAMS_BASE); d = "" if k == pairs[0][1] else " delta vs base-only " + json.dumps(paired(base, s, FAMS_BASE))
        print("  ", l, {f: v["pass1"] for f, v in t.items()}, "pooled", pooled(t, FAMS_BASE), d)
print()
print("### repaired-closer diagnostic (round 1, arm B and C)")
for k in ["main_own", "main_all"]:
    print(k, report.repaired_table(k, NEW_WORDS))
print("### adoption arm B:", json.dumps(report.adoption(load("main_own"))))
