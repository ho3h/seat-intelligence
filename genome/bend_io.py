"""B1 arm plumbing: the same interface contract for programs written in Bend.

The author writes `def prog(x): ...` (single argument, any Bend). We compile it with `bend gen-hvm`, drop Bend's own
@main, and run `@main = r & @prog ~ (INPUT r)` on the same executor, so B1 and the native arm differ in exactly one
thing: whether a human language sits between the author and the net.

Inputs arrive as materialised Bend-encoded values (no construction cost). Bend encodes a constructor value as
`((tag (f1 (f2 ... (fk c)))) c)` with one fresh wire c per value, numbers as NUMs, tuples as plain pairs.
"""
from __future__ import annotations
import os, re, subprocess, tempfile
from .types import U24, List, Tup, Adt, Rec, NODE_BUDGET
from .digest import _Gen
from .executor import ROOT, ENV

BEND = os.path.join(ROOT, "physics", "bend", "bin", "bend")
# B1 gets its strongest fair configuration: all optimisations, and the experimental type checker off (it trips on
# user names that collide with builtin helpers, e.g. `go`).
BEND_OPTS = ["-O", "all", "-O", "no-type-check"]  # order matters: `all` would re-enable the checker
SPILL = 1200


def _adt_of_list(t): return Adt("list", ((), (t.elem, Rec())))


# ------------------------------------------------------------------ encoding (materialised Bend values)
class _Enc:
    def __init__(self, tag):
        self.tag = tag; self.defs = []; self.n = 0

    def var(self):
        self.n += 1
        return f"c{self.n}"

    def enc(self, v, t):
        """-> (text, nodes)"""
        if isinstance(t, U24): return str(v), 0
        if isinstance(t, Tup):
            parts = [self.enc(x, et) for x, et in zip(v, t.elems)]
            text, nodes = parts[-1]
            for ptxt, pn in reversed(parts[:-1]): text, nodes = f"({ptxt} {text})", nodes + pn + 1
            return text, nodes
        if isinstance(t, List): return self.enc_list(v, t)
        if isinstance(t, Adt): return self.enc_adt(v, t, t)
        raise TypeError(t)

    def enc_list(self, v, t):
        elems = [self.enc(x, t.elem) for x in v]
        chunks, cur, cn = [], [], 0
        for i, (txt, n) in enumerate(elems):
            if cur and cn + n + 4 > NODE_BUDGET: chunks.append(cur); cur, cn = [], 0
            cur.append(txt); cn += n + 4
        chunks.append(cur)
        c0 = self.var(); tail = f"((0 {c0}) {c0})"
        first = None
        for ci in range(len(chunks) - 1, -1, -1):
            pre, suf = [], []
            for x in chunks[ci]:
                c = self.var()
                pre.append(f"((1 ({x} ("); suf.append(f" {c}))) {c})")
            body = "".join(pre) + tail + "".join(reversed(suf))
            if ci == 0: return body, cn
            name = f"__{self.tag}_{len(self.defs)}"
            self.defs.append(f"@{name} = {body}")
            tail = f"@{name}"

    def enc_adt(self, v, t, whole):
        idx, fields = v[0], v[1:]
        ft = t.ctors[idx]
        parts = []
        for x, f in zip(fields, ft):
            if isinstance(f, Rec):
                txt, n = self.enc_adt(x, whole, whole)
                if n > SPILL:
                    name = f"__{self.tag}_{len(self.defs)}"; self.defs.append(f"@{name} = {txt}"); txt, n = f"@{name}", 0
                parts.append((txt, n))
            else: parts.append(self.enc(x, f))
        c = self.var()
        rest, nodes = c, 0
        for txt, n in reversed(parts): rest, nodes = f"({txt} {rest})", nodes + n + 1
        return f"(({idx} {rest}) {c})", nodes + 2


def encode_bend(v, t, tag="in"):
    e = _Enc(tag); text, _ = e.enc(v, t)
    return text, e.defs


# ------------------------------------------------------------------ digest over Bend-encoded values
class _GenBend(_Gen):
    """Same digest as the native one, consuming Bend-encoded values. A constructor value V = (X c), X = (tag rest):
    connect V ~ ((sw pl) r), switch on the tag, destructure pl, tie the final wire to r."""

    def for_type(self, t, whole=None, whole_name=None):
        if isinstance(t, List): t = _adt_of_list(t)
        if isinstance(t, Adt): return self.adt_bend(t)
        if isinstance(t, Tup):
            nm = self.name("tup"); subs = [self.for_type(et) for et in t.elems]
            vs = [f"v{i}" for i in range(len(subs))]; pat = vs[-1]
            for v in reversed(vs[:-1]): pat = f"({v} {pat})"
            lines = [f"@{nm} = ({pat} (acc0 out))"]
            for i, sd in enumerate(subs):
                lines.append(f"  & @{sd} ~ ({vs[i]} (acc{i} acc{i+1}))" if i < len(subs) - 1 else f"  & @{sd} ~ ({vs[i]} (acc{i} out))")
            self.defs[nm] = "\n".join(lines); return nm
        return super().for_type(t)

    def adt_bend(self, t):
        key = ("adt", t)
        if key in self.memo: return self.memo[key]
        nm = self.name(t.name); self.memo[key] = nm; feed = self.feed_def()
        ctx = "(pl (r (acc out)))"
        bodies = []
        for i, ftypes in enumerate(t.ctors):
            bn = f"{nm}_c{i}"; bodies.append(bn)
            fvs = [f"f{j}" for j in range(len(ftypes))]
            rest = "z"
            for v in reversed(fvs): rest = f"({v} {rest})"
            # branch receives ctx (i == 0) or (pred ctx): pattern binds pl = rest, r, acc, out
            inner = f"({rest} (z (acc0 out)))"
            head = inner  # the switch chain already consumed the predecessor number
            lines = [f"@{bn} = {head}", f"  & @{feed} ~ ({i} (acc0 s0))"]
            for j, ft in enumerate(ftypes):
                sub = nm if isinstance(ft, Rec) else self.for_type(ft)
                dst = "out" if j == len(ftypes) - 1 else f"s{j+1}"
                lines.append(f"  & @{sub} ~ ({fvs[j]} (s{j} {dst}))")
            if not ftypes: lines[-1:] = [f"  & @{feed} ~ ({i} (acc0 out))"]
            self.defs[bn] = "\n".join(lines)
        k = len(bodies)
        top = f"@{nm} = (((?((@{bodies[0]} @{nm}_s0) {ctx}) pl) r) (acc out))" if k > 1 else \
              f"@{nm} = (((?((@{bodies[0]} @{nm}_bad) {ctx}) pl) r) (acc out))"
        self.defs[nm] = top
        if k == 1:
            self.defs[nm + "_bad"] = f"@{nm}_bad = (* (* (* (* *))))"; return nm
        for i in range(k - 1):
            if i == k - 2:
                self.defs[f"{nm}_s{i}"] = (f"@{nm}_s{i} = (* (pl (r (acc out))))\n"
                                            f"  & @{bodies[k-1]} ~ (pl (r (acc out)))")
            else:
                self.defs[f"{nm}_s{i}"] = (f"@{nm}_s{i} = (m (pl (r (acc out))))\n"
                                            f"  & m ~ ?((@{bodies[i+1]} @{nm}_s{i+1}) (pl (r (acc out))))")
        return nm


def gen_digest_bend(t):
    g = _GenBend(); root = g.for_type(t)
    return "\n\n".join(g.defs.values()) + "\n", root


# ------------------------------------------------------------------ compile + assemble
def bend_type_decls(t, seen=None) -> str:
    """Bend `type` declarations for every Adt reachable from t (List is builtin). Ctors are C0, C1, ...; fields f0, f1, ..."""
    seen = {} if seen is None else seen
    out = []
    def walk(x):
        if isinstance(x, List): walk(x.elem)
        elif isinstance(x, Tup):
            for e in x.elems: walk(e)
        elif isinstance(x, Adt) and x.name not in seen:
            seen[x.name] = True
            cs = []
            for i, c in enumerate(x.ctors):
                cs.append(f"  C{i}" + (" { " + ", ".join(f"f{j}" for j in range(len(c))) + " }" if c else ""))
                for f in c:
                    if not isinstance(f, Rec): walk(f)
            out.append(f"type {bend_type_name(x)}:\n" + "\n".join(cs))
    walk(t)
    return "\n\n".join(out)


def bend_type_name(a: Adt) -> str:
    return "G" + a.name.replace("-", "_")


def compile_bend(source: str, timeout: float = 120.0):
    """-> (hvm_book_text without Bend's @main, error). Bend's main must call prog so it is not pruned."""
    with tempfile.NamedTemporaryFile("w", suffix=".bend", delete=False, dir=os.path.join(ROOT, "scratch")) as f:
        f.write(source); path = f.name
    try:
        p = subprocess.run([BEND, "gen-hvm", *BEND_OPTS, path], capture_output=True, text=True, timeout=timeout, env=ENV)
    except subprocess.TimeoutExpired:
        return None, "bend compile timed out"
    finally:
        try: os.unlink(path)
        except OSError: pass
    if p.returncode != 0 or "@prog" not in p.stdout:
        msg = re.sub(r"\x1b\[[0-9;]*m", "", (p.stderr or p.stdout))[:700]
        return None, msg or "bend produced no @prog"
    # drop Bend's @main definition (harness owns @main)
    blocks = re.split(r"\n\s*\n", p.stdout)
    blocks = [b for b in blocks if not re.match(r"\s*@main\s*=", b)]
    return "\n\n".join(blocks) + "\n", None


def assemble_bend(p, hvm_book: str, value, digest: bool = True) -> str:
    root_in, defs = encode_bend(value, p.inp)
    if not digest:
        return f"@main = r\n  & @prog ~ ({root_in} r)\n\n" + "\n".join(defs) + "\n\n" + hvm_book
    dbook, droot = gen_digest_bend(p.out)
    return (f"@main = r\n  & @prog ~ ({root_in} o)\n  & @{droot} ~ (o ((0 0) r))\n\n" + "\n".join(defs) + "\n\n" + hvm_book + "\n\n" + dbook)


def bend_source(p, author_code: str) -> str:
    """Prelude types + author code + a main that keeps prog alive. The author writes `def prog(x)` and helpers."""
    decl = bend_type_decls(p.inp) 
    d2 = bend_type_decls(p.out)
    return "\n\n".join(x for x in (decl, d2, author_code.strip(), "def main():\n  return prog(0)") if x) + "\n"


# ------------------------------------------------------------------ decoding printed Bend values (for feedback)
def _btokens(s):
    return re.findall(r"\(|\)|\*|[^\s()*]+", s)


def _bparse(s):
    toks = _btokens(s); pos = 0
    import sys; sys.setrecursionlimit(max(sys.getrecursionlimit(), 200000))
    def go():
        nonlocal pos
        t = toks[pos]; pos += 1
        if t == "(":
            a = go(); b = go(); assert toks[pos] == ")"; pos += 1
            return ("con", a, b)
        if t == "*": return ("era",)
        if re.fullmatch(r"\d+", t): return ("num", int(t))
        if t.startswith("@"): return ("ref", t[1:])
        return ("var", t)
    tr = go()
    return tr


def _ref_ctor_index(name, t):
    """`List/Nil`->0, `List/Cons/tag`->1, `Gexpr/C2/tag`->2 ..."""
    m = re.match(r"(?:List/(Nil|Cons)|G\w+/C(\d+))(?:/tag)?$", name)
    if not m: return None
    if m.group(1): return 0 if m.group(1) == "Nil" else 1
    return int(m.group(2))


def decode_bend(text: str, t):
    from .types import DecodeError
    tr = _bparse(text)
    def val(tr, t):
        if isinstance(t, U24):
            if tr[0] != "num": raise DecodeError(f"expected u24, got {_short(tr)}")
            return tr[1]
        if isinstance(t, Tup):
            out = []
            for et in t.elems[:-1]:
                if tr[0] != "con": raise DecodeError(f"expected tuple, got {_short(tr)}")
                out.append(val(tr[1], et)); tr = tr[2]
            out.append(val(tr, t.elems[-1])); return tuple(out)
        if isinstance(t, List):
            out = []
            while True:
                idx, fields = ctor(tr)
                if idx == 0: return out
                out.append(val(fields[0], t.elem)); tr = fields[1]
        if isinstance(t, Adt): return adt_val(tr, t, t)
        raise TypeError(t)
    def ctor(tr):
        if tr[0] == "ref":
            i = _ref_ctor_index(tr[1], None)
            if i is None: raise DecodeError(f"unexpanded reference @{tr[1]} where a value was expected")
            return i, []
        if tr[0] != "con" or tr[1][0] != "con": raise DecodeError(f"expected a constructor value, got {_short(tr)}")
        x = tr[1]; tg = x[1]
        idx = tg[1] if tg[0] == "num" else (_ref_ctor_index(tg[1], None) if tg[0] == "ref" else None)
        if idx is None: raise DecodeError(f"bad constructor tag {_short(tg)}")
        rest, fields = x[2], []
        while rest[0] == "con":
            fields.append(rest[1]); rest = rest[2]
        return idx, fields
    def adt_val(tr, t, whole):
        idx, fields = ctor(tr)
        if idx >= len(t.ctors) or len(fields) != len(t.ctors[idx]): raise DecodeError(f"malformed {t.name} value")
        return (idx, *[adt_val(f, whole, whole) if isinstance(ft, Rec) else val(f, ft) for f, ft in zip(fields, t.ctors[idx])])
    return val(tr, t)


def _short(tr, n=120):
    s = str(tr); return s if len(s) <= n else s[:n] + "…"
