"""Type-directed digest nets.

At scale the printed normal form of an output is too deep for HVM2's recursive readback, and refs left in
untouched subtrees stay unexpanded. So for large cases the harness composes the author's output with a fixed
digest net that walks the whole structure inside the executor and returns two 24-bit hashes. Its own cost is
subtracted from the reported interactions (measured by digesting the reference output alone).

The digest is a fixed harness component (like the input encoder). It is not part of what authors write.
"""
from __future__ import annotations
from .types import U24, List, Tup, Adt, Rec, MASK

MA, MB = 31, 131


def _feed(a, b, x):
    return (a * MA + x + 1) & MASK, (b * MB + x) & MASK


def py_digest(v, t, acc=(0, 0)):
    """Reference implementation of the digest; mirrors gen_digest exactly."""
    a, b = acc
    if isinstance(t, U24):
        return _feed(a, b, v)
    if isinstance(t, Tup):
        for x, et in zip(v, t.elems): a, b = py_digest(x, et, (a, b))
        return a, b
    if isinstance(t, List):
        for x in v:
            a, b = _feed(a, b, 1)
            a, b = py_digest(x, t.elem, (a, b))
        return _feed(a, b, 0)
    if isinstance(t, Adt):
        def go(x, acc):
            idx, fields = x[0], x[1:]
            acc = _feed(*acc, idx)
            for f, ft in zip(fields, t.ctors[idx]):
                acc = go(f, acc) if isinstance(ft, Rec) else py_digest(f, ft, acc)
            return acc
        # iterative on the spine would be nicer; recursion depth = tree depth, fine for our sizes
        import sys; sys.setrecursionlimit(max(sys.getrecursionlimit(), 100000))
        return go(v, (a, b))
    raise TypeError(t)


class _Gen:
    def __init__(self):
        self.defs = {}
        self.n = 0
        self.memo = {}

    def name(self, hint):
        self.n += 1
        return f"__D{self.n}_{hint}"

    def feed_def(self):
        if "feed" in self.memo: return self.memo["feed"]
        nm = "__Dfeed"
        self.defs[nm] = (f"@{nm} = (x ((a b) (a2 b2)))\n  & x ~ {{x1 x2}}\n"
                         f"  & a ~ $([*] $({MA} t1))\n  & t1 ~ $([+] $(x1 t2))\n  & t2 ~ $([+] $(1 a2))\n"
                         f"  & b ~ $([*] $({MB} u1))\n  & u1 ~ $([+] $(x2 b2))")
        self.memo["feed"] = nm
        return nm

    def for_type(self, t, whole=None, whole_name=None):
        key = (t, id(whole) if whole is not None else None)
        if isinstance(t, U24): return self.feed_def()
        if isinstance(t, Tup):
            nm = self.name("tup")
            subs = [self.for_type(et) for et in t.elems]
            vs = [f"v{i}" for i in range(len(subs))]
            pat = vs[-1]
            for v in reversed(vs[:-1]): pat = f"({v} {pat})"
            lines = [f"@{nm} = ({pat} (acc0 out))"]
            for i, sd in enumerate(subs):
                lines.append(f"  & @{sd} ~ ({vs[i]} (acc{i} acc{i+1}))" if i < len(subs) - 1 else f"  & @{sd} ~ ({vs[i]} (acc{i} out))")
            self.defs[nm] = "\n".join(lines)
            return nm
        if isinstance(t, List):
            nm = self.name("list"); elem = self.for_type(t.elem); feed = self.feed_def()
            self.defs[nm] = (f"@{nm} = ((?((@{nm}_nil @{nm}_cons) (pl (acc out))) pl) (acc out))")
            self.defs[nm + "_nil"] = f"@{nm}_nil = (* (acc out))\n  & @{feed} ~ (0 (acc out))"
            self.defs[nm + "_cons"] = (f"@{nm}_cons = (* ((h tl) (acc out)))\n  & @{feed} ~ (1 (acc a1))\n"
                                       f"  & @{elem} ~ (h (a1 a2))\n  & @{nm} ~ (tl (a2 out))")
            return nm
        if isinstance(t, Adt):
            nm = self.name(t.name); feed = self.feed_def()
            # per-constructor bodies
            bodies = []
            for i, ftypes in enumerate(t.ctors):
                bn = f"{nm}_c{i}"; bodies.append(bn)
                fvs = [f"f{j}" for j in range(len(ftypes))]
                if not ftypes: pat = "*"
                else:
                    pat = fvs[-1]
                    for v in reversed(fvs[:-1]): pat = f"({v} {pat})"
                lines = [f"@{bn} = ({pat} (acc0 out))", f"  & @{feed} ~ ({i} (acc0 s0))"]
                for j, ft in enumerate(ftypes):
                    sub = nm if isinstance(ft, Rec) else self.for_type(ft)
                    src = f"s{j}"; dst = "out" if j == len(ftypes) - 1 else f"s{j+1}"
                    lines.append(f"  & @{sub} ~ ({fvs[j]} ({src} {dst}))")
                if not ftypes: lines[-1:] = [f"  & @{feed} ~ ({i} (acc0 out))"]
                self.defs[bn] = "\n".join(lines)
            # dispatch on the tag: chain of switches, ctx = (payload (acc out))
            self.defs[nm] = f"@{nm} = ((?((@{nm}_d0) (pl (acc out))) pl) (acc out))"
            self._dispatch(nm, bodies)
            return nm
        raise TypeError(t)

    def _dispatch(self, nm, bodies):
        k = len(bodies)
        # switch case list: (zero_branch, succ_branch); succ receives (n-1, ctx)
        # d_i handles tag i given ctx; d_i is entered with the remaining count in a nested switch
        def cases(i):
            if i == k - 1: return f"@{bodies[i]}", None
            return f"@{bodies[i]}", f"@{nm}_s{i}"
        z, s = cases(0)
        if k == 1:
            self.defs[nm] = f"@{nm} = ((?((@{bodies[0]} @{nm}_bad) (pl (acc out))) pl) (acc out))"
            self.defs[nm + "_bad"] = f"@{nm}_bad = (* (* (acc out)))\n  & acc ~ *"
            return
        self.defs[nm] = f"@{nm} = ((?((@{bodies[0]} @{nm}_s0) (pl (acc out))) pl) (acc out))"
        # succ branch i: receives (m, ctx) where m = tag-1-i; the *previous* zero branch was erased
        for i in range(k - 1):
            if i == k - 2:
                # remaining tag is 0 -> last ctor
                self.defs[f"{nm}_s{i}"] = (f"@{nm}_s{i} = (* (pl (acc out)))\n  & @{bodies[k-1]} ~ (pl (acc out))")
            else:
                self.defs[f"{nm}_s{i}"] = (f"@{nm}_s{i} = (m (pl (acc out)))\n"
                                            f"  & m ~ ?((@{bodies[i+1]} @{nm}_s{i+1}) (pl (acc out)))")


def gen_digest(t):
    """-> (book_text, root_def_name). The root def is (value ((a b) out)); out is the pair (a b)."""
    g = _Gen()
    root = g.for_type(t)
    return "\n\n".join(g.defs.values()) + "\n", root
