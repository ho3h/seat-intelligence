# API: glue (typed, checked composition over graphprims)

Import:

```python
import sys, os
sys.path.insert(0, "<home>/Genome")
from genome.lib.glue import Program, GlueError, NUM, DEPTH, ANY, LIST, TRIE, TUP, HOLE, EDGE, WEDGE, ADJ, INF
```

You never write HVM text. A `Program` holds primitive instances; every definition (the `@prog` root, a walker step, a
leaf body, a branch) is a **Python function whose first argument `d` is a composer**, whose other arguments are
**wires**, and which **returns wires** (or ints). Each wire must be used exactly once. The checker raises a
`GlueError` naming your source line BEFORE anything runs (unconnected port, value used twice, kind mismatch, value
never used, wrong number of arguments/returns, a wire used inside another definition, ...). Fix what it says.

Kinds: `NUM`, `DEPTH` (a trie depth, from `lg`), `TRIE(k)`, `LIST(k)`, `TUP(k1, k2, ...)`, `ADJ` (adjacency trie),
`EDGE = TUP(NUM, NUM)`, `WEDGE = TUP(NUM, NUM, NUM)`, `HOLE(k)` (a place to put a value later), `ANY`.

## Primitive instances (make them first, at top level)

`P = Program()`, then (full port lists: `runs/exp14/brief/PORTS_CHECKED.txt`, or `prim.help()`):

| factory | call ports (in -> out) |
| --- | --- |
| `P.lg()` | x -> L (depth) |
| `P.const_trie(name, 0 or INF or ...)` / `P.empty_adj()` / `P.iota_trie(name)` | L [, base=0] -> t |
| `P.update(name, act)` act in set1 inc dec (no P) / set add or min max (P in) / push / peek (P out) / a function f(d, leaf, p) -> leaf | t, k, L [, P] -> t2 |
| `P.adjacency()` | G, u, L, v, w=0 -> G2 (pushes (v w) onto u's list) |
| `P.get(name)` | t, k, L -> o (consumes t) |
| `P.reduce(name, leaf, op, index=False, env=None)`; leaf(d, x[, i][, E]) -> num; op in + \| & max min | t, L [, base=0] [, E] -> o |
| `P.fold(name, leaf, acc=KIND, index=True, env=None)`; leaf(d, x[, i][, E], acc) -> acc | t, L [, base] [, E], acc -> o |
| `P.to_list(name)` | t, L, n [, tail=[]] -> o (first n leaves) |
| `P.filter_list(name, pred, emit="i" or "x", env=NUM)`; pred(d, x, i, E) -> 0/1 | t, L [, E=0] [, tail] -> o |
| `P.scatter(name, upd, key, env=NUM)`; key(d, x, i, E) -> (k, P) (just k if upd has no payload) | t, L, Lh, E, H -> H2 |
| `P.zip2(name, leaf)`; leaf(d, x, y) -> value / `P.zip2e(name, leaf, env)` | a, c, L [, E] -> o |
| `P.mapreduce(name, leaf, op, index=True, env=None)`; leaf(d, x[, i][, E]) -> (x2, r) | t, L [, base] [, E] -> (t2, o) |
| `P.mc_empty(name)` / `P.mc_request(name)` / `P.mc_deliver(name)` / `P.mc_deliver_keep(name)` | L -> q / q, k, L -> (r, q2) / v, q, L -> nothing / v, q, L -> v2 |
| `P.stream(p, step, fin, state=[(name, KIND), ...], elem=EDGE)`; step(d, *state, *elem) -> new state; fin(d, *state) -> result | list, init=(state values) -> out |
| `P.relax(p, maximize=False)` / `P.frontier(p, act, msg, comb, ident, ...)` | G, D, C, L [, X] -> D2 |
| `P.sssp(p)` | n, s, L [, budget=INF], G -> D |
| `P.iterate(p, body, state=[...])`; body(d, *state) -> (*new_state, go) | init=(...) -> final state fields |

## Inside a body: `d.*`

| method | meaning |
| --- | --- |
| `d.call(prim, port=value, ...)` | connect a primitive; returns its output wire (a tuple if several, in signature order) |
| `d.op(a, "+", b)` | a op b; op in `+ - * / % = ! < > & \| ^ << >>` (comparisons give 1/0) |
| `a1, a2, a3 = d.fanout(a, 3)` | a number needed 3 times (numbers only) |
| `d.erase(x, ...)` / `d.erase_unused()` | drop values you do not need / drop every value still unused when the body returns |
| `d.select(c, if_true, if_false)` | c != 0 ? if_true : if_false (both are built; for numbers and small data) |
| `d.branch(c, zero, nonzero, *passed)` | switch: zero(b, *passed) if c == 0 else nonzero(b, c-1, *passed); returns their result(s) |
| `d.split(w)` / tuples | take a tuple wire apart; pass a Python tuple `(a, b)` where a tuple is expected |
| `d.nil()`, `d.cons(h, t)` | lists |
| `val, hole = d.hole(LIST(NUM))`; `h2 = d.fill_cons(hole, x)`; `d.fill(hole, d.nil())` | build a list front-to-back (e.g. in input order, carrying the hole in a walker state); return `val` |
| `d.as_depth(x)` | declare a computed number to be a depth |

Wires are not Python values: `w + 1` or `if w:` raise an error; use `d.op`, `d.select`, `d.branch`. A wire made in one
definition cannot be used in another (no Python closures over wires): pass it through the walker state, the
environment `E`, or the `*passed` arguments of `d.branch`.

## The root

```python
def prog(d, n, es):           # one argument per field of the program's input tuple
    ...
    return result             # kind checked against the contract's output type
P.prog("<program id>", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
```

Worked examples: `runs/exp14/examples_checked.py` (t3_degrees and t3_cc_largest; the same programs as the library
author's raw versions, and they compile to the same net).
