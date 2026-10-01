"""Swing 18: the K-cell lookahead list walker as a machine-applied transformation on parsed HVM2 nets.

Input: any verified native net. Output: the same net where every standard list walker whose cons branch continues
unconditionally into a list walker on its own tail is replaced by a K-cell blocked walker (runs/exp5/lib.py `stream`,
generalised): the block matches K cells speculatively with one nested pattern, puts one SWI per cell tag, runs the
author's own per-cell cons work K times in list order (state/output wires threaded cell to cell), and gets
end-of-list for free: a Nil payload `*` erases every cell pattern, SWI and context past the end.

Pipeline (all on genome.netast trees):
 1. Find list patterns LP = ((?((@N @C) CTX) PL)) anywhere a list is consumed (def roots, redex sides, inside CON
    trees; never inside a SWI branch tuple). PL is a payload var that sits in CTX, or a payload pattern (h t) whose
    vars sit in CTX. A walker "key" is the pair (N, C); CTX gives its template (the argument shape).
 2. Give every key a synthetic walker def  @<C>_lw = (LP' REST)  and replace each LP occurrence by a fresh wire v
    plus a call  @<C>_lw ~ (v REST)  (the author's inline recursion patterns and wrapper defs become calls).
 3. Continuation analysis of C: the tail var t (right child of the payload) must reach exactly one call
    @<C'>_lw ~ (t X). Allowed on the way: static reduction (genome.opt.reduce_def), inlining of non-recursive
    wrapper defs (e.g. the author's @sum -> @sum_lw), and hoisting the call out of both branches of a switch when
    both branches continue on the tail (e.g. max/min keep/take). cont(N,C) = (N',C').
 4. Chains: cell 1 uses key k, cell i+1 uses cont(key_i), up to K cells (so manual unrolls and walker handoffs like
    prefix_sums' first-cell walker become multi-state blocks). Cells 1..L-1 use C_la = C with the tail call
    replaced by a wire to the next cell's context; cell L uses C itself (which calls the next block).
 5. Nil branches must erase the payload slot (they then erase the speculative next-cell context too).

Exact by construction: every rewrite is either a static reduction, an inlining, a wire re-routing that leaves the
same normal form (confluence), or the blocked walker whose Nil path reduces to the original Nil branch plus
erasure of speculative structure. Nothing is trusted: every result is re-verified by genome.verify.

usage: python -m genome.exp12.lookahead <net.hvm> K  > out.hvm
"""
from __future__ import annotations
import sys, os
sys.setrecursionlimit(100000)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT not in sys.path: sys.path.insert(0, ROOT)
from genome.netast import parse_book, print_book, size
from genome.opt import reduce_def

BIN = ("con", "dup", "opr", "swi")


class Fresh:
    def __init__(self, used):
        self.used = set(used); self.n = 0

    def var(self, base="q"):
        while True:
            self.n += 1; v = f"{base}{self.n}"
            if v not in self.used: self.used.add(v); return v

    def name(self, base):
        v = base; i = 0
        while v in self.used: i += 1; v = f"{base}{i}"
        self.used.add(v); return v


def names(t, acc):
    if t[0] in ("var", "ref"): acc.add(t[1])
    elif t[0] in BIN: names(t[1], acc); names(t[2], acc)
    return acc


def tvars(t, acc=None):
    """vars in DFS order (with repeats)."""
    acc = [] if acc is None else acc
    if t[0] == "var": acc.append(t[1])
    elif t[0] in BIN: tvars(t[1], acc); tvars(t[2], acc)
    return acc


def rename(t, m, fresh):
    if t[0] == "var":
        if t[1] not in m: m[t[1]] = fresh.var()
        return ("var", m[t[1]])
    if t[0] in BIN: return (t[0], rename(t[1], m, fresh), rename(t[2], m, fresh))
    return t


def rename_def(d, fresh):
    root, reds = d; m = {}
    return rename(root, m, fresh), [(p, rename(a, m, fresh), rename(b, m, fresh)) for p, a, b in reds]


def get(t, path):
    for s in path:
        if t is None or t[0] != "con": return None
        t = t[1 + s]
    return t


def put(t, path, new):
    if not path: return new
    assert t[0] == "con"
    return ("con", put(t[1], path[1:], new), t[2]) if path[0] == 0 else ("con", t[1], put(t[2], path[1:], new))


def con_path(t, v, path=()):
    """path to var v through CON nodes only."""
    if t[0] == "var": return list(path) if t[1] == v else None
    if t[0] == "con":
        r = con_path(t[1], v, path + (0,))
        return r if r is not None else con_path(t[2], v, path + (1,))
    return None


def any_path(t, v, path=()):
    """path to var v through any binary node: list of (kind, side)."""
    if t[0] == "var": return list(path) if t[1] == v else None
    if t[0] in BIN:
        for s in (0, 1):
            r = any_path(t[1 + s], v, path + ((t[0], s),))
            if r is not None: return r
    return None


def all_paths(t, v, path=(), out=None):
    out = [] if out is None else out
    if t[0] == "var" and t[1] == v: out.append(list(path))
    elif t[0] in BIN:
        for sd in (0, 1): all_paths(t[1 + sd], v, path + ((t[0], sd),), out)
    return out


def tup(vs):
    if not vs: return ("era",)
    t = ("var", vs[-1])
    for v in reversed(vs[:-1]): t = ("con", ("var", v), t)
    return t


def simple_ctx(t):
    if t[0] in ("var", "era", "num"): return True
    return t[0] == "con" and simple_ctx(t[1]) and simple_ctx(t[2])


def skel(t, slots):
    if t[0] == "var": return slots.get(t[1], "V")
    if t[0] == "con": return (skel(t[1], slots), skel(t[2], slots))
    return t


def as_lp(t):
    """-> (key, slot, ctx, slotvars) or None. slot = ('pl', P) | ('ht', Ph, Pt)."""
    if t[0] != "con" or t[1][0] != "swi": return None
    sw, pay = t[1], t[2]
    br, ctx = sw[1], sw[2]
    if br[0] != "con" or br[1][0] != "ref" or br[2][0] != "ref": return None
    if not simple_ctx(ctx): return None
    vs = tvars(ctx)
    if len(vs) != len(set(vs)): return None
    key = (br[1][1], br[2][1])
    if pay[0] == "var":
        P = con_path(ctx, pay[1])
        return None if P is None else (key, ("pl", P), ctx, {pay[1]: "P"})
    if pay[0] == "con" and pay[1][0] == "var" and pay[2][0] == "var":
        Ph, Pt = con_path(ctx, pay[1][1]), con_path(ctx, pay[2][1])
        if Ph is None or Pt is None: return None
        return key, ("ht", Ph, Pt), ctx, {pay[1][1]: "H", pay[2][1]: "T"}
    return None


def lp_occurrences(t, out):
    """LP subtrees reachable through CON nodes only."""
    if as_lp(t): out.append(t); return out
    if t[0] == "con": lp_occurrences(t[1], out); lp_occurrences(t[2], out)
    return out


def erased_at(root, reds, path):
    t = root
    for s in path:
        if t[0] == "era": return True
        if t[0] != "con": break
        t = t[1 + s]
    if t[0] == "era": return True
    if t[0] == "var":
        return any((a == t and b == ("era",)) or (b == t and a == ("era",)) for _, a, b in reds)
    return False


def rest_vars(ctx, slotvars):
    return [v for v in tvars(ctx) if v not in slotvars]


class Fail(Exception):
    pass


class Transformer:
    def __init__(self, text, K, allowed=None, max_inline_depth=12):
        self.defs, self.order = parse_book(text)
        self.K = K
        used = set(self.order)
        for n in self.order:
            r, rd = self.defs[n]; names(r, used)
            for _, a, b in rd: names(a, used); names(b, used)
        self.fresh = Fresh(used)
        self.allowed = allowed
        self.maxd = max_inline_depth
        self.log = []

    # ---------------------------------------------------------------- step 1-2: templates and LP -> calls
    def count_lps(self, d):
        r, rd = d; occ = lp_occurrences(r, [])
        for _, a, b in rd: lp_occurrences(a, occ); lp_occurrences(b, occ)
        return len(occ)

    def templates(self):
        for n in self.order:   # a list pattern split over redexes (t ~ (T (E t1)), T ~ ?(..)) is joined by static reduction
            d = self.defs[n]
            if any(x[0] == "swi" for _, a, b in d[1] for x in (a, b)):
                r2, rd2, _ = reduce_def(*d)
                if self.count_lps((r2, rd2)) > self.count_lps(d): self.defs[n] = (r2, rd2)
        T = {}
        for n in self.order:
            r, rd = self.defs[n]
            occ = lp_occurrences(r, [])
            for _, a, b in rd: lp_occurrences(a, occ); lp_occurrences(b, occ)
            for lp in occ:
                key, slot, ctx, sv = as_lp(lp)
                if key[0] not in self.defs or key[1] not in self.defs: continue
                sk = (slot[0], skel(ctx, sv))
                if key in T:
                    if T[key]["skel"] != sk: T[key]["bad"] = True
                    continue
                T[key] = {"skel": sk, "slot": slot, "ctx": ctx, "sv": sv, "rest": rest_vars(ctx, sv), "bad": False}
        good = {}
        for key, tp in T.items():
            if tp["bad"]: self.log.append(f"{key}: inconsistent list-pattern shapes"); continue
            N = self.defs[key[0]]
            paths = [tp["slot"][1]] if tp["slot"][0] == "pl" else [tp["slot"][1], tp["slot"][2]]
            if not all(erased_at(N[0], N[1], p) for p in paths):
                self.log.append(f"{key}: nil branch does not erase the payload"); continue
            good[key] = tp
        return good

    def replace_lps(self, T):
        self.W = {k: self.fresh.name(k[1] + "_lw") for k in T}
        self.W2key = {w: k for k, w in self.W.items()}

        def repl(t, extra):
            lp = as_lp(t)
            if lp:
                key, slot, ctx, sv = lp
                if key in T and (slot[0], skel(ctx, sv)) == T[key]["skel"]:
                    v = self.fresh.var("lv")
                    extra.append((False, ("ref", self.W[key]), ("con", ("var", v), tup(rest_vars(ctx, sv)))))
                    return ("var", v)
                return t
            if t[0] == "con": return ("con", repl(t[1], extra), repl(t[2], extra))
            return t

        for n in self.order:
            r, rd = self.defs[n]; extra = []
            r = repl(r, extra)
            rd = [(p, repl(a, extra), repl(b, extra)) for p, a, b in rd]
            self.defs[n] = (r, rd + extra)
        for k, w in self.W.items():   # plain synthetic walker: ((?((@N @C) ctx) pl) REST)
            tp = T[k]; m = {}
            ctx = rename(tp["ctx"], m, self.fresh)
            if tp["slot"][0] == "pl": pay = ("var", m[[v for v, s in tp["sv"].items() if s == "P"][0]])
            else:
                h = [v for v, s in tp["sv"].items() if s == "H"][0]; tt = [v for v, s in tp["sv"].items() if s == "T"][0]
                pay = ("con", ("var", m[h]), ("var", m[tt]))
            lp = ("con", ("swi", ("con", ("ref", k[0]), ("ref", k[1])), ctx), pay)
            self.defs[w] = (("con", lp, tup([m[v] for v in tp["rest"]])), [])
            self.order.append(w)

    # ---------------------------------------------------------------- step 3: continuation analysis
    def occurrences(self, root, reds, v):
        out = []
        p = any_path(root, v)
        if p is not None: out.append(("root", p))
        cnt = tvars(root).count(v)
        for i, (_, a, b) in enumerate(reds):
            for s, x in ((0, a), (1, b)):
                c = tvars(x).count(v); cnt += c
                if c: out.append((i, s, any_path(x, v)))
        return out, cnt

    def cut(self, t, p):
        """replace the subtree at path p by a fresh wire z; -> (tree, (z, subtree))"""
        if not p:
            z = ("var", self.fresh.var("z")); return z, (z, t)
        sub, got = self.cut(t[1 + p[0][1]], p[1:])
        return ((t[0], sub, t[2]) if p[0][1] == 0 else (t[0], t[1], sub)), got

    def make_direct(self, root, reds, tpath, depth=0):
        """-> (root, reds, newdefs{name:def}, key, call_index) with reds[call_index] = (_, @W, (t X))."""
        root, reds, _ = reduce_def(root, reds)
        return self.make_direct_nr(root, reds, tpath, depth)

    def make_direct_nr(self, root, reds, tpath, depth=0):
        t = get(root, tpath)
        if t is None or t[0] != "var": raise Fail("tail slot is not a wire")
        tv = t[1]
        occ, cnt = self.occurrences(root, reds, tv)
        if cnt != 2: raise Fail(f"tail wire used {cnt} times")
        rp = [p for p in all_paths(root, tv) if [sd for _, sd in p] != list(tpath)]
        if rp:   # the tail's consumer was substituted into the root pattern: lift the enclosing switch out
            p = rp[0]
            js = [j for j, (k, sd) in enumerate(p) if k == "swi" and sd == 1 and all(k2 == "con" for k2, _ in p[j + 1:])]
            if not js or depth >= self.maxd: raise Fail("tail consumed in the root")
            root2, sw = self.cut(root, p[:js[-1]])
            return self.make_direct_nr(root2, list(reds) + [(False, sw[0], sw[1])], tpath, depth + 1)
        other = [o for o in occ if o[0] != "root"]
        if len(other) != 1: raise Fail("tail consumed in the root")
        i, s, path = other[0]
        par, a, b = reds[i]
        S, O = (a, b) if s == 0 else (b, a)
        # undo static wire substitution: if the tail sits in the context of a switch nested inside a bigger tree,
        # lift that switch out as its own redex (z ~ ?(...)); exact, it is the inverse of wire substitution
        js = [j for j, (k, sd) in enumerate(path) if k == "swi" and sd == 1 and all(k2 == "con" for k2, _ in path[j + 1:])]
        if js and js[-1] > 0 and depth < self.maxd:
            S2, sw = self.cut(S, path[:js[-1]])
            reds2 = list(reds); reds2[i] = (par, S2, O) if s == 0 else (par, O, S2)
            reds2.append((False, sw[0], sw[1]))
            return self.make_direct_nr(root, reds2, tpath, depth + 1)
        # (a) direct call of a synthetic walker on the tail
        if O[0] == "ref" and O[1] in self.W2key:
            if S[0] == "con" and S[1] == ("var", tv):
                return root, reds, {}, self.W2key[O[1]], i
            raise Fail("tail passed to a walker in a non-list slot (zip/merge shape)")
        # (b) inline a non-recursive helper
        if O[0] == "ref" and O[1] in self.defs and depth < self.maxd:
            D = self.defs[O[1]]
            if O[1] in self.rec: raise Fail(f"tail passed to recursive helper @{O[1]}")
            if size(D[0]) + sum(size(x) + size(y) for _, x, y in D[1]) > 400: raise Fail("helper too large to inline")
            Dr, Drd = rename_def(D, self.fresh)
            reds2 = reds[:i] + reds[i + 1:] + [(par, Dr, S)] + Drd
            return self.make_direct(root, reds2, tpath, depth + 1)
        # (c) hoist the call out of both branches of a switch
        if S[0] == "swi" and path[0] == ("swi", 1) and all(k == "con" for k, _ in path[1:]) and depth < self.maxd:
            br = S[1]
            if br[0] != "con" or br[1][0] != "ref" or br[2][0] != "ref": raise Fail("switch branches are not references")
            q = [sd for _, sd in path[1:]]
            news, keys, nd = [], set(), {}
            for j in (0, 1):
                bn = br[1 + j][1]
                if bn not in self.defs or bn in self.W2key: raise Fail("bad branch")
                Br, Brd = rename_def(self.defs[bn], self.fresh)
                bpath = q if j == 0 else [1] + q
                if get(Br, bpath) is None or get(Br, bpath)[0] != "var": raise Fail(f"branch @{bn} does not keep the tail (early exit)")
                r2, rd2, nd2, key, ci = self.make_direct(Br, Brd, bpath, depth + 1)
                X = rd2[ci][2][2] if rd2[ci][1][0] == "ref" else rd2[ci][1][2]
                w = self.fresh.var("hw")
                r2 = put(r2, bpath, ("var", w))
                rd2 = list(rd2); rd2[ci] = (False, ("var", w), X)
                nm = self.fresh.name(bn + "_hz")
                nd.update(nd2); nd[nm] = (r2, rd2); news.append(nm); keys.add(key)
            if len(keys) != 1: raise Fail("branches continue into different walkers")
            key = keys.pop()
            xw = self.fresh.var("xw")
            S2 = ("swi", ("con", ("ref", news[0]), ("ref", news[1])), put(S[2], q, ("var", xw)))
            reds2 = list(reds); reds2[i] = (par, S2, O) if s == 0 else (par, O, S2)
            reds2.append((False, ("ref", self.W[key]), ("con", ("var", tv), ("var", xw))))
            return root, reds2, nd, key, len(reds2) - 1
        raise Fail("tail does not reach a walker call")

    # ---------------------------------------------------------------- driver
    def run(self):
        from genome.opt import call_graph, recursive
        T = self.templates()
        if self.allowed is not None: T = {k: v for k, v in T.items() if k in self.allowed}
        if not T: raise Fail("no list walker found")
        self.T = T
        self.replace_lps(T)
        cg = {n: {m for m in e if m not in self.W2key} for n, e in call_graph(self.defs).items()}
        self.rec = recursive(self.defs, cg)   # recursion that does not pass through a walker call
        cont, norm = {}, {}
        for key, tp in T.items():
            C = key[1]
            slot = tp["slot"]
            try:
                r, rd = self.defs[C]
                r, rd, _ = reduce_def(r, rd)
                if slot[0] == "pl":
                    pp = [1] + slot[1]
                    if get(r, pp) is None or get(r, pp)[0] != "con": raise Fail("cons branch does not split the payload")
                    tpath, hpath = pp + [1], pp + [0]
                else:
                    tpath = [1] + slot[2]
                r, rd, nd, k2, ci = self.make_direct(r, rd, tpath)
                cont[key] = k2; norm[key] = (r, rd, nd, ci, tpath)
            except Fail as e:
                self.log.append(f"{key}: {e}")
                cont[key] = None
        self.cont = cont
        chains = {}
        for key in T:
            ch = [key]
            while len(ch) < self.K and cont.get(ch[-1]) is not None: ch.append(cont[ch[-1]])
            if len(ch) >= 2: chains[key] = ch
        if not chains: raise Fail("no walker continues on its own tail: " + "; ".join(self.log[-3:]))
        involved = set()
        for ch in chains.values():
            involved |= set(ch)
            if cont.get(ch[-1]): involved.add(cont[ch[-1]])
        return T, cont, norm, chains, involved

    def emit(self, T, cont, norm, chains):
        la = {}
        for key, (r, rd, nd, ci, tpath) in norm.items():
            if not any(key in ch for ch in chains.values()): continue
            for n, d in nd.items(): self.defs[n] = d; self.order.append(n)
            self.defs[key[1]] = (r, rd)          # normalized cons branch (same semantics)
            X = rd[ci][2][2] if rd[ci][1][0] == "ref" else rd[ci][1][2]
            RN = self.fresh.var("rn")
            r2 = put(r, tpath, ("var", RN))
            rd2 = list(rd); rd2[ci] = (False, ("var", RN), X)
            r2, rd2, _ = reduce_def(r2, rd2)
            nm = self.fresh.name(key[1] + "_la")
            self.defs[nm] = (r2, rd2); self.order.append(nm); la[key] = nm
        for key, ch in chains.items():
            self.defs[self.W[key]] = self.block(ch, la)
        return print_book(self.defs, self.order)

    def block(self, ch, la):
        L = len(ch); f = self.fresh
        ctxs, rests, slots = [], [], []
        for k in ch:
            tp = self.T[k]; m = {}
            ctxs.append(rename(tp["ctx"], m, f)); rests.append(tup([m[v] for v in tp["rest"]])); slots.append(tp["slot"])
        E = [f.var("e") for _ in ch]; G = [f.var("g") for _ in ch]; tK = f.var("tk"); LV = f.var("ls")
        pat = ("var", tK)
        for i in reversed(range(L)): pat = ("con", ("var", G[i]), ("con", ("var", E[i]), pat))
        reds = [(False, ("var", LV), pat)]
        for i, k in enumerate(ch):
            nxt = rests[i + 1] if i < L - 1 else ("var", tK)
            sl = slots[i]
            if sl[0] == "pl": ctx = put(ctxs[i], sl[1], ("con", ("var", E[i]), nxt))
            else: ctx = put(put(ctxs[i], sl[1], ("var", E[i])), sl[2], nxt)
            cons = la[k] if i < L - 1 else k[1]
            reds.append((False, ("var", G[i]), ("swi", ("con", ("ref", k[0]), ("ref", cons)), ctx)))
        return ("con", ("var", LV), rests[0]), reds


def transform(text: str, K: int):
    """-> (new_text, info) ; raises Fail if not applicable."""
    t0 = Transformer(text, K)
    T, cont, norm, chains, involved = t0.run()
    t1 = Transformer(text, K, allowed=involved)   # second pass: touch only the walkers that get blocked
    T, cont, norm, chains, _ = t1.run()
    out = t1.emit(T, cont, norm, chains)
    info = {"chains": {f"{k[0]}|{k[1]}": [c[1] for c in ch] for k, ch in chains.items()},
            "walkers": len(T), "blocked": len(chains), "log": t1.log}
    return out, info


def net_size(text):
    defs, order = parse_book(text)
    return sum(size(defs[n][0]) + sum(size(a) + size(b) for _, a, b in defs[n][1]) for n in order)


if __name__ == "__main__":
    text = open(sys.argv[1]).read(); K = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    try:
        out, info = transform(text, K)
        print(out); print(info, file=sys.stderr)
    except Fail as e:
        print("not applicable:", e, file=sys.stderr); sys.exit(2)
