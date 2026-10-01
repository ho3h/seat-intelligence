"""Tests for genome/lib/glue.py: every glue mistake class raises a precise GlueError before anything runs, the
helpers (fanout, erase_unused, hole, branch, select) emit lint-clean nets that compute the right thing, and the
re-expressed exp8 programs cost the same as the hand-wired ones.
usage: python3 -m genome.lib.test_glue [--cost]   (--cost also runs the verifier on t3_degrees / t3_cc_largest)"""
import os, re, sys
from genome.lib.glue import Program, GlueError, NUM, DEPTH, TRIE, ADJ, EDGE, LIST, HOLE, INF
from genome.types import encode, decode, u24, list_of, tup
from genome.executor import run_net

RESULTS = []


def expect(name, fn, *frags):
    try:
        fn()
    except GlueError as e:
        msg = str(e)
        miss = [f for f in frags if f not in msg]
        ok = not miss
        RESULTS.append(ok)
        print(f"{'PASS' if ok else 'FAIL'}  {name:34s} GlueError: {msg.splitlines()[0][:150]}")
        if miss: print("      missing fragments:", miss, "\n      full:", msg)
        return
    RESULTS.append(False)
    print(f"FAIL  {name:34s} no GlueError raised")


def runs(name, P, it, ot, cases):
    txt = P.build()
    bad = []
    for v, want in cases:
        root, defs = encode(v, it)
        r = run_net(f"@main = r\n  & @prog ~ ({root} r)\n\n" + "\n".join(defs) + "\n\n" + txt, "run", 60)
        got = decode(r.result, ot) if r.ok else ("ERROR", r.error[:200])
        if got != want: bad.append((v, got, want))
    RESULTS.append(not bad)
    print(f"{'PASS' if not bad else 'FAIL'}  {name:34s} {len(cases) - len(bad)}/{len(cases)} cases")
    for b in bad[:2]: print("      ", b)


# ---------------------------------------------------------------- a small valid program used by several tests
def degrees(step=None, fin=None, prog=None):
    P = Program()
    lg = P.lg(); z0 = P.const_trie("z0", 0); inc = P.update("dinc", "inc"); tl = P.to_list("tl")

    def step0(d, L, h, u, v):
        L1, L2, L3 = d.fanout(L, 3)
        return L3, d.call(inc, t=d.call(inc, t=h, k=u, L=L1), k=v, L=L2)

    def fin0(d, L, h):
        d.erase(L); return h
    w = P.stream("w", step or step0, fin or fin0, state=[("L", DEPTH), ("h", TRIE(NUM))], elem=EDGE)

    def prog0(d, n, es):
        def empty(b, es): b.erase(es); return b.nil()
        def nonempty(b, nm1, es):
            a, c = b.fanout(nm1, 2)
            L1, L2, L3 = b.fanout(b.call(lg, x=a), 3)
            H = b.call(w, list=es, init=(L2, b.call(z0, L=L1)))
            return b.call(tl, t=H, L=L3, n=b.op(c, "+", 1))
        return d.branch(n, empty, nonempty, es)
    P.prog("t3_degrees", (prog or prog0)(lg, z0, inc, tl, w) if prog else prog0)
    return P


def main():
    # ---------------------------------------------------------------- error classes
    def unconnected():
        P = Program(); inc = P.update("u", "inc")
        def prog(d, n, es):
            d.erase(es); return d.call(inc, t=n, L=3)
        P.prog("t3_degrees", prog)
    expect("unconnected input port", unconnected, "input port `k` is not connected", "update `u`")

    def unknown_port():
        P = Program(); lg = P.lg()
        def prog(d, n, es):
            d.erase(es); return d.call(lg, n=n)
        P.prog("t3_degrees", prog)
    expect("unknown port name", unknown_port, "port `n` does not exist", "in  x: num")

    def out_as_in():
        P = Program(); lg = P.lg()
        def prog(d, n, es):
            d.erase(es); return d.call(lg, x=n, L=3)
        P.prog("t3_degrees", prog)
    expect("output passed as input", out_as_in, "port `L` is an OUTPUT")

    def used_twice():
        def step(d, L, h, u, v):
            L1, L2 = d.fanout(L, 2)
            inc = d.P.prims["dinc"]
            return L2, d.call(inc, t=d.call(inc, t=h, k=u, L=L1), k=v, L=L1)
        degrees(step=step)
    expect("wire used twice", used_twice, "used a second time", "`L1`", "already used at")

    def needs_dup():
        def step(d, L, h, u, v):
            inc = d.P.prims["dinc"]
            return L, d.call(inc, t=h, k=u, L=L)
        degrees(step=step)
    expect("value needed twice, no DUP", needs_dup, "d.fanout(L, 2)")

    def trie_twice():
        P = Program(); lg = P.lg(); z0 = P.const_trie("z0", 0); tl = P.to_list("tl"); mx = P.reduce("mx", lambda d, x: x, "max")
        def prog(d, n, es):
            d.erase(es); a, b = d.fanout(n, 2); T = d.call(z0, L=3)
            d.erase(d.call(mx, t=T, L=3))
            d.erase(a)
            return d.call(tl, t=T, L=3, n=b)
        P.prog("t3_degrees", prog)
    expect("trie used twice", trie_twice, "cannot be duplicated safely", "mc_deliver_keep")

    def fanout_trie():
        P = Program(); z0 = P.const_trie("z0", 0)
        def prog(d, n, es):
            d.erase(es, n); T = d.call(z0, L=3); d.fanout(T, 2)
        P.prog("t3_degrees", prog)
    expect("fanout of a trie", fanout_trie, "cannot fanout", "trie[num]")

    def unused_output():
        def fin(d, L, h):
            return h
        degrees(fin=fin)
    expect("unused value (no erase)", unused_output, "never used", "`L` (depth", "d.erase(x)")

    def kind_mismatch():
        P = Program(); lg = P.lg(); tl = P.to_list("tl"); z0 = P.const_trie("z0", 0)
        def prog(d, n, es):
            a, b = d.fanout(n, 2)
            L = d.call(lg, x=a)
            return d.call(tl, t=es, L=L, n=b)
        P.prog("t3_degrees", prog)
    expect("kind mismatch (list for trie)", kind_mismatch, "kind mismatch", "expected trie", "got list[(num num)]")

    def depth_mismatch():
        P = Program(); z0 = P.const_trie("z0", 0); tl = P.to_list("tl")
        def prog(d, n, es):
            d.erase(es); a, b, c = d.fanout(n, 3)
            return d.call(tl, t=d.call(z0, L=a), L=b, n=c)
        P.prog("t3_degrees", prog)
    expect("number where a depth is expected", depth_mismatch, "expected depth", "d.as_depth")

    def wrong_out_kind():
        P = Program()
        def prog(d, n, es):
            d.erase(es); return n
        P.prog("t3_degrees", prog)
    expect("wrong output kind for contract", wrong_out_kind, "expected list[num], got num")

    def arity_in():
        def step(d, L, h, e):
            return L, h
        degrees(step=step)
    expect("wrong arity (arguments)", arity_in, "wrong arity", "d plus 4 value(s)", "(d, L, h, e)")

    def arity_out():
        def step(d, L, h, u, v):
            d.erase(u, v); return h
        degrees(step=step)
    expect("wrong arity (returns)", arity_out, "must return 2 value(s) (L, h)", "returned 1")

    def returns_none():
        def fin(d, L, h):
            d.erase(L, h)
        degrees(fin=fin)
    expect("forgot return", returns_none, "must return exactly one value")

    def closure_capture():
        P = Program(); lg = P.lg(); z0 = P.const_trie("z0", 0); inc = P.update("dinc", "inc"); tl = P.to_list("tl")
        box = {}
        def step(d, h, u, v):
            return d.call(inc, t=d.call(inc, t=h, k=u, L=box["L"]), k=v, L=box["L"])
        def prog(d, n, es):
            a, c = d.fanout(n, 2)
            box["L"] = d.call(lg, x=a)
            w = P.stream("w", step, lambda d, h: h, state=[("h", TRIE(NUM))])
            return d.call(tl, t=d.call(w, list=es, init=d.call(z0, L=3)), L=3, n=c)
        P.prog("t3_degrees", prog)
    expect("wire captured from another def", closure_capture, "belongs to @prog", "pass the value in")

    def python_arith():
        def step(d, L, h, u, v):
            return L, h + u
        degrees(step=step)
    expect("python arithmetic on a wire", python_arith, "wires are not Python numbers", "d.op(")

    def python_if():
        def step(d, L, h, u, v):
            if u: pass
        degrees(step=step)
    expect("python `if` on a wire", python_if, "d.select", "d.branch")

    def env_not_copyable():
        P = Program()
        P.reduce("r", lambda d, x, E: x, "+", env=TRIE(NUM))
    expect("non-copyable environment", env_not_copyable, "copied to every leaf")

    def name_clash():
        P = Program(); P.update("a", "inc"); P.const_trie("a", 0)
    expect("primitive name clash", name_clash, "name clash")

    def branch_mismatch():
        P = Program()
        def prog(d, n, es):
            return d.branch(n, lambda b, es: (b.erase(es), b.nil())[1], lambda b, m, es: (b.erase(es, m), 0)[1], es)
        P.prog("t3_degrees", prog)
    expect("branches return different kinds", branch_mismatch, "kind mismatch", "branch nonzero case")

    # ---------------------------------------------------------------- helpers work
    runs("degrees (fanout, branch, stream)", degrees(), tup(u24, list_of(tup(u24, u24))), list_of(u24),
         [((0, []), []), ((1, []), [0]), ((3, [(0, 1), (1, 2)]), [1, 2, 1]), ((5, [(4, 0), (0, 2), (2, 4)]), [2, 0, 2, 0, 2])])

    def _eu(d, n, es):
        d.erase_unused()
        c = d.select(n, 7, 9)
        return d.cons(c, d.nil())
    P = Program(); P.prog("t3_degrees", _eu)
    assert P.auto_erased == [("prog", ["es"])], P.auto_erased
    runs("select + cons + erase", P, tup(u24, list_of(tup(u24, u24))), list_of(u24),
         [((0, []), [9]), ((4, [(0, 1)]), [7])])

    # hole: output the list of edge sums in input order through the walker state
    P = Program()
    def step(d, h, u, v):
        return d.fill_cons(h, d.op(u, "+", v))
    def fin(d, h):
        d.fill(h, d.nil()); return 0
    w = P.stream("w", step, fin, state=[("h", HOLE(LIST(NUM)))], elem=EDGE)
    def prog(d, n, es):
        d.erase(n)
        val, hole = d.hole(LIST(NUM))
        d.erase(d.call(w, list=es, init=hole))
        return val
    P.prog("t3_degrees", prog)
    runs("hole (list in input order)", P, tup(u24, list_of(tup(u24, u24))), list_of(u24),
         [((0, []), []), ((9, [(1, 2), (3, 4), (0, 0)]), [3, 7, 0])])

    # ---------------------------------------------------------------- cost parity with the hand-wired exp8 nets
    if "--cost" in sys.argv:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "runs", "exp14"))
        import examples_checked as EX
        from genome.corpus import load_all
        from genome.verify import verify
        root = os.path.join(os.path.dirname(__file__), "..", "..")
        for name in ("t3_degrees", "t3_cc_largest"):
            p = load_all()[name]
            a = verify(p, getattr(EX, name)().build(), 0, 60.0, 3)
            b = verify(p, open(os.path.join(root, "runs", "exp8", name + ".hvm")).read(), 0, 60.0, 3)
            ma, mb = a["metrics"], b["metrics"]
            dd = ma["depth_median_big"] / mb["depth_median_big"] - 1
            di = ma["itrs_median_big"] / mb["itrs_median_big"] - 1
            ok = a["status"] == b["status"] == "pass" and abs(dd) <= 0.02 and abs(di) <= 0.02
            RESULTS.append(ok)
            print(f"{'PASS' if ok else 'FAIL'}  cost {name:29s} typed depth {ma['depth_median_big']} itrs {ma['itrs_median_big']}"
                  f" | exp8 depth {mb['depth_median_big']} itrs {mb['itrs_median_big']} | {dd:+.2%} depth, {di:+.3%} itrs")

    print(f"\n{sum(RESULTS)}/{len(RESULTS)} pass")
    return 0 if all(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
