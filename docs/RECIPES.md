# RECIPES: algorithm templates with typed holes (swing 26, exp20, 2026-09-30)

Code: `genome/lib/recipes.py` (the library), `genome/lib/test_recipes.py` (unit tests through `genome.verify`),
`runs/exp20/` (plan, briefs, author runs, results). Built on `genome/lib/glue.py` (docs/TYPED-GLUE.md), which is built
on `genome/lib/graphprims.py` (docs/GRAPH-LIB.md). glue.py and graphprims.py are unchanged.

## 1. What a recipe is

glue checks the wiring between primitives but leaves the algorithm to the author. A recipe packages a whole
algorithm (walks, keyed updates, multicast lookups, fixpoint rounds) as ONE primitive with a typed port signature.
The author CHOOSES a recipe and FILLS its holes: small Python functions (a key, a predicate, a value, a combiner)
that receive the composer `d` and wires. Everything is compiled through glue, so the checker still catches
linearity, kind and arity mistakes, and `P.build()` still lints the emitted net.

```python
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib.glue import Program, NUM, DEPTH, LIST, TRIE, TUP, EDGE, WEDGE, INF
from genome.lib import recipes as R

P = Program()
# 1. make recipe instances at top level: R.<recipe>(P, "<unique name>", <element kind>, <holes...>)
keep = R.filter_in_order(P, "keep", WEDGE, lambda d, u, v, s, tau: R.ge(d, s, tau), env=NUM)
# 2. connect them inside bodies with d.call, like any primitive
def prog(d, tau, cands):
    return d.call(keep, list=cands, E=tau)
P.prog("t5_decide_filter", prog)
P.write(os.path.join(os.path.dirname(os.path.abspath(__file__)), "net.hvm"))
```

Rules for holes:
* A hole is `f(d, *fields [, E])`. A tuple element is passed as separate fields: for `WEDGE` elements `(u, v, s)`
  the hole is `f(d, u, v, s)` (plus `E` when the recipe has an environment).
* Fields a hole does not use are erased automatically. Fields it uses must be used once each (`d.fanout` for
  more).
* Use `d.op`, `d.select`, and the helpers below. Never Python `if`/`+` on wires.
* `recipe.help()` prints the port signature. `d.call` returns the outputs in the order listed.

## 2. The recipes

`elem` is the list element kind: `NUM`, `EDGE` = (u v), `WEDGE` = (u v w), or `TUP(NUM, ...)`.

### Lists

| recipe | ports (in -> out) | holes | edge-case semantics |
| --- | --- | --- | --- |
| `list_length_and_copy(P, name, elem, copies=1, key=None)` | `list` -> `n`, [`mx`], `c1`..`c<copies>` | `key(d, *f)` -> num (optional) | `[]` gives n = 0, mx = 0, empty copies. A list cannot be DUPed: use this whenever the input list is needed more than once. |
| `list_to_trie(P, name, elem, pad=0)` | `list`, `L` -> `t` with `t[i]` = i-th element | none | Leaves past the end hold `pad`. Needs len <= 2^L. |
| `filter_in_order(P, name, elem, pred, env=None)` | `list` [, `E`] -> `o` | `pred(d, *f [, E])` -> nonzero keeps | Input order, repeats kept, `[]` gives `[]`. |
| `count_where(P, name, elem, pred, env=None)` | `list` [, `E`] -> `n` | `pred` | Every occurrence counts. `[]` gives 0. |
| `take_first(P, name, elem)` | `list`, `k` -> `o`, `rest` | none | The first k elements (all of them if the list is shorter). `rest` = max(0, len - k). k = 0 gives `([], len)`. |
| `argmax_first(P, name, elem, value, env=None)` | `list` [, `E`] -> `mx`, `idx` | `value(d, *f [, E])` -> num < 16777215 | Ties go to the lowest index. `[]` gives (0, 16777215). All zeros give (0, 0). |
| `sort_by(P, name, elem, key)` | `list` -> `o` | `key(d, *f)` -> k or (k1, k2, ...) | A stable sort, ascending and lexicographic. Equal keys keep input order, and repeats are kept. For descending on s, use `d.op(1000, "-", s)` (or `16777215 - s`). Keys can be any 24-bit numbers. |

### Keyed

| recipe | ports | holes | semantics |
| --- | --- | --- | --- |
| `lookup_many(P, name, elem, keys, nkeys=1)` | `list`, `V` (trie[num]), `L` -> `o`: list of (fields..., V[k1], ...) | `keys(d, *f)` -> k or (k1, k2) | Input order; every original field is kept and the looked-up values are appended. V is consumed. Keys >= 2^L read leaf k mod 2^L. All lookups are answered at once (multicast). |
| `reduce_by_key(P, name, elem, keyval, combine="add", ident=None, env=None)` | `list`, `L` [, `E`] -> `H` (trie[num]) | `keyval(d, *f [, E])` -> (k, v), or just k for `inc`/`set1`; `combine`: `add` `max` `min` `or` `set` `inc` `set1` or `f(d, leaf, v)` | Untouched leaves hold `ident` (0; INF for min). To skip an element, send the identity. A group whose values sum to 0 looks like an absent group, so keep a `set1` presence trie or store v + 1. k < 2^L. |

### Tries (after a `reduce_by_key` / `list_to_trie`)

| recipe | ports | holes | semantics |
| --- | --- | --- | --- |
| `select_sorted(P, name, pred, emit, leaf_kind=NUM, env=NUM)` | `t`, `L`, `E` -> `o` | `pred(d, x, i, E)`, `emit(d, x, i, E)` -> value or tuple | A list in ASCENDING KEY ORDER of emit for every leaf where pred holds. This is how sorted or de-duplicated outputs are made. Test `i < n` (n in E) when padding leaves could pass. |
| `count_where_trie(P, name, pred, leaf_kind=NUM, env=NUM)` | `t`, `L`, `E` -> `n` | `pred(d, x, i, E)` | Counts leaves. Guard padding with `i < n`. |
| `argmax_first_trie(P, name, value, leaf_kind=NUM, env=NUM)` | `t`, `L`, `E` -> `mx`, `idx` | `value(d, x, i, E)` -> (ok, v) | Only leaves with ok != 0 take part. Ties go to the smallest index (so "ties to the smallest value" when keyed by value). No participant gives (0, 16777215). |

### Graphs and pointers

| recipe | ports | holes | semantics |
| --- | --- | --- | --- |
| `frontier_relax(P, name, combine="min", msg=None, mode=None, ident=None)` | `G` (adj), `D`, `C`, `L` -> `D2` | `combine`: `min` `max` `or` `add` or `f(d, a, b)`; `msg(d, m, w)` | "fixpoint" mode: new = combine(old, incoming), and a vertex sends when it changed. "wave" mode (the default for add): add incoming and send it on, for path counting on a level DAG. Default msg: m + w for min (so BFS needs w = 1, and w = 0 means a free edge); m for max/or; m * w for add. Seed via C (for example 0 at s with INF elsewhere for min, or 1 at s for or/add). |
| `layered_bfs_count(P, name, directed=True)` | `n`, `s`, `es`, `L` -> `D`, `C` | none | D[v] = BFS distance (16777215 if unreachable). C[v] = number of shortest paths mod 2^24, with C[s] = 1 (the empty path) and 0 when unreachable. Needs n >= 1 and s < n. |
| `pointer_jump(P, name, rounds=8)` | `list` (p) -> `o` | none | o[i] = p applied 2^rounds times (the root when chains are < 256 long). `[]` gives `[]`. On a cycle, o[i] is some node ON the cycle, so test `p[o[i]] == o[i]` with lookup_many to detect it. |

### Helpers (call inside a body: they take `d`)

| helper | meaning |
| --- | --- |
| `R.depth_for(P, d, m)` | trie depth for keys 0..m-1, **safe for m = 0** (never `lg(n - 1)` with n = 0 = a 16M-leaf trie) |
| `R.ge(d, a, b)`, `R.le(d, a, b)` | a >= b, a <= b as 1/0 (no `tau - 1` wrap at tau = 0) |
| `R.not0(d, a)` | a != 0 |
| `R.min2(d, a, b)` | (min, max) of two numbers (normalise a pair) |
| `R.max2(d, a, b)` | max |
| `R.pack(d, a, b, bits)`, `R.unpack(d, k, bits)` | pair key `a << bits | b` and back; `bits` may be a depth wire. Needs b < 2^bits and 2*bits <= 24 |

## 3. Composition patterns

**Look up c[i] for every pair (clustering programs).**
```python
lc  = R.list_length_and_copy(P, "lc", NUM)
tri = R.list_to_trie(P, "ct", NUM)
lk  = R.lookup_many(P, "lk", EDGE, lambda d, a, b: (a, b), nkeys=2)   # -> list of (a, b, c[a], c[b])
def prog(d, c, pairs):
    n, c1 = d.call(lc, list=c)
    L1, L2 = d.fanout(R.depth_for(P, d, n), 2)
    return ... d.call(lk, list=pairs, V=d.call(tri, list=c1, L=L1), L=L2) ...
```

**Sorted distinct pairs (dedup + lexicographic sort by a trie keyed by the packed pair).**
```python
lc  = R.list_length_and_copy(P, "lc", EDGE, key=lambda d, u, v: R.max2(d, u, v))        # n, max id, copy
rk  = R.reduce_by_key(P, "rk", EDGE, lambda d, u, v, B: R.pack(d, u, v, B), "set1", env=NUM)
sel = R.select_sorted(P, "sel", lambda d, x, i, B: x, lambda d, x, i, B: R.unpack(d, i, B))
def prog(d, es):
    n, mx, c = d.call(lc, list=es); d.erase(n)
    B1, B2, B3 = d.fanout(R.depth_for(P, d, d.op(mx, "+", 1)), 3)   # bits per id
    L1, L2 = d.fanout(d.as_depth(d.op(B1, "*", 2)), 2)               # pair-key depth = 2 * bits
    H = d.call(rk, list=c, L=L1, E=B2)
    return d.call(sel, t=H, L=L2, E=B3)
```
Keep pair-key tries small: 2 x 8 bits (ids < 256) gives 65,536 leaves, which is fine. Do not build 2^20+ leaves.

**Group-by then pick.** `reduce_by_key` (count with `inc`, or sum with `add`) followed by `argmax_first_trie`
(majority, ties to the smallest key), `count_where_trie` (number of groups), or `select_sorted` (the groups in order).

**Filter, sort, take.** `filter_in_order` -> `sort_by` -> `take_first` (for example: accept by threshold, order
by descending score then u then v, then stage the first cap).

## 4. Edge-case checklist

* n = 0 or an empty list: use `R.depth_for` (depth 0), or `d.branch(n, empty, nonempty, ...)`.
* `>= tau`: use `R.ge(d, s, tau)`, never `s > tau - 1`.
* Weight 0 vs 1: shortest paths in edges need w = 1 on every edge.
* INF = 16777215 means "none/unreachable". Numbers wrap at 2^24.
* Ties: `argmax_first*` give the lowest index, and `sort_by` is stable.
* Padding leaves (i >= n) exist in every trie. Guard with `i < n` in trie holes.
* Keys >= 2^L alias. Choose L from the largest key + 1.

## 5. Tests and cost (`python3 -m genome.lib.test_recipes`, log `runs/exp20/test_recipes.log`)

All 16 wrappers pass `genome.verify.verify` on seed 0 (edge + random + 64-128-size + exhaustive sweep). Five of them
are real corpus programs outside the exp20 held-out set: t5_decide_filter, t5_decide_count, t3_cc_label,
t3_sp_count and t5_rewrite_sameas_roots.

| recipe (test) | depth, large case | interactions, large case | note |
| --- | --- | --- | --- |
| filter_in_order (t5_decide_filter) | 534 | 8,777 | same as Sonnet's hand composition (533) |
| count_where (t5_decide_count) | 435 | 4,541 | |
| take_first | 1,038 | 4,000 | |
| list_length_and_copy (2 copies + max) | 1,167 | 7,003 | |
| argmax_first | 1,049 | 5,505 | |
| list_to_trie + lookup_many | 781 | 104,224 | |
| reduce_by_key (min, inc) + argmax_first_trie | 902 | 161,276 | |
| reduce_by_key + count_where_trie (distinct values) | 1,576 | 72,254 | |
| reduce_by_key (pair key) + select_sorted | 1,661 | 1,197,796 | 2^14 to 2^16-leaf pair trie |
| sort_by (3 keys) | 1,052 | 1,443,900 | O(n 2^L) rank sort |
| sort_by (1 key) | 1,042 | 947,336 | |
| frontier_relax min (t3_cc_label) | 2,660 | 415,417 | exp14 checked: 2,585 / 416,180 |
| frontier_relax or (reachability) | 1,996 | 116,025 | |
| layered_bfs_count directed (t3_sp_count) | 4,895 | 540,611 | Sonnet's own net, packaged |
| layered_bfs_count undirected | 3,488 | 839,728 | |
| pointer_jump (t5_rewrite_sameas_roots) | 2,118 | 722,952 | 8 rounds (Sonnet's net: 2,116) |

A recipe costs what the hand composition it came from costs, because it IS that composition. The expensive
recipes are sort_by (quadratic work, linear depth) and wide pair-key tries (2^16 leaves).

## 6. Measurement: weak authors with and without recipes (exp20)

**Programs.** `runs/exp20/PLAN.md` was frozen before any recipe code or author run. It lists 16 held-out programs,
**all 16 of them T5**. Only 20 T3/T5 programs are unmentioned in runs/exp5, exp8, exp9, exp10, exp14, exp18 and
exp19. Just two of those are T3 (bfs_order, bridges), and both were excluded as not covered by any recipe.

**Recipe list.** It is not independent of the held-out set. I read the held-out contracts before freezing the list,
and **sort_by and take_first were added after reading them**, because the "descending score, then u, then v" ORDER
recurs across T5. Before the runs, I also composed t5_decide_order myself with filter_in_order + sort_by, as a
feasibility check.

**Protocol.**
* One fresh Haiku subagent per (program, condition), 32 runs.
* Identical prompts that differ only in the API file list (`runs/exp20/prompts.json`).
* Randomised launch order (seed 26), at most 6 attempts, and seed 0 through the unmodified `genome.verify`.
* Passing nets were re-verified on seeds 1 and 2.
* Condition A = checked glue + primitives (the swing-23 condition). Condition B = A + recipes.py + this document.

All 32 runs completed; none was dropped.

Deviations, applied to both conditions and logged in `runs/exp20/nudges.log`:
* **Shared verification lock.** Nets that hung held the lock for minutes, and callers waiting in the queue were
  killed by their 600 s tool timeout. From the run midpoint, `attempt.py` changed in three ways:
  * the per-case timeout dropped from 60 s to 10 s;
  * a net identical to the previous attempt is refused without using an attempt;
  * the contract's edge examples are pre-screened at 5 s each.
* **Messages to stopped authors.** Authors who stopped early got one "continue" nudge (as in exp14). Authors who
  believed killed calls had been counted got a factual message with their recorded count. In all, 13 A runs and 5 B runs got at
  least one such message (not counting the two rate-limit resumes); the imbalance favours A.
* **Rate limit.** Two runs (A conflict_pairs, B rewrite_weighted) were interrupted by an API rate limit and resumed.
* **Timeout re-checks.** Every timeout failure was re-run with long timeouts (`reverify_notes.txt`):
  * two turned out to be wrong answers and were reclassified;
  * B prop_majority's four prescreen timeouts ran correctly under recheck on the smallest edge example; the program
    passed at attempt 5 either way.
  * No attempt predates the other agent's `pkill -f hvm` (about 05:00; the first attempt was logged at 05:03), so
    0 are "stale".

### Results (`runs/exp20/results.json`, `classify.json`)

| program | A: attempts, result | B: attempts, result | recipes in B's final build |
| --- | --- | --- | --- |
| t5_decide_normalise | 6, fail | 6, fail | sort_by, list_to_trie, select_sorted |
| t5_decide_drop_known | 2, fail | 6, **pass** | reduce_by_key, lookup_many, filter_in_order |
| t5_decide_order | 3, fail | 1, **pass** | filter_in_order, sort_by |
| t5_decide_top_k | 6, fail | 1, **pass** | sort_by, take_first |
| t5_decide_stage_cap | 0 (never compiled), fail | 1, **pass** | filter_in_order, sort_by, take_first |
| t5_decide_stage_idem | 3, fail | 3, **pass** | none (hand-composed streams) |
| t5_conflict_pairs | 6, fail | 1, **pass** | list_to_trie, sort_by |
| t5_prop_conflicts | 2, fail | 3, **pass** | lookup_many, reduce_by_key (custom combiner), count_where_trie |
| t5_prop_majority | 4, fail | 5, **pass** | lookup_many, filter_in_order, reduce_by_key, argmax_first_trie |
| t5_rewrite_edges | 3, fail | 1, **pass** | lookup_many, filter_in_order, reduce_by_key, select_sorted |
| t5_rewrite_weighted | 1, fail | 6, fail | the same chain |
| t5_rewrite_collapsed | 2, **pass** | 4, fail | lookup_many, reduce_by_key, count_where_trie |
| t5_rewrite_degrees | 3, fail | 6, fail | the same chain + a hand-written walk |
| t5_rewrite_sameas_cycle | 6, fail | 1, **pass** | pointer_jump, lookup_many, count_where |
| t5_metric_pairwise | 3, fail | 4, fail | list_to_trie only |
| t5_metric_rand | 6, fail | 5, fail | reduce_by_key |
| **pass, seed 0** | **1/16** | **10/16** | |
| **pass, seeds 0-2** | **1/16** | **10/16** (every seed-0 pass also passed seeds 1-2) | |
| mean attempts, passing / all | 2.0 / 3.5 | 2.3 / 3.4 | |
| GlueErrors caught before running | 334 | 139 | |
| failed attempts by class | algorithm 42, edge 7, perf 6 (+1 program never compiled) | algorithm 16, edge 11, recipe misuse 13, perf 4 | |

**Paired by program:** B only 10, A only 1 (rewrite_collapsed), both 0, neither 5. A one-sided sign test on the 11
discordant pairs gives p = 12/2048 = 0.006. The difference is **+56 points** (62.5% vs 6.25%).

**Sensitivity to the post-hoc recipes.** Drop the 4 programs whose B pass used sort_by or take_first (order, top_k,
stage_cap, conflict_pairs): B still passes 6/12 and A 1/12 (+42 points). Also drop stage_idem, which B passed without
any recipe: B passes 5/11 and A 1/11.

**Depth and interactions of passing nets** (seed 0, median over large cases):

| program | depth | itrs |
| --- | --- | --- |
| B decide_order | 813 | 455k |
| B stage_cap | 796 | 138k |
| B top_k | 2,077 | 4.9M |
| B conflict_pairs | 905 | 64k |
| B prop_conflicts | 1,541 | 309k |
| B prop_majority | 1,836 | 700k |
| B rewrite_edges | 1,861 | 4.8M |
| B sameas_cycle | 3,094 | 822k |
| B stage_idem | 417 | 167k |
| B drop_known | 1,376 | **51.6M** |
| A rewrite_collapsed | 1,007 | 3.5M |

All pass seeds 0-2. drop_known's 51.6M comes from a 2^24-leaf-scale pair trie, which is correct but wasteful. The
recipe nets cost what their recipes cost: wide pair-key tries and sort_by account for most of the interactions.

### Verdict

**Kill rule not hit: a positive result.** B beats A by 56 points of pass rate on seeds 0-2: 10/16 vs 1/16, paired
10-1, p = 0.006. The baseline is lower than in swing 23 (A 1/16 here vs 6/10 there). These programs need keyed
lookups, sorting and de-duplication, and the A authors almost never found an algorithm for them: 42 of 55 failed A
attempts are "algorithm", mostly stubs and placeholders after "a trie cannot be read twice".

**Recipes used.** 12 of the 15 were used.
argmax_first (list), frontier_relax and layered_bfs_count were not used, because there were no graph programs in the
set. By my judgement no program needed a new recipe: all 16 are composable from the library plus primitives. Two
packagings would have removed most remaining failures:
* `sorted_distinct_pairs` / `group_by_pair`: pack + reduce_by_key + select_sorted with the padding and occupancy
  guards built in. It would have covered rewrite_degrees, rewrite_weighted, rewrite_collapsed and normalise.
* a histogram-pair-count recipe for the metric programs (Σ C(k, 2) per group).

**What weak authors still cannot do with recipes.**
1. **Fill holes correctly.** There were 13 recipe-misuse failures:
   * a select_sorted pred that ignores occupancy, so padding leaves are emitted or counted;
   * a pair key packed into an L-deep trie instead of 2L;
   * a combiner identity of 0 that collides with real values;
   * "sum 0" confused with "absent". This last trap is documented in RECIPES.md and was still hit.
2. **Derive an algorithm the library does not spell out.** The metric programs (Σ C(k, 2) over three histograms) and
   normalise (max per normalised pair) failed in both conditions.
3. **Size tries.** Several nets used depth 16-24 tries on tiny inputs (timeouts, stack overflow), even though
   depth_for exists.
4. **Keep going.** Most authors stopped after 1-3 attempts and needed a nudge.

**How big a library would T3+T5 need?** By the corpus families:
* T5 (50 programs): the 15 recipes cover the decide, conflict, rewrite and prop families. About 5 more would cover
  nearly all of T5: sorted_distinct_pairs/group_by, a histogram sum, label relabel/rank for arbitrary labels,
  first-occurrence dedup, and a sequential greedy union-find for conflict_greedy and the reconcile pipelines. That is
  about 20 in all.
* T3 (50 programs): about 20-25 further algorithm-specific recipes, each used by one to three programs. Examples: the
  all-sources bitset BFS (msbfs), Kahn topo order, SCC, DFS lowpoint (bridges/articulation), Prim/MST, girth,
  augmenting paths, max-flow, greedy colouring, clique, Euler, DAG DP, k-core peel, APSP/eccentricity, triangles.
* Estimate: about 40-50 recipes for about 90% of T3+T5, with a long tail.

Because 13 of 44 failed B attempts were hole-filling mistakes, recipe count alone does not bound weak-author success.
Recipes need their guards built in.
