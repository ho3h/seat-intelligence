# Common notes (both conditions)

You compose an HVM2 net for ONE program from the graph primitive library `genome/lib/graphprims.py`
(documented in `docs/GRAPH-LIB.md`; the medium is described in `PHYSICS.md`).

## Workflow

1. Write `build.py` in your working directory. Running it must write `net.hvm` in the same directory.
   Run it as often as you like (`python3 <your dir>/build.py`).
2. Test the net ONLY with: `python3 runs/exp20/attempt.py <COND: A or B> <PROG> <your dir>/net.hvm`
   It runs the static check and the hidden test suite (seed 0) and reports PASS, or the smallest failing input with
   the expected and actual output, or the static-check / runtime error. **Each call is one attempt; you have 6.**
   Stop at the first PASS.
3. Do not run `hvm`, `genome.executor`, `genome.verify` or `genome.verify.lint_net` yourself, and do not write your
   own test runner: attempt.py is the only way to test.

## Library facts that matter for every program (read GRAPH-LIB.md for the rest)

* A trie of depth `L` has `2^L` leaves, keyed by vertex id. For `n >= 1` vertices use `L = lg(n - 1)`.
  `n = 0` would give `lg(16777215) = 24` (a huge trie), so guard `n == 0` separately (switch on n).
* Keys `>= 2^L` alias to `key mod 2^L`. Leaves with index `>= n` exist (padding) and hold the initial value:
  when you reduce/filter/fold over the whole trie, make padding leaves contribute nothing (test `i < n`).
* 16777215 (INF) is the usual "unreachable" value. Numbers are 24-bit and wrap.
* A trie, a list or a request trie must not be duplicated with a DUP. Numbers may be.
* `stream` walks a list with a state; `update` applies keyed updates; `reduce`/`fold`/`to_list`/`filter_list`
  traverse a trie; `relax`/`sssp`/`frontier` run fixpoint rounds over an adjacency trie; `mc_request` +
  `mc_deliver` answer many keyed lookups at once.
