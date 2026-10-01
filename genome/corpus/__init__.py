"""The corpus: programs as contracts. Each has a reference, an input generator and test sizes."""
from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import Callable

REGISTRY: dict[str, "Program"] = {}


@dataclass
class Program:
    id: str
    tier: str
    desc: str
    inp: object            # interface type of the input
    out: object            # interface type of the output
    ref: Callable          # reference implementation: input -> output
    gen: Callable          # gen(rng, n) -> input value of size parameter n
    sizes: list            # size parameters used while authoring
    test_sizes: list       # size parameters used only by the verifier (up to 16x)
    edges: list = field(default_factory=list)  # hand-picked inputs (always run)
    pre: object = None     # optional precondition: input -> bool (used to filter the exhaustive sweep)


def program(id, tier, desc, inp, out, ref, gen, sizes, test_sizes=None, edges=None, pre=None):
    assert id not in REGISTRY, id
    if test_sizes is None:
        m = max(sizes)
        test_sizes = sorted({max(1, m * 8), m * 16})
    REGISTRY[id] = Program(id, tier, desc, inp, out, ref, gen, list(sizes), list(test_sizes), edges or [], pre)
    return REGISTRY[id]


def load_all():
    import importlib, pkgutil
    for m in ('t1', 't2', 't3_a', 't3_b', 't4_a', 't4_b', 't5_a', 't5_b'):
        try: importlib.import_module(f'{__name__}.{m}')
        except ModuleNotFoundError as e:
            if e.name != f'{__name__}.{m}': raise
    return REGISTRY
