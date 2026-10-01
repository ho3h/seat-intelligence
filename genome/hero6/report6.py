"""Score all HERO-6 samples and print the tables. python3 -m genome.hero6.report6"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, os, sys, subprocess, collections
sys.path.insert(0, _REPO)
from genome.hero6 import judge6
O = _REPO + "/runs/hero6/samples"


def old(tag, test):
    env = dict(os.environ, TEST_FILE=test)
    subprocess.run([sys.executable, "-m", "genome.hero1.evaluate", f"{O}/{tag}.json"], env=env, check=True, capture_output=True)
    r = json.load(open(f"{O}/{tag}.scored.json"))["result"]
    o = r["overall"]
    return f"{o['passed']}/{o['samples']} = {100 * o['pass1']:.1f}% [{100 * o['ci'][0]:.1f}, {100 * o['ci'][1]:.1f}], exact text {100 * o['text_match']:.1f}%, parsed {100 * o['parsed']:.1f}%", r


def new(tag):
    r = judge6.main(f"{O}/{tag}.json")
    per = json.load(open(f"{O}/{tag}.scored.json"))["per"]
    strict = {}
    for pid, p in per.items():
        strict[pid] = sum(judge6.judge_strict(s["text"], p["gold"]) for s in p["samples"]) / p["n"]
    sv = sum(strict.values()) / len(strict)
    ns = sum(round(strict[i] * per[i]["n"]) for i in per); nt = sum(per[i]["n"] for i in per)
    fails = {pid: [(s["text"], s["why"]) for s in p["samples"] if not s["passed"]] for pid, p in per.items() if p["passed"] < p["n"]}
    return r, dict(strict_pass1=round(sv, 4), strict_passed=ns, samples=nt), fails, per


if __name__ == "__main__":
    out = {}
    for tag, test in (("test_t07", "data/hero/policies_test.json"), ("test_greedy", "data/hero/policies_test.json"),
                      ("test2_t07", "data/hero/policies_test2.json"), ("test2_greedy", "data/hero/policies_test2.json")):
        if os.path.exists(f"{O}/{tag}.json"):
            s, r = old(tag, _REPO + "/" + test); out[tag] = r; print(tag, s)
            print("   failing:", {k: v for k, v in r["policy_pass"].items() if v.split("/")[0] != v.split("/")[1]})
    for tag in ("test6_t07", "test6_greedy"):
        if os.path.exists(f"{O}/{tag}.json"):
            r, st, fails, per = new(tag); out[tag] = dict(result=r, strict=st)
            print(tag, "STRICT", st)
            for pid, fs in fails.items():
                print("  FAIL", pid, per[pid]["passed"], "/", per[pid]["n"], "|", per[pid]["text"][:150].replace("\n", " / "), "| gold:", per[pid]["gold"].replace("\n", "; "))
                for t, w in collections.Counter((t.strip().replace("\n", "; "), w) for t, w in fs).most_common(3): print("       ", t, "|", w)
    json.dump(out, open(_REPO + "/runs/hero6/report.json", "w"), indent=1, default=str)
