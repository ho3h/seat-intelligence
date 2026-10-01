"""HERO-2 pre-registered test corpus (written and frozen BEFORE the normalizer was run on it; see docs/HERO-2.md s.1).

A Case is a pair of nets (A, B), each a full HVM2 book whose entry is `@prog = (input output)`. `expect` is the label by
construction: "equal" (A and B compute the same thing on every input of type `inp`) or "unequal" (some input separates them).
Classes:
  syn-equal   (a) 46 pairs: F1 associativity, F2 identity insertion, F3 dup/erase laws, F4 reordering independent stages,
              F5 inlining vs call, F6 wrapper (recipe-like) vs hand-expanded form
  syn-unequal (b) 46 pairs: U1 off-by-one wiring, U2 swapped ports, U3 dropped stage, U4 wrong constant, U5 misc + rare-witness
  real        (c) pairs from the repo: R1 genome/opt.py (static+inline) vs original, R2 opt.py (static only) vs original,
              R3 glue-composed vs hand-wired (exp14 typed/raw vs exp8), R4 recipe wrappers vs opt.py-inlined expansion
  extra       informational only, NOT in any denominator: extensionally-equal-but-restructured pairs (exp12 lookahead)
"""
from __future__ import annotations
import os
from dataclasses import dataclass, field

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class Case:
    id: str
    cls: str            # F1..F6, U1..U5, R1..R4, X1
    expect: str         # equal | unequal
    A: str
    B: str
    inp: object = None  # genome.types type (synthetic) ...
    prog: object = None  # ... or a genome.corpus Program (real)
    note: str = ""
    denom: bool = True  # counted in the kill-rule denominators


# ============================================================================ standard library of small helper nets
STD = """
@id = (x x)
@inc = (x y)
  & x ~ $([+1] y)
@dbl = (x y)
  & x ~ $([*2] y)
@dec = (x y)
  & x ~ $([-] $(1 y))
@add7 = (x y)
  & x ~ $([+7] y)
@sq = (x y)
  & x ~ {a b}
  & a ~ $([*] $(b y))
@neg = (x y)
  & 0 ~ $([-] $(x y))
@cmp = (f (g (x z)))
  & f ~ (x y)
  & g ~ (y z)
@fst = ((a *) a)
@snd = ((* b) b)
@swap = ((a b) (b a))
@addp = ((a b) c)
  & a ~ $([+] $(b c))
@mulp = ((a b) c)
  & a ~ $([*] $(b c))
@subp = ((a b) c)
  & a ~ $([-] $(b c))
@map_inc = ((?((@mi_nil @mi_cons) (pl out)) pl) out)
@mi_nil = (* (0 *))
@mi_cons = (* ((h t) out))
  & out ~ (1 (d tl))
  & h ~ $([+1] d)
  & t ~ (?((@mi_nil @mi_cons) (pl tl)) pl)
@map_dbl = ((?((@md_nil @md_cons) (pl out)) pl) out)
@md_nil = (* (0 *))
@md_cons = (* ((h t) out))
  & out ~ (1 (d tl))
  & h ~ $([*2] d)
  & t ~ (?((@md_nil @md_cons) (pl tl)) pl)
@sum = (l out)
  & @sm ~ (l (0 out))
@sm = ((?((@sm_nil @sm_cons) (pl (acc out))) pl) (acc out))
@sm_nil = (* (a a))
@sm_cons = (* ((h t) (acc out)))
  & acc ~ $([+] $(h a2))
  & @sm ~ (t (a2 out))
@len = (l out)
  & @ln ~ (l (0 out))
@ln = ((?((@ln_nil @ln_cons) (pl (acc out))) pl) (acc out))
@ln_nil = (* (a a))
@ln_cons = (* ((h t) (acc out)))
  & h ~ *
  & acc ~ $([+1] a2)
  & @ln ~ (t (a2 out))
@fl = ((?((@fl_nil @fl_cons) (pl out)) pl) out)
@fl_nil = (* (0 *))
@fl_cons = (* ((h t) out))
  & h ~ {h1 h2}
  & h1 ~ $([>] $(3 c))
  & c ~ ?((@fl_no @fl_yes) (h2 (t out)))
@fl_no = (h (t out))
  & h ~ *
  & @fl ~ (t out)
@fl_yes = (* (h (t out)))
  & out ~ (1 (h tl))
  & @fl ~ (t tl)
@sa = ((a b) (a2 b))
  & @inc ~ (a a2)
@sb = ((a b) (a b2))
  & @dbl ~ (b b2)
@t1 = ((a (b c)) (a2 (b c)))
  & @inc ~ (a a2)
@t2 = ((a (b c)) (a (b2 c)))
  & @dbl ~ (b b2)
@t3 = ((a (b c)) (a (b c2)))
  & @sq ~ (c c2)
@sl = ((l n) (l2 n))
  & @map_inc ~ (l l2)
@sn = ((l n) (l n2))
  & @inc ~ (n n2)
"""

_NUM = None  # types are imported lazily so that `import corpus` is cheap
def _T():
    from genome.types import u24, list_of, tup
    return u24, list_of(u24), tup(u24, u24), tup(u24, u24, u24), tup(list_of(u24), u24)


def _blocks(text):
    import re
    parts = re.split(r"(?m)^(?=@[\w]+\s*=)", text.strip() + "\n")
    return [b for b in parts if b.strip()]


def book(defs: str) -> str:
    """STD helpers + the pair's own definitions. A definition in `defs` replaces a same-named STD definition."""
    import re
    own = {re.match(r"@(\w+)", b).group(1) for b in _blocks(defs)}
    keep = [b for b in _blocks(STD) if re.match(r"@(\w+)", b).group(1) not in own]
    return "".join(b if b.endswith("\n") else b + "\n" for b in keep) + "\n" + defs.strip() + "\n"


def prog(body: str, sig: str = "(x out)") -> str:
    return f"@prog = {sig}\n{body.rstrip()}\n" if body.strip() else f"@prog = {sig}\n"


# ---------------------------------------------------------------------------- composition builders (cmp combinator)
def cmp_left(fs):
    """((f0;f1);f2);...  as @cmp calls on function values."""
    L = [f"  & @cmp ~ (@{fs[0]} (@{fs[1]} c1))"]
    for i, f in enumerate(fs[2:], 2):
        L.append(f"  & @cmp ~ (c{i-1} (@{f} c{i}))")
    L.append(f"  & c{len(fs)-1} ~ (x out)")
    return "\n".join(L)


def cmp_right(fs):
    """f0;(f1;(f2;...))"""
    n = len(fs)
    L = [f"  & @cmp ~ (@{fs[n-2]} (@{fs[n-1]} c1))"]
    for k in range(2, n):
        L.append(f"  & @cmp ~ (@{fs[n-1-k]} (c{k-1} c{k}))")
    L.append(f"  & c{n-1} ~ (x out)")
    return "\n".join(L)


def glue(fs, first="x", last="out"):
    """plain glue chain: x -f0-> a1 -f1-> a2 ... -> out"""
    L = []
    prev = first
    for i, f in enumerate(fs):
        nxt = last if i == len(fs) - 1 else f"a{i+1}"
        L.append(f"  & @{f} ~ ({prev} {nxt})")
        prev = nxt
    return "\n".join(L)


CASES: list[Case] = []


def eq(cls, name, A, B, inp, note=""):
    CASES.append(Case(f"{cls}_{name}", cls, "equal", A, B, inp=inp, note=note))


def ne(cls, name, A, B, inp, note=""):
    CASES.append(Case(f"{cls}_{name}", cls, "unequal", A, B, inp=inp, note=note))


def build_synthetic():
    if CASES: return
    U, LST, PAIR, TRI, LN = _T()

    # ------------------------------------------------------------------ F1 associativity of composition (8)
    def assoc(name, fs, inp, note=""):
        eq("F1", name, book(prog(cmp_left(fs))), book(prog(cmp_right(fs))), inp, note)
    assoc("num3a", ["inc", "dbl", "sq"], U)
    assoc("num3b", ["dbl", "sq", "dec"], U)
    assoc("num3c", ["sq", "inc", "add7"], U)
    assoc("num4", ["inc", "dbl", "sq", "dec"], U)
    eq("F1", "num4_balanced",
       book(prog("  & @cmp ~ (@inc (@dbl c1))\n  & @cmp ~ (@sq (@dec c2))\n  & @cmp ~ (c1 (c2 c3))\n  & c3 ~ (x out)")),
       book(prog("  & @cmp ~ (@dbl (@sq c1))\n  & @cmp ~ (c1 (@dec c2))\n  & @cmp ~ (@inc (c2 c3))\n  & c3 ~ (x out)")), U,
       "(a;b);(c;d) vs a;((b;c);d)")
    assoc("pair_fst", ["fst", "inc", "dbl"], PAIR)
    assoc("list3", ["map_inc", "map_dbl", "sum"], LST)
    eq("F1", "glue_vs_cmp", book(prog(glue(["inc", "dbl", "sq"]))), book(prog(cmp_right(["inc", "dbl", "sq"]))), U,
       "plain redex chain vs combinator-built composition")

    # ------------------------------------------------------------------ F2 identity insertion (8)
    eq("F2", "id_before", book(prog(glue(["inc"]))), book(prog(glue(["id", "inc"]))), U)
    eq("F2", "id_after", book(prog(glue(["inc"]))), book(prog(glue(["inc", "id"]))), U)
    eq("F2", "id_middle", book(prog(glue(["sq", "dbl"]))), book(prog(glue(["sq", "id", "dbl"]))), U)
    eq("F2", "id_after_map", book(prog(glue(["map_inc"]))), book(prog(glue(["map_inc", "id"]))), LST)
    eq("F2", "id_in_cmp", book(prog("  & @cmp ~ (@inc (@id c))\n  & c ~ (x out)")), book(prog(glue(["inc"]))), U)
    eq("F2", "id_cmp_ids", book(prog("  & @cmp ~ (@id (@id c1))\n  & @cmp ~ (@id (c1 c2))\n  & c2 ~ (x out)")),
       book(prog(glue(["id"]))), U, "three ids composed = one id")
    eq("F2", "id_on_component",
       book(prog("  & @inc ~ (a a2)\n  & out ~ (a2 b)", "((a b) out)")),
       book(prog("  & @inc ~ (a a1)\n  & @id ~ (a1 a2)\n  & out ~ (a2 b)", "((a b) out)")), PAIR)
    eq("F2", "id_on_fan_branch",
       book(prog("  & x ~ {a b}\n  & a ~ $([+] $(b out))")),
       book(prog("  & x ~ {a b}\n  & @id ~ (b b2)\n  & a ~ $([+] $(b2 out))")), U)

    # ------------------------------------------------------------------ F3 dup/erase laws (8)
    eq("F3", "dup_literal",
       book(prog("  & 7 ~ {a b}\n  & a ~ $([+] $(b c))\n  & c ~ $([+] $(x out))")),
       book(prog("  & 7 ~ $([+] $(7 c))\n  & c ~ $([+] $(x out))")), U, "duplicating a literal = writing it twice")
    eq("F3", "dup_of_eraser_dead",
       book(prog("  & * ~ {a b}\n  & @inc ~ (a c)\n  & @dbl ~ (b d)\n  & c ~ *\n  & d ~ *\n  & x ~ out")),
       book(prog("", "(x x)")), U, "dead subnet fed by a duplicated eraser")
    eq("F3", "dup_erase_one", book(prog("  & x ~ {out *}")), book(prog("", "(x x)")), U, "{a *} = wire (label-oblivious law)")
    eq("F3", "dup_reassoc",
       book(prog("  & x ~ {a {b c}}\n  & a ~ $([+] $(b s))\n  & s ~ $([+] $(c out))")),
       book(prog("  & x ~ {{a b} c}\n  & a ~ $([+] $(b s))\n  & s ~ $([+] $(c out))")), U, "fan-out associativity")
    eq("F3", "dup_swap_branches",
       book(prog("  & x ~ {a b}\n  & a ~ $([-] $(b out))")),
       book(prog("  & x ~ {b a}\n  & a ~ $([-] $(b out))")), U, "x - x with the two copies exchanged")
    eq("F3", "dup_over_pair",
       book(prog("  & (p q) ~ {a b}\n  & @addp ~ (a s)\n  & @mulp ~ (b m)\n  & out ~ (s m)", "((p q) out)")),
       book(prog("  & p ~ {p1 p2}\n  & q ~ {q1 q2}\n  & @addp ~ ((p1 q1) s)\n  & @mulp ~ ((p2 q2) m)\n  & out ~ (s m)", "((p q) out)")),
       PAIR, "duplicating a constructed pair = duplicating its components")
    eq("F3", "dead_code",
       book(prog("  & @inc ~ (x y)\n  & y ~ *\n  & out ~ 0")),
       book(prog("  & x ~ *\n  & out ~ 0")), U, "computing a value then erasing it = erasing the input (dead-code elimination)")
    eq("F3", "dup_output_swap",
       book(prog("  & @inc ~ (x y)\n  & y ~ {a b}\n  & out ~ (a b)")),
       book(prog("  & @inc ~ (x y)\n  & y ~ {b a}\n  & out ~ (a b)")), U, "copies of one value placed in a pair, order of the fan-out exchanged")

    # ------------------------------------------------------------------ F4 reordering of independent stages (8)
    eq("F4", "pair_sa_sb", book(prog(glue(["sa", "sb"]))), book(prog(glue(["sb", "sa"]))), PAIR, "inc on a, dbl on b")
    eq("F4", "triple_123_321", book(prog(glue(["t1", "t2", "t3"]))), book(prog(glue(["t3", "t2", "t1"]))), TRI)
    eq("F4", "triple_123_213", book(prog(glue(["t1", "t2", "t3"]))), book(prog(glue(["t2", "t1", "t3"]))), TRI)
    eq("F4", "list_num_sl_sn", book(prog(glue(["sl", "sn"]))), book(prog(glue(["sn", "sl"]))), LN, "(list, n): map_inc on list, inc on n")
    eq("F4", "redex_order_pair",
       book(prog("  & @inc ~ (a a2)\n  & @dbl ~ (b b2)\n  & out ~ (a2 b2)", "((a b) out)")),
       book(prog("  & @dbl ~ (b b2)\n  & @inc ~ (a a2)\n  & out ~ (a2 b2)", "((a b) out)")), PAIR, "statement order in the glue body")
    eq("F4", "redex_order_triple",
       book(prog("  & @sq ~ (a a2)\n  & @inc ~ (b b2)\n  & @dbl ~ (c c2)\n  & out ~ (a2 (b2 c2))", "((a (b c)) out)")),
       book(prog("  & @dbl ~ (c c2)\n  & @sq ~ (a a2)\n  & @inc ~ (b b2)\n  & out ~ (a2 (b2 c2))", "((a (b c)) out)")), TRI)
    eq("F4", "with_identity_stage",
       book(prog(glue(["sa", "id", "sb"]))), book(prog(glue(["sb", "sa", "id"]))), PAIR)
    eq("F4", "num_list_sn_sl", book(prog(glue(["sn", "sl", "sn"]))), book(prog(glue(["sl", "sn", "sn"]))), LN, "two inc stages on n, one map on l")

    # ------------------------------------------------------------------ F5 inlining vs call (8)
    eq("F5", "inline_op", book(prog("  & @inc ~ (x out)")), book(prog("  & x ~ $([+1] out)")), U)
    eq("F5", "call_inside_branch",
       book("@prog = ((?((@a_nil @a_cons) (pl out)) pl) out)\n@a_nil = (* (0 *))\n@a_cons = (* ((h t) out))\n"
            "  & out ~ (1 (d tl))\n  & @dbl ~ (h d)\n  & t ~ (?((@a_nil @a_cons) (pl tl)) pl)\n"),
       book("@prog = ((?((@a_nil @a_cons) (pl out)) pl) out)\n@a_nil = (* (0 *))\n@a_cons = (* ((h t) out))\n"
            "  & out ~ (1 (d tl))\n  & h ~ $([*2] d)\n  & t ~ (?((@a_nil @a_cons) (pl tl)) pl)\n"), LST,
       "helper call inside a branch def vs its body")
    eq("F5", "inline_dup_helper", book(prog("  & @sq ~ (x out)")),
       book(prog("  & x ~ {a b}\n  & a ~ $([*] $(b out))")), U, "helper containing a DUP")
    eq("F5", "two_layer",
       book("@h2 = (x y)\n  & @inc ~ (x a)\n  & @dbl ~ (a y)\n" + prog("  & @h2 ~ (x out)")),
       book(prog("  & x ~ $([+1] a)\n  & a ~ $([*2] out)")), U, "helper of helpers, fully inlined")
    eq("F5", "unroll_recursion_once", book(prog("  & @sum ~ (x out)")),
       book("@sm_cons = (* ((h t) (acc out)))\n  & acc ~ $([+] $(h a2))\n"
            "  & t ~ (?((@sm_nil @sm_cons) (pl (a2 out))) pl)\n" + prog("  & @sum ~ (x out)")), LST,
       "recursive call replaced by the callee's dispatcher")
    eq("F5", "inline_leaf_under_switch",
       book(prog("  & @sum ~ (x out)")),
       book("@sm = ((?(((* (a a)) @sm_cons) (pl (acc out))) pl) (acc out))\n" + prog("  & @sum ~ (x out)")), LST,
       "leaf branch def replaced by its literal tree, under a data-dependent switch")
    eq("F5", "inline_body", book("@body = (x out)\n  & @inc ~ (x a)\n  & @dbl ~ (a out)\n" + prog("  & @body ~ (x out)")),
       book(prog(glue(["inc", "dbl"]))), U)
    eq("F5", "inline_const_fn", book("@k5 = (* 5)\n" + prog("  & @k5 ~ (x out)")),
       book(prog("  & x ~ *\n  & out ~ 5")), U, "constant function with an erased argument")

    # ------------------------------------------------------------------ F6 wrapper vs hand-expanded (6)
    eq("F6", "wrapper2", book("@w2 = (x out)\n  & @inc ~ (x a)\n  & @dbl ~ (a out)\n" + prog("  & @w2 ~ (x out)")),
       book(prog(glue(["inc", "dbl"]))), U)
    eq("F6", "wrapper_tuple",
       book("@wt = ((a b) (a2 b2))\n  & @inc ~ (a a2)\n  & @dbl ~ (b b2)\n" + prog("  & @wt ~ (p out)", "(p out)")),
       book(prog("  & p ~ (a b)\n  & @inc ~ (a a2)\n  & @dbl ~ (b b2)\n  & out ~ (a2 b2)", "(p out)")), PAIR)
    eq("F6", "twice_inc",
       book("@twice = (f (x out))\n  & f ~ {f1 f2}\n  & f1 ~ (x a)\n  & f2 ~ (a out)\n" + prog("  & @twice ~ (@inc (x out))")),
       book(prog(glue(["inc", "inc"]))), U, "hole = a safe reference passed as a value")
    eq("F6", "twice_dbl",
       book("@twice = (f (x out))\n  & f ~ {f1 f2}\n  & f1 ~ (x a)\n  & f2 ~ (a out)\n" + prog("  & @twice ~ (@dbl (x out))")),
       book(prog(glue(["dbl", "dbl"]))), U)
    eq("F6", "pipe2_holes",
       book("@pipe2 = (f (g (x out)))\n  & f ~ (x a)\n  & g ~ (a out)\n" + prog("  & @pipe2 ~ (@inc (@dbl (x out)))")),
       book(prog(glue(["inc", "dbl"]))), U)
    eq("F6", "wrapper_dead_arg",
       book("@twoarg = ((a b) out)\n  & b ~ *\n  & @inc ~ (a out)\n" + prog("  & @twoarg ~ (p out)", "(p out)")),
       book(prog("  & p ~ (a b)\n  & b ~ *\n  & @inc ~ (a out)", "(p out)")), PAIR)

    # ================================================================== (b) UNEQUAL
    # ------------------------------------------------------------------ U1 off-by-one wiring (8)
    ne("U1", "stage1_output_dropped", book(prog(glue(["inc", "dbl"]))),
       book(prog("  & x ~ {x1 x2}\n  & @inc ~ (x1 a)\n  & a ~ *\n  & @dbl ~ (x2 out)")), U, "dbl reads the input, not inc's output")
    ne("U1", "grouping_off_by_one",
       book(prog("  & @addp ~ ((b c) s)\n  & @subp ~ ((a s) out)", "((a (b c)) out)")),
       book(prog("  & @subp ~ ((a b) s)\n  & @addp ~ ((s c) out)", "((a (b c)) out)")), TRI, "a-(b+c) vs (a-b)+c")
    ne("U1", "triple_rotated", book(prog("", "((a (b c)) (a (b c)))")), book(prog("", "((a (b c)) (b (c a)))")), TRI)
    ne("U1", "middle_stage_skips", book(prog(glue(["inc", "dbl", "sq"]))),
       book(prog("  & @inc ~ (x a)\n  & a ~ {a1 a2}\n  & @dbl ~ (a1 b)\n  & b ~ *\n  & @sq ~ (a2 out)")), U, "sq reads inc's output instead of dbl's")
    ne("U1", "sum_of_pair_vs_double", book(prog("  & @addp ~ ((a b) out)", "((a b) out)")),
       book(prog("  & b ~ *\n  & a ~ {a1 a2}\n  & @addp ~ ((a1 a2) out)", "((a b) out)")), PAIR, "a+b vs a+a")
    ne("U1", "triple_sum_wrong_pair",
       book(prog("  & @addp ~ ((a s) out)\n  & @addp ~ ((b c) s)", "((a (b c)) out)")),
       book(prog("  & @addp ~ ((a s) out)\n  & b ~ {b1 b2}\n  & c ~ *\n  & @addp ~ ((b1 b2) s)", "((a (b c)) out)")), TRI, "a+b+c vs a+b+b")
    ne("U1", "stage_on_wrong_component", book(prog(glue(["sa", "sb"]))),
       book("@sb2 = ((a b) (a2 b))\n  & @dbl ~ (a a2)\n" + prog(glue(["sa", "sb2"]))), PAIR, "second stage doubles a instead of b")
    ne("U1", "output_pair_wired_crosswise", book(prog("  & @inc ~ (a a2)\n  & @dbl ~ (b b2)\n  & out ~ (a2 b2)", "((a b) out)")),
       book(prog("  & @inc ~ (a a2)\n  & @dbl ~ (b b2)\n  & out ~ (b2 a2)", "((a b) out)")), PAIR)

    # ------------------------------------------------------------------ U2 swapped ports (8)
    ne("U2", "subp_operands", book(prog("  & @subp ~ (p out)", "(p out)")),
       book(prog("  & p ~ (a b)\n  & @subp ~ ((b a) out)", "(p out)")), PAIR, "a-b vs b-a")
    ne("U2", "cmp_order", book(prog("  & @cmp ~ (@inc (@dbl c))\n  & c ~ (x out)")),
       book(prog("  & @cmp ~ (@dbl (@inc c))\n  & c ~ (x out)")), U, "inc;dbl vs dbl;inc")
    ne("U2", "swap_vs_id", book(prog("  & @id ~ (p out)", "(p out)")), book(prog("  & @swap ~ (p out)", "(p out)")), PAIR)
    ne("U2", "filter_branches_swapped", book(prog("  & @fl ~ (x out)")),
       book("@fl2 = ((?((@fl_nil @fl_cons2) (pl out)) pl) out)\n@fl_cons2 = (* ((h t) out))\n  & h ~ {h1 h2}\n  & h1 ~ $([>] $(3 c))\n"
            "  & c ~ ?((@fl_keepz @fl_drops) (h2 (t out)))\n"
            "@fl_keepz = (h (t out))\n  & out ~ (1 (h tl))\n  & @fl2 ~ (t tl)\n"
            "@fl_drops = (* (h (t out)))\n  & h ~ *\n  & @fl2 ~ (t out)\n" + prog("  & @fl2 ~ (x out)")), LST, "keeps <=3 instead of >3")
    ne("U2", "comparison_direction", book(prog("  & @fl ~ (x out)")),
       book("@fl3 = ((?((@fl_nil @fl_cons3) (pl out)) pl) out)\n@fl_cons3 = (* ((h t) out))\n  & h ~ {h1 h2}\n  & h1 ~ $([<] $(3 c))\n"
            "  & c ~ ?((@fl_no3 @fl_yes3) (h2 (t out)))\n@fl_no3 = (h (t out))\n  & h ~ *\n  & @fl3 ~ (t out)\n"
            "@fl_yes3 = (* (h (t out)))\n  & out ~ (1 (h tl))\n  & @fl3 ~ (t tl)\n" + prog("  & @fl3 ~ (x out)")), LST, "[>] vs [<] operand order")
    ne("U2", "triple_tail_swapped", book(prog("", "((a (b c)) (a (b c)))")), book(prog("", "((a (b c)) (a (c b)))")), TRI)
    ne("U2", "output_tuple_order",
       book(prog("  & x ~ {x1 x2}\n  & @sum ~ (x1 s)\n  & @len ~ (x2 n)\n  & out ~ (s n)")),
       book(prog("  & x ~ {x1 x2}\n  & @sum ~ (x1 s)\n  & @len ~ (x2 n)\n  & out ~ (n s)")), LST, "(sum, len) vs (len, sum). Duplicates a list of numbers: safe only because the list is resolved data")
    ne("U2", "const_minus_order", book(prog("  & x ~ $([-] $(7 out))")), book(prog("  & 7 ~ $([-] $(x out))")), U, "x-7 vs 7-x")

    # ------------------------------------------------------------------ U3 dropped stage (8)
    ne("U3", "drop_inc", book(prog(glue(["inc", "dbl"]))), book(prog(glue(["dbl"]))), U)
    ne("U3", "drop_dbl_of_three", book(prog(glue(["inc", "dbl", "sq"]))), book(prog(glue(["inc", "sq"]))), U)
    ne("U3", "drop_map", book(prog(glue(["map_inc", "sum"]))), book(prog(glue(["sum"]))), LST)
    ne("U3", "drop_pair_stage", book(prog(glue(["sa", "sb"]))), book(prog(glue(["sa"]))), PAIR)
    ne("U3", "double_inc_vs_inc", book(prog(glue(["inc", "inc"]))), book(prog(glue(["inc"]))), U)
    ne("U3", "drop_triple_stage", book(prog(glue(["t1", "t2", "t3"]))), book(prog(glue(["t1", "t3"]))), TRI)
    ne("U3", "drop_dec", book(prog(glue(["sq", "dec"]))), book(prog(glue(["sq"]))), U)
    ne("U3", "drop_add7", book(prog(glue(["add7", "dbl"]))), book(prog(glue(["add7"]))), U)

    # ------------------------------------------------------------------ U4 wrong constant (8)
    ne("U4", "add7_vs_add8", book(prog(glue(["add7"]))), book("@add8 = (x y)\n  & x ~ $([+8] y)\n" + prog(glue(["add8"]))), U)
    ne("U4", "dbl_vs_triple", book(prog(glue(["dbl"]))), book("@tri = (x y)\n  & x ~ $([*3] y)\n" + prog(glue(["tri"]))), U)
    ne("U4", "filter_gt3_vs_gt4",
       book(prog("  & @fl ~ (x out)")),
       book("@fl4 = ((?((@fl_nil @fl_cons4) (pl out)) pl) out)\n@fl_cons4 = (* ((h t) out))\n  & h ~ {h1 h2}\n  & h1 ~ $([>] $(4 c))\n"
            "  & c ~ ?((@fl_no4 @fl_yes4) (h2 (t out)))\n@fl_no4 = (h (t out))\n  & h ~ *\n  & @fl4 ~ (t out)\n"
            "@fl_yes4 = (* (h (t out)))\n  & out ~ (1 (h tl))\n  & @fl4 ~ (t tl)\n" + prog("  & @fl4 ~ (x out)")), LST)
    ne("U4", "sum_init_1", book(prog("  & @sum ~ (x out)")),
       book(prog("  & @sm ~ (x (1 out))")), LST, "accumulator seed 0 vs 1")
    ne("U4", "dec_vs_sub2", book(prog(glue(["dec"]))), book("@sub2 = (x y)\n  & x ~ $([-] $(2 y))\n" + prog(glue(["sub2"]))), U)
    ne("U4", "neg_vs_one_minus", book(prog(glue(["neg"]))), book("@omx = (x y)\n  & 1 ~ $([-] $(x y))\n" + prog(glue(["omx"]))), U)
    ne("U4", "literal_5_vs_6", book(prog("  & x ~ *\n  & out ~ 5")), book(prog("  & x ~ *\n  & out ~ 6")), U)
    ne("U4", "sq_vs_cube_prefix", book(prog(glue(["sq"]))),
       book("@sq2 = (x y)\n  & x ~ {a b}\n  & a ~ $([*] $(b z))\n  & z ~ $([+1] y)\n" + prog(glue(["sq2"]))), U, "x*x vs x*x+1")

    # ------------------------------------------------------------------ U5 misc (14): wrong operator, extra stage, non-commuting, rare-witness
    ne("U5", "addp_vs_subp", book(prog("  & @addp ~ (p out)", "(p out)")), book(prog("  & @subp ~ (p out)", "(p out)")), PAIR, "wrong operator")
    ne("U5", "mulp_vs_addp", book(prog("  & @mulp ~ (p out)", "(p out)")), book(prog("  & @addp ~ (p out)", "(p out)")), PAIR)
    ne("U5", "inc_sq_vs_sq_inc", book(prog(glue(["inc", "sq"]))), book(prog(glue(["sq", "inc"]))), U, "non-commuting stages")
    ne("U5", "map_inc_vs_map_dbl", book(prog(glue(["map_inc"]))), book(prog(glue(["map_dbl"]))), LST)
    ne("U5", "sum_vs_len", book(prog(glue(["sum"]))), book(prog(glue(["len"]))), LST)
    ne("U5", "map_then_filter_vs_filter", book(prog(glue(["map_inc", "fl"]))), book(prog(glue(["fl"]))), LST)
    ne("U5", "filter_map_vs_map_filter", book(prog(glue(["fl", "map_inc"]))), book(prog(glue(["map_inc", "fl"]))), LST, "filter/map do not commute here: the filter reads the value map changes")
    ne("U5", "sl_sn_on_swapped", book(prog(glue(["sl", "sn"]))), book("@sn2 = ((l n) (l n2))\n  & @dbl ~ (n n2)\n" + prog(glue(["sl", "sn2"]))), LN)
    # rare-witness pairs: agree on almost all inputs
    ne("U5", "rare_dec_clamp", book(prog(glue(["dec"]))),
       book("@decc = (x y)\n  & x ~ {a b}\n  & a ~ $([=] $(0 z))\n  & z ~ ?((@dec_no @dec_yes) (b y))\n"
            "@dec_no = (b y)\n  & @dec ~ (b y)\n@dec_yes = (* (b y))\n  & b ~ y\n" + prog(glue(["decc"]))), U, "differs only at x = 0 (wrap vs clamp)")
    ne("U5", "rare_inc_mod1000", book(prog(glue(["inc"]))),
       book("@incm = (x y)\n  & x ~ $([+1] z)\n  & z ~ $([%] $(1000 y))\n" + prog(glue(["incm"]))), U, "differs only for x >= 999")
    ne("U5", "rare_sum_first_two", book(prog("  & @sum ~ (x out)")),
       book(_SUM2 + prog("  & @s2 ~ (x out)")), LST, "differs only for lists of length >= 3 (with a nonzero third element)")
    ne("U5", "rare_inc_saturating_at_max", book(prog("  & @map_inc ~ (x out)")),
       book(_MAPINC_SAT + prog("  & @mis ~ (x out)")), LST, "differs only for elements equal to 16777215 (wrap vs saturate)")
    ne("U5", "rare_len_vs_len_cap", book(prog("  & @len ~ (x out)")),
       book(_LENCAP + prog("  & @lnc ~ (x out)")), LST, "differs only for lists longer than 5")
    ne("U5", "rare_swap_pair_only_when_lt",
       book(prog("", "((a b) (a b))")),
       book("@ord = ((a b) out)\n  & a ~ {a1 a2}\n  & b ~ {b1 b2}\n  & a1 ~ $([<] $(b1 c))\n  & c ~ ?((@ord_no @ord_yes) (a2 (b2 out)))\n"
            "@ord_no = (a (b (a b)))\n@ord_yes = (* (a (b (b a))))\n" + prog("  & @ord ~ (p out)", "(p out)")), PAIR,
       "swaps the pair only when a < b")


_SUM2 = """@s2 = (l out)
  & @sm2 ~ (l (0 (2 out)))
@sm2 = ((?((@sm2_nil @sm2_cons) (pl (acc (k out)))) pl) (acc (k out)))
@sm2_nil = (* (a (k a)))
  & k ~ *
@sm2_cons = (* ((h t) (acc (k out))))
  & k ~ ?((@sm2_stop @sm2_go) (h (t (acc out))))
@sm2_stop = (h (t (acc out)))
  & h ~ *
  & t ~ *
  & acc ~ out
@sm2_go = (k1 (h (t (acc out))))
  & acc ~ $([+] $(h a2))
  & @sm2 ~ (t (a2 (k1 out)))
"""
_MAPINC_SAT = """@mis = ((?((@mis_nil @mis_cons) (pl out)) pl) out)
@mis_nil = (* (0 *))
@mis_cons = (* ((h t) out))
  & out ~ (1 (d tl))
  & h ~ {h1 h2}
  & h1 ~ $([=] $(16777215 e))
  & e ~ ?((@mis_inc @mis_keep) (h2 d))
  & t ~ (?((@mis_nil @mis_cons) (pl tl)) pl)
@mis_inc = (h d)
  & h ~ $([+1] d)
@mis_keep = (* (h h))
"""
_LENCAP = """@lnc = (l out)
  & @lnc_go ~ (l (0 out))
@lnc_go = ((?((@lnc_nil @lnc_cons) (pl (acc out))) pl) (acc out))
@lnc_nil = (* (a a))
@lnc_cons = (* ((h t) (acc out)))
  & h ~ *
  & acc ~ {c1 c2}
  & c1 ~ $([<] $(5 lt))
  & lt ~ ?((@lnc_stay @lnc_up) (c2 (t out)))
@lnc_stay = (c (t out))
  & c ~ a2
  & @lnc_go ~ (t (a2 out))
@lnc_up = (* (c (t out)))
  & c ~ $([+1] a2)
  & @lnc_go ~ (t (a2 out))
"""


# ============================================================================ (c) real pairs from the repo
# Selection rules were fixed before any result existed:
#   R1/R2  every 12th (indices 0,12,...,156) of the 167 sorted native base nets in runs/exp3/base/*.native.hvm  -> 14 programs
#          R1 = genome.opt.optimize(net) with defaults (static reduction + inlining, rounds=2, max_size=40)
#          R2 = genome.opt.optimize(net, inline=False)                    (static reduction only)
#   R3     exp8 hand-wired graphprims composition vs exp14 glue-API (typed) composition, for the two programs exp14 re-expressed
#   R4     the 16 recipe wrappers of genome/lib/test_recipes.py: glue-built net vs genome.opt.optimize(net, rounds=3, max_size=100)
#   X1     informational (denom=False): exp12 K=4 lookahead-transformed nets vs the original, 6 t1 programs
def build_real():
    import glob
    from genome.corpus import load_all
    from genome.opt import optimize
    R = load_all()
    out = []
    files = sorted(glob.glob(os.path.join(ROOT, "runs/exp3/base/*.native.hvm")))
    pids = [os.path.basename(f)[:-len(".native.hvm")] for f in files]
    sel = pids[0::12]
    for pid in sel:
        text = open(os.path.join(ROOT, "runs/exp3/base", pid + ".native.hvm")).read()
        o1, _ = optimize(text)
        o2, _ = optimize(text, inline=False)
        out.append(Case(f"R1_{pid}", "R1", "equal", text, o1, prog=R[pid], note="genome.opt.optimize default"))
        out.append(Case(f"R2_{pid}", "R2", "equal", text, o2, prog=R[pid], note="genome.opt.optimize static only"))
    for pid in ("t3_degrees", "t3_cc_largest"):
        a = open(os.path.join(ROOT, "runs/exp8", pid + ".hvm")).read()
        b = open(os.path.join(ROOT, "runs/exp14", "typed_" + pid + ".hvm")).read()
        out.append(Case(f"R3_{pid}", "R3", "equal", a, b, prog=R[pid], note="exp8 hand-wired vs exp14 glue API"))
    import genome.lib.test_recipes as T
    for name, fn in T.TESTS.items():
        P, cp = fn()
        text = P.build()
        o, _ = optimize(text, rounds=3, max_size=100)
        out.append(Case(f"R4_{name}", "R4", "equal", text, o, prog=cp, note="recipe wrapper vs opt.py-inlined expansion"))
    for pid in ("t1_map_inc", "t1_filter_even", "t1_sum", "t1_reverse", "t1_length", "t1_map_double"):
        a = open(os.path.join(ROOT, "runs/exp3/base", pid + ".native.hvm")).read()
        f = os.path.join(ROOT, "runs/exp12/nets/t1", pid + ".K4.hvm")
        if os.path.exists(f):
            out.append(Case(f"X1_{pid}", "X1", "equal", a, open(f).read(), prog=R[pid], note="exp12 K=4 lookahead", denom=False))
    return out


def all_cases():
    build_synthetic()
    return list(CASES) + build_real()
