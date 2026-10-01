"""HERO-4 seating words as verified parametric net templates (each = ONE Python function -> HVM2 net text).

BASE (5, authored before the experiment starts): group, spread, order, sections, captains.
NEW (10, authored one at a time, in this order, each logged in runs/hero4/authoring_log.jsonl): limit pair apart vip stagger
headseat bigfirst waitlist snake sectionlead.  Semantics = the Python references in refs.py (the hidden suite compares them).
"""
from __future__ import annotations
from genome.compose import compose_nets
from genome.hero4.refs import CATS, CO
from genome.hero4.netlib import (scan_net, fold_bank_net, sort_net, strip_net, keyed_sort_word, compile_expr, Gen, split, _book, _walk,
                                 sel, eq, ne, lt, gt, ge, le, add, sub, mul, div, mod, mn, IDX, RANK, CAT, COMP, RI, bank_lit)

BIG = (1 << 24) - 1
IDENTITY = "@prog = (l l)\n"


def _ksort(annot): return keyed_sort_word(annot)


# =============================================================== BASE
def net_group(field):
    key = ("-", COMP(), 1) if field == "company" else CAT()
    return _ksort(scan_net("gp", key=key))


def net_spread():
    return _ksort(scan_net("sp1", K=8, upd=add("c", 1), cls=CAT(), key="occ"))


def net_order(mode, names=()):
    if mode == "rank": key = RANK()
    elif mode == "rankdesc": key = sub(31, RANK())
    else:
        codes = [CATS[n] for n in names] if mode == "category" else [CO[n] for n in names]
        fld = CAT() if mode == "category" else COMP()
        key = len(codes)
        for i in reversed(range(len(codes))): key = sel(eq(fld, codes[i]), i, key)
    return _ksort(scan_net("od", key=key))


def net_sections(S):
    return scan_net("sc", use_pos=True, key=add(mul(div("pos", S), 64), IDX()), emit="value")


def net_captains(S):
    """closing scan: one output per section of S seats = section index * 64 + idx of the member with the smallest (rank, idx)."""
    g = Gen(); c = []
    compile_expr(mn(RI("h"), "m"), {"h": "h", "m": "mn"}, "nm", g, c)
    pe, pv, pn = split("pos", 3, g, c)
    c.append(f"{pn} ~ $([+] $(1 pos1))")
    compile_expr(eq(mod("p", S), S - 1), {"p": pe}, "isend", g, c)
    nv, nm2 = split("nm", 2, g, c)
    compile_expr(add(mul(div("p", S), 64), ("&", "n", 63)), {"p": pv, "n": nv}, "val", g, c)
    c.append(f"isend ~ ?((@cp_no @cp_yes) ({nm2} (pos1 (val (t out)))))")
    g2 = Gen(); rn = []
    compile_expr(add(mul(div(sub("p", 1), S), 64), ("&", "n", 63)), {"p": "pb", "n": "mn"}, "val", g2, rn)
    defs = [
        ("cp", _walk("cp", "(pos (mn out))"), []),
        ("cp_nil", "(* (pos (mn out)))", ["pos ~ {pa pb}", f"pa ~ $([%] $({S} pc))", "pc ~ ?((@cpn_z @cpn_nz) (pb (mn out)))"]),
        ("cpn_z", "(pb (mn (0 *)))", ["pb ~ *", "mn ~ *"]),
        ("cpn_nz", "(* (pb (mn (1 (val (0 *))))))", rn),
        ("cp_cons", "(* ((h t) (pos (mn out))))", c),
        ("cp_no", "(nm2 (pos1 (val (t out))))", ["val ~ *", "@cp ~ (t (pos1 (nm2 out)))"]),
        ("cp_yes", "(* (nm2 (pos1 (val (t (1 (val t2)))))))", ["nm2 ~ *", f"@cp ~ (t (pos1 ({BIG} t2)))"]),
        ("prog", "(l out)", [f"@cp ~ (l (0 ({BIG} out)))"]),
    ]
    return _book(defs)


# registry: name -> (arrange?, builder taking the parsed args)
BUILD = {
    "group": lambda a: net_group(a[0]), "spread": lambda a: net_spread(),
    "order": lambda a: net_order(a[0], a[1:]),
    "sections": lambda a: net_sections(a[0]), "captains": lambda a: net_captains(a[0]),
}
