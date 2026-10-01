"""HERO-4 net library: the fixed HVM2 fragments every seating word is built from.

Every arrange word (genome/hero4/words.py) is  annotate -> stable sort -> strip  (a closing word is one scan). This module holds
the FRAGMENT generators. They are infrastructure written once, before the ten new words; the new words add expressions and,
twice, a new fragment. All fragments define `@prog = (list out)` so genome.compose.compose_nets can pipe them.

  compile_expr   expression tree -> redexes (DUP chains inserted automatically). ops: + - * / % = ! < > & | ^ << >>
  bank_defs      counter bank (chain of K numbers): (k (v (bank (old bank2)))): leaf k := upd(old, v), returns old
  scan_net       list walker, state (pos, bank): element -> (key . guest) pair, or -> plain value (closing words)
  fold_bank_net  first pass of a two-pass word: copies the list and returns the final bank
  sort_net       STABLE insertion sort of (key . guest) pairs by key
  strip_net      (key . guest) -> guest
"""
from __future__ import annotations

ALL_OPS = {"+", "-", "*", "/", "%", "=", "!", "<", ">", "&", "|", "^", "<<", ">>"}


class Gen:
    def __init__(self): self.n = 0
    def w(self, base="w"): self.n += 1; return f"{base}{self.n}"


def count_uses(e, c):
    if isinstance(e, int): return
    if isinstance(e, str): c[e] = c.get(e, 0) + 1; return
    for a in e[1:]: count_uses(a, c)


def split(wire, n, gen, reds):
    """DUP chain: wire -> n fresh wires (n >= 1; n == 0 erases)."""
    if n == 0: reds.append(f"{wire} ~ *"); return []
    names, cur = [], wire
    for _ in range(n - 1):
        a, b = gen.w("u"), gen.w("u"); reds.append(f"{cur} ~ {{{a} {b}}}"); names.append(a); cur = b
    names.append(cur)
    return names


def compile_expr(e, env, out, gen, reds):
    """e: int | var name | (op, a, b). env: var -> wire carrying it (unused vars are erased). Result goes to wire `out`."""
    uses = {}; count_uses(e, uses)
    bad = set(uses) - set(env)
    if bad: raise KeyError(f"unbound variables {bad}")
    src = {v: split(w, uses.get(v, 0), gen, reds) for v, w in env.items()}
    idx = {v: 0 for v in src}

    def val(x):
        if isinstance(x, int): return str(x)
        if isinstance(x, str): n = src[x][idx[x]]; idx[x] += 1; return n
        op, a, b = x
        assert op in ALL_OPS, op
        la, lb = val(a), val(b); o = gen.w("e"); reds.append(f"{la} ~ $([{op}] $({lb} {o}))"); return o

    if isinstance(e, (int, str)): e = ("+", e, 0)
    op, a, b = e
    assert op in ALL_OPS, op
    la, lb = val(a), val(b); reds.append(f"{la} ~ $([{op}] $({lb} {out}))")


def uses_of(e):
    c = {}; count_uses(e, c); return c


# expression sugar (all boolean values are 0/1)
def sel(c, a, b): return ("+", b, ("*", c, ("-", a, b)))          # c ? a : b   (c in {0,1}); exact mod 2^24
def eq(a, b): return ("=", a, b)
def ne(a, b): return ("!", a, b)
def lt(a, b): return ("<", a, b)
def gt(a, b): return (">", a, b)
def le(a, b): return ("-", 1, (">", a, b))
def ge(a, b): return ("-", 1, ("<", a, b))
def add(a, b): return ("+", a, b)
def sub(a, b): return ("-", a, b)
def mul(a, b): return ("*", a, b)
def div(a, b): return ("/", a, b)
def mod(a, b): return ("%", a, b)
def mn(a, b): return sel(lt(a, b), a, b)


# guest field expressions (g is a variable name)
def IDX(g="g"): return ("&", g, 63)
def RANK(g="g"): return ("&", (">>", g, 6), 31)
def CAT(g="g"): return ("&", (">>", g, 11), 7)
def COMP(g="g"): return ("&", (">>", g, 14), 31)
def RI(g="g"): return ("&", g, 2047)                                # rank<<6 | idx  (captain / head-seat key)


def _book(defs):
    return "\n\n".join(f"@{n} = {root}" + "".join(f"\n  & {r}" for r in reds) for n, root, reds in defs) + "\n"


def _walk(W, ctx):
    return f"((?((@{W}_nil @{W}_cons) (p {ctx})) p) {ctx})"


def bank_lit(K, v=0):
    s = "*"
    for _ in range(K): s = f"({v} {s})"
    return s


def bank_defs(P, upd):
    """@P ~ (k (v (bank (old bank2)))): leaf k of a K-chain bank is replaced by upd(c, v) (c = old leaf, v operand); old is returned.
    k must be < K."""
    g = Gen(); zreds = []
    compile_expr(upd, {"c": "cc", "v": "v"}, "c2", g, zreds)
    return [
        (P, "(k (v (bank out)))", [f"k ~ ?((@{P}_z @{P}_s) (v (bank out)))"]),
        (f"{P}_z", "(v ((c rest) (c1 (c2 rest))))", ["c ~ {c1 cc}"] + zreds),
        (f"{P}_s", "(k1 (v ((c rest) (old (c rest2)))))", [f"@{P} ~ (k1 (v (rest (old rest2))))"]),
    ]


def scan_net(N, *, use_pos=False, K=0, upd=None, cls=None, val=0, key, emit="pair", init_bank=None, input_bank=False):
    """List walker. For each element g (with position pos and, if K>0, bank fetch-and-update):
         cls  (expr over g,pos)      bank index, < K
         val  (expr over g,pos)      operand v of the bank update
         upd  (expr over c,v)        new leaf value;  the OLD leaf is available to `key` as variable `occ`
         key  (expr over g,pos,cls,occ)
       emit='pair' -> element (key . g);  emit='value' -> element key.
       input_bank=True: the initial bank is a second component of the input `(list bank)` instead of a literal (second pass)."""
    has_bank = K > 0
    def ctx(p, b, o):
        s = o
        if has_bank: s = f"({b} {s})"
        if use_pos: s = f"({p} {s})"
        return s
    nil_root = f"(* {ctx('*', '*', '(0 *)')})"
    g = Gen(); reds = []
    gnames = split("h", 4, g, reds)                       # cls, val, key, output
    hc, hv, hk, ho = gnames
    if use_pos:
        pc, pv, pk, pn = split("pos", 4, g, reds)
        reds.append(f"{pn} ~ $([+] $(1 pos2))")
    else:
        pc = pv = pk = None
    def envg(hw, pw):
        e = {"g": hw}
        if use_pos: e["pos"] = pw
        return e
    kenv = envg(hk, pk)
    if has_bank:
        compile_expr(cls, envg(hc, pc), "cv", g, reds)
        cv1, cv2 = split("cv", 2, g, reds)
        compile_expr(val, envg(hv, pv), "vv", g, reds)
        reds.append(f"@{N}_bx ~ ({cv1} (vv (bank (occ bank2))))")
        kenv["cls"] = cv2; kenv["occ"] = "occ"
    else:
        reds.append(f"{hc} ~ *"); reds.append(f"{hv} ~ *")
        if use_pos: reds.append(f"{pc} ~ *"); reds.append(f"{pv} ~ *")
    compile_expr(key, kenv, "kv", g, reds)
    if emit == "pair": elem = f"(kv {ho})"
    else: elem = "kv"; reds.append(f"{ho} ~ *")
    cons_root = f"(* ((h t) {ctx('pos', 'bank', f'(1 ({elem} t2))')}))"
    nxt = ctx("pos2", "bank2", "t2")
    reds.append(f"@{N} ~ (t {nxt})")
    defs = [(N, _walk(N, ctx("pos", "bank", "out")), []), (f"{N}_nil", nil_root, []), (f"{N}_cons", cons_root, reds)]
    if has_bank: defs += bank_defs(f"{N}_bx", upd)
    # entry
    init = ctx("0", bank_lit(K, 0 if init_bank is None else init_bank), "out")
    if input_bank:
        init = ctx("0", "bk", "out")
        defs.append(("prog", "((l bk) out)", [f"@{N} ~ (l {init})"]))
    else:
        defs.append(("prog", "(l out)", [f"@{N} ~ (l {init})"]))
    return _book(defs)


def fold_bank_net(N, *, use_pos, K, upd, cls, val=0, init_bank=0):
    """First pass: returns the pair (copy of the list, final bank). Each element g updates leaf cls(g,pos) := upd(c, v(g,pos))."""
    def ctx(p, b, o): return f"({p} ({b} {o}))" if use_pos else f"({b} {o})"
    nil_root = f"(* {ctx('*', 'bank', '((0 *) bank)')})"
    g = Gen(); reds = []
    h1, hc, hv = split("h", 3, g, reds)
    cons_root = f"(* ((h t) {ctx('pos', 'bank', f'((1 ({h1} t2)) bf)')}))"
    if use_pos:
        pc, pv, pn = split("pos", 3, g, reds); reds.append(f"{pn} ~ $([+] $(1 pos2))")
    def envg(hw, pw):
        e = {"g": hw}
        if use_pos: e["pos"] = pw
        return e
    compile_expr(cls, envg(hc, pc if use_pos else None), "cv", g, reds)
    compile_expr(val, envg(hv, pv if use_pos else None), "vv", g, reds)
    reds.append(f"@{N}_bx ~ (cv (vv (bank (old bank2))))")
    reds.append("old ~ *")
    reds.append(f"@{N} ~ (t {ctx('pos2', 'bank2', '(t2 bf)')})")
    defs = [(N, _walk(N, ctx("pos", "bank", "out")), []), (f"{N}_nil", nil_root, []), (f"{N}_cons", cons_root, reds)]
    defs += bank_defs(f"{N}_bx", upd)
    defs.append(("prog", "(l out)", [f"@{N} ~ (l {ctx('0', bank_lit(K, init_bank), 'out')})"]))
    return _book(defs)


def sort_net():
    """Stable ascending insertion sort of a list of (key . guest) pairs on key."""
    return _book([
        ("prog", "(l out)", ["@so ~ (l ((0 *) out))"]),
        ("so", _walk("so", "(a out)"), []),
        ("so_nil", "(* (a a))", []),
        ("so_cons", "(* ((h t) (a out)))", ["@ins ~ (h (a a2))", "@so ~ (t (a2 out))"]),
        ("ins", "(x (l out))", ["l ~ (?((@ins_nil @ins_cons) (p (x out))) p)"]),
        ("ins_nil", "(* (x (1 (x (0 *)))))", []),
        ("ins_cons", "(* (((kh gh) t) ((kx gx) out)))",
         ["kx ~ {kx1 kx2}", "kh ~ {kh1 kh2}", "kx1 ~ $([<] $(kh1 c))",
          "c ~ ?((@ins_later @ins_here) ((kx2 gx) ((kh2 gh) (t out))))"]),
        ("ins_later", "((kx gx) ((kh gh) (t (1 ((kh gh) r)))))", ["@ins ~ ((kx gx) (t r))"]),
        ("ins_here", "(* ((kx gx) ((kh gh) (t (1 ((kx gx) (1 ((kh gh) t))))))))", []),
    ])


def strip_net():
    return _book([
        ("prog", "(l out)", ["@sp ~ (l out)"]),
        ("sp", _walk("sp", "out"), []),
        ("sp_nil", "(* (0 *))", []),
        ("sp_cons", "(* (((* g) t) (1 (g t2))))", ["@sp ~ (t t2)"]),
    ])


def keyed_sort_word(annot_net):
    """annotate -> stable sort -> strip, as ONE net"""
    from genome.compose import compose_nets
    return compose_nets([annot_net, sort_net(), strip_net()])
