"""Markdown fragments from the result files (so the doc numbers are copied by machine).  python3 -m genome.hero1.report <fragment>"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, os, sys, collections
R = _REPO + "/runs/hero1"
J = lambda p: json.load(open(os.path.join(R, p)))
pct = lambda x: f"{100 * x:.1f}%"


def ci(a): return f"[{100 * a['ci'][0]:.1f}, {100 * a['ci'][1]:.1f}]" if a.get("ci") else ""


def row(name, a):
    return f"| {name} | {a['policies']} | {a['passed']}/{a['samples']} | {pct(a['pass1'])} {ci(a)} | {a['passed'] if False else ''}{pct(a['text_match'])} |"


def main_table(path, label):
    r = J(path)["result"]
    L = [f"| {label} | policies | passed samples | pass@1 [95% CI] | exact program text |", "|---|---|---|---|---|"]
    L.append(row("all policies", r["overall"]))
    if r["heldout_combo"]["policies"]:
        L.append(row("seen stage combination", r["seen_combo"]))
        L.append(row("held-out combination (H1-H6)", r["heldout_combo"]))
    for v, a in r["by_voice"].items(): L.append(row(f"voice: {v}", a))
    for h, a in r["by_heldout"].items():
        if a["policies"]: L.append(row(f"held-out {h}", a))
    return "\n".join(L)


if __name__ == "__main__":
    which = sys.argv[1]
    if which == "t07": print(main_table("samples/test_t07.scored.json", "test set 1, T=0.7, n=5"))
    if which == "greedy": print(main_table("samples/test_greedy.scored.json", "test set 1, greedy"))
    if which == "t07n20": print(main_table("samples/test_t07_n20.scored.json", "test set 1, T=0.7, n=20"))
    if which == "t2": print(main_table("samples/test2_t07.scored.json", "test set 2, T=0.7, n=5"))
    if which == "t2g": print(main_table("samples/test2_greedy.scored.json", "test set 2, greedy"))
    if which == "zs4b": print(main_table("samples/zs4b_t07.scored.json", "untuned 4B-Instruct + vocabulary, T=0.7, n=5"))
