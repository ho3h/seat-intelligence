"""HERO-7 judge for the fresh test set data/hero/policies_test7.json (frozen with the test set, before any HERO-7 model output).
Identical in construction to genome/hero6/judge6.py, with the test-7 invented guests:
  PASS (lenient) iff the sample parses under the strict lang6 parser and, on three guest lists - the real 34-guest chart, SYN_A,
  SYN_B - the section assignment computed by the tag-mask net (genome/hero6/sectioner6.py on the HVM2 executor, via
  genome.hero6.stress6.run_assign) for the sample's program equals the Python reference assignment of the GOLD program.
  SYN_A / SYN_B = real 34 + the 10 invented guests of test 7 (`extra_guests`) + the invented colleagues at real companies of
  judge6 (COLL_A / COLL_B) + synthetic filler, shuffled with seeds 701 / 702.
  STRICT = PASS and the same seating as the gold on 100 probe lists (all named guests: 34 + 10 + 21 colleagues, no filler, 100
  fixed shuffles, seeds 7100..7199; reference, the net equals it - genome/hero6/stress6.py).
"""
from __future__ import annotations
import functools, json, random, sys
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
sys.path.insert(0, _REPO)
from genome.hero6 import lang6 as L
from genome.hero6.lang6 import CID, ParseError
from genome.hero6.judge6 import COLL_A, COLL_B
from genome.hero1.guests import gen_guests

TEST7 = _REPO + "/data/hero/policies_test7.json"


def extra_guests(path=TEST7):
    return [(g["org"], CID[g["category"]], g["name"]) for g in json.load(open(path))["extra_guests"]]


@functools.lru_cache(maxsize=1)
def lists():
    real, _ = L.load_real()
    cat_of = {g[0]: g[1] for g in real if g[0]}
    extra = extra_guests()
    def build(coll, n_fill, seed, mix):
        fill = [(o, c, None) for o, c in gen_guests(n_fill, seed, mix)]
        g = real + extra + [(o, cat_of[o], nm) for o, nm in coll] + fill
        random.Random(seed).shuffle(g)
        return g
    return [("real34", real), ("synA", build(COLL_A, 20, 701, "balanced")), ("synB", build(COLL_B, 40, 702, "tech_heavy"))]


@functools.lru_cache(maxsize=None)
def _net_on_lists(canon):
    from genome.hero6.stress6 import run_assign
    pol = L.parse(canon)
    return [run_assign(g, pol) for _, g in lists()]


@functools.lru_cache(maxsize=None)
def _gold_on_lists(canon):
    pol = L.parse(canon)
    return [L.assign_ref(g, pol) for _, g in lists()]


def judge(sample_text, gold_text):
    gold = L.to_text(L.parse(gold_text))
    try: pol = L.parse(sample_text)
    except ParseError as e: return dict(passed=False, parsed=False, text_match=False, why=f"parse: {e}")
    canon = L.to_text(pol)
    try: got = _net_on_lists(canon)
    except (AssertionError, ParseError) as e: return dict(passed=False, parsed=True, text_match=False, why=f"prep: {e}")
    want = _gold_on_lists(gold)
    ok = all(a is not None and a == b for a, b in zip(got, want))
    return dict(passed=ok, parsed=True, text_match=(canon == gold), canon=canon,
                why="" if ok else "differs on " + ",".join(n for (n, _), a, b in zip(lists(), got, want) if a != b))


@functools.lru_cache(maxsize=1)
def probe_lists(k=100):
    real, _ = L.load_real()
    cat_of = {g[0]: g[1] for g in real if g[0]}
    base = real + extra_guests() + [(o, cat_of[o], nm) for o, nm in COLL_A + COLL_B]
    out = []
    for s in range(k):
        g = list(base); random.Random(7100 + s).shuffle(g); out.append(g)
    return out


@functools.lru_cache(maxsize=None)
def _probe(canon):
    pol = L.parse(canon)
    return tuple(tuple(L.assign_ref(g, pol)) for g in probe_lists())


def judge_strict(sample_text, gold_text):
    j = judge(sample_text, gold_text)
    if not j["passed"]: return False
    return _probe(j["canon"]) == _probe(L.to_text(L.parse(gold_text)))


if __name__ == "__main__":
    # sanity on gold programs only: every name token in a gold program matches at least one guest of the request guest list;
    # golds pass themselves; lenient-criterion blind spots (gold == empty program on the 3 lists) and single-line deletions detected.
    real, _ = L.load_real(); G = real + extra_guests()
    pols = json.load(open(TEST7))["policies"]
    bad = [(p["id"], x) for p in pols for ab in L.parse(p["gold"]).avoids + L.parse(p["gold"]).pairs for x in ab if not any(L.is_who(g, x) for g in G)]
    print("unmatched gold names:", bad)
    assert all(judge(p["gold"], p["gold"])["passed"] and judge_strict(p["gold"], p["gold"]) for p in pols)
    blind = sum(judge("none", p["gold"])["passed"] for p in pols)
    dl = dt = ds = 0
    for p in pols:
        ls = L.to_text(L.parse(p["gold"])).split("\n")
        if len(ls) < 2 and ls != ["none"]:
            dl += 1; dt += not judge("none", p["gold"])["passed"]; ds += not judge_strict("none", p["gold"]); continue
        for i in range(len(ls)):
            t = "\n".join(ls[:i] + ls[i + 1:]); dl += 1; dt += not judge(t, p["gold"])["passed"]; ds += not judge_strict(t, p["gold"])
    print(f"gold == empty program on the 3 lists: {blind}/100; single-line deletions detected: lenient {dt}/{dl}, strict {ds}/{dl}")
