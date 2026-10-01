# TYPED-GLUE: can a checked composition layer rescue weak authors? (swing 23, exp14, 2026-09-30)

Question: GRAPH-LIB (`docs/GRAPH-LIB.md`) showed that a strong author composes correct, shallow nets from 24 graph
primitives on the first try, while a Haiku author failed 2 of 4 programs on wiring mistakes in the GLUE between
primitives (linearity, a value used twice without a DUP, an unused wire, a half-written `@prog`). The library removes
wiring inside primitives; this swing adds a layer that removes or flags wiring between them, then measures whether
it raises weak authors' pass rate.

Code: `genome/lib/glue.py` (the layer), `genome/lib/test_glue.py` (tests), `runs/exp14/` (briefs, harness, author
directories with every attempt, results).

## 1. The checker design (`genome/lib/glue.py`)

The author never writes HVM text. Composition is Python function calls on named wires:

* A `Program` holds primitive instances. Every graphprims primitive has a factory (`P.update(name, act)`,
  `P.reduce(name, leaf, op, index, env)`, `P.stream(p, step, fin, state, elem)`, ...) that emits exactly the
  graphprims definitions and returns a `Prim` with a **declared port signature**: for each port its name, direction
  (in / out), kind, and connection count (exactly once, or 0..1 with a default such as `base=0`, `w=0`,
  `tail=[]`, `budget=INF`). Positional HVM trees such as `(t (L (0 ((Lh E) (H H2)))))` become keyword ports
  (`d.call(sc, t=D, L=L7, Lh=L8, E=n, H=H0)`), and constants the author used to have to remember (the `0` base of
  `to_list`, the `*` payload of `inc`) are filled in by the signature.
* Every definition the author used to write as text (the `@prog` root, walker `step`/`fin`, leaf bodies, scatter
  keys, frontier `act`/`msg`, custom update acts, iterate bodies, switch branches) is a Python function
  `f(d, *wires) -> wires`. `d` is a per-definition composer with `call`, `op`, `fanout`, `erase`,
  `erase_unused`, `select`, `branch`, `split`, `nil`/`cons`, `hole`/`fill`/`fill_cons`, `as_depth`.
* Kinds: `num`, `depth`, `trie[k]`, `list[k]`, tuples, `adj`, `request-trie`, `hole[k]`, `any`, and per-call type
  variables (`get`, `to_list` are generic in the leaf kind). The `@prog` input fields and output kind are read from
  the frozen contract (`P.prog("t3_degrees", fn)`).

Errors raised before anything runs (each names the author's source line; all 21 are exercised by `test_glue.py`):

| mistake | when | message (abridged) |
| --- | --- | --- |
| unconnected input port | call | `input port k is not connected in this call of update u (act inc)` + full signature |
| unknown port / output passed as input | call | `port n does not exist on lg`, `port L is an OUTPUT (it is returned by d.call)` |
| value used twice (port connected twice) | second use | `wire L1 (depth, copy 1 of L, made at build.py:91) is used a second time (update dinc port L); it was already used at build.py:93` |
| value needed twice without a DUP | second use | same, plus `write a, b = d.fanout(L, 2)`; `fanout` inserts the DUP chain `{a {b c}}` |
| trie / list used twice | second use, `fanout` | `a trie[num] cannot be duplicated safely (HVM2 DUPs are unlabelled)... mc_deliver_keep returns a copy` |
| unused output or argument | end of body | `1 value(s) never used: L (depth, argument L of fin of stream w)`; fix with `d.erase(x)` or the auto-erase helper `d.erase_unused()` |
| kind mismatch | call / return | `expected trie[?], got list[(num num)] es from argument in1 of @prog`; `expected depth, got num ... use d.as_depth(x)`; contract output kind |
| wrong arity | body compile | `step of stream w is called as f(d, L:depth, h:trie[num], e0:num, e1:num)... your function takes 4 (d, L, h, e)`; `must return 2 value(s) (L, h); returned 1`; `returned None... forgot return?` |
| wire captured from another definition | use | `wire L belongs to @prog, but is used in step of stream w... pass it through the state / environment / branch arguments` |
| Python arithmetic / `if` on a wire | use | `wires are not Python numbers; use d.op(...)`; `use d.select or d.branch` |
| non-copyable environment | factory | `the environment of reduce r is copied to every leaf by DUPs, so it must be numbers` |
| branches of different kinds, name clashes | compile / factory | `kind mismatch at branch nonzero case`, `name clash: a is already update a` |

What it cannot check: semantics (key ranges `>= 2^L` alias, padding leaves `i >= n`, the `n = 0` guard, which
algorithm to use, contract edge cases). As a last safety net `P.build()` runs the verifier's static lint on the whole
emitted net (raw-text bodies are still accepted for backward compatibility).

## 2. Cost check: the checked API costs nothing

`runs/exp14/examples_checked.py` re-expresses the strong author's t3_degrees and t3_cc_largest (runs/exp8) through
the checked API (`python3 -m genome.lib.test_glue --cost` reproduces the comparison):

| program | exp8 hand glue depth / itrs (seed 0) | checked API depth / itrs | seeds 0-2 |
| --- | --- | --- | --- |
| t3_degrees | 464 / 69,287 | **464 / 69,283** (0.00%, -0.006%) | pass |
| t3_cc_largest | 2,783 / 537,149 | **2,783 / 537,147** (0.00%, -0.0004%) | pass |

The emitted nets are the graphprims nets plus the author's bodies; the only differences are the `n = 0` branch as
its own definition and one wire-to-wire link, which cost nothing. The existing graphprims suite still passes (29/29,
`runs/exp14/test_graphprims.log`; graphprims.py is unchanged).

## 3. The measurement

**Programs** (10). These are T3/T5 programs from the composability table's class A that do not appear in runs/exp5,
exp8 (including exp8/weak), exp9 or exp10: t3_reach_count, t3_sp_len, t3_cc_label, t3_sp_count, t5_decide_count,
t5_decide_filter, t5_decide_singleton, t5_conflict_count, t5_conflict_flags, t5_rewrite_sameas_roots.

**Protocol** (`runs/exp14/brief/`). Each (program, condition) pair got one fresh subagent. Both conditions received the
same instructions (the prompt differs only in the API files), the same contract brief (`<prog>.md`: contract, types,
sizes, the frozen edge examples), the same common notes (`COMMON.md`), PHYSICS.md, GRAPH-LIB.md and graphprims.py.
Each also got two worked examples, t3_degrees and t3_cc_largest, in its own API: raw for unchecked
(`examples_raw.py`, the strong author's exp8 code) and checked (`examples_checked.py`, which compiles to the same
nets).

- Unchecked also received `API_UNCHECKED.md`.
- Checked also received `API_CHECKED.md`, `PORTS_CHECKED.txt` and glue.py.

There were no algorithm hints beyond the library docs. Running the builder was free and unlimited. The only way to
test a net was `runs/exp14/attempt.py`, which runs the unmodified `genome.verify.verify` on seed 0 with 3 workers
(one verification machine-wide at a time), logs every attempt, keeps each net, and refuses a 7th attempt. The
condition order per program was randomised (`launch_order.json`, seed 23). Passing nets were re-verified on seeds 1
and 2 by `results.py`. Failed attempts were hand-classified in `classify.json`. The GlueErrors raised while building
in the checked condition (free, pre-run catches) were logged to `glue_errors.log`.

### Haiku (the weak author)

| program | unchecked: attempts, result | checked: attempts, result | checked-condition GlueErrors caught before running |
| --- | --- | --- | --- |
| t3_reach_count | 6, fail (6 glue) | **1, pass** | 2 |
| t3_sp_len | 5, pass (3 glue + 1 semantic: w = 0) | 2, pass (1 semantic: w = 0) | 1 |
| t3_cc_label | 1, pass | 2, pass (1 semantic: D seeded with iota) | 0 |
| t3_sp_count | 6, fail (5 glue + 1 semantic) | 3, fail (3 algorithm: counted 1 path of 2)* | 14 |
| t5_decide_count | 6, fail (5 glue + 1 semantic: tau = 0 wraps) | **2, pass** (1 semantic: tau = 0 wraps) | 3 |
| t5_decide_filter | 6, fail (6 glue) | **1, pass** | 5 |
| t5_decide_singleton | 6, fail (6 glue: 2 lint, 4 parse errors) | 6, fail (1 semantic, 1 bypass, 4 stale) | 20 |
| t5_conflict_count | 6, fail (6 glue) | **1, pass** | 3 |
| t5_conflict_flags | 6, fail (6 glue) | 6, fail (6 bypass: raw HVM by hand) | 1 |
| t5_rewrite_sameas_roots | 6, fail (6 glue) | 6, fail (2 algorithm, 4 bypass) | 7 |
| **pass, seed 0** | **2/10** | **6/10** | |
| **pass, seeds 0-2** | **2/10** | **6/10** (every seed-0 pass also passed seeds 1 and 2) | |
| mean attempts (passing / all) | 3.0 / 5.4 | 1.5 / 3.0 | 56 in total |
| failed attempts by class | glue 49, semantic 3 | glue in glue-built nets **0**; bypass 11, stale 4, semantic 4, algorithm 5 | |

\* The checked t3_sp_count author stopped after attempt 1 while it still had attempts left. It was told once to
continue (the same nudge was given to the checked t5_decide_singleton author), made attempts 2-3, then went silent.
It is scored as 3 attempts, fail.

Legend for the classes:

- **glue**: the verifier's static check rejected the net (linearity, brackets), the net failed to parse, or the
  output was non-canonical because of wiring (`*` or an unresolved DUP returned).
- **semantic**: a contract edge case. Weight 0 was copied from the unweighted example into a shortest-path program;
  `score > tau - 1` wraps at tau = 0; ties on all-zero input.
- **algorithm**: the wrong algorithm.
- **bypass**: the author abandoned the glue API and submitted hand-written HVM, which was rejected by lint.
- **stale**: build.py kept raising GlueErrors (in nested branches), and the author resubmitted an old hand-written
  net unchanged (identical md5 on attempts 2-6).

Paired by program:

- 4 programs pass only with the checker: reach_count, decide_count, decide_filter, conflict_count.
- 0 programs pass only without it.
- 2 pass in both: sp_len, cc_label.
- 4 fail in both: sp_count, decide_singleton, conflict_flags, sameas_roots.
- A one-sided sign test on the 4 discordant pairs gives p = 1/16.

**Wiring failures:** 49 of 52 failed unchecked attempts (94%) are glue. **No net produced by the glue API failed on
wiring**, because `P.build()` lints its own output: all 9 failing nets that the API built ran and failed on semantics or algorithm. Every lint reject in the
checked condition was a hand-written net: the author left the API (3 authors, 15 attempts), which is the remaining
wiring failure mode.

Depth and interactions of passing nets are the same library algorithms in both conditions (seed 0, median over the
large cases):

| program | unchecked depth / itrs | checked depth / itrs |
| --- | --- | --- |
| t3_sp_len | 2,052 / 276,021 | 2,052 / 276,021 |
| t3_cc_label | 2,585 / 416,184 | 2,585 / 416,180 |
| t3_reach_count | - | 4,729 / 245,986 |
| t5_decide_count | - | 348 / 4,989 |
| t5_decide_filter | - | 2,551 / 8,722 |
| t5_conflict_count | - | 528 / 50,415 |

The one checked pass with a weak net is t5_conflict_count. Its author hard-coded `L = lg(255)` in place of computing
the length and used a sequential peek walk. It passes seeds 0-2, but only because the contract caps n at 144.

### Sonnet (a stronger author, same protocol)

| | unchecked | checked |
| --- | --- | --- |
| pass, seed 0 | 10/10, all at attempt 1 | 10/10, all at attempt 1 |
| pass, seeds 0-2 | 10/10 | 10/10 |
| GlueErrors caught before running | - | 1 (wrong arity for a bare-list input) |

Sonnet is at the ceiling in both conditions, so the checker neither helps nor hurts it. Its nets are also good. It
invented pointer doubling by multicast for sameas_roots, a two-frontier shortest-path DAG count for sp_count, and
level-synchronous frontier counting in the raw condition. Depth is comparable across its two conditions (for example
decide_filter 533 checked vs 4,582 raw, sameas 2,116 vs 3,084, conflict_flags 903 vs 828).

Harness notes:

- Several `attempt.py` calls were killed by the 120 s tool timeout while they waited for the verification lock
  (exit 144). A killed call never completed a verification and was not logged, so it was not counted.
- Two unchecked Sonnet authors (t5_decide_filter and t5_decide_singleton) wrote plain HVM and used no primitive; both
  passed.

## 4. Verdict

**Kill rule not hit: a positive result.** For the weak author, the checked API raised the pass rate from 2/10 to 6/10
(+40 points, seeds 0-2 identical). It cut wiring failures from 49 of 52 failed attempts (unchecked) to 0 of 9 failed attempts on API-built nets.
It halved attempts per passing program (3.0 to 1.5), and it caught 56 mistakes before running at no attempt cost:

| mistake the checker caught | count |
| --- | --- |
| value used twice or needing a fanout | 21 |
| wrong arity | 13 |
| wire captured across definitions | 10 |
| unused value | 4 |
| forgot `return` | 4 |
| other | 4 |

It costs 0% depth and less than 0.01% interactions. The sample is small (n = 10 programs, 1 run each; p = 1/16
paired), and the effect is confined to authors below the ceiling (Sonnet: 10/10 in both conditions).

**What the weak author still cannot do.**

1. **Algorithm design.** sp_count needs "count shortest paths" as a layered frontier. sameas_roots needs pointer
   jumping or root propagation. Haiku found neither in either condition, while Sonnet found both.
2. **Contract edge cases.** Weight 0 was copied from an example, `tau - 1` wraps at 0, ties, s == t, and n = 0 when
   n is not an input field.
3. **Staying inside the API when it gets hard.** 3 of 10 checked authors fell back to raw HVM, and all 3 failed
   there.
4. **Nested control flow.** `d.branch` needs every outer wire passed explicitly, and a three-level comparison
   produced 20 GlueErrors that the author could not resolve.

**Next layer.**

1. **Algorithm templates as named recipes** with typed holes, each a verified composition:
   - `count_where(trie, pred)`
   - `lookup_many(values, keys)` (mc_request + deliver)
   - `list_length_and_copy` (bare-list inputs)
   - `layered_bfs_count`
   - `pointer_jump(p, rounds)`
   - `argmax_first`
   - `filter_in_order`

   The Sonnet solutions are the source: every Sonnet algorithm above is one recipe.
2. **Glue ergonomics:**
   - `d.branch` / `d.select` auto-capture outer wires (lambda lifting done by the composer);
   - `fanout` of tuples of numbers;
   - `>=`, `<=` and `min`/`max` operators so authors stop writing `x > t - 1`;
   - a `P.length(list)` helper.
3. **Harness:** refuse to submit a net older than build.py (the stale-net failure) and reject hand-written nets in
   the checked condition.
