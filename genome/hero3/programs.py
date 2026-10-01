"""Program objects (contracts) for HERO-3: the list program of each fold and the tree-input program of its rewrite.

list program  : the corpus program when the fold IS a corpus contract (t1/t2), otherwise a new Program (not registered).
tree program  : input is a rope (Nil | One(x) | Cat(l, r)); reference = the list reference on the in-order leaves
                (mode "py"), or the ORIGINAL NET run on the in-order leaves (mode "net": differential against the original).
"""
from __future__ import annotations
import random
from functools import lru_cache
from ..corpus import Program, load_all
from ..types import list_of, decode, DecodeError
from ..executor import run_net
from ..verify import assemble
from .folds import Fold
from .nets import rope_t, seq_net

EDGE_LISTS_DEFAULT = [[], [0], [1, 1, 1]]


def list_program(f: Fold) -> Program:
    if f.corpus:
        return load_all()[f.corpus]
    edges = [list(e) for e in (f.edges or [[], [0], [1, 1, 1]])]
    return Program(id="h3_" + f.id, tier="H3", desc=f.desc, inp=list_of(f.elem_t), out=f.out_t,
                   ref=lambda xs: f.ref(list(xs)), gen=lambda rng, n: [f.gen(rng) for _ in range(n)],
                   sizes=list(range(0, 17)), test_sizes=[128, 256], edges=edges, pre=None)


def flatten(t):
    out, stack = [], [t]
    while stack:
        x = stack.pop()
        if x[0] == 0: continue
        if x[0] == 1: out.append(x[1])
        else: stack.append(x[2]); stack.append(x[1])
    return out


def build_rope(items, rng=None, shape="balanced"):
    n = len(items)
    if n == 0: return (0,)
    if n == 1: return (1, items[0])
    if shape == "balanced": k = n // 2
    elif shape == "left": k = n - 1
    elif shape == "right": k = 1
    else:  # random
        k = rng.randrange(1, n) if rng.random() > 0.15 else rng.choice([0, n])
        if k in (0, n):  # an empty subtree next to a non-empty one; still terminate
            sub = build_rope(items, rng, "balanced" if rng.random() < .5 else "left")
            return (2, (0,), sub) if k == 0 else (2, sub, (0,))
    return (2, build_rope(items[:k], rng, shape), build_rope(items[k:], rng, shape))


SHAPES = ["balanced", "random", "random", "left", "right"]


def tree_program(f: Fold, mode: str = "py", orig_net: str | None = None) -> Program:
    lp = list_program(f)
    rt = rope_t(f.elem_t)
    if mode == "py":
        ref = lambda t: lp.ref(flatten(t))
    else:
        assert orig_net
        def ref(t):
            xs = flatten(t)
            r = run_net(assemble(lp, orig_net, xs), "run", 60)
            if not r.ok: raise RuntimeError("original net failed: " + r.error)
            try: return decode(r.result, lp.out)
            except DecodeError as e: raise RuntimeError("original net output: " + str(e))

    def gen(rng, n):
        items = lp.gen(rng, n)
        return build_rope(items, rng, rng.choice(SHAPES))

    edges = [build_rope(e, random.Random(1), "balanced") for e in lp.edges] + \
            [(0,), (2, (0,), (0,))]
    for e in lp.edges:
        if len(e) >= 3:
            edges.append(build_rope(e, None, "left")); edges.append(build_rope(e, None, "right"))
    return Program(id=("h3t_" if mode == "py" else "h3n_") + f.id, tier="H3", desc="tree input: " + f.desc, inp=rt, out=lp.out,
                   ref=ref, gen=gen, sizes=list(range(0, 17)), test_sizes=[128, 256], edges=edges, pre=None)
