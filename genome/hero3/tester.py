"""HERO-3 property tester: the real executor (HVM2) tests the algebraic properties of a fold's combiner.

Everything is decided by running the fold's OWN nets (@comb, @lift, @step, unit) inside driver nets; Python only builds
inputs and compares results. Tests are batched (one executor run per property) and every driver receives independent
copies of its inputs as data, so the driver itself contains no duplicators.

Properties (all on REACHABLE states = final states of the original walker on many short lists):
  assoc    comb(comb(a,b),c) == comb(a,comb(b,c))
  identity comb(unit,a) == a  and  comb(a,unit) == a
  hom      step(a,x) == comb(a, lift(x))        (the original's sequential step IS the monoid step)
  comm     comb(a,b) == comb(b,a)                (reported; the order-preserving tree fold does not need it)
Decision: ACCEPT iff assoc, identity (both sides) and hom all hold on every test. Test states come from
  * exhaustive-small: all lists of length <= 3 over the fold's small alphabet, all triples of the first states,
  * random: lists of length 0..30 drawn from a wide mixture (small, medium, full 24-bit, edge values).
"""
from __future__ import annotations
import hashlib, itertools, random
from ..executor import run_net
from ..types import encode, decode, DecodeError, list_of, tup
from .folds import Fold, lit
from .nets import all_defs, rope_t
from .programs import build_rope

EXH_STATES = 14          # exhaustive triples over this many enumerated states
RAND_TRIPLES = 3000
RAND_PAIRS = 2000
RAND_HOM = 1500


def _rng(fid, seed):
    return random.Random(int.from_bytes(hashlib.sha256(f"h3tester|{fid}|{seed}".encode()).digest()[:8], "big"))


def _pat(names):
    return names[0] if len(names) == 1 else "(" + names[0] + " " + _pat(names[1:]) + ")"


def _drive(f: Fold, in_ts, out_t, body: str, out_vars, items, timeout=180):
    """Run `body` (redex lines over wires v0..vk) for every item; returns decoded list of out tuples."""
    in_t = tup(*in_ts) if len(in_ts) > 1 else in_ts[0]
    root, defs = encode(items, list_of(in_t), tag="tin")
    vs = [f"v{i}" for i in range(len(in_ts))]
    head = _pat(vs)
    outh = _pat(out_vars)
    drv = f"""@drv = ((?((@drv_nil @drv_cons) (pl out)) pl) out)

@drv_nil = (* (0 *))

@drv_cons = (* (({head} t) (1 ({outh} tl))))
{body}
  & @drv ~ (t tl)
"""
    text = f"@main = r\n  & @drv ~ ({root} r)\n\n" + "\n".join(defs) + "\n\n" + drv + "\n" + all_defs(f)
    r = run_net(text, "run", timeout)
    if not r.ok: raise RuntimeError("driver failed: " + r.error[:300])
    ot = tup(*out_t) if len(out_t) > 1 else out_t[0]
    try: return decode(r.result, list_of(ot))
    except DecodeError as e: raise RuntimeError("driver output: " + str(e))


def enum_ropes(alpha):
    out = [(0,)]
    out += [(1, x) for x in alpha]
    out += [(2, (1, x), (1, y)) for x in alpha for y in alpha]
    for x in alpha:
        for y in alpha:
            for z in alpha:
                out.append((2, (1, x), (2, (1, y), (1, z))))
                out.append((2, (2, (1, x), (1, y)), (1, z)))
    return out


def reachable_states(f: Fold, rng):
    """States that can occur in a tree reduction: unit, lift(x), and comb-closures of lifts (tree folds of ropes of every
    shape, evaluated by the fold's own nets), plus the states of the original sequential walker on longer lists."""
    S = f.state_t
    ropes = enum_ropes(f.enum)
    n_enum = len(ropes)
    ropes += [build_rope([f.gen(rng) for _ in range(rng.randrange(0, 13))], rng, rng.choice(["random", "random", "balanced", "left", "right"])) for _ in range(260)]
    res = _drive(f, [rope_t(f.elem_t)], [S], "  & @tf ~ (v0 s)", ["s"], ropes)
    lists = [[f.gen(rng) for _ in range(rng.randrange(0, 31))] for _ in range(120)]
    res2 = _drive(f, [list_of(f.elem_t)], [S], "  & @sw ~ (v0 (" + f.unit_txt + " s))", ["s"], lists)
    enum_states, seen, pool = [], set(), []
    for i, s in enumerate(list(res) + list(res2)):
        s = tuple(s) if isinstance(s, list) else s
        if s in seen: continue
        seen.add(s); pool.append(s)
        if i < n_enum: enum_states.append(s)
    return enum_states, pool


def _unpack1(res):  # driver outputs with one out var come back as the bare value
    return res


def test_fold(f: Fold, seed: int = 7) -> dict:
    rng = _rng(f.id, seed)
    S = f.state_t
    enum_states, pool = reachable_states(f, rng)
    ex = enum_states[:EXH_STATES]
    triples = [t for t in itertools.product(ex, repeat=3)]
    triples += [tuple(rng.choice(pool) for _ in range(3)) for _ in range(RAND_TRIPLES)]
    # ---- associativity
    items = [(a, b, c, a, b, c) for a, b, c in triples]
    body = ("  & @comb ~ (v0 (v1 ab))\n  & @comb ~ (ab (v2 lhs))\n  & @comb ~ (v4 (v5 bc))\n  & @comb ~ (v3 (bc rhs))")
    res = _drive(f, [S] * 6, [S, S], body, ["lhs", "rhs"], items)
    bad_assoc = [(items[i][:3], r) for i, r in enumerate(res) if r[0] != r[1]]
    # ---- identity
    unit = f.unit
    items = [(a, a) for a in pool]
    body = f"  & @comb ~ ({f.unit_txt} (v0 lhs))\n  & @comb ~ (v1 ({f.unit_txt} rhs))"
    res = _drive(f, [S, S], [S, S], body, ["lhs", "rhs"], items)
    bad_idl = [(items[i][0], r[0]) for i, r in enumerate(res) if r[0] != items[i][0]]
    bad_idr = [(items[i][0], r[1]) for i, r in enumerate(res) if r[1] != items[i][0]]
    # ---- commutativity (reported)
    pairs = [(a, b) for a, b in itertools.product(ex, repeat=2)] + [(rng.choice(pool), rng.choice(pool)) for _ in range(RAND_PAIRS)]
    items = [(a, b, a, b) for a, b in pairs]
    body = "  & @comb ~ (v0 (v1 lhs))\n  & @comb ~ (v3 (v2 rhs))"
    res = _drive(f, [S] * 4, [S, S], body, ["lhs", "rhs"], items)
    bad_comm = [(items[i][:2], r) for i, r in enumerate(res) if r[0] != r[1]]
    # ---- homomorphism: original step == comb(acc, lift x)
    elems = list(f.enum) + [f.gen(rng) for _ in range(RAND_HOM)]
    hom_items = [(rng.choice(pool), x) for x in elems]
    items = [(a, x, a, x) for a, x in hom_items]
    body = "  & @step ~ (v0 (v1 lhs))\n  & @lift ~ (v3 hx)\n  & @comb ~ (v2 (hx rhs))"
    res = _drive(f, [S, f.elem_t, S, f.elem_t], [S, S], body, ["lhs", "rhs"], items)
    bad_hom = [(items[i][:2], r) for i, r in enumerate(res) if r[0] != r[1]]
    out = dict(fold=f.id, seed=seed, states_pool=len(pool), enum_states=len(enum_states),
               n_assoc=len(triples), n_ident=len(pool), n_comm=len(pairs), n_hom=len(items),
               fail_assoc=len(bad_assoc), fail_idl=len(bad_idl), fail_idr=len(bad_idr), fail_comm=len(bad_comm), fail_hom=len(bad_hom),
               commutative=(len(bad_comm) == 0))
    out["accept"] = out["fail_assoc"] == 0 and out["fail_idl"] == 0 and out["fail_idr"] == 0 and out["fail_hom"] == 0
    reasons = [k for k, v in (("assoc", bad_assoc), ("identity_left", bad_idl), ("identity_right", bad_idr), ("hom", bad_hom)) if v]
    out["reject_reasons"] = reasons
    ce = {}
    if bad_assoc: ce["assoc"] = bad_assoc[0]
    if bad_idl: ce["identity_left"] = bad_idl[0]
    if bad_idr: ce["identity_right"] = bad_idr[0]
    if bad_hom: ce["hom"] = bad_hom[0]
    out["counterexamples"] = {k: repr(v)[:300] for k, v in ce.items()}
    return out
