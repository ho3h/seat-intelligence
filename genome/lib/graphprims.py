"""graphprims: a library of parallel graph primitives for HVM2 nets (exp8, 2026-09-30).

Distilled from the hand-written GRAPH-SWING nets (runs/exp5). Every primitive is a Python function that ADDS HVM2
definitions to a `Book` and returns the name of its entry definition. A program is composed by calling primitives and
writing a little glue (the `@prog` root and the per-edge `step`/`fin` bodies of a walker). Nothing here is searched
or learned; the verifier is the only judge of correctness.

Conventions (all primitives)
----------------------------
* Trie = complete binary trie of depth L (2^L leaves), leaf i reached by the bits of i, high bit first; an internal
  node is `(left right)`, a leaf is whatever the user stores (a number unless said otherwise). Keys >= 2^L alias to
  key mod 2^L, so glue must guard out-of-range keys. For n vertices use L = lg(n-1) (n >= 1).
* Port signatures are written as the tree the entry REF must meet, e.g. `@X ~ (t (k (L (P t2))))` means "connect
  a 4-ary call: trie t, key k, depth L, payload P; result trie t2".
* Bodies passed in by the author (leaf actions, leaf maps, walker steps) are the right-hand side of a definition,
  e.g. "(x (* o))\n  & x ~ $([+1] o)"; the primitive names the definition.
* Cost notes: "rounds" is parallel depth in the oracle's round scheduler; "itrs" is interactions. They are measured
  orders of magnitude from the unit tests and the exp5/exp8 nets, not guarantees.

The central idea (why these are shallow): the control flow of a keyed update depends only on its key and L, so a
chain of m updates on one trie expands before the trie exists and collapses in O(L) rounds after the keys are known,
not O(m*L). Traversals depend only on L. Lists are the only sequential floor (the walker reads K cells per step).
"""
from __future__ import annotations
import re

INF = 16777215


class Book:
    """A set of named definitions. Adding an identical definition twice is a no-op (shared helpers); adding a
    different body under an existing name is an error (name clash between two primitive instances)."""

    def __init__(self):
        self.defs: dict[str, str] = {}
        self.order: list[str] = []

    def add(self, text: str):
        text = re.sub(r"(?m)^\s*//[^\n]*\n", "", text.strip() + "\n")
        parts = re.split(r"(?m)^(?=@[\w]+\s*=)", text)
        for blk in parts:
            blk = blk.strip()
            if not blk: continue
            m = re.match(r"@(\w+)\s*=", blk)
            assert m, f"text outside a definition: {blk[:60]!r}"
            name = m.group(1)
            if name in self.defs:
                assert self.defs[name] == blk, f"name clash: @{name} defined twice with different bodies"
                continue
            self.defs[name] = blk
            self.order.append(name)
        return self

    def define(self, name: str, body: str):
        return self.add(f"@{name} = {body.strip()}")

    def text(self) -> str:
        return "\n".join(self.defs[n] for n in self.order) + "\n"

    def size(self):
        """(definitions, lines) of the emitted net."""
        t = self.text()
        return len(self.defs), t.count("\n")


# ====================================================================== shared helpers
def _sel(b: Book):
    """Selectors on a switch context (a (b o)): Z-branch forms and S-branch forms (S-branch swallows n-1)."""
    b.add("""
@gl_sel1 = (x (* x))
@gl_sel2 = (* (y y))
@gl_sel1s = (* (x (* x)))
@gl_sel2s = (* (* (y y)))
""")


def _combine(b: Book, op: str, x="x", y="y", o="o") -> str:
    """Redex lines combining numbers x, y into o. op in + | & max min."""
    if op in ("+", "|", "&", "^", "*"):
        return f"  & {x} ~ $([{op}] $({y} {o}))"
    _sel(b)
    if op == "max":
        return (f"  & {x} ~ {{{x}1 {x}2}}\n  & {y} ~ {{{y}1 {y}2}}\n  & {x}1 ~ $([<] $({y}1 {x}lt))\n"
                f"  & {x}lt ~ ?((@gl_sel1 @gl_sel2s) ({x}2 ({y}2 {o})))")
    if op == "min":
        return (f"  & {x} ~ {{{x}1 {x}2}}\n  & {y} ~ {{{y}1 {y}2}}\n  & {x}1 ~ $([<] $({y}1 {x}lt))\n"
                f"  & {x}lt ~ ?((@gl_sel2 @gl_sel1s) ({x}2 ({y}2 {o})))")
    raise ValueError(op)


# ====================================================================== 1. trie depth
def lg(b: Book) -> str:
    """@lg ~ (x L): L = number of bits of x (0 for x = 0). For n >= 1 vertices use L = lg(n-1).
    Cost: ~4 rounds and ~6 itrs per bit (sequential in the bit count, <= 24)."""
    b.add("""
@lg = (?((0 @lg_s) o) o)
@lg_s = (xm o)
  & xm ~ $([+1] x)
  & x ~ $([>>] $(1 y))
  & @lg ~ (y z)
  & z ~ $([+1] o)
""")
    return "lg"


# ====================================================================== 2. constant and identity tries
def const_trie(b: Book, name: str, leaf: str) -> str:
    """@name ~ (L t): trie of depth L whose every leaf is the closed term `leaf` (e.g. `0`, `16777215`, `(0 *)` for
    empty lists, `(y y)` for empty multicast chains). Cost: ~2L rounds, ~3 itrs per trie node."""
    b.add(f"""
@{name} = (?(({leaf} @{name}_n) o) o)
@{name}_n = (lm (a c))
  & lm ~ {{l1 l2}}
  & @{name} ~ (l1 a)
  & @{name} ~ (l2 c)
""")
    return name


def iota_trie(b: Book, name: str) -> str:
    """@name ~ (L (base t)): leaf i holds base + i.  Cost: ~3L rounds, ~6 itrs per node."""
    b.add(f"""
@{name} = (L (base o))
  & L ~ ?((@{name}_leaf @{name}_node) (base o))
@{name}_leaf = (x x)
@{name}_node = (lm (base (a c)))
  & lm ~ {{l1 {{l2 l3}}}}
  & base ~ {{b1 b2}}
  & 1 ~ $([<<] $(l3 half))
  & b2 ~ $([+] $(half bR))
  & @{name} ~ (l1 (b1 a))
  & @{name} ~ (l2 (bR c))
""")
    return name


# ====================================================================== 3. keyed update (the core word)
ACTS = {
    # leaf actions: body of @act ~ (leaf (P leaf'))
    "set1": "(* (* 1))",                                           # leaf := 1 (P ignored; pass *)
    "set": "(* (p p))",                                            # leaf := P
    "inc": "(x (* o))\n  & x ~ $([+1] o)",                          # leaf += 1 (P ignored)
    "add": "(x (c o))\n  & x ~ $([+] $(c o))",                     # leaf += P
    "or": "(x (c o))\n  & x ~ $([|] $(c o))",                      # leaf |= P
    "min": "(x (c o))\n  & x ~ {x1 x2}\n  & c ~ {c1 c2}\n  & c1 ~ $([<] $(x1 lt))\n  & lt ~ ?((@gl_sel1 @gl_sel2s) (x2 (c2 o)))",
    "max": "(x (c o))\n  & x ~ {x1 x2}\n  & c ~ {c1 c2}\n  & x1 ~ $([<] $(c1 lt))\n  & lt ~ ?((@gl_sel1 @gl_sel2s) (x2 (c2 o)))",
    "push": "(l (x (1 (x l))))",                                   # leaf is a list; push P on its front
    "reply": "((i o) (x (i o2)))\n  & o ~ {x o2}",                 # leaf is a multicast chain (in out); P is a reply wire
    "dec": "(x (* o))\n  & x ~ $([-] $(1 o))",                     # leaf -= 1 (P ignored)                      [v2]
    "peek": "(l (p l2))\n  & l ~ {p l2}",                        # P receives a DUP copy of the leaf (closed data) [v2]
}


def update(b: Book, name: str, act: str) -> str:
    """Keyed update.  @name ~ (t (k (L (P t2)))): t2 is t with leaf k replaced by act(leaf, P).
    `act` is a key of ACTS or a custom body for @name_act ~ (leaf (P leaf')). P is opaque (a number, a tuple, a wire).
    Control flow (level switch, key-bit switch) depends only on k and L: the update expands as soon as k and L are
    known, before t exists, and a chain of updates on one trie collapses in O(L) rounds once keys are known.
    Cost: ~16 rounds/level on its own path; ~12 itrs per level plus the act."""
    body = ACTS.get(act, act)
    if "@gl_sel" in body: _sel(b)
    b.add(f"""
@{name} = (t (k (L (P o))))
  & L ~ ?((@{name}_leaf @{name}_node) (t (k (P o))))
@{name}_leaf = (t (* (P o)))
  & @{name}_act ~ (t (P o))
@{name}_act = {body}
@{name}_node = (lm (t (k (P o))))
  & k ~ {{k1 k2}}
  & lm ~ {{l1 l2}}
  & k1 ~ $([>>] $(l1 sh))
  & sh ~ $([&] $(1 bt))
  & bt ~ ?((@{name}_L @{name}_R) (t (k2 (l2 (P o)))))
@{name}_L = ((l r) (k (L (P (l2 r)))))
  & @{name} ~ (l (k (L (P l2))))
@{name}_R = (* ((l r) (k (L (P (l r2))))))
  & @{name} ~ (r (k (L (P r2))))
""")
    return name


def get(b: Book, name: str) -> str:
    """Keyed read that consumes the trie.  @name ~ (t (k (L o))): o = leaf k; every other leaf is erased.
    Control depends only on k and L. Cost: ~12 rounds/level, erasure of the rest runs in parallel."""
    b.add(f"""
@{name} = (t (k (L o)))
  & L ~ ?((@{name}_leaf @{name}_node) (t (k o)))
@{name}_leaf = (x (* x))
@{name}_node = (lm (t (k o)))
  & k ~ {{k1 k2}}
  & lm ~ {{l1 l2}}
  & k1 ~ $([>>] $(l1 sh))
  & sh ~ $([&] $(1 bt))
  & bt ~ ?((@{name}_L @{name}_R) (t (k2 (l2 o))))
@{name}_L = ((l *) (k (L o)))
  & @{name} ~ (l (k (L o)))
@{name}_R = (* ((* r) (k (L o))))
  & @{name} ~ (r (k (L o)))
""")
    return name


# ====================================================================== 4. whole-trie traversals
def _index_lines(name):
    return ("  & base ~ {b1 b2}\n  & 1 ~ $([<<] $(l3 half))\n  & b2 ~ $([+] $(half bR))\n")


def reduce(b: Book, name: str, leaf: str, op: str, idx: bool = False, env: bool = False) -> str:
    """Tree reduction with a leaf map.  Signature (brackets only if the flag is on):
         @name ~ (t (L [(base] [(E] o)))      leaf body: (x [(i] [(E] o)))
    o = op over all leaves of leaf(x_i [, i] [, E]); op in + | & max min. i = base + leaf index, E is an environment
    term copied to every leaf (DUP per node; keep it small). Pure traversal: depends only on L.
    Cost: ~3-5 rounds/level + leaf; ~5-9 itrs per node."""
    I = lambda s: f"({s} " if idx else ""
    Ev = lambda s: f"({s} " if env else ""
    close = lambda: ")" * (idx + env)
    sig = lambda bs, es, o: f"{I(bs)}{Ev(es)}{o}{close()}"
    lm = "{l1 {l2 l3}}" if idx else "{l1 l2}"
    lines = [f"@{name} = (t (L {sig('base', 'E', 'o')}))",
             f"  & L ~ ?((@{name}_leaf @{name}_node) (t {sig('base', 'E', 'o')}))",
             f"@{name}_leaf = {leaf.strip()}",
             f"@{name}_node = (lm ((a c) {sig('base', 'E', 'o')}))",
             f"  & lm ~ {lm}"]
    if idx: lines.append(_index_lines(name).rstrip("\n"))
    if env: lines.append("  & E ~ {E1 E2}")
    lines.append(f"  & @{name} ~ (a (l1 {sig('b1', 'E1', 'x')}))")
    lines.append(f"  & @{name} ~ (c (l2 {sig('bR', 'E2', 'y')}))")
    lines.append(_combine(b, op))
    b.add("\n".join(lines))
    return name


def fold(b: Book, name: str, leaf: str, idx: bool = True, env: bool = True) -> str:
    """Threaded fold over the leaves, right to left (so list outputs come out in key order).
         @name ~ (t (L [(base] [(E] (acc o))))      leaf body: (x [(i] [(E] (acc o))))
    Each leaf receives the accumulator from the leaf to its right and passes its own. All leaves run in parallel:
    only the accumulator wiring is sequential, and a leaf that just prepends a cell `(1 (x acc))` does not wait for
    acc. Instances: tree->list, filter->list, scatter (each leaf applies a keyed update to a threaded trie).
    Cost: ~4 rounds/level + leaf; ~9 itrs per node."""
    I = lambda s: f"({s} " if idx else ""
    Ev = lambda s: f"({s} " if env else ""
    close = lambda: ")" * (idx + env)
    sig = lambda bs, es, a, o: f"{I(bs)}{Ev(es)}({a} {o}){close()}"
    lm = "{l1 {l2 l3}}" if idx else "{l1 l2}"
    lines = [f"@{name} = (t (L {sig('base', 'E', 'acc', 'o')}))",
             f"  & L ~ ?((@{name}_leaf @{name}_node) (t {sig('base', 'E', 'acc', 'o')}))",
             f"@{name}_leaf = {leaf.strip()}",
             f"@{name}_node = (lm ((a c) {sig('base', 'E', 'acc', 'o')}))",
             f"  & lm ~ {lm}"]
    if idx: lines.append(_index_lines(name).rstrip("\n"))
    if env: lines.append("  & E ~ {E1 E2}")
    lines.append(f"  & @{name} ~ (a (l1 {sig('b1', 'E1', 'mid', 'o')}))")
    lines.append(f"  & @{name} ~ (c (l2 {sig('bR', 'E2', 'acc', 'mid')}))")
    b.add("\n".join(lines))
    return name


def to_list(b: Book, name: str) -> str:
    """Tree -> list of the first n leaves in key order, prepended to a tail.
         @name ~ (t (L (0 (n (tail o)))))     (base must be 0)
    Instance of fold with leaf `i < n ? (1 (x acc)) : acc`."""
    b.add(f"""
@{name}_drop = (* (t t))
@{name}_keep = (* (x (t (1 (x t)))))
""")
    return fold(b, name, f"""(x (i (n (acc o))))
  & i ~ $([<] $(n keep))
  & keep ~ ?((@{name}_drop @{name}_keep) (x (acc o)))""")


def filter_list(b: Book, name: str, pred: str, emit: str = "i") -> str:
    """Tree -> list of `emit` for every leaf where pred holds, in key order.
         @name ~ (t (L (0 (E (tail o)))))
    pred: body of @name_p ~ (x (i (E f))) giving f in {0,1} (it may consume x, i, E; use DUPs if emit needs them);
    emit: 'i' (the index) or 'x' (the leaf value).  Instance of fold."""
    b.add(f"""
@{name}_p = {pred.strip()}
@{name}_no = (* (t t))
@{name}_yes = (* (v (t (1 (v t)))))
""")
    keep = "i2" if emit == "i" else "x2"
    other = "x2" if emit == "i" else "i2"
    return fold(b, name, f"""(x (i (E (acc o))))
  & x ~ {{x1 x2}}
  & i ~ {{i1 i2}}
  & {other} ~ *
  & @{name}_p ~ (x1 (i1 (E f)))
  & f ~ ?((@{name}_no @{name}_yes) ({keep} (acc o)))""")


def scatter(b: Book, name: str, upd: str, key: str) -> str:
    """Tree -> keyed updates into another trie H threaded through the leaves (histogram, inverse map, ...).
         @name ~ (t (L (0 ((Lh E) (H H2)))))
    For every leaf (x, i): the author's key body  @name_k ~ (x (i (E (k P))))  computes a key k and payload P, and
    the leaf applies @upd ~ (H (k (Lh (P H')))) (an `update` instance over a trie of depth Lh). A leaf that must not
    contribute should send the combiner's identity as P (e.g. P = 0 for add) to a harmless key.
    Each update expands as soon as its key is known; the threaded H only carries data. Instance of fold."""
    b.define(f"{name}_k", key)
    return fold(b, name, f"""(x (i (LE (acc o))))
  & LE ~ (Lh E)
  & @{name}_k ~ (x (i (E (k P))))
  & @{upd} ~ (acc (k (Lh (P o))))""")


def zip2(b: Book, name: str, leaf: str) -> str:
    """Leafwise combine of two tries of the same depth.  @name ~ (a (c (L o))): o is the trie with leaf
    leaf(a_i, c_i). leaf body: (x (y o)). Pure traversal. Cost ~3 rounds/level."""
    b.add(f"""
@{name} = (a (c (L o)))
  & L ~ ?((@{name}_leaf @{name}_node) (a (c o)))
@{name}_leaf = {leaf.strip()}
@{name}_node = (lm ((a1 a2) ((c1 c2) (o1 o2))))
  & lm ~ {{l1 l2}}
  & @{name} ~ (a1 (c1 (l1 o1)))
  & @{name} ~ (a2 (c2 (l2 o2)))
""")
    return name


def zip2e(b: Book, name: str, leaf: str) -> str:
    """[v2, added in exp8 for the batched-reachability programs] zip2 with an environment copied to every leaf:
         @name ~ (a (c (L (E o))))      leaf body: (x (y (E o)))
    Typical use: run an independent sub-computation (e.g. a whole `frontier` loop) at every leaf of an outer trie,
    all in parallel."""
    b.add(f"""
@{name} = (a (c (L (E o))))
  & L ~ ?((@{name}_leaf @{name}_node) (a (c (E o))))
@{name}_leaf = {leaf.strip()}
@{name}_node = (lm ((a1 a2) ((c1 c2) (E (o1 o2)))))
  & lm ~ {{l1 l2}}
  & E ~ {{E1 E2}}
  & @{name} ~ (a1 (c1 (l1 (E1 o1))))
  & @{name} ~ (a2 (c2 (l2 (E2 o2))))
""")
    return name


def bcast(b: Book, name: str, upd: str) -> str:
    """[v2, added in exp8 for the batched-reachability programs] Broadcast keyed update: apply the same inner update
    @upd ~ (t (k (Li (P t2)))) to EVERY sub-trie hanging from the leaves of an outer trie of depth Lo.
         @name ~ (T (Lo ((Li (k P)) T2)))
    (Li, k, P) are copied to every outer leaf by DUPs (numbers / closed data only). Cost: 2^Lo inner updates."""
    b.add(f"""
@{name} = (t (Lo (E o)))
  & Lo ~ ?((@{name}_leaf @{name}_node) (t (E o)))
@{name}_leaf = (t ((Li (k P)) o))
  & @{upd} ~ (t (k (Li (P o))))
@{name}_node = (lm ((a c) (E (o1 o2))))
  & lm ~ {{l1 l2}}
  & E ~ {{E1 E2}}
  & @{name} ~ (a (l1 (E1 o1)))
  & @{name} ~ (c (l2 (E2 o2)))
""")
    return name


# leaf-body helper (not a definition): 24-bit popcount of x into o, SWAR
POP24 = """  & x ~ {x1 x2}
  & x1 ~ $([>>] $(1 xa))
  & xa ~ $([&] $(5592405 xb))
  & x2 ~ $([-] $(xb y))
  & y ~ {y1 y2}
  & y1 ~ $([&] $(3355443 ya))
  & y2 ~ $([>>] $(2 yb))
  & yb ~ $([&] $(3355443 yc))
  & ya ~ $([+] $(yc z))
  & z ~ {z1 z2}
  & z2 ~ $([>>] $(4 za))
  & z1 ~ $([+] $(za zb))
  & zb ~ $([&] $(986895 u))
  & u ~ {u1 {u2 u3}}
  & u2 ~ $([>>] $(8 ua))
  & u3 ~ $([>>] $(16 ub))
  & u1 ~ $([+] $(ua uc))
  & uc ~ $([+] $(ub ud))
  & ud ~ $([&] $(255 o))"""


def mapreduce(b: Book, name: str, leaf: str, op: str, idx: bool = True, env: bool = True) -> str:
    """[v2, added in exp8 for t3_topo_order] `reduce` that also rebuilds the trie (reduce without consuming):
         @name ~ (t (L [(base] [(E] (t2 o)))))      leaf body: (x [(i] [(E] (x2 r))))
    t2 has leaf x2 where t had x; o = op over all r. Pure traversal, same cost as reduce plus one CON per node."""
    I = lambda s: f"({s} " if idx else ""
    Ev = lambda s: f"({s} " if env else ""
    close = lambda: ")" * (idx + env)
    sig = lambda bs, es, t2, o: f"{I(bs)}{Ev(es)}({t2} {o}){close()}"
    lm = "{l1 {l2 l3}}" if idx else "{l1 l2}"
    lines = [f"@{name} = (t (L {sig('base', 'E', 't2', 'o')}))",
             f"  & L ~ ?((@{name}_leaf @{name}_node) (t {sig('base', 'E', 't2', 'o')}))",
             f"@{name}_leaf = {leaf.strip()}",
             f"@{name}_node = (lm ((a c) {sig('base', 'E', '(a2 c2)', 'o')}))",
             f"  & lm ~ {lm}"]
    if idx: lines.append(_index_lines(name).rstrip("\n"))
    if env: lines.append("  & E ~ {E1 E2}")
    lines.append(f"  & @{name} ~ (a (l1 {sig('b1', 'E1', 'a2', 'x')}))")
    lines.append(f"  & @{name} ~ (c (l2 {sig('bR', 'E2', 'c2', 'y')}))")
    lines.append(_combine(b, op))
    b.add("\n".join(lines))
    return name


def iterate(b: Book, p: str, body: str) -> str:
    """[v2, added in exp8 for t3_topo_order] Sequential loop over an arbitrary state:
         @<p>_it ~ (S Sfinal)       body: @<p>_body ~ (S (S2 go))   repeats while go != 0.
    Use only for inherently sequential algorithms (each iteration is on the critical path)."""
    b.define(f"{p}_body", body)
    b.add(f"""
@{p}_it = (S o)
  & @{p}_body ~ (S (S2 go))
  & go ~ ?((@{p}_stop @{p}_more) (S2 o))
@{p}_stop = (s s)
@{p}_more = (* (S o))
  & @{p}_it ~ (S o)
""")
    return f"{p}_it"


# ====================================================================== 5. multicast (wires as return addresses)
def mc_empty(b: Book, name: str) -> str:
    """@name ~ (L q): request trie whose leaves are empty multicast chains (in out) = (y y)."""
    return const_trie(b, name, "(y y)")


def mc_request(b: Book, name: str) -> str:
    """@name ~ (q (k (L (r q2)))): register reply wire r at key k. After delivery, r carries the value stored at k.
    (keyed update with the `reply` act: the leaf chain (in out) becomes (in o2) with out ~ {r o2})."""
    return update(b, name, "reply")


def mc_deliver(b: Book, name: str) -> str:
    """@name ~ (v (q L)): wire leaf k of value trie v into the chain at leaf k of request trie q; every registered
    reply wire receives a copy (DUP chain); the chain's spare end is erased. Pure wiring, O(L) rounds; values must be
    fully computed data (numbers or closed trees) because the chain copies them with DUPs."""
    b.add(f"""
@{name} = (m (q L))
  & L ~ ?((@{name}_leaf @{name}_node) (m q))
@{name}_leaf = (R (R *))
@{name}_node = (lm ((m1 m2) (q1 q2)))
  & lm ~ {{l1 l2}}
  & @{name} ~ (m1 (q1 l1))
  & @{name} ~ (m2 (q2 l2))
""")
    return name


def mc_deliver_keep(b: Book, name: str) -> str:
    """[v2, added in exp8 for t3_two_colour] Like mc_deliver, but the chain's spare end is kept:
         @name ~ (v (q (L v2)))    v2 = a copy of the value trie v (leafwise, via the multicast DUP chains).
    This is also the safe way to use a numeric trie twice (a DUP of a whole trie can meet unresolved DUPs)."""
    b.add(f"""
@{name} = (m (q (L o)))
  & L ~ ?((@{name}_leaf @{name}_node) (m (q o)))
@{name}_leaf = (R ((R e) e))
@{name}_node = (lm ((m1 m2) ((q1 q2) (o1 o2))))
  & lm ~ {{l1 l2}}
  & @{name} ~ (m1 (q1 (l1 o1)))
  & @{name} ~ (m2 (q2 (l2 o2)))
""")
    return name


# ====================================================================== 6. list walker with K-cell lookahead
def stream(b: Book, p: str, k: int, step: str, fin: str) -> str:
    """Blocked speculative list walker.  Entry: @<p>_blk ~ (list (S0 out)).
    step body: @<p>_step ~ (S (elem S2));  fin body: @<p>_fin ~ (S out).
    Matches k cells ahead with one nested pattern (2 rounds/cell, no switch in the way), one SWI per cell tag, the
    per-cell steps chained on the state. A Nil erases everything past the end (no end-of-list test).
    Cost: ~2.3 rounds/cell at k=16 (vs ~7 for a one-switch-per-cell walker)."""
    b.define(f"{p}_step", step)
    b.define(f"{p}_fin", fin)
    pat = f"t{k}"
    for i in range(k, 0, -1):
        pat = f"(T{i} (E{i} {pat}))"
    lines = [f"@{p}_blk = (t (S0 o0))", f"  & t ~ {pat}"]
    for i in range(1, k):
        lines.append(f"  & T{i} ~ ?((@{p}_nil @{p}_cons) (S{i-1} (o{i-1} (E{i} (S{i} o{i})))))")
    lines.append(f"  & T{k} ~ ?((@{p}_nil @{p}_last) (S{k-1} (o{k-1} (E{k} t{k}))))")
    lines += [
        f"@{p}_nil = (S (o *))",
        f"  & @{p}_fin ~ (S o)",
        f"@{p}_cons = (* (S (o (E (S2 o)))))",
        f"  & @{p}_step ~ (S (E S2))",
        f"@{p}_last = (* (S (o (E t))))",
        f"  & @{p}_step ~ (S (E S2))",
        f"  & @{p}_blk ~ (t (S2 o))",
    ]
    b.add("\n".join(lines))
    return f"{p}_blk"


# ====================================================================== 7. frontier rounds (generic fixpoint)
def frontier(b: Book, p: str, act: str, msg: str, comb: str, ident: str) -> str:
    """Frontier fixpoint over tries (generalised Bellman-Ford).  Entry:
         @<p>_loop ~ ((G (D (C (L X)))) Dfinal)
    G: adjacency trie, leaf = list of (v w).  D: state trie.  C: incoming-message trie for the first round.
    L: depth; X: an environment term copied to every leaf each round (e.g. a budget, k).
    Each round is ONE traversal of (G, D, C). At each leaf the author's
        act body:  @<p>_act ~ (X (d (c (d2 (f m)))))   new state d2, flag f in {0,1}, message base m
    runs; if f = 1, the leaf sends  msg body: @<p>_msg ~ (m (w r))  to every neighbour v of its list, combined into
    the NEXT round's message trie by the keyed update with act `comb` (ACTS key or body) over leaves `ident`
    (the combiner identity). Flags are OR-reduced; the loop stops after a round with no flag.
    Cost: ~75-155 rounds per round (the gated emission is the critical path); itrs ~ (traversal + emissions)."""
    const_trie(b, f"{p}_zc", ident)
    update(b, f"{p}_cu", comb)
    b.define(f"{p}_act", act)
    b.define(f"{p}_msg", msg)
    b.add(f"""
@{p}_loop = ((g (dt (c E))) o)
  & E ~ {{E1 {{E2 E3}}}}
  & E1 ~ (L1 *)
  & @{p}_zc ~ (L1 ci)
  & E2 ~ {{Ea Eb}}
  & Ea ~ (Lr *)
  & @{p}_rd ~ (Lr (Eb (g (dt (c (ci (g2 (dt2 (co any)))))))))
  & any ~ ?((@{p}_done @{p}_again) (g2 (dt2 (co (E3 o)))))
@{p}_done = (* (dt (* (* dt))))
@{p}_again = (* (g (dt (c (E o)))))
  & @{p}_loop ~ ((g (dt (c E))) o)
@{p}_rd = (L (E (g (dt (c (ci (g2 (dt2 (co any)))))))))
  & L ~ ?((@{p}_leaf @{p}_node) (E (g (dt (c (ci (g2 (dt2 (co any)))))))))
@{p}_node = (lm (E ((g1 gr) ((d1 dr) ((c1 cr) (ci ((h1 hr) ((e1 er) (co any)))))))))
  & lm ~ {{l1 l2}}
  & E ~ {{Ea Eb}}
  & @{p}_rd ~ (l1 (Ea (g1 (d1 (c1 (ci (h1 (e1 (cm a1)))))))))
  & @{p}_rd ~ (l2 (Eb (gr (dr (cr (cm (hr (er (co a2)))))))))
  & a1 ~ $([|] $(a2 any))
@{p}_leaf = (E (g (d (c (ci (g2 (d2 (co any))))))))
  & E ~ {{Ex Ey}}
  & Ey ~ (* X)
  & @{p}_act ~ (X (d (c (d2 (f m)))))
  & f ~ {{any f3}}
  & f3 ~ ?((@{p}_quiet @{p}_emit) (g (m (ci (g2 (co Ex))))))
@{p}_quiet = (g (* (ci (g (ci *)))))
@{p}_emit = (* (g (nd (ci (g2 (co E))))))
  & E ~ (L *)
  & @{p}_em ~ (g (nd (ci (g2 (co L)))))
@{p}_em = ((?((@{p}_em_nil @{p}_em_cons) (q (nd (ci (g2 (co L)))))) q) (nd (ci (g2 (co L)))))
@{p}_em_nil = (* (* (ci ((0 *) (ci *)))))
@{p}_em_cons = (* (((v w) rest) (nd (ci ((1 ((v2 w2) rest2)) (co L))))))
  & v ~ {{v1 v2}}
  & w ~ {{w1 w2}}
  & nd ~ {{n1 n2}}
  & L ~ {{La Lb}}
  & @{p}_msg ~ (n1 (w1 cand))
  & @{p}_cu ~ (ci (v1 (La (cand cm))))
  & @{p}_em ~ (rest (n2 (cm (rest2 (co Lb)))))
""")
    return f"{p}_loop"


RELAX = """(b (d (c (d2 (f m)))))
  & c ~ {c1 {c2 c3}}
  & d ~ {dA dB}
  & c1 ~ $([<] $(dA lt))
  & c2 ~ $([>] $(b gt))
  & lt ~ $([>] $(gt f0))
  & f0 ~ {f1 f}
  & f1 ~ ?((@gl_sel1 @gl_sel2s) (dB (c3 nd)))
  & nd ~ {d2 m}"""
RELAX_MAX = """(* (d (c (d2 (f m)))))
  & c ~ {c1 c3}
  & d ~ {dA dB}
  & dA ~ $([<] $(c1 f0))
  & f0 ~ {f1 f}
  & f1 ~ ?((@gl_sel1 @gl_sel2s) (dB (c3 nd)))
  & nd ~ {d2 m}"""


def relax(b: Book, p: str, maximize: bool = False) -> str:
    """Min-plus relaxation (shortest paths / min-label propagation) on `frontier`: d2 = min(d, c) accepted only if
    c <= X (the budget; X = 16777215 means none); message = d2 + w; combiner min; identity INF.
    maximize=True: max-label propagation (d2 = max(d, c), message = d2 * w, so w = 1 keeps an edge and w = 0
    disables it; combiner max; identity 0; X ignored).  Entry @<p>_loop as in frontier."""
    _sel(b)
    if maximize:
        return frontier(b, p, RELAX_MAX, "(m (w r))\n  & m ~ $([*] $(w r))", "max", "0")
    return frontier(b, p, RELAX, "(m (w r))\n  & m ~ $([+] $(w r))", "min", str(INF))


def sssp(b: Book, p: str) -> str:
    """Single-source shortest paths over an adjacency trie, composed from relax + const_trie + update.
         @<p>_sssp ~ (n (s (L (budget (G D)))))
    D: distance trie (INF = unreachable or > budget). s >= n gives all INF."""
    relax(b, p)
    const_trie(b, "gl_inf", str(INF))
    update(b, f"{p}_seed", "min")
    b.add(f"""
@{p}_sssp = (n (s (L (bud (g o)))))
  & s ~ {{s1 s2}}
  & s1 ~ $([<] $(n inr))
  & inr ~ {{i1 i2}}
  & s2 ~ $([*] $(i1 key))
  & i2 ~ ?(({INF} (* 0)) val)
  & L ~ {{L1 {{L2 {{L3 L4}}}}}}
  & @gl_inf ~ (L1 D0)
  & @gl_inf ~ (L2 Ci)
  & @{p}_seed ~ (Ci (key (L3 (val C0))))
  & @{p}_loop ~ ((g (D0 (C0 (L4 bud)))) o)
""")
    return f"{p}_sssp"


def adjacency(b: Book, name: str = "gl_adj") -> str:
    """Adjacency builder: @name ~ (G (u (L ((v w) G2)))) pushes (v w) onto u's list; empty adjacency trie is
    @gl_zl ~ (L G0). (update with the push act over a const_trie of (0 *).)"""
    const_trie(b, "gl_zl", "(0 *)")
    return update(b, name, "push")
