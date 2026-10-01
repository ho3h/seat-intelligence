"""prove: decide whether two HVM2 books, entered at @prog = (input output), have the same normal form with the interface left open.
Tiers (docs/HERO-2.md s.1.2): S, S~a, U, U~a, D. Returns a Verdict; `equal=True` means canonical forms coincide at `tier`."""
from __future__ import annotations
from dataclasses import dataclass, field
from . import inet as I

TIERS = [
    # name, unfold, use_safe, dlaws
    ("S", False, True, False),
    ("S~a", False, False, False),
    ("U", True, True, False),
    ("U~a", True, False, False),
    ("D", True, False, True),
]


@dataclass
class Verdict:
    equal: bool
    tier: str | None = None
    reason: str = ""
    stats: dict = field(default_factory=dict)


def call_net(prefix: str, entry: str = "prog") -> I.Net:
    net = I.Net()
    r = net.node("R", prefix + entry); c = net.node("C")
    fx = net.node("F", "x"); fr = net.node("F", "r")
    net.link(3 * c + 1, 3 * fx); net.link(3 * c + 2, 3 * fr); net.link(3 * r, 3 * c)
    return net


class Prover:
    def __init__(self, textA: str, textB: str, fuel_def=60000, fuel_top=400000):
        self.reg = I.Registry().add_book(textA, "A:").add_book(textB, "B:").finalize()
        self.fuel_def, self.fuel_top = fuel_def, fuel_top

    def _reduce(self, net, eng, dl, fuel):
        ok = eng.run(net, fuel)
        while ok and dl:
            if not I.dlaws(net): break
            # dlaws may create contacts: re-queue every principal pair
            for i, k in enumerate(net.kind):
                if k is None or k == "F": continue
                q = net.p[i][0]
                if q >= 0 and q % 3 == 0 and q // 3 > i and net.kind[q // 3] not in (None, "F"): net.work.append((i, q // 3))
            ok = eng.run(net, fuel)
        return ok

    def normalize(self, unfold, use_safe, dl):
        eng = I.Engine(self.reg, unfold=unfold)
        nf = {}
        incomplete = 0
        for name, d in self.reg.defs.items():
            net = d.tpl.copy()
            ok = self._reduce(net, eng, dl, self.fuel_def)
            if not ok:                                   # fuel: fall back to the raw instance (always a valid state)
                net = d.tpl.copy(); incomplete += 1
            nf[name] = net
        # coinductive classes over the union of both books
        names = list(self.reg.defs)
        cls = {n: (int(self.reg.defs[n].safe) if use_safe else 0) for n in names}
        ncls = len(set(cls.values()))
        for _ in range(64):
            refcls = lambda nm, cls=cls: cls.get(nm, ("undef", nm))
            keys = {n: (cls[n], I.canon(nf[n], refcls, dl)) for n in names}
            ids = {}
            new = {n: ids.setdefault(keys[n], len(ids)) for n in names}
            stable = len(ids) == ncls
            cls, ncls = new, len(ids)
            if stable: break
        return eng, nf, cls, incomplete

    def compare(self, tier) -> Verdict:
        name, unfold, use_safe, dl = tier
        eng, nf, cls, incomplete = self.normalize(unfold, use_safe, dl)
        refcls = lambda nm: cls.get(nm, ("undef", nm))
        nets = {}
        for side in ("A:", "B:"):
            n = call_net(side)
            ok = self._reduce(n, eng, dl, self.fuel_top)
            nets[side] = (n, ok)
        (na, oka), (nb, okb) = nets["A:"], nets["B:"]
        st = {"itrsA": na.itrs, "itrsB": nb.itrs, "residA": dict(I.ncount(na)), "residB": dict(I.ncount(nb)),
              "defs": len(self.reg.defs), "classes": len(set(cls.values())), "def_fuel_fallbacks": incomplete}
        bad = (na.flags | nb.flags) & {"fuel", "abort", "crash-or-unsupported", "undefined-ref"}
        if bad or not (oka and okb) or I.stuck_redexes(na) or I.stuck_redexes(nb):
            return Verdict(False, None, f"not normalized cleanly: flags={sorted(bad)} stuck={len(I.stuck_redexes(na))}/{len(I.stuck_redexes(nb))}", st)
        ca, cb = I.canon(na, refcls, dl), I.canon(nb, refcls, dl)
        if ca == cb:
            import hashlib
            st["code_sha256"] = hashlib.sha256(repr(ca).encode()).hexdigest()[:16]
            return Verdict(True, name, "canonical forms coincide", st)
        return Verdict(False, None, f"residual nets differ (A {sum(st['residA'].values())} nodes, B {sum(st['residB'].values())} nodes)", st)

    def prove(self, tiers=TIERS) -> Verdict:
        last = None
        for t in tiers:
            v = self.compare(t)
            if v.equal: return v
            last = v
        return last


def prove(textA: str, textB: str, **kw) -> Verdict:
    return Prover(textA, textB, **kw).prove()
