"""stage program text -> policy -> guest sequence -> verified sectioner net (HVM2 executor) -> section per guest.
Also the pipeline agreement test used by the kill rule."""
from __future__ import annotations
import os, sys, functools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genome.hero1.lang import parse, ParseError, prep, assign_ref, violations, to_text, load_real, Policy
from genome.hero1.guests import gen_guests, AGREE_LISTS
from genome.hero1 import sectioner as S
from genome.verify import assemble
from genome.executor import run_net
from genome.types import decode

_P = None


def program():
    global _P
    if _P is None: _P = S.make_program()
    return _P


def net_input(guests, pol):
    seq = prep(guests, pol)
    return (pol.cap, pol.rules(), [(c, s) for _, c, s in seq]), seq


def run_net_assign(guests, pol, backend="run", timeout=60.0):
    """-> (assignment per guest or None, Run). Uses the verified net."""
    x, seq = net_input(guests, pol)
    r = run_net(assemble(program(), S.net_text(), x), backend, timeout)
    if not r.ok: return None, r
    secs = decode(r.result, S.OUT)
    a = [None] * len(guests)
    for (i, _, _), sc in zip(seq, secs): a[i] = sc
    return a, r


@functools.lru_cache(maxsize=1)
def agree_lists():
    real, _ = load_real()
    return [("real34", real)] + [(f"syn{n}_{m}", gen_guests(n, s, m)) for n, s, m in AGREE_LISTS]


@functools.lru_cache(maxsize=None)
def _net_on_lists(canon_text):
    pol = parse(canon_text)
    res = []
    for name, g in agree_lists():
        a, r = run_net_assign(g, pol)
        res.append(a)
    return res


@functools.lru_cache(maxsize=None)
def _gold_on_lists(canon_text):
    pol = parse(canon_text)
    return [assign_ref(g, pol) for _, g in agree_lists()]


def judge(sample_text, gold_text):
    """-> dict(passed, parsed, text_match, violations (of the gold rules, total over the 4 lists), why)"""
    gold = to_text(parse(gold_text))
    try:
        pol = parse(sample_text)
    except ParseError as e:
        return dict(passed=False, parsed=False, text_match=False, why=f"parse: {e}")
    canon = to_text(pol)
    try:
        got = _net_on_lists(canon)
    except AssertionError as e:
        return dict(passed=False, parsed=True, text_match=False, why=f"prep: {e}")
    want = _gold_on_lists(gold)
    ok = all(a is not None and a == b for a, b in zip(got, want))
    viol = 0
    if all(a is not None for a in got):
        gp = parse(gold_text)
        viol = sum(violations(g, gp, a)["total"] for (_, g), a in zip(agree_lists(), got))
    return dict(passed=ok, parsed=True, text_match=(canon == gold), gold_violations=viol,
                why="" if ok else "assignment differs from reference on " + ",".join(n for (n, _), a, b in zip(agree_lists(), got, want) if a != b))
