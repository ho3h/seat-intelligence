"""inet: an exact port-graph model of the HVM2 (v2.0.22) rewrite rules, with OPEN wires, plus canonical forms and a
coinductive comparer of definitions. HERO-2 (swing 29). Nothing here is learned.

WHAT IS MODELLED (physics/hvm2/src/hvm.rs, `get_rule`, `interact_*`):
  nodes R (ref), E (eraser), N (number word), C (con), D (dup), O (opr), S (swi), F (a free/open wire end: never reduces).
  VOID  : R/E/N against R/E/N vanish
  CALL  : R against C/O/S expands the definition; R against D copies the reference if the definition has no DUP node of its
          own (`def.safe`), otherwise the real runtime aborts ("attempt to clone a non-affine global reference"): here that redex
          is left in place and the net is flagged `abort`.
  ERAS  : E against C/D/O/S, and N against C/D: the node spreads into both aux ports
  ANNI  : C~C, D~D, O~O, S~S: link aux to aux (this IS the unlabelled-DUP rule: two DUPs always annihilate)
  COMM  : every other pair of {C,D,O,S}: the 4-node crossed square
  OPER  : N~O ; SWIT : N~S (same code paths as hvm.rs, numbers are 29-bit words: 5 type bits + 24 value bits)
Redexes whose principal partner is an open wire (F) or an aux port never fire: they are the residual (stuck) net.
By strong confluence of the rule system the residual net is independent of the order of reductions.
"""
from __future__ import annotations
import sys
from genome import netast

sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))

TAG = {"R": 1, "E": 2, "N": 3, "C": 4, "D": 5, "O": 6, "S": 7}
KIND_OF = {"con": "C", "dup": "D", "opr": "O", "swi": "S"}
BIN = "CDOS"
M24 = (1 << 24) - 1
M29 = (1 << 29) - 1

# ------------------------------------------------------------------------------------------------ numbers (hvm.rs Numb)
TY_SYM, TY_U24, TY_I24, TY_F24 = 0, 1, 2, 3
OPS = {"+": 4, "-": 5, ":-": 6, "*": 7, "/": 8, ":/": 9, "%": 10, ":%": 11, "=": 12, "!": 13, "<": 14, ">": 15, "&": 16,
       "|": 17, "^": 18, "<<": 19, ":<<": 20, ">>": 21, ":>>": 22}
OP_ORDER = sorted(OPS, key=lambda s: -len(s))


def u24(v): return ((v & M24) << 5) | TY_U24


def parse_numb(text: str):
    """text as netast tokenises it -> int word, or ('x', text) for a form we do not evaluate (i24, f24, casts)."""
    t = text.strip()
    if t.startswith("["):
        inner = t[1:t.index("]")]
        tail = t[t.index("]") + 1:]
        if inner in ("u24", "i24", "f24"): return ("x", t)
        for op in OP_ORDER:
            if inner.startswith(op):
                rest = inner[len(op):].strip() or tail.strip()
                if not rest: return OPS[op] << 5                                # a bare symbol: typ SYM, sym = opcode
                lit = parse_numb(rest)
                if isinstance(lit, tuple): return ("x", t)
                return ((lit & ~0x1F) | OPS[op]) & M29                            # partial(op, lit)
        return ("x", t)
    if "." in t or "inf" in t or "NaN" in t or t[0] in "+-": return ("x", t)
    return u24(int(t, 0) if t.lower().startswith("0x") else int(t))


def show_numb(w) -> str:
    if isinstance(w, tuple): return w[1]
    typ = w & 31
    if typ == TY_U24: return str(w >> 5)
    if typ == TY_SYM:
        for s, o in OPS.items():
            if (w >> 5) == o: return f"[{s}]"
        return f"[sym{w >> 5}]"
    for s, o in OPS.items():
        if typ == o: return f"[{s}{w >> 5}]"
    return f"<{w}>"


def operate(a, b):
    """hvm.rs Numb::operate for U24 data and symbolic/partial operators. Returns a word, or None when the operation is
    outside what we model (i24/f24/casts) or would crash the runtime (division/remainder by zero)."""
    if isinstance(a, tuple) or isinstance(b, tuple): return None
    at, bt = a & 31, b & 31
    if at == TY_SYM and bt == TY_SYM: return u24(0)
    def is_cast(x): return (x & 31) == TY_SYM and TY_U24 <= (x >> 5) <= TY_F24
    def is_num(x): return TY_U24 <= (x & 31) <= TY_F24
    if is_cast(a) and is_num(b): return b if ((a >> 5) == TY_U24 and (b & 31) == TY_U24) else None
    if is_cast(b) and is_num(a): return a if ((b >> 5) == TY_U24 and (a & 31) == TY_U24) else None
    if at == TY_SYM and bt != TY_SYM: return ((b & ~0x1F) | (a >> 5)) & M29
    if at != TY_SYM and bt == TY_SYM: return ((a & ~0x1F) | (b >> 5)) & M29
    if at >= 4 and bt >= 4: return u24(0)
    if at < 4 and bt < 4: return u24(0)
    if at >= 4: op, x, ty, y = at, a, bt, b
    else: op, x, ty, y = bt, b, at, a
    if ty != TY_U24: return None if ty in (TY_I24, TY_F24) else u24(0)
    av, bv = (x >> 5) & M24, (y >> 5) & M24
    if op in (8, 10) and bv == 0: return None
    if op in (9, 11) and av == 0: return None
    r = {4: lambda: av + bv, 5: lambda: av - bv, 6: lambda: bv - av, 7: lambda: av * bv,
         8: lambda: av // bv if bv else 0, 9: lambda: bv // av if av else 0, 10: lambda: av % bv if bv else 0,
         11: lambda: bv % av if av else 0, 12: lambda: int(av == bv), 13: lambda: int(av != bv), 14: lambda: int(av < bv),
         15: lambda: int(av > bv), 16: lambda: av & bv, 17: lambda: av | bv, 18: lambda: av ^ bv,
         19: lambda: av << (bv & 31), 20: lambda: bv << (av & 31), 21: lambda: av >> (bv & 31), 22: lambda: bv >> (av & 31)}[op]()
    return u24(r & 0xFFFFFFFF)


# ------------------------------------------------------------------------------------------------ the graph
class Net:
    """Port graph. Port id = 3*node + slot (slot 0 principal, 1/2 aux). kind None = dead."""
    __slots__ = ("kind", "val", "p", "work", "itrs", "flags", "root_f")

    def __init__(self):
        self.kind: list = []; self.val: list = []; self.p: list = []; self.work: list = []
        self.itrs = 0; self.flags: set = set(); self.root_f = -1

    def node(self, k, v=None) -> int:
        i = len(self.kind); self.kind.append(k); self.val.append(v); self.p.append([-1, -1, -1]); return i

    def link(self, a: int, b: int):
        pa, pb = self.p[a // 3], self.p[b // 3]
        pa[a % 3] = b; pb[b % 3] = a
        if a % 3 == 0 and b % 3 == 0:
            ka, kb = self.kind[a // 3], self.kind[b // 3]
            if ka != "F" and kb != "F": self.work.append((a // 3, b // 3))

    def alive(self): return [i for i, k in enumerate(self.kind) if k is not None]

    def copy(self) -> "Net":
        n = Net(); n.kind = list(self.kind); n.val = list(self.val); n.p = [list(x) for x in self.p]
        n.work = list(self.work); n.itrs = self.itrs; n.flags = set(self.flags); n.root_f = self.root_f
        return n


def build_trees(root, reds, prefix="", root_name="$root", free_ok=True) -> Net:
    """netast trees -> Net. Vars occurring twice become wires; a var occurring once becomes an F (open wire) node named after it;
    the root tree hangs off an F node called $root (when root is not None)."""
    net = Net()
    occ: dict = {}
    alias: list = []
    acount: dict = {}

    def build(t):
        k = t[0]
        if k == "var": return ("v", t[1])
        if k == "era": return ("p", 3 * net.node("E"))
        if k == "num": return ("p", 3 * net.node("N", parse_numb(t[1])))
        if k == "ref": return ("p", 3 * net.node("R", prefix + t[1]))
        i = net.node(KIND_OF[k])
        for s, ch in ((1, t[1]), (2, t[2])): attach(3 * i + s, build(ch))
        return ("p", 3 * i)

    def attach(port, r):
        if r[0] == "p": net.link(port, r[1])
        else: occ.setdefault(r[1], []).append(port)

    if root is not None:
        rf = net.node("F", root_name); net.root_f = rf
        attach(3 * rf, build(root))
    for par, a, b in reds:
        ra, rb = build(a), build(b)
        if ra[0] == "p" and rb[0] == "p": net.link(ra[1], rb[1])
        elif ra[0] == "p": occ.setdefault(rb[1], []).append(ra[1])
        elif rb[0] == "p": occ.setdefault(ra[1], []).append(rb[1])
        else:
            alias.append((ra[1], rb[1]))
            acount[ra[1]] = acount.get(ra[1], 0) + 1; acount[rb[1]] = acount.get(rb[1], 0) + 1
    uf: dict = {}

    def find(x):
        while uf.get(x, x) != x:
            uf[x] = uf.get(uf[x], uf[x]); x = uf[x]
        return x
    for v, w in alias:
        rv, rw = find(v), find(w)
        if rv != rw: uf[rv] = rw
    names = set(occ) | set(acount)
    for v in sorted(names):
        cnt = len(occ.get(v, [])) + acount.get(v, 0)
        if cnt == 1:
            f = net.node("F", v); occ.setdefault(v, []).append(3 * f)
        elif cnt != 2:
            raise ValueError(f"wire {v!r} occurs {cnt} times")
    classes: dict = {}
    for v in names: classes.setdefault(find(v), []).extend(occ.get(v, []))
    for ends in classes.values():
        if len(ends) == 2: net.link(ends[0], ends[1])
        elif len(ends) != 0: raise ValueError("bad wire class")
    return net


# ------------------------------------------------------------------------------------------------ definitions
class Def:
    __slots__ = ("name", "tpl", "safe", "refs", "has_dup", "rec", "deep_free", "nf", "nf_ok", "abort")

    def __init__(self, name, tpl, safe, refs, has_dup):
        self.name, self.tpl, self.safe, self.refs, self.has_dup = name, tpl, safe, refs, has_dup
        self.rec = False; self.deep_free = False; self.nf = None; self.nf_ok = False; self.abort = False


def _refs_and_dup(root, reds):
    refs, dup = set(), [False]

    def go(t):
        k = t[0]
        if k == "ref": refs.add(t[1])
        elif k == "dup": dup[0] = True; go(t[1]); go(t[2])
        elif k in ("con", "opr", "swi"): go(t[1]); go(t[2])
    go(root)
    for _, a, b in reds: go(a); go(b)
    return refs, dup[0]


class Registry:
    """Definitions from several books under distinct prefixes."""

    def __init__(self):
        self.defs: dict[str, Def] = {}

    def add_book(self, text: str, prefix: str):
        defs, order = netast.parse_book(text)
        for n in order:
            root, reds = defs[n]
            refs, dup = _refs_and_dup(root, reds)
            tpl = build_trees(root, reds, prefix)
            self.defs[prefix + n] = Def(prefix + n, tpl, not dup, {prefix + r for r in refs}, dup)
        return self

    def finalize(self):
        d = self.defs
        # reachability
        reach = {}
        for n in d:
            seen, stack = set(), list(d[n].refs)
            while stack:
                m = stack.pop()
                if m in seen or m not in d: continue
                seen.add(m); stack.extend(d[m].refs)
            reach[n] = seen
        for n in d:
            d[n].rec = n in reach[n]
            d[n].deep_free = (not d[n].has_dup) and all(not d[m].has_dup for m in reach[n])
        return self


# ------------------------------------------------------------------------------------------------ reduction
def instantiate(net: Net, tpl: Net) -> int:
    """Copy tpl into net. Returns the (live) port that the template's root was attached to; the caller must link it."""
    base = len(net.kind)
    net.kind.extend(tpl.kind); net.val.extend(tpl.val)
    off = 3 * base
    for pp in tpl.p: net.p.append([q + off if q >= 0 else -1 for q in pp])
    for a, b in tpl.work: net.work.append((a + base, b + base))
    rf = tpl.root_f + base
    peer = net.p[rf][0]
    net.kind[rf] = None
    return peer


class Splice:
    """Contract wires through removed ports (handles self-loops and aux-aux wires between the removed nodes)."""

    def __init__(self, net: Net, removed_nodes):
        self.net = net
        self.S = {}
        for n in removed_nodes:
            for s in (1, 2):
                if net.kind[n] in BIN or net.kind[n] is None: self.S[3 * n + s] = net.p[n][s]
        self.nl: dict = {}

    def pair(self, s, t):
        """removed port s is now connected to t (a live port, or another removed port)."""
        self.nl[s] = t
        if t in self.S: self.nl[t] = s

    def finish(self):
        net, S, nl = self.net, self.S, self.nl
        done = set()

        def walk(start_type, s):
            typ = start_type
            seen = set()
            while True:
                if (s, typ) in seen: return None
                seen.add((s, typ))
                t = nl.get(s, -1) if typ == "existing" else S[s]
                nt = "new" if typ == "existing" else "existing"
                if t < 0: return None
                if t not in S: return t
                s, typ = t, nt
        # starts: live ports whose existing peer is a removed port  (arrive via existing edge)
        for s, q in S.items():
            if q >= 0 and q not in S:                         # live port q wired to removed port s
                if q in done: continue
                t = walk("existing", s)
                if t is not None:
                    done.add(q); done.add(t); net.link(q, t)
        # starts: live new ports whose new-link partner is a removed port (arrive via new edge)
        for s, t in list(nl.items()):
            if s in S and t not in S and t not in done:
                r = walk("new", s)
                if r is not None:
                    done.add(t); done.add(r); net.link(t, r)


class Engine:
    def __init__(self, reg: Registry, unfold=False, fuel=400000, rng=None):
        self.reg = reg; self.unfold = unfold; self.fuel = fuel; self.rng = rng

    # -- one interaction on the principal pair (a, b)
    def step(self, net: Net, a: int, b: int) -> bool:
        k = net.kind
        if k[a] is None or k[b] is None or net.p[a][0] != 3 * b: return False
        ka, kb = k[a], k[b]
        if TAG[ka] > TAG[kb]: a, b, ka, kb = b, a, kb, ka
        p = net.p
        if ka in "REN" and kb in "REN":                                             # VOID
            k[a] = None; k[b] = None; net.itrs += 1; return True
        if ka == "R":
            d = self.reg.defs.get(net.val[a])
            if d is None: net.flags.add("undefined-ref"); return False
            if kb == "D":
                if d.safe:                                                          # copy the reference into both aux ports
                    self._spread(net, a, b, lambda: net.node("R", net.val[a])); return True
                net.flags.add("abort"); return False
            root_peer = instantiate(net, d.tpl)
            k[a] = None
            net.link(root_peer, 3 * b)
            net.itrs += 1
            return True
        if ka in "EN" and kb in BIN and (ka == "E" or kb in "CD"):                  # ERAS
            self._spread(net, a, b, (lambda: net.node("E")) if ka == "E" else (lambda: net.node("N", net.val[a]))); return True
        if ka == kb and ka in BIN:                                                  # ANNI
            sp = Splice(net, (a, b))
            sp.pair(3 * a + 1, 3 * b + 1); sp.pair(3 * a + 2, 3 * b + 2)
            k[a] = None; k[b] = None
            sp.finish(); net.itrs += 1; return True
        if ka in BIN and kb in BIN:                                                 # COMM
            sp = Splice(net, (a, b))
            n0, n1 = net.node(kb), net.node(kb)
            n2, n3 = net.node(ka), net.node(ka)
            k[a] = None; k[b] = None
            net.link(3 * n0 + 1, 3 * n2 + 1); net.link(3 * n0 + 2, 3 * n3 + 1)
            net.link(3 * n1 + 1, 3 * n2 + 2); net.link(3 * n1 + 2, 3 * n3 + 2)
            sp.pair(3 * a + 1, 3 * n0); sp.pair(3 * a + 2, 3 * n1); sp.pair(3 * b + 1, 3 * n2); sp.pair(3 * b + 2, 3 * n3)
            sp.finish(); net.itrs += 1; return True
        if ka == "N" and kb == "O":                                                 # OPER
            w1 = p[b][1]
            if w1 >= 0 and w1 % 3 == 0 and k[w1 // 3] == "N":
                r = operate(net.val[a], net.val[w1 // 3])
                if r is None: net.flags.add("crash-or-unsupported"); return False
                sp = Splice(net, (b,)); nn = net.node("N", r)
                sp.S.pop(3 * b + 1, None)                                           # aux1 held the operand number: consumed
                k[a] = None; k[w1 // 3] = None; k[b] = None
                sp.pair(3 * b + 2, 3 * nn)
                sp.finish(); net.itrs += 1; return True
            sp = Splice(net, (b,)); no = net.node("O"); nn = net.node("N", net.val[a])
            k[a] = None; k[b] = None
            net.link(3 * no + 1, 3 * nn); sp.pair(3 * b + 2, 3 * no + 2); sp.pair(3 * b + 1, 3 * no)
            sp.finish(); net.itrs += 1; return True
        if ka == "N" and kb == "S":                                                 # SWIT
            av = (net.val[a] >> 5) & M24 if not isinstance(net.val[a], tuple) else None
            if av is None: net.flags.add("crash-or-unsupported"); return False
            sp = Splice(net, (b,)); k[a] = None; k[b] = None
            c0 = net.node("C"); e = net.node("E")
            if av == 0:
                net.link(3 * c0 + 2, 3 * e)
                sp.pair(3 * b + 2, 3 * c0 + 1); sp.pair(3 * b + 1, 3 * c0)
            else:
                c1 = net.node("C"); nn = net.node("N", u24(av - 1))
                net.link(3 * c0 + 1, 3 * e); net.link(3 * c0 + 2, 3 * c1); net.link(3 * c1 + 1, 3 * nn)
                sp.pair(3 * b + 2, 3 * c1 + 2); sp.pair(3 * b + 1, 3 * c0)
            sp.finish(); net.itrs += 1; return True
        net.flags.add(f"no-rule-{ka}{kb}")
        return False

    def _spread(self, net: Net, a: int, b: int, mk):
        """a (nullary) against b: b disappears, a is copied to both aux ports (used for ERAS and REF copy)."""
        sp = Splice(net, (b,))
        n1, n2 = mk(), mk()
        net.kind[a] = None; net.kind[b] = None
        sp.pair(3 * b + 1, 3 * n1); sp.pair(3 * b + 2, 3 * n2)
        sp.finish(); net.itrs += 1

    def run(self, net: Net, fuel=None) -> bool:
        """Reduce to normal form (order-independent by strong confluence). Returns False when fuel runs out.
        Redexes that cannot fire (runtime abort, crash, unsupported number form) stay in the net; see stuck_redexes()."""
        fuel = self.fuel if fuel is None else fuel
        start = net.itrs
        while True:
            while net.work:
                if self.rng is not None and len(net.work) > 1:
                    j = self.rng.randrange(len(net.work)); net.work[j], net.work[-1] = net.work[-1], net.work[j]
                a, b = net.work.pop()
                self.step(net, a, b)
                if net.itrs - start > fuel:
                    net.flags.add("fuel"); return False
            if self.unfold and self._unfold(net): continue
            break
        return True

    def _unfold(self, net: Net) -> bool:
        """Mode U: expand references sitting in aux positions or on open wires, when their definition is finite (non-recursive)
        and DUP-free all the way down (so copying the reference and copying its body agree)."""
        changed = False
        for i in range(len(net.kind)):
            if net.kind[i] != "R": continue
            q = net.p[i][0]
            if q < 0: continue
            qn = q // 3
            if q % 3 == 0 and net.kind[qn] not in (None, "F"): continue           # a contact: the normal rules handle it
            d = self.reg.defs.get(net.val[i])
            if d is None or d.rec or not d.deep_free: continue
            root_peer = instantiate(net, d.tpl)
            net.kind[i] = None
            net.link(root_peer, q)
            changed = True
        return changed


# ------------------------------------------------------------------------------------------------ canonical form
def dlaws(net: Net) -> bool:
    """Label-oblivious DUP laws (mode D): a DUP with an eraser on one aux port is a wire; with two erasers, an eraser.
    Sound only when the values reaching the DUP are DUP-free data (a DUP meeting a DUP would not be a copy). Returns changed."""
    changed = False
    for i in range(len(net.kind)):
        if net.kind[i] != "D": continue
        pp = net.p[i]
        er = [s for s in (1, 2) if pp[s] >= 0 and pp[s] % 3 == 0 and net.kind[pp[s] // 3] == "E"]
        if not er: continue
        q0 = pp[0]
        if len(er) == 2:
            e1, e2 = pp[1] // 3, pp[2] // 3
            net.kind[i] = None; net.kind[e1] = None; net.kind[e2] = None
            ne = net.node("E"); net.link(q0, 3 * ne) if q0 >= 0 else None
        else:
            s = er[0]; other = pp[3 - s]
            e = pp[s] // 3
            net.kind[i] = None; net.kind[e] = None
            if other == 3 * i + s: continue
            net.link(q0, other)
        changed = True
    return changed


def _label(net, i, refcls, dfan=False):
    k = net.kind[i]
    if k == "R": return ("R", refcls(net.val[i]))
    if k == "N": return ("N", net.val[i])
    if k == "F": return ("F", net.val[i])
    return (k,)


def canon(net: Net, refcls, dfan=False):
    """Canonical code of a net up to renaming of nodes, with F nodes (open wires) fixed by name and REF nodes labelled by
    refcls(name). Two nets have the same code iff they are isomorphic (with these labels). With dfan=True, chains of DUP nodes
    (aux -> principal) are treated as one unordered fan-out (label-oblivious mode)."""
    if dfan: net = _fanify(net, refcls)
    live = [i for i, k in enumerate(net.kind) if k is not None]
    p, kind = net.p, net.kind
    seen = {}
    comps = []

    def encode(start):
        num = {start: 0}; order = [start]; qi = 0; code = []
        while qi < len(order):
            n = order[qi]; qi += 1
            ent = [_label(net, n, refcls)]
            for s in _slots(net, n):
                q = p[n][s]
                if q < 0: ent.append(None); continue
                m = q // 3
                if m not in num:
                    num[m] = len(order); order.append(m)
                ent.append((num[m], q % 3))
            code.append(tuple(ent))
        return tuple(code), order

    anchored = sorted((net.val[i], i) for i in live if kind[i] == "F")
    parts = []
    for name, i in anchored:
        if i in seen: continue
        code, order = encode(i)
        for n in order: seen[n] = 1
        parts.append(code)
    rest = [i for i in live if i not in seen]
    unanch = []
    while rest:
        i0 = rest[0]
        # component of i0
        comp = [i0]; cs = {i0}; qi = 0
        while qi < len(comp):
            n = comp[qi]; qi += 1
            for q in p[n]:
                if q >= 0 and q // 3 not in cs and kind[q // 3] is not None: cs.add(q // 3); comp.append(q // 3)
        best = None
        cand = comp if len(comp) <= 64 else sorted(comp, key=lambda n: (_label(net, n, refcls), n))[:16]
        for s in cand:
            code, order = encode(s)
            if best is None or code < best: best = code
        unanch.append(best)
        for n in comp: seen[n] = 1
        rest = [n for n in rest if n not in cs]
    return (tuple(parts), tuple(sorted(unanch, key=repr)))


def _slots(net, n):
    return (0, 1, 2) if net.kind[n] in BIN else (0,)


def stuck_redexes(net: Net):
    """principal-principal pairs that did not fire (abort / crash / unsupported)"""
    out = []
    for i, k in enumerate(net.kind):
        if k is None or k == "F": continue
        q = net.p[i][0]
        if q >= 0 and q % 3 == 0 and q // 3 > i and net.kind[q // 3] not in (None, "F"): out.append((i, q // 3))
    return out


def _fanify(net: Net, refcls) -> Net:
    """Mode D canonical shape: every maximal tree of DUP nodes (aux -> principal) becomes a right comb over its leaves sorted by a
    structural key; leaves that are erasers are dropped, one leaf is a wire, no leaf is an eraser."""
    n = net.copy(); n.work = []
    kind, p = n.kind, n.p

    def key(q):
        m = q // 3
        nb = tuple(sorted((str(_label(n, q2 // 3, refcls)), q2 % 3) for q2 in p[m] if q2 >= 0 and q2 // 3 != m))
        return (str(_label(n, m, refcls)), q % 3, nb)

    def is_child(d):
        q = p[d][0]
        return q >= 0 and q % 3 != 0 and kind[q // 3] == "D"
    for d0 in [i for i, k in enumerate(list(kind)) if k == "D"]:
        if kind[d0] != "D" or is_child(d0): continue
        tree, leaves, stack = [], [], [d0]
        ok = True
        while stack:
            d = stack.pop(); tree.append(d)
            for s in (1, 2):
                q = p[d][s]
                if q < 0: ok = False; continue
                if q % 3 == 0 and kind[q // 3] == "D": stack.append(q // 3)
                else: leaves.append((3 * d + s, q))
        tset = set(tree)
        if not ok or any(q // 3 in tset for _, q in leaves): continue          # a wire from the fan to itself: leave it
        root_peer = p[d0][0]
        real, erased = [], []
        for port, q in leaves:
            if q % 3 == 0 and kind[q // 3] == "E": erased.append(q // 3)
            else: real.append(q)
        for d in tree: kind[d] = None
        for e in erased: kind[e] = None
        real.sort(key=key)
        if not real:
            e = n.node("E")
            if root_peer >= 0: n.link(root_peer, 3 * e)
        elif len(real) == 1:
            if root_peer >= 0: n.link(root_peer, real[0])
        else:
            chain = [n.node("D") for _ in range(len(real) - 1)]
            if root_peer >= 0: n.link(root_peer, 3 * chain[0])
            for i, c in enumerate(chain):
                n.link(3 * c + 1, real[i])
                if i + 1 < len(chain): n.link(3 * c + 2, 3 * chain[i + 1])
                else: n.link(3 * c + 2, real[i + 1])
    n.work = []
    return n


def ncount(net):
    from collections import Counter
    return Counter(k for k in net.kind if k is not None)
