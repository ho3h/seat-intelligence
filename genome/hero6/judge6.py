"""HERO-6 judge for named rules (frozen with the test set, before any model output).

A sample passes iff (1) it parses under the strict lang6 parser and (2) on all THREE guest lists - the real 34-guest chart,
SYN_A and SYN_B below - the section assignment computed by the tag-mask net (genome/hero6/sectioner6.py, run on the HVM2
executor) for the SAMPLE's program equals the Python reference assignment (lang6.assign_ref) of the GOLD program.

SYN_A / SYN_B: the 34 real guests + the 16 invented guests of data/hero/policies_test6.json (`extra_guests`) + invented
colleagues at real companies (so a company token and a person token differ) + synthetic filler guests
(genome/hero1/guests.gen_guests), shuffled with a fixed seed.
  python3 -m genome.hero6.judge6 <samples.json> [out.json]      (samples from genome/hero1/sample.py --set data/hero/policies_test6.json)
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import functools, json, os, random, sys, collections
sys.path.insert(0, _REPO)
from genome.hero6 import lang6 as L
from genome.hero6.lang6 import CID, ParseError
from genome.hero1.guests import gen_guests

TEST6 = _REPO + "/data/hero/policies_test6.json"
COLL_A = [("OpenAI", "Yuki Tanabe"), ("OpenAI", "Marcus Webb"), ("Anthropic", "Priscilla Moyo"), ("Google", "Henrik Alm"),
          ("Microsoft", "Rosa Ibanez"), ("Nvidia", "Kai Brandt"), ("Palantir", "Dana Whitcomb"), ("Meta", "Omar Sayegh"),
          ("Amazon", "Lena Fischer"), ("NASA", "Tobias Reyes")]
COLL_B = [("OpenAI", "Nina Sorensen"), ("Anthropic", "Felix Aranda"), ("Anthropic", "June Park"), ("Google", "Ravi Menon"),
          ("Google", "Clara Voss"), ("Microsoft", "Idris Bello"), ("AMD", "Sofia Lindgren"), ("Meta", "Theo Marchetti"),
          ("Social Capital", "Maya Castell"), ("Service Now", "Paul Okafor"), ("X, Tesla, Space X", "Rita Kowal")]


@functools.lru_cache(maxsize=1)
def lists():
    real, _ = L.load_real()
    cat_of = {g[0]: g[1] for g in real if g[0]}
    extra = [(g["org"], CID[g["category"]], g["name"]) for g in json.load(open(TEST6))["extra_guests"]]
    def build(coll, n_fill, seed, mix):
        fill = [(o, c, None) for o, c in gen_guests(n_fill, seed, mix)]
        g = real + extra + [(o, cat_of[o], nm) for o, nm in coll] + fill
        random.Random(seed).shuffle(g)
        return g
    return [("real34", real), ("synA", build(COLL_A, 20, 601, "balanced")), ("synB", build(COLL_B, 40, 602, "tech_heavy"))]


def net_assign(g, pol):
    from genome.hero6.stress6 import run_assign
    return run_assign(g, pol)


@functools.lru_cache(maxsize=None)
def _net_on_lists(canon):
    pol = L.parse(canon)
    return [net_assign(g, pol) for _, g in lists()]


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


def boot(xs, B=4000, seed=0):
    r = random.Random(seed); n = len(xs); ms = sorted(sum(r.choice(xs) for _ in range(n)) / n for _ in range(B))
    return ms[int(0.025 * B)], ms[int(0.975 * B)]


def main(path, out=None):
    pols = {p["id"]: p for p in json.load(open(TEST6))["policies"]}
    S = json.load(open(path))["samples"]
    per = {}
    for pid, texts in S.items():
        p = pols[pid]; js = []
        for t in texts:
            j = judge(t, p["gold"]); j["text"] = t; js.append(j)
        per[pid] = dict(voice=p["voice"], invented=p.get("invented", False), n=len(js), passed=sum(j["passed"] for j in js),
                        text_match=sum(j["text_match"] for j in js), parsed=sum(j["parsed"] for j in js), gold=p["gold"], text=p["text"], samples=js)
    def agg(sel):
        sel = list(sel); v = [per[i]["passed"] / per[i]["n"] for i in sel]
        tn = sum(per[i]["n"] for i in sel)
        return dict(policies=len(sel), samples=tn, passed=sum(per[i]["passed"] for i in sel),
                    pass1=round(sum(v) / len(v), 4) if v else None, ci=[round(x, 4) for x in boot(v)] if v else None,
                    text_match=round(sum(per[i]["text_match"] for i in sel) / tn, 4) if tn else None,
                    parsed=round(sum(per[i]["parsed"] for i in sel) / tn, 4) if tn else None)
    ids = sorted(per)
    gold = {i: L.parse(pols[i]["gold"]) for i in ids}
    res = dict(source=path, overall=agg(ids),
               invented=agg(i for i in ids if per[i]["invented"]), real_only=agg(i for i in ids if not per[i]["invented"]),
               avoid_only=agg(i for i in ids if gold[i].avoids and not gold[i].pairs),
               pair_only=agg(i for i in ids if gold[i].pairs and not gold[i].avoids),
               both=agg(i for i in ids if gold[i].pairs and gold[i].avoids),
               with_old_words=agg(i for i in ids if gold[i].old().sig()),
               named_only=agg(i for i in ids if not gold[i].old().sig()),
               policy_pass=collections.OrderedDict((i, f"{per[i]['passed']}/{per[i]['n']}") for i in ids))
    json.dump(dict(result=res, per=per), open(out or path.replace(".json", ".scored.json"), "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "policy_pass"}, indent=1))
    return res


if __name__ == "__main__": main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)


# ------------------------------------------------------------------ STRICT secondary criterion (frozen with the test set)
# The 3-list criterion above is the one the kill rule names. It is lenient for named rules: an `avoid` line that is dropped goes
# unnoticed whenever the two guests land in different sections anyway (8 of the 72 gold programs give the same seating as an
# empty program on all 3 lists). STRICT additionally requires the same seating as the gold on 100 probe lists: all named guests
# (34 real + 16 invented + the 21 invented colleagues above, no filler) in 100 fixed random orders. Reference only (the net
# equals the reference: genome/hero6/stress6.py).
@functools.lru_cache(maxsize=1)
def probe_lists(k=100):
    real, _ = L.load_real()
    cat_of = {g[0]: g[1] for g in real if g[0]}
    extra = [(g["org"], CID[g["category"]], g["name"]) for g in json.load(open(TEST6))["extra_guests"]]
    base = real + extra + [(o, cat_of[o], nm) for o, nm in COLL_A + COLL_B]
    out = []
    for s in range(k):
        g = list(base); random.Random(7000 + s).shuffle(g); out.append(g)
    return out


@functools.lru_cache(maxsize=None)
def _probe(canon):
    pol = L.parse(canon)
    return tuple(tuple(L.assign_ref(g, pol)) for g in probe_lists())


def judge_strict(sample_text, gold_text):
    j = judge(sample_text, gold_text)
    if not j["passed"]: return False
    return _probe(j["canon"]) == _probe(L.to_text(L.parse(gold_text)))
