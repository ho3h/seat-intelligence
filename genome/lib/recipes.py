"""recipes: named, verified algorithm templates with typed holes, built on glue (swing 26, 2026-09-30).

glue.py checks the WIRING between primitives; it does not choose the algorithm. A recipe is the next layer: a whole
algorithm (a walk plus lookups plus a delivery, a pointer-doubling loop, a BFS that also counts paths, a rank sort)
packaged as ONE primitive with a typed port signature. The author only CHOOSES a recipe and FILLS its holes (small
Python functions such as a key, a predicate or a combiner), then connects it with `d.call` like any other primitive.
Everything is compiled through glue, so every recipe inherits the checker (linearity, kinds, arity) and the emitted
net is linted by P.build().

Usage (inside a normal glue build script):

    from genome.lib.glue import Program, NUM, EDGE, WEDGE, LIST, TUP, INF
    from genome.lib import recipes as R
    P = Program()
    keep = R.filter_in_order(P, "keep", WEDGE, lambda d, u, v, s, tau: R.ge(d, s, tau), env=NUM)
    def prog(d, tau, cands):
        return d.call(keep, list=cands, E=tau)
    P.prog("t5_decide_filter", prog)

Holes: a hole function receives the composer `d` first, then wires. Fields a hole does not use are erased
automatically (no need to d.erase them). A hole must not capture wires from elsewhere (glue checks this).

Recipe list (details, edge cases and cost notes in each docstring and in docs/RECIPES.md):
  lists     list_length_and_copy, list_to_trie, filter_in_order, count_where, take_first, argmax_first, sort_by
  keyed     lookup_many, reduce_by_key
  tries     select_sorted, count_where_trie, argmax_first_trie
  graphs    frontier_relax, layered_bfs_count, pointer_jump
  helpers   depth_for, ge, le, min2, max2, pack, unpack, not0
"""
from __future__ import annotations
import inspect
from .glue import (Program, GlueError, Kind, NUM, DEPTH, ANY, MCQ, LIST, TRIE, TUP, HOLE, EDGE, ADJ, INF, Lit,
                   _in, _out, chain, _loc)

__all__ = ["list_length_and_copy", "list_to_trie", "filter_in_order", "count_where", "take_first", "argmax_first",
           "sort_by", "lookup_many", "reduce_by_key", "select_sorted", "count_where_trie", "argmax_first_trie",
           "frontier_relax", "layered_bfs_count", "pointer_jump", "depth_for", "ge", "le", "min2", "max2", "pack",
           "unpack", "not0", "RECIPES"]


# ============================================================================ internals
def _fields(elem: Kind):
    return list(elem.args) if elem.tag == "tup" else [elem]


def _as_elem(vals, elem):
    """Python tuple of wires for a tuple element, the single wire otherwise."""
    return tuple(vals) if elem.tag == "tup" else vals[0]


def _hole(fn, d, args, what, extra=""):
    """Call an author hole fn(d, *args); erase the args it did not use; return its result."""
    if not callable(fn):
        raise GlueError(f"{_loc()}: {what} must be a Python function (d, ...) -> value(s); got {fn!r}")
    try:
        sig = inspect.signature(fn)
        ps = list(sig.parameters.values())
        var = any(p.kind == p.VAR_POSITIONAL for p in ps)
        if not var and len(ps) != len(args) + 1:
            raise GlueError(f"wrong arity: {what} is called as f(d, {', '.join(a.hint if hasattr(a, 'hint') else str(a) for a in args)})"
                            f", i.e. d plus {len(args)} value(s){extra}; your function `{fn.__name__}` takes {len(ps)} "
                            f"parameter(s).")
    except (TypeError, ValueError):
        pass
    r = fn(d, *args)
    ret = set()

    def walk(v):
        if isinstance(v, (tuple, list)):
            for x in v: walk(x)
        else: ret.add(id(v))
    walk(r)
    for a in args:
        if hasattr(a, "uses") and not a.uses and id(a) not in ret:
            d.erase(a)
    if r is None:
        raise GlueError(f"{what}: `{getattr(fn, '__name__', 'hole')}` returned None. Did you forget `return`?")
    return r


def _fan(d, w, n):
    if n == 1: return (w,)
    return d.fanout(w, n)


def _fan_elem(d, es, n):
    """Copy every element field n times: returns n lists of fields."""
    cols = [_fan(d, e, n) for e in es]
    return [[c[i] for c in cols] for i in range(n)]


def _recipe(P: Program, name, desc, fn, ins, outs, **meta):
    """Compile fn(d, *ins) -> outs as definition @name and register it as a Prim with a typed signature."""
    if not isinstance(name, str) or not name.replace("_", "a").isalnum() or not name[0].isalpha():
        raise GlueError(f"{_loc()}: recipe name {name!r} must be letters/digits/_ and start with a letter")
    if name in P.prims:
        raise GlueError(f"{_loc()}: name clash: `{name}` is already {P.prims[name].desc}")
    P.define(name, fn, ins, [k for _, k in outs])
    sig = chain(*([_in(n, k) for n, k in ins] + [_out(n, k) for n, k in outs]))
    return P._prim(name, name, desc, sig, **meta)


# ============================================================================ helpers used inside bodies
def ge(d, a, b):
    """a >= b as 1/0 (no `b - 1` wrap at b = 0)."""
    return d.op(1, "-", d.op(a, "<", b)) if not (isinstance(a, int) and isinstance(b, int)) else int(a >= b)


def le(d, a, b):
    """a <= b as 1/0."""
    return d.op(1, "-", d.op(a, ">", b)) if not (isinstance(a, int) and isinstance(b, int)) else int(a <= b)


def not0(d, a):
    """a != 0 as 1/0."""
    return d.op(a, "!", 0)


def min2(d, a, b):
    """(min(a, b), max(a, b)) for two numbers."""
    a1, a2, a3 = d.fanout(a, 3)
    b1, b2, b3 = d.fanout(b, 3)
    lt1, lt2 = d.fanout(d.op(a1, "<", b1), 2)
    return d.select(lt1, a2, b2), d.select(lt2, b3, a3)


def max2(d, a, b):
    """max(a, b)."""
    a1, a2 = d.fanout(a, 2)
    b1, b2 = d.fanout(b, 2)
    return d.select(d.op(a1, "<", b1), b2, a2)


def pack(d, a, b, bits):
    """(a << bits) | b: a pair key. bits may be a wire (e.g. a depth L) or an int. Needs b < 2^bits and the result
    < 2^24 (24-bit numbers)."""
    return d.op(d.op(a, "<<", bits), "|", b)


def unpack(d, k, bits):
    """(k >> bits, k & (2^bits - 1)): inverse of pack. bits may be a wire or an int."""
    k1, k2 = d.fanout(k, 2)
    if isinstance(bits, int):
        return d.op(k1, ">>", bits), d.op(k2, "&", (1 << bits) - 1)
    b1, b2 = d.fanout(bits, 2)
    mask = d.op(d.op(1, "<<", b2), "-", 1)
    return d.op(k1, ">>", b1), d.op(k2, "&", mask)


def depth_for(P: Program, d, m):
    """A trie depth L for keys 0..m-1 that is safe for m = 0 (depth 0, one leaf) and m = 1. Never lg(m - 1) with
    m = 0 (that is lg(16777215) = 24, a 16M-leaf trie)."""
    lg = P.lg()
    m1, m2 = d.fanout(m, 2)
    mm = d.op(m1, "+", d.op(m2, "=", 0))       # max(m, 1)
    return d.call(lg, x=d.op(mm, "-", 1))


# ============================================================================ list recipes
def list_length_and_copy(P: Program, name: str, elem: Kind = NUM, copies: int = 1, key=None):
    """Length (and optionally the max of a key) of a list, plus `copies` fresh copies of it in the same order.
    Ports:  in list: list[elem]  ->  out n: num, [mx: num if key], c1 .. c<copies>: list[elem]
    key(d, *fields) -> number: mx = max key over the list (0 for the empty list).
    Use it because a list cannot be duplicated: every consumer needs its own copy. Elements must be numbers or
    tuples of numbers (they are DUPed). Cost: one walk, ~2.3 rounds and ~15 itrs per cell per copy."""
    fs = _fields(elem)
    has_key = key is not None
    state = [("n", NUM)] + ([("mx", NUM)] if has_key else []) + [(f"h{i}", HOLE(LIST(elem))) for i in range(copies)]
    if has_key: state.append(("hm", HOLE(NUM)))

    def step(d, *a):
        a = list(a)
        n = a.pop(0)
        mx = a.pop(0) if has_key else None
        hs = [a.pop(0) for _ in range(copies)]
        hm = a.pop(0) if has_key else None
        es = a
        cols = _fan_elem(d, es, copies + (1 if has_key else 0))
        out = [d.op(n, "+", 1)]
        if has_key:
            k = _hole(key, d, cols[-1], f"key of list_length_and_copy `{name}`")
            out.append(max2(d, mx, k))
        out += [d.fill_cons(h, _as_elem(cols[i], elem)) for i, h in enumerate(hs)]
        if has_key: out.append(hm)
        return tuple(out)

    def fin(d, *a):
        a = list(a)
        n = a.pop(0)
        mx = a.pop(0) if has_key else None
        hs = [a.pop(0) for _ in range(copies)]
        for h in hs: d.fill(h, d.nil())
        if has_key: d.fill(a.pop(0), mx)
        return n
    w = P.stream(name + "_w", step, fin, state=state, elem=elem)

    def body(d, lst):
        vals, holes = [], []
        for _ in range(copies):
            v, h = d.hole(LIST(elem)); vals.append(v); holes.append(h)
        init = [0] + ([0] if has_key else []) + holes
        mval = None
        if has_key:
            mval, mh = d.hole(NUM); init.append(mh)
        n = d.call(w, list=lst, init=tuple(init))
        return tuple([n] + ([mval] if has_key else []) + vals)
    outs = [("n", NUM)] + ([("mx", NUM)] if has_key else []) + [(f"c{i + 1}", LIST(elem)) for i in range(copies)]
    return _recipe(P, name, f"recipe list_length_and_copy `{name}`", body, [("list", LIST(elem))], outs)


def list_to_trie(P: Program, name: str, elem: Kind = NUM, pad=0):
    """Trie t of depth L with t[i] = the i-th list element (i = 0, 1, ...); leaves past the end hold `pad`
    (an int, or a tuple of ints for a tuple element).
    Ports:  in list: list[elem], L: depth  ->  out t: trie[elem]
    Precondition: len(list) <= 2^L (element i >= 2^L overwrites leaf i mod 2^L). Typical: c[i] as a trie, then
    lookup_many(keys, t). Cost: one walk + one keyed update per element (all updates expand in parallel)."""
    fs = _fields(elem)
    if elem.tag == "tup":
        pv = pad if isinstance(pad, (tuple, list)) else tuple([pad] * len(fs))
        txt = str(pv[-1] & 0xFFFFFF)
        for x in reversed(pv[:-1]): txt = f"({x & 0xFFFFFF} {txt})"
        z = P.const_trie(name + "_z", Lit(txt, elem), kind=elem)
    else:
        z = P.const_trie(name + "_z", pad)
    st = P.update(name + "_set", "set", leaf=elem, payload=elem)

    def step(d, L, i, T, *es):
        L1, L2 = d.fanout(L, 2)
        i1, i2 = d.fanout(i, 2)
        return L2, d.op(i2, "+", 1), d.call(st, t=T, k=i1, L=L1, P=_as_elem(list(es), elem))

    def fin(d, L, i, T):
        d.erase(L, i)
        return T
    w = P.stream(name + "_w", step, fin, state=[("L", DEPTH), ("i", NUM), ("T", TRIE(elem))], elem=elem)

    def body(d, lst, L):
        L1, L2 = d.fanout(L, 2)
        return d.call(w, list=lst, init=(L2, 0, d.call(z, L=L1)))
    return _recipe(P, name, f"recipe list_to_trie `{name}`", body, [("list", LIST(elem)), ("L", DEPTH)],
                   [("t", TRIE(elem))])


def filter_in_order(P: Program, name: str, elem: Kind, pred, env: Kind | None = None):
    """The elements for which pred holds, unchanged, in input order (repeats kept).
    Ports:  in list: list[elem] [, E: env]  ->  out o: list[elem]
    pred(d, *fields [, E]) -> number; nonzero keeps the element. Write `>= tau` as R.ge(d, s, tau), never
    `s > tau - 1` (tau - 1 wraps to 16777215 at tau = 0). env must be numbers (copied per element).
    Empty list gives []. Cost: one walk, one switch per element."""
    fs = _fields(elem)
    has_env = env is not None
    state = ([("E", env)] if has_env else []) + [("h", HOLE(LIST(elem)))]

    def step(d, *a):
        a = list(a)
        E = a.pop(0) if has_env else None
        h = a.pop(0)
        es = a
        c1, c2 = _fan_elem(d, es, 2)
        extra = []
        if has_env:
            E1, E2 = d.fanout(E, 2); extra = [E1]; E = E2
        f = _hole(pred, d, c1 + extra, f"pred of filter_in_order `{name}`")

        def drop(b, h, *xs):
            b.erase(*xs)
            return h

        def keep(b, fm1, h, *xs):
            b.erase(fm1)
            return b.fill_cons(h, _as_elem(list(xs), elem))
        h2 = d.branch(f, drop, keep, h, *c2)
        return tuple(([E] if has_env else []) + [h2])

    def fin(d, *a):
        a = list(a)
        if has_env: d.erase(a.pop(0))
        d.fill(a.pop(0), d.nil())
        return 0
    w = P.stream(name + "_w", step, fin, state=state, elem=elem)

    def body(d, lst, *E):
        v, h = d.hole(LIST(elem))
        r = d.call(w, list=lst, init=tuple(list(E) + [h]) if has_env else h)
        d.erase(r)
        return v
    ins = [("list", LIST(elem))] + ([("E", env)] if has_env else [])
    return _recipe(P, name, f"recipe filter_in_order `{name}`", body, ins, [("o", LIST(elem))])


def count_where(P: Program, name: str, elem: Kind, pred, env: Kind | None = None):
    """Number of list elements for which pred(d, *fields [, E]) is nonzero (every occurrence counts).
    Ports:  in list: list[elem] [, E: env]  ->  out n: num.   Empty list gives 0. Cost: one walk."""
    has_env = env is not None
    state = [("c", NUM)] + ([("E", env)] if has_env else [])

    def step(d, c, *a):
        a = list(a)
        E = a.pop(0) if has_env else None
        extra = []
        if has_env:
            E1, E2 = d.fanout(E, 2); extra = [E1]; E = E2
        f = _hole(pred, d, a + extra, f"pred of count_where `{name}`")
        c2 = d.op(c, "+", d.op(f, "!", 0))
        return (c2, E) if has_env else c2

    def fin(d, c, *E):
        d.erase(*E)
        return c
    w = P.stream(name + "_w", step, fin, state=state, elem=elem)

    def body(d, lst, *E):
        return d.call(w, list=lst, init=(0, E[0]) if has_env else 0)
    ins = [("list", LIST(elem))] + ([("E", env)] if has_env else [])
    return _recipe(P, name, f"recipe count_where `{name}`", body, ins, [("n", NUM)])


def take_first(P: Program, name: str, elem: Kind = NUM):
    """The first k elements of a list (all of them if the list is shorter) and how many were left over.
    Ports:  in list: list[elem], k: num  ->  out o: list[elem], rest: num.   k = 0 gives ([], len). Cost: one walk."""
    def step(d, k, h, r, *es):
        def zero(b, h, r, *xs):
            b.erase(*xs)
            return 0, h, b.op(r, "+", 1)

        def more(b, km1, h, r, *xs):
            return km1, b.fill_cons(h, _as_elem(list(xs), elem)), r
        return d.branch(k, zero, more, h, r, *es)

    def fin(d, k, h, r):
        d.erase(k)
        d.fill(h, d.nil())
        return r
    w = P.stream(name + "_w", step, fin, state=[("k", NUM), ("h", HOLE(LIST(elem))), ("r", NUM)], elem=elem)

    def body(d, lst, k):
        v, h = d.hole(LIST(elem))
        r = d.call(w, list=lst, init=(k, h, 0))
        return v, r
    return _recipe(P, name, f"recipe take_first `{name}`", body, [("list", LIST(elem)), ("k", NUM)],
                   [("o", LIST(elem)), ("rest", NUM)])


def argmax_first(P: Program, name: str, elem: Kind, value, env: Kind | None = None):
    """Largest value(element) over a list and the index of its FIRST occurrence (ties go to the lowest index).
    Ports:  in list: list[elem] [, E: env]  ->  out mx: num, idx: num
    value(d, *fields [, E]) -> number < 16777215. Empty list gives (0, 16777215). All-zero values give (0, 0).
    Cost: one walk (two selects per element)."""
    has_env = env is not None
    state = [("b", NUM), ("bi", NUM), ("i", NUM)] + ([("E", env)] if has_env else []) + [("hi", HOLE(NUM))]

    def step(d, b, bi, i, *a):
        a = list(a)
        E = a.pop(0) if has_env else None
        hi = a.pop(0)
        extra = []
        if has_env:
            E1, E2 = d.fanout(E, 2); extra = [E1]; E = E2
        v = d.op(_hole(value, d, a + extra, f"value of argmax_first `{name}`"), "+", 1)   # 0 = nothing yet
        v1, v2 = d.fanout(v, 2)
        b1, b2 = d.fanout(b, 2)
        i1, i2 = d.fanout(i, 2)
        g1, g2 = d.fanout(d.op(v1, ">", b1), 2)
        return tuple([d.select(g1, v2, b2), d.select(g2, i1, bi), d.op(i2, "+", 1)] + ([E] if has_env else []) + [hi])

    def fin(d, b, bi, i, *a):
        a = list(a)
        if has_env: d.erase(a.pop(0))
        d.erase(i)
        d.fill(a.pop(0), bi)
        b1, b2 = d.fanout(b, 2)
        return d.select(b1, d.op(b2, "-", 1), 0)
    w = P.stream(name + "_w", step, fin, state=state, elem=elem)

    def body(d, lst, *E):
        iv, ih = d.hole(NUM)
        m = d.call(w, list=lst, init=tuple([0, INF, 0] + list(E) + [ih]))
        return m, iv
    ins = [("list", LIST(elem))] + ([("E", env)] if has_env else [])
    return _recipe(P, name, f"recipe argmax_first `{name}`", body, ins, [("mx", NUM), ("idx", NUM)])


def sort_by(P: Program, name: str, elem: Kind, key):
    """Stable sort of a list by a lexicographic key: ascending on key(d, *fields) -> k or (k1, k2, ...) (numbers).
    Equal keys keep their input order. For DESCENDING on a field s use a key like d.op(1000, "-", s) (or
    d.op(16777215, "-", s)). Repeats are kept.
    Ports:  in list: list[elem]  ->  out o: list[elem]
    Method (rank sort): every element j is broadcast to every trie leaf i, which counts the elements that sort
    before it (rank). Then each element is written at position rank. No key-size limit (keys are compared, not used
    as trie keys). Cost: O(n * 2^L) interactions (n = length; ~40 itrs per pair), depth ~O(n) pipelined (the
    broadcasts are chained leaf by leaf). Fine for n up to a few hundred."""
    fs = _fields(elem)
    ne = len(fs)
    nk_box = []

    def keys_of(d, es):
        k = _hole(key, d, list(es), f"key of sort_by `{name}`")
        ks = list(k) if isinstance(k, (tuple, list)) else [k]
        if not nk_box: nk_box.append(len(ks))
        elif nk_box[0] != len(ks): raise GlueError(f"key of sort_by `{name}` must always return {nk_box[0]} value(s)")
        return ks

    # 1. length + two copies
    cp = list_length_and_copy(P, name + "_len", elem, copies=2)
    # 2. walk 1: the key tuple of every element j (nk known after this compile)
    #    walk 2 (built below): trie T[i] = (fields..., keys..., rank=0)
    kl_state = [("h", HOLE(LIST(ANY)))]

    def kstep(d, h, *es):
        ks = keys_of(d, es)
        return d.fill_cons(h, tuple(ks) if len(ks) > 1 else ks[0])

    def kfin(d, h):
        d.fill(h, d.nil())
        return 0
    kw = P.stream(name + "_kw", kstep, kfin, state=kl_state, elem=elem)   # compiled now: nk known
    nk = nk_box[0]
    leafk = TUP(*([NUM] * (ne + nk + 1)))
    z = P.const_trie(name + "_z", Lit(_zeros(ne + nk + 1), leafk), kind=leafk)
    st = P.update(name + "_set", "set", leaf=leafk, payload=leafk)

    def tstep(d, L, i, T, *es):
        L1, L2 = d.fanout(L, 2)
        i1, i2 = d.fanout(i, 2)
        c1, c2 = _fan_elem(d, es, 2)
        ks = keys_of(d, c1)
        T2 = d.call(st, t=T, k=i1, L=L1, P=tuple(list(c2) + ks + [0]))
        return L2, d.op(i2, "+", 1), T2

    def tfin(d, L, i, T):
        d.erase(L, i)
        return T
    tw = P.stream(name + "_tw", tstep, tfin, state=[("L", DEPTH), ("i", NUM), ("T", TRIE(leafk))], elem=elem)

    # 3. rank: for every j, map every leaf i: rank_i += [key_j < key_i or (key_j == key_i and j < i)]
    envk = TUP(*([NUM] * (nk + 1)))

    def rleaf(d, x, i, E):
        xs = list(d.split(x))
        ev = list(d.split(E))
        kj, j = ev[:nk], ev[nk]
        e, ki, rank = xs[:ne], xs[ne:ne + nk], xs[ne + nk]
        ki2 = []
        less, eq = None, None
        # lexicographic compare kj ? ki from the last key backwards: before = lt_k or (eq_k and before_rest)
        ka = [d.fanout(k, 3) for k in ki]
        kb = [d.fanout(k, 2) for k in kj]
        i1, i2 = d.fanout(i, 2)
        before = d.op(j, "<", i1)                     # tie-break: input order
        d.erase(i2)
        for t in reversed(range(nk)):
            lt = d.op(kb[t][0], "<", ka[t][0])
            eqt = d.op(kb[t][1], "=", ka[t][1])
            before = d.op(lt, "|", d.op(eqt, "&", before))
        ki2 = [ka[t][2] for t in range(nk)]
        return tuple(e + ki2 + [d.op(rank, "+", before)]), 0
    mr = P.mapreduce(name + "_mr", rleaf, "+", index=True, env=envk, leaf_kind=leafk)

    def rstep(d, L, j, T, *ks):
        L1, L2 = d.fanout(L, 2)
        j1, j2 = d.fanout(j, 2)
        ks = list(ks)
        T2, o = d.call(mr, t=T, L=L1, E=tuple(ks + [j1]))
        d.erase(o)
        return L2, d.op(j2, "+", 1), T2

    def rfin(d, L, j, T):
        d.erase(L, j)
        return T
    rw = P.stream(name + "_rw", rstep, rfin, state=[("L", DEPTH), ("j", NUM), ("T", TRIE(leafk))],
                  elem=TUP(*([NUM] * nk)) if nk > 1 else NUM)
    # 4. place: O[rank_i] := element i (i < n); padding leaves write to their own index >= n
    oz = P.const_trie(name + "_oz", Lit(_zeros(ne), elem) if ne > 1 else 0, kind=elem)
    oset = P.update(name + "_oset", "set", leaf=elem, payload=elem)

    def pkey(d, x, i, n):
        xs = list(d.split(x))
        e, rank = xs[:ne], xs[ne + nk]
        d.erase(*xs[ne:ne + nk])
        i1, i2 = d.fanout(i, 2)
        real = d.op(i1, "<", n)
        return d.select(real, rank, i2), _as_elem(e, elem)
    sc = P.scatter(name + "_sc", oset, pkey, leaf_kind=leafk, env=NUM)
    tl = P.to_list(name + "_tl")
    lg = P.lg()

    def body(d, lst):
        n, c1, c2 = d.call(cp, list=lst)

        def empty(b, c1, c2):
            b.erase(c1, c2)
            return b.nil()

        def nonempty(b, nm1, c1, c2):
            nm1a, nm1b = b.fanout(nm1, 2)
            n1, n2 = b.fanout(b.op(nm1b, "+", 1), 2)
            L = b.call(lg, x=nm1a)
            L1, L2, L3, L4, L5, L6, L7 = b.fanout(L, 7)
            kv, kh = b.hole(LIST(ANY))
            b.erase(b.call(kw, list=c1, init=kh))
            # c1 was consumed by the key walk; the trie needs the elements: rebuild from c2 (fields + keys)
            T = b.call(tw, list=c2, init=(L2, 0, b.call(z, L=L1)))
            T = b.call(rw, list=kv, init=(L3, 0, T))
            O = b.call(sc, t=T, L=L4, Lh=L5, E=n1, H=b.call(oz, L=L6))
            return b.call(tl, t=O, L=L7, n=n2)
        return d.branch(n, empty, nonempty, c1, c2)
    return _recipe(P, name, f"recipe sort_by `{name}`", body, [("list", LIST(elem))], [("o", LIST(elem))])


def _zeros(k):
    t = "0"
    for _ in range(k - 1): t = f"(0 {t})"
    return t


# ============================================================================ keyed recipes
def lookup_many(P: Program, name: str, elem: Kind, keys, nkeys: int = 1):
    """For every list element, look up nkeys values V[k] in a numeric trie, all at once (multicast).
    Ports:  in list: list[elem], V: trie[num], L: depth  ->  out o: list[(fields..., V[k1], ..., V[k_nkeys])]
    keys(d, *fields) -> k (nkeys = 1) or a tuple of nkeys keys. The output keeps the input order and every
    original field, followed by the looked-up values. V is consumed (use list_to_trie to make it; to keep using
    V afterwards, build it twice). Preconditions: every key < 2^L (a key >= 2^L reads leaf k mod 2^L);
    V's leaves are numbers. Cost: one walk + one request per key; all answers arrive in one O(L) delivery."""
    fs = _fields(elem)
    outk = TUP(*(fs + [NUM] * nkeys))
    rq = P.mc_request(name + "_rq")
    dv = P.mc_deliver(name + "_dv")
    mce = P.mc_empty(name + "_q0")

    def step(d, L, q, h, V, *es):
        c1, c2 = _fan_elem(d, es, 2)
        k = _hole(keys, d, c1, f"keys of lookup_many `{name}`")
        ks = list(k) if isinstance(k, (tuple, list)) else [k]
        if len(ks) != nkeys:
            raise GlueError(f"keys of lookup_many `{name}` returned {len(ks)} key(s); the recipe was made with "
                            f"nkeys={nkeys}")
        Ls = d.fanout(L, nkeys + 1)
        rs = []
        for t, kk in enumerate(ks):
            r, q = d.call(rq, q=q, k=kk, L=Ls[t])
            rs.append(r)
        h2 = d.fill_cons(h, tuple(list(c2) + rs))
        return Ls[-1], q, h2, V

    def fin(d, L, q, h, V):
        d.fill(h, d.nil())
        d.call(dv, v=V, q=q, L=L)
        return 0
    w = P.stream(name + "_w", step, fin,
                 state=[("L", DEPTH), ("q", MCQ), ("h", HOLE(LIST(outk))), ("V", TRIE(NUM))], elem=elem)

    def body(d, lst, V, L):
        L1, L2 = d.fanout(L, 2)
        v, h = d.hole(LIST(outk))
        d.erase(d.call(w, list=lst, init=(L2, d.call(mce, L=L1), h, V)))
        return v
    return _recipe(P, name, f"recipe lookup_many `{name}`", body,
                   [("list", LIST(elem)), ("V", TRIE(NUM)), ("L", DEPTH)], [("o", LIST(outk))])


_IDENT = {"add": 0, "or": 0, "max": 0, "min": INF, "set": 0, "inc": 0, "set1": 0}


def reduce_by_key(P: Program, name: str, elem: Kind, keyval, combine: str = "add", ident=None,
                  env: Kind | None = None):
    """Group-by: a trie H with H[k] = combine over the values of all elements whose key is k.
    Ports:  in list: list[elem], L: depth [, E: env]  ->  out H: trie[num]
    keyval(d, *fields [, E]) -> (k, v); for combine "inc" (count) or "set1" (presence) just k.
    combine: "add" | "max" | "min" | "or" | "set" (last in list order wins) | "inc" | "set1" | a function
    f(d, leaf, v) -> new leaf. ident: the value of an untouched leaf (default: 0, INF for min).
    Preconditions: k < 2^L (larger keys alias to k mod 2^L). To skip an element send the identity (v = 0 for
    add/or/max, INF for min) or a key you ignore later. A present-with-value-0 group is indistinguishable from an
    absent one under add: store v + 1 or keep a second set1 trie. Pair keys: R.pack(d, a, b, bits).
    Cost: one walk; the keyed updates expand before the trie exists and collapse in O(L) rounds."""
    if ident is None: ident = _IDENT.get(combine, 0) if isinstance(combine, str) else 0
    nopay = combine in ("inc", "set1")
    has_env = env is not None
    z = P.const_trie(name + "_z", ident)
    if callable(combine):
        up = P.update(name + "_u", combine)
    else:
        up = P.update(name + "_u", combine)
    state = [("L", DEPTH), ("H", TRIE(NUM))] + ([("E", env)] if has_env else [])

    def step(d, L, H, *a):
        a = list(a)
        E = a.pop(0) if has_env else None
        extra = []
        if has_env:
            E1, E2 = d.fanout(E, 2); extra = [E1]; E = E2
        kv = _hole(keyval, d, a + extra, f"keyval of reduce_by_key `{name}`")
        L1, L2 = d.fanout(L, 2)
        if nopay:
            if isinstance(kv, (tuple, list)):
                raise GlueError(f"keyval of reduce_by_key `{name}` (combine {combine}) must return just the key k")
            H2 = d.call(up, t=H, k=kv, L=L1)
        else:
            if not isinstance(kv, (tuple, list)) or len(kv) != 2:
                raise GlueError(f"keyval of reduce_by_key `{name}` must return (k, v)")
            H2 = d.call(up, t=H, k=kv[0], L=L1, P=kv[1])
        return tuple([L2, H2] + ([E] if has_env else []))

    def fin(d, L, H, *E):
        d.erase(L, *E)
        return H
    w = P.stream(name + "_w", step, fin, state=state, elem=elem)

    def body(d, lst, L, *E):
        L1, L2 = d.fanout(L, 2)
        return d.call(w, list=lst, init=tuple([L2, d.call(z, L=L1)] + list(E)))
    ins = [("list", LIST(elem)), ("L", DEPTH)] + ([("E", env)] if has_env else [])
    return _recipe(P, name, f"recipe reduce_by_key `{name}` ({combine if isinstance(combine, str) else 'fn'})",
                   body, ins, [("H", TRIE(NUM))])


# ============================================================================ trie recipes
def select_sorted(P: Program, name: str, pred, emit, leaf_kind: Kind = NUM, env: Kind = NUM):
    """Trie -> list, in ascending key order, of emit(d, x, i, E) for every leaf (value x, index i) where
    pred(d, x, i, E) is nonzero. This is how sorted / de-duplicated outputs are produced: put items in a trie keyed
    by their sort key (reduce_by_key, e.g. with a packed pair key), then select the occupied leaves.
    Ports:  in t: trie[leaf_kind], L: depth, E: env  ->  out o: list
    Leaves i >= n are padding: pass n in E and test i < n in pred when the trie is indexed by position.
    emit may return a number or a tuple (e.g. R.unpack(d, i, B) for a pair key). Cost: one traversal; the list is
    threaded right to left (~4 rounds per level + the leaf)."""
    def leaf(d, x, i, E, acc):
        x1, x2 = d.fanout(x, 2) if _copyable(leaf_kind) else (x, None)
        i1, i2 = d.fanout(i, 2)
        E1, E2 = d.fanout(E, 2)
        f = _hole(pred, d, [x1, i1, E1], f"pred of select_sorted `{name}`")

        def no(b, x, i, E, acc):
            b.erase(x, i, E)
            return acc

        def yes(b, fm1, x, i, E, acc):
            b.erase(fm1)
            return b.cons(_hole(emit, b, [x, i, E], f"emit of select_sorted `{name}`"), acc)
        return d.branch(f, no, yes, x2, i2, E2, acc)
    if not _copyable(leaf_kind):
        raise GlueError(f"{_loc()}: select_sorted needs numeric (or tuple of numbers) leaves; got {leaf_kind}")
    fo = P.fold(name + "_f", leaf, acc=LIST(ANY), index=True, env=env, leaf_kind=leaf_kind)

    def body(d, t, L, E):
        return d.call(fo, t=t, L=L, E=E, acc=d.nil())
    return _recipe(P, name, f"recipe select_sorted `{name}`", body,
                   [("t", TRIE(leaf_kind)), ("L", DEPTH), ("E", env)], [("o", LIST(ANY))])


def _copyable(k):
    from .glue import _copyable as c
    return c(k)


def count_where_trie(P: Program, name: str, pred, leaf_kind: Kind = NUM, env: Kind = NUM):
    """Number of leaves (value x, index i) with pred(d, x, i, E) nonzero. Pass n in E and test i < n to skip
    padding leaves. Ports: in t: trie, L: depth, E: env -> out n: num. Cost: one traversal, O(L) depth."""
    def leaf(d, x, i, E):
        return d.op(_hole(pred, d, [x, i, E], f"pred of count_where_trie `{name}`"), "!", 0)
    r = P.reduce(name + "_r", leaf, "+", index=True, env=env, leaf_kind=leaf_kind)

    def body(d, t, L, E):
        return d.call(r, t=t, L=L, E=E)
    return _recipe(P, name, f"recipe count_where_trie `{name}`", body,
                   [("t", TRIE(leaf_kind)), ("L", DEPTH), ("E", env)], [("n", NUM)])


def argmax_first_trie(P: Program, name: str, value, leaf_kind: Kind = NUM, env: Kind = NUM):
    """Largest value over the leaves and the LOWEST leaf index that has it.
    Ports:  in t: trie, L: depth, E: env  ->  out mx: num, idx: num
    value(d, x, i, E) -> (ok, v): leaves with ok == 0 do not take part (use it for padding i >= n and for absent
    entries); v < 16777215. No leaf taking part gives (0, 16777215). Ties -> smallest index (e.g. "ties go to the
    smallest value" when the trie is keyed by value). Cost: two traversals (mapreduce max + reduce min), O(L)."""
    def l1(d, x, i, E):
        r = _hole(value, d, [x, i, E], f"value of argmax_first_trie `{name}`")
        if not isinstance(r, (tuple, list)) or len(r) != 2:
            raise GlueError(f"value of argmax_first_trie `{name}` must return (ok, v)")
        ok, v = r
        s = d.op(d.op(ok, "!", 0), "*", d.op(v, "+", 1))     # v + 1, or 0 when not taking part
        s1, s2 = d.fanout(s, 2)
        return s1, s2
    mr = P.mapreduce(name + "_mx", l1, "max", index=True, env=env, leaf_kind=leaf_kind)

    def l2(d, x, i, M):
        x1, x2 = d.fanout(x, 2)
        hit = d.op(d.op(x1, "=", M), "&", d.op(x2, "!", 0))
        return d.select(hit, i, INF)
    rm = P.reduce(name + "_ix", l2, "min", index=True, env=NUM)

    def body(d, t, L, E):
        L1, L2 = d.fanout(L, 2)
        t2, M = d.call(mr, t=t, L=L1, E=E)
        M1, M2, M3 = d.fanout(M, 3)
        idx = d.call(rm, t=t2, L=L2, E=M1)
        return d.select(M2, d.op(M3, "-", 1), 0), idx
    return _recipe(P, name, f"recipe argmax_first_trie `{name}`", body,
                   [("t", TRIE(leaf_kind)), ("L", DEPTH), ("E", env)], [("mx", NUM), ("idx", NUM)])


# ============================================================================ graph recipes
def frontier_relax(P: Program, name: str, combine="min", msg=None, mode=None, ident=None):
    """Propagate values over an adjacency trie until nothing changes (generalised Bellman-Ford / label propagation).
    Ports:  in G: adj, D: trie[num] (initial state), C: trie[num] (first-round messages), L: depth -> out D2
    combine (the hole for the update): "min" | "max" | "or" | "add" | f(d, a, b) -> c (must be idempotent and
    monotone for mode "fixpoint").
    msg(d, m, w) -> the value sent along an edge (v w) from a vertex whose value is m. Default: m + w for min
    (shortest paths: use w = 1 for BFS, never w = 0 unless 0-weight edges are meant), m for max / or, m * w for add.
    mode "fixpoint" (default except add): new = combine(old, incoming); a vertex sends when its value changed.
    mode "wave" (default for add): new = old + incoming; a vertex sends its incoming amount when it is nonzero:
    counting over a DAG whose edges go level k -> k+1 (path counts). On a cycle the wave never stops.
    ident: the combine identity for "no message" (INF for min, 0 otherwise).
    Seed: C holds the start messages (e.g. 0 at s, INF elsewhere for min; 1 at s, 0 elsewhere for add); D holds the
    identity. Cost: ~75-155 rounds per round of propagation; rounds = longest shortest path + 1."""
    if mode is None: mode = "wave" if combine == "add" else "fixpoint"
    if ident is None: ident = INF if combine == "min" else 0

    def comb(d, a, b):
        if callable(combine): return combine(d, a, b)
        if combine == "min": return _minv(d, a, b)
        if combine == "max": return max2(d, a, b)
        if combine == "or": return d.op(a, "|", b)
        if combine == "add": return d.op(a, "+", b)
        raise GlueError(f"{_loc()}: frontier_relax combine {combine!r}")

    def act(d, X, dv, c):
        d.erase(X)
        if mode == "wave":
            c1, c2, c3 = d.fanout(c, 3)
            return d.op(dv, "+", c1), d.op(c2, "!", 0), c3
        dv1, dv2 = d.fanout(dv, 2)
        new = comb(d, dv1, c)
        n1, n2, n3 = d.fanout(new, 3)
        return n1, d.op(n2, "!", dv2), n3

    def default_msg(d, m, w):
        if combine == "min": return d.op(m, "+", w)
        if combine == "add": return d.op(m, "*", w)
        d.erase(w)
        return m
    mfn = msg or default_msg
    cu = combine if isinstance(combine, str) else (lambda d, leaf, p: combine(d, leaf, p))
    fr = P.frontier(name + "_fr", act, lambda d, m, w: _hole(mfn, d, [m, w], f"msg of frontier_relax `{name}`"),
                    cu, ident, env=NUM, env_default=0)

    def body(d, G, D, C, L):
        return d.call(fr, G=G, D=D, C=C, L=L)
    return _recipe(P, name, f"recipe frontier_relax `{name}` ({combine if isinstance(combine, str) else 'fn'}, {mode})",
                   body, [("G", ADJ), ("D", TRIE(NUM)), ("C", TRIE(NUM)), ("L", DEPTH)], [("D2", TRIE(NUM))])


def _minv(d, a, b):
    a1, a2 = d.fanout(a, 2)
    b1, b2 = d.fanout(b, 2)
    return d.select(d.op(b1, "<", a1), b2, a2)


def layered_bfs_count(P: Program, name: str, directed: bool = True):
    """BFS distances from s AND the number of shortest paths to every vertex (mod 2^24), in one recipe.
    Ports:  in n: num, s: num, es: list[(u v)], L: depth  ->  out D: trie[num], C: trie[num]
    D[v] = number of edges on a shortest path s -> v (16777215 if unreachable); C[v] = number of distinct
    shortest paths (0 if unreachable, C[s] = 1 = the empty path). directed=False adds both orientations.
    Preconditions: n >= 1, s < n, L = depth for n (R.depth_for); vertices < n. The count wave stops early only if a
    count is an exact multiple of 2^24 (not reachable at corpus sizes).
    Method: one walk builds the unit-weight graph and, for every edge (u v), the DAG edge weight
    [D[u] + 1 == D[v]] via multicast lookups of D (delivered after sssp); then a level-synchronous add-wave over the
    DAG from C = [s: 1]. Cost: sssp rounds + wave rounds (~ 2 x eccentricity x 100 depth)."""
    adj = P.adjacency(name + "_adj")
    eadj = P.empty_adj()
    mce = P.mc_empty(name + "_q0")
    rq = P.mc_request(name + "_rq")
    dvk = P.mc_deliver_keep(name + "_dv")
    sp = P.sssp(name + "_sp")
    z = P.const_trie(name + "_z", 0)
    seed = P.update(name + "_seed", "add")
    wave = frontier_relax(P, name + "_wave", "add")

    def one(d, g1, g2, q, L, a, b):
        L1, L2, L3, L4 = d.fanout(L, 4)
        a1, a2, a3 = d.fanout(a, 3)
        b1, b2, b3 = d.fanout(b, 3)
        g1 = d.call(adj, G=g1, u=a1, L=L1, v=b1, w=1)
        ra, q = d.call(rq, q=q, k=a3, L=L2)
        rb, q = d.call(rq, q=q, k=b3, L=L3)
        flag = d.op(d.op(ra, "+", 1), "=", rb)
        g2 = d.call(adj, G=g2, u=a2, L=L4, v=b2, w=flag)
        return g1, g2, q

    def step(d, L, n, s, hD, g1, g2, q, u, v):
        if directed:
            L1, L2 = d.fanout(L, 2)
            g1, g2, q = one(d, g1, g2, q, L1, u, v)
            return L2, n, s, hD, g1, g2, q
        L1, L2, L3 = d.fanout(L, 3)
        u1, u2 = d.fanout(u, 2)
        v1, v2 = d.fanout(v, 2)
        g1, g2, q = one(d, g1, g2, q, L1, u1, v1)
        g1, g2, q = one(d, g1, g2, q, L2, v2, u2)
        return L3, n, s, hD, g1, g2, q

    def fin(d, L, n, s, hD, g1, g2, q):
        L1, L2, L3, L4, L5, L6 = d.fanout(L, 6)
        s1, s2 = d.fanout(s, 2)
        D = d.call(sp, n=n, s=s1, L=L1, G=g1)
        D2 = d.call(dvk, v=D, q=q, L=L2)
        d.fill(hD, D2)
        C0 = d.call(seed, t=d.call(z, L=L3), k=s2, L=L4, P=1)
        return d.call(wave, G=g2, D=d.call(z, L=L5), C=C0, L=L6)
    w = P.stream(name + "_w", step, fin,
                 state=[("L", DEPTH), ("n", NUM), ("s", NUM), ("hD", HOLE(TRIE(NUM))), ("g1", ADJ), ("g2", ADJ),
                        ("q", MCQ)], elem=EDGE)

    def body(d, n, s, es, L):
        L1, L2, L3, L4 = d.fanout(L, 4)
        Dv, hD = d.hole(TRIE(NUM))
        C = d.call(w, list=es, init=(L4, n, s, hD, d.call(eadj, L=L1), d.call(eadj, L=L2), d.call(mce, L=L3)))
        return Dv, C
    return _recipe(P, name, f"recipe layered_bfs_count `{name}`", body,
                   [("n", NUM), ("s", NUM), ("es", LIST(EDGE)), ("L", DEPTH)], [("D", TRIE(NUM)), ("C", TRIE(NUM))])


def pointer_jump(P: Program, name: str, rounds: int = 8):
    """Pointer doubling: for a pointer list p (p[i] < n), return q = p applied 2^rounds times: q[i] = p^(2^rounds)(i).
    With roots (p[r] == r) and chains shorter than 2^rounds, q[i] is the root reached from i.
    Ports:  in list: list[num]  ->  out o: list[num]   (same length, same order; [] gives [])
    Preconditions: every p[i] < n; the default rounds = 8 covers chains up to 255 steps (n <= 256). On a cycle,
    q[i] is some node ON the cycle; detect cycles by checking p[q[i]] == q[i] afterwards (lookup_many).
    Method: each round one walk writes V[i] = x and requests V[x] for every element (all answered by one
    delivery). Cost: rounds x (one walk + one delivery); depth ~ rounds x (2.3 n + 30 L)."""
    lg = P.lg()
    z = P.const_trie(name + "_z", 0)
    st = P.update(name + "_set", "set")
    mce = P.mc_empty(name + "_q0")
    rq = P.mc_request(name + "_rq")
    dv = P.mc_deliver(name + "_dv")
    cp = list_length_and_copy(P, name + "_len", NUM)

    def step(d, L, i, V, q, h, x):
        L1, L2, L3 = d.fanout(L, 3)
        i1, i2 = d.fanout(i, 2)
        x1, x2 = d.fanout(x, 2)
        V2 = d.call(st, t=V, k=i1, L=L1, P=x1)
        r, q2 = d.call(rq, q=q, k=x2, L=L2)
        return L3, d.op(i2, "+", 1), V2, q2, d.fill_cons(h, r)

    def fin(d, L, i, V, q, h):
        d.erase(i)
        d.fill(h, d.nil())
        d.call(dv, v=V, q=q, L=L)
        return 0
    w = P.stream(name + "_w", step, fin,
                 state=[("L", DEPTH), ("i", NUM), ("V", TRIE(NUM)), ("q", MCQ), ("h", HOLE(LIST(NUM)))], elem=NUM)

    def body(d, lst):
        n, c = d.call(cp, list=lst)

        def empty(b, c):
            b.erase(c)
            return b.nil()

        def nonempty(b, nm1, cur):
            Ls = list(b.fanout(b.call(lg, x=nm1), 3 * rounds)) if rounds > 0 else []
            for _ in range(rounds):
                val, hole = b.hole(LIST(NUM))
                V = b.call(z, L=Ls.pop())
                q = b.call(mce, L=Ls.pop())
                b.erase(b.call(w, list=cur, init=(Ls.pop(), 0, V, q, hole)))
                cur = val
            return cur
        return d.branch(n, empty, nonempty, c)
    return _recipe(P, name, f"recipe pointer_jump `{name}`", body, [("list", LIST(NUM))], [("o", LIST(NUM))])


RECIPES = ["list_length_and_copy", "list_to_trie", "filter_in_order", "count_where", "take_first", "argmax_first",
           "sort_by", "lookup_many", "reduce_by_key", "select_sorted", "count_where_trie", "argmax_first_trie",
           "frontier_relax", "layered_bfs_count", "pointer_jump"]
