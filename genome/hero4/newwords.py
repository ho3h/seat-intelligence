"""The ten NEW words, authored one at a time (order = refs.NEW_WORDS). Each is one Python function -> net text; see author.py for the log."""
from __future__ import annotations
from genome.hero4.refs import CATS, CO
from genome.hero4.netlib import (scan_net, fold_bank_net, keyed_sort_word, sel, eq, ne, lt, gt, ge, le, add, sub, mul, div, mod, mn,
                                 IDX, RANK, CAT, COMP, RI, compile_expr)
from genome.hero4.words import IDENTITY, _ksort, BIG

BUILD_NEW = {}
SRC = {}


# ---------------------------------------------------------------- 1. limit <cat> <k> <S>: at most k guests of a category per section
def net_limit(cat, k, S):
    if k >= S: return IDENTITY
    key = sel("cls", mul(div("occ", k), 2), add(mul(div("occ", S - k), 2), 1))
    return _ksort(scan_net("lm", K=2, upd=add("c", 1), cls=eq(CAT(), CATS[cat]), key=key))
BUILD_NEW["limit"] = lambda a: net_limit(a[0], a[1], a[2]); SRC["limit"] = net_limit


# ---------------------------------------------------------------- 2. pair <catA> <catB>: A_j immediately followed by B_j, everyone else after
def net_pair(a, b):
    cls = sel(eq(CAT(), CATS[a]), 1, sel(eq(CAT(), CATS[b]), 2, 0))
    key = sel(eq("cls", 1), mul("occ", 2), sel(eq("cls", 2), add(mul("occ", 2), 1), 4096))
    return _ksort(scan_net("pr", K=3, upd=add("c", 1), cls=cls, key=key))
BUILD_NEW["pair"] = lambda a: net_pair(a[0], a[1]); SRC["pair"] = net_pair


# ---------------------------------------------------------------- 3. apart <CoX> <CoY>: company X first, everyone else, company Y last
def net_apart(x, y):
    key = sel(eq(COMP(), CO[x]), 0, sel(eq(COMP(), CO[y]), 2, 1))
    return _ksort(scan_net("ap", key=key))
BUILD_NEW["apart"] = lambda a: net_apart(a[0], a[1]); SRC["apart"] = net_apart


# ---------------------------------------------------------------- 4. vip <R>: rank <= R first (stable), then the rest
def net_vip(R):
    return _ksort(scan_net("vp", key=gt(RANK(), R)))
BUILD_NEW["vip"] = lambda a: net_vip(a[0]); SRC["vip"] = net_vip


# ---------------------------------------------------------------- 5. stagger <m>: rounds; each round takes at most m guests per company
def net_stagger(m):
    key = sel(ne("cls", 0), div("occ", m), 0)
    return _ksort(scan_net("sg", K=32, upd=add("c", 1), cls=COMP(), key=key))
BUILD_NEW["stagger"] = lambda a: net_stagger(a[0]); SRC["stagger"] = net_stagger


# ---------------------------------------------------------------- 6. headseat: the smallest-(rank, idx) guest takes seat 1   [two-pass: aggregate, then map]
def two_pass(name, K, fold_upd, fold_cls, fold_val, get_cls, key, use_pos=False, init=0):
    """pass 1 folds an aggregate into a K-bank, pass 2 maps every guest with a read-only lookup (bank leaf = variable `occ`), then sort, strip"""
    from genome.compose import compose_nets
    from genome.hero4.netlib import sort_net, strip_net
    fold = fold_bank_net(name + "f", use_pos=use_pos, K=K, upd=fold_upd, cls=fold_cls, val=fold_val, init_bank=init)
    scan = scan_net(name + "s", use_pos=use_pos, K=K, upd=add("c", 0), cls=get_cls, key=key, input_bank=True)
    return compose_nets([fold, scan, sort_net(), strip_net()])


def net_headseat():
    return two_pass("hd", 1, mn("c", "v"), 0, RI(), 0, sel(eq(RI(), "occ"), 0, 1), init=BIG)
BUILD_NEW["headseat"] = lambda a: net_headseat(); SRC["headseat"] = (two_pass, net_headseat)


# ---------------------------------------------------------------- 7. bigfirst: bigger company delegations first (ties by company id), no company last
def net_bigfirst():
    key = sel(eq(COMP(), 0), 3000, add(mul(sub(64, "occ"), 32), COMP()))
    return two_pass("bg", 32, add("c", 1), COMP(), 0, COMP(), key)
BUILD_NEW["bigfirst"] = lambda a: net_bigfirst(); SRC["bigfirst"] = net_bigfirst


# ---------------------------------------------------------------- 8. waitlist <cat> <k>: only the first k of a category keep their place, the rest go last
def net_waitlist(cat, k):
    return _ksort(scan_net("wl", K=2, upd=add("c", 1), cls=eq(CAT(), CATS[cat]), key=mul("cls", ge("occ", k))))
BUILD_NEW["waitlist"] = lambda a: net_waitlist(a[0], a[1]); SRC["waitlist"] = net_waitlist


# ---------------------------------------------------------------- 9. snake <S>: seat order reversed inside every second section
def net_snake(S):
    b, r = div("pos", S), mod("pos", S)
    key = add(mul(b, S), sel(("&", b, 1), sub(S - 1, r), r))
    return _ksort(scan_net("sn", use_pos=True, key=key))
BUILD_NEW["snake"] = lambda a: net_snake(a[0]); SRC["snake"] = net_snake


# ---------------------------------------------------------------- 10. sectionlead <S>: the smallest-(rank, idx) guest of each section moves to the section's first seat
def net_sectionlead(S):
    K = 64 // S + 1                                   # sections of an input of at most 63 guests
    key = add(add(mul(div("pos", S), 4096), sel(eq(RI(), "occ"), 0, 2048)), "pos")
    return two_pass("sl", K, mn("c", "v"), div("pos", S), RI(), div("pos", S), key, use_pos=True, init=BIG)
BUILD_NEW["sectionlead"] = lambda a: net_sectionlead(a[0]); SRC["sectionlead"] = net_sectionlead
