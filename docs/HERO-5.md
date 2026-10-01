# HERO-5: exact explain-by-trace for merge / seat decisions (swing 32, 2026-09-30)

Question: can "why did these two records merge / why is this guest in this section?" be answered EXACTLY from the reduction
itself? Union-find gives no reason. A net has deterministic local reductions, so provenance may be recoverable, but values are
copied and erased on the way, so naive tracing may over-attribute.

Everything below is a game: the "rules" are the host's rules over the printed org and the coarse category on the chart, and
every sentence in this document is the output of a program applied to those rules. None of it is a claim about the guests.

## Verdict (kill rule first)

**KILL RULE HIT on the hypothesis as stated.** "Answered exactly from the reduction itself" (K1, the causal set of input facts
that the tracer reports, rendered as a sentence): **0 of 100 explanations exact**, under both tracer policies.

| explanation | exact | over-inclusive | incomplete | wrong | denominator |
| --- | --- | --- | --- | --- | --- |
| K1, tracer policy F (data + control provenance) | 0 | 100 | 0 | 0 | 100 (50 hero + 50 synthetic) |
| K1, tracer policy D (data provenance only) | 0 | 0 | 100 | 0 | 100 |
| K2, trace + kernel-aware generator (T-F+G) | 100 | 0 | 0 | 0 | 100 |
| generator on all facts, no trace (G-full) | 100 | 0 | 0 | 0 | 100 |
| delta debugging by re-execution, context preserving (DDc) | 100 | 0 | 0 | 0 | 100 |
| delta debugging by re-execution, plain (DD) | 99 | 0 | 0 | 1 | 100 |
| leave-one-out re-execution (LOO) | 60 | 1 | 39 | 0 | 100 |

What the numbers say, plainly:

* **The trace itself explains nothing on these nets.** Policy F returns the *entire input* as the causal set of every decided
  value (100 of 100 decisions; and 5,170 of 5,170 sampled record labels, including records that occur in no fact at all).
  Policy D returns the empty set (100 of 100; 5,170 of 5,170). F follows every interaction dependency (data and control), D only data
  flow, which here never reaches a fact; both are useless as explanations. A second, different net
  (label-propagation cluster canon, `runs/exp10`) behaves the same way (section 4.3).
* **A working pipeline exists, but the trace adds nothing to it.** The kernel-aware generator gets 100/100 exact (the 900 classifications took 3,255
  executor runs, 0 disagreements with the reference), on the trace's causal set *and* on all
  facts without any trace (G-full 100/100), because the causal set is all facts. Delta debugging restricted to the causal set
  (T-F+DD) is the same run as delta debugging over all facts (DD): identical answers and cost, since the sets are equal.
* **The strong simple baseline wins.** Context-preserving delta debugging (DDc) is exact on 100/100, needs no kernel
  knowledge and no tracer, and costs a median of 20 reruns (hero) and 70 reruns (synthetic) per decision, max 174 and 296.
  On the 10 hero and 10 synthetic decisions I replayed through the executor that is a median 1.9 s and 17.5 s of executor time
  per decision, less than one traced run of a 2,000-record problem (median 45 s, and that run serves two decisions).
  Plain DD (the task's neutral-world definition) is exact on 99/100 and returns one unfaithful witness (section 4.2).
  Leave-one-out is cheap to state but only 60/100 (it fails whenever the evidence is redundant or the cause is a capacity
  overflow that no single fact removal repairs).
* **Tracing overhead** (section 5): the traced copy reproduces the untraced oracle's interaction count and parallel depth
  exactly on all 30 problems; annotating the input as facts costs +0.0007% to +0.021% interactions and +1 depth against the
  plain input. Wall-clock ratio traced/untraced oracle: median 1.32x for policy F (range 0.70-2.35, noisy: the machine ran at
  load 25-40). Peak memory 2.0x on the one problem I measured (1.37 GB to 2.73 GB). The provenance store is small (2,800-3,300
  distinct sets per 2,000-record problem, 37-43 million unions with a 99.7-100% memo hit rate) because almost every union is of sets already seen.
* **What this does not show:** that provenance from reductions cannot work. Positive control (section 4.1): on a keyed lookup the
  tracer returns exactly the one fact that was read, under both policies. The failure is specific to nets whose control state is
  global (a sorted candidate stream, a sequential greedy state, a broadcast relabel). I did not isolate which of these causes the
  saturation.

Files: `genome/hero5/` (tracer patch `tracer/`, `core.py`, `gen.py`, `evalx.py`, `run_eval.py`, `report.py`), `runs/hero5/`
(`eval_set.json`, `traces/`, `results_all.jsonl`, `report.md`, `tracer_tests.py`, `canon_probe.py`, logs).


## 1. Kill rule, definitions and the frozen test (written and hashed before any evaluation-set result existed)

### 1.1 Kill rule

At least 80 of the 100 explanations must be EXACT (definition 1.3). Fewer is a hit.

Two readings, fixed in advance, both reported:

* **K1 (the kill-rule reading, "from the reduction itself"):** the explanation is what the tracer reports, the causal set of
  input facts of the decided value, rendered as a sentence, with no further execution and no reference implementation in the
  loop. Two tracer policies are tested (1.5); the kill rule is evaluated on each.
* **K2 (best case pipeline):** trace, then a kernel-aware explanation generator that reads the causal set. This uses the
  reference semantics of the greedy (one logged simulation on the causal set), so it is not "the reduction itself". It is
  reported because the task asks for the generator, and because it shows what the trace is worth to a downstream explainer.

I chose K1 as the kill-rule reading after I had seen the dev-set traces (see 1.7). The evaluation-set tracing was already running
when this section was written, but I had seen only its completion lines (run time, output-correct flag), no causal set and no score. The reason is the wording of the hypothesis ("answered exactly from the reduction itself"): a generator that re-runs
the reference greedy on the trace is answering from the reference, not from the reduction.

### 1.2 What a decision, a fact and an explanation are

The kernel is the verified net `runs/exp18/t5_conflict_greedy_cap.hvm` (ordered must-not-link greedy with a size cap) on
input `(n, cap, mnl, cands)`; it outputs each record's section label (the largest id in its section). A section is a cluster.
Facts, the units an explanation may name:

* an **edge row** `(u, v, score)`: a proposed "keep together" (rule clause or matched pair, with its priority = its score);
* a **must-not-link row** `(x, y)`: the "never in one section" rule instance;
* the **cap clause**: the section size limit.

The record count `n` is structure, not a fact. The processing order is "score descending, ties by u then v", so the order of
edge rows is carried by their scores (list order in the input is arbitrary and is not a fact).

A **decision** D is one of:

* MERGE(a, b): records a and b end in the same section (any pair in one section: direct edge or multi-hop);
* REFUSE(u, v): the proposed pair (u, v) (an edge row, the *subject*) ends with u and v in different sections. Since clusters
  only grow, a skipped pair is never merged later, so this is exactly "the pair was skipped". The subject row is part of the
  question; it is always present in every world and is not counted in an explanation.

An **explanation** E is a set of facts (with their scores/order) plus a sentence naming exactly those facts.

### 1.3 EXACT (the task's definition, made operational)

The **E-alone world** W(E): the input with every edge row and MNL row outside E deleted (except the subject), the cap clause
replaced by "no cap" unless the cap clause is in E, and record ids compressed order-preservingly (the greedy depends only on
the order of ids, so this is a metamorphic identity; the run is checked against the reference on every call). "Deleted" is the
neutral replacement for a row; "no cap" is the neutral replacement for the cap.

E is **EXACT** iff all of:

* (S) sufficiency: D holds in W(E), run through the verified executor (`run_net`, Rust interpreter, decoded);
* (N) necessity of each fact: for every f in E, D fails in W(E minus f), through the executor;
* (M) minimality: no proper subset of E is sufficient. Checked exhaustively over all proper subsets with the reference
  implementation when |E| <= 14 (the reference is checked against the executor on every executor call; mismatches are
  reported), otherwise reported as 1-minimal only (N holds);
* (F) faithfulness, for MERGE decisions: D also holds in the world with E plus every blocking clause (all MNL rows and the cap)
  present. Without this test a witness can be "sufficient" only in a world where a rule that is really present would have
  blocked it.

Necessity (N) is judged in the E-alone world, not by deleting a fact from the full input, because with redundant evidence
(two chains link a and b) no single fact of either chain is necessary in the full input, and an exact explanation would not
exist. The full-input reading is reported as a diagnostic (`N_full`: how many of E's facts flip D when deleted from the
untouched input; reference implementation).

Classes (each explanation gets exactly one):

* **exact**: S, N, M, F.
* **over-inclusive**: sufficient (S) but not minimal (some fact is redundant).
* **incomplete**: not sufficient, and the reason it names is compatible with the truth (or it names nothing).
* **wrong**: not sufficient and it names a different reason than the truth; or S, N, M hold but F fails (an unfaithful
  witness: sufficient only because a real blocking rule was left out).

The reason a set "names" is read from its content: cap in E and no MNL row = capacity; MNL row and no cap = must-not-link;
both = "both" (compatible with either truth); neither = nothing. Truth is from the reference: MERGE, MNL, or CAP.

### 1.4 Decision bins (ground truth from the reference implementation only)

Per edge row the reference logs merge / no-op / skip and, for a skip, which rule blocked it (must-not-link, capacity, or
both). Skips blocked by both rules are excluded (ambiguous reason). Bins:

* **MERGE**: a pair of distinct records in one section. About one third are pairs joined by a direct edge row, two thirds are
  multi-hop pairs.
* **MNL**: refusal caused by a must-not-link pair, and not order dependent.
* **CAP**: refusal caused by the size cap (many of these are also order dependent; the flag is kept in the data).
* **ORDER**: a must-not-link refusal that flips to a merge if the subject swaps processing positions with ONE adjacent edge
  row (sharing a record) of a different score. That is the "who is placed first when rules collide" case.

### 1.5 Explanation methods

Tracer: `genome/hero5/tracer` is a copy of the depth oracle `physics/hvm2-depth` with a shadow provenance store (a set of input
facts per port slot, per wire, per redex end; hash-consed bitsets). Same rewrite rules, same round scheduler; the traced run
must reproduce the interaction count, the depth and the output of the untraced oracle (checked). Facts are seeded by naming each
input row as a definition `@fact_k`; the cap clause is `@fact_C`. Rules (unit-tested in `runs/hero5/tracer_tests.py`):

* DUP copies keep provenance, ERA drops it, NUM~CON/DUP copies keep the number's provenance.
* OPR: result = union of the two operands.
* **Policy D (data provenance)**: nothing else adds provenance. SWI selects a branch without tainting it.
* **Policy F (full provenance, data plus control)**: every interaction adds the union of the two interacting agents to what it
  creates or links (SWI's chosen branch, annihilation endpoints, commutation copies). A REF instantiates its definition with
  the REF's own provenance (unfolding is not a dependency on the other side).

The causal set of an output value is the union over the value itself and its list cell (tag, payload, head), not over the
list spine before it.

Methods (each yields a set E, then the classification 1.3):

| id | method | uses |
| --- | --- | --- |
| T-D | causal set under policy D | the reduction only |
| T-F | causal set under policy F | the reduction only |
| T-F+G | policy F causal set, then the kernel-aware generator | reference semantics on the causal set (K2) |
| T-F+DD | ddmin restricted to the policy F causal set | re-execution on the causal set |
| T-F+DDc | same, context-preserving (MERGE: MNL rows and cap stay present, only edges are minimised) | re-execution |
| DD | ddmin (delta debugging) over all facts, the strong simple baseline | re-execution only, no trace, no kernel knowledge |
| DDc | context-preserving ddmin over all facts | re-execution |
| LOO | leave-one-out: rerun with each single fact removed from the full input, keep the facts whose removal flips D | re-execution (F+1 full-size reruns) |
| G-full | the generator on all facts (no trace) | reference semantics |

The generator: one logged reference simulation on the rows in the causal set (cap only if in the set); MERGE = shortest chain
of merged edges from a to b; MNL refusal = the blocking MNL row plus the merged-edge chains from u and v to its two ends; CAP
refusal = the cap clause plus connected sub-clusters around u and v, grown alternately, of total size cap+1. If the simulation
does not reproduce the decision it falls back to the whole causal set.

### 1.6 The frozen evaluation set

`runs/hero5/eval_set.json`, sha256 `3f47748260925b29e65bef82872acb2946d827eb1feca12f5929b7aafc16c1d6`, generated by
`python3 -m genome.hero5.gen runs/hero5/eval_set.json` from reference-implementation analysis only, before any tracer output
for it existed. 100 decisions:

* **50 on the hero data**: the real 34-guest chart (`data/hero/luncheon.json`), five host rule sets (built only from printed org
  and category; see `genome/hero5/gen.py::hero_problem`): R1 colleagues+peers cap 6; R2 R1 + no rival AI labs; R3 chips beside AI
  labs + no rival AI labs, cap 7; R4 peers at small tables, cap 4, no two big-tech firms together; R5 a house mix with several
  must-not-link families, cap 6. 14 MERGE, 12 MNL, 12 CAP, 12 ORDER.
* **50 on synthetic 2,000-record reconciliation problems**: 25 problems (seeds 9100-9124) of n = 2,000 records with about 100
  entity groups of 2-8 records (361-426 edge rows), 30 noise bridges, 43-52 must-not-link rows, 14 planted order gadgets, cap in 4-7; two
  decisions each. 14 MERGE, 14 MNL, 11 CAP, 11 ORDER.

A separate dev set (`runs/hero5/dev_set.json`, sha256 `055c0490b8c1eb13f1e72abf7036916542bc526718bf31074bf9bad922b46da5`, seeds 8100+,
17 decisions) was used to debug the harness.

### 1.7 What was known when

Before the evaluation set was traced I had run the tracer on 3 hero and 3 synthetic dev problems. There, policy D gave
empty causal sets and policy F gave every fact of the problem for every record (checked on 61/61, 17/17, 79/79 and 408/408
facts). I recorded that before choosing to state K1 as the kill-rule reading. I did not look at any evaluation-set causal set or
score before this section was written (I had seen only the completion lines of the trace job).

## 2. What was run

1. `python3 -m genome.hero5.trace_all runs/hero5/eval_set.json runs/hero5/traces 3`: for each of the 30 problems, the plain
   verified net on the depth oracle and on the Rust interpreter, the annotated book on the untouched depth oracle, and the
   traced copy under policy F and policy D. Every traced run reproduced the reference labels (60 of 60) and the interaction
   count of the untraced oracle on the same book (60 of 60).
2. `python3 -m genome.hero5.run_eval ...`: for each of the 100 decisions, the nine methods of 1.5, each classified by section 1.3.
   Sufficiency (S), every single-fact deletion (N) and faithfulness (F) are run through the executor
   (`genome.executor.run_net`, Rust interpreter, decoded, compared with the reference: 3,255 runs, 0 disagreements). The
   exhaustive subset check for minimality (M) uses the reference, for sets of at most 14 facts (largest exact set: 7).
   The delta-debugging and leave-one-out *searches* use the reference as oracle (same answers), and their executor cost is
   the number of reruns plus, for every 5th decision (10 hero, 10 synthetic), a replay of the exact rerun sequence through the executor.
   As a check, `runs/hero5/dd_on_net.py` reran the DD and DDc *searches themselves* with the executor as the oracle on 60 decisions
   (all 50 hero, 10 synthetic): 120 of 120 searches returned exactly the stored answers (5,604 executor runs, 0 disagreements with the reference).
3. `python3 -m genome.hero5.report ...` produced the tables below (`runs/hero5/report.md`).

## 3. Results (all 100 decisions; hero 50 + synthetic 50)

#### Class counts, all 100 decisions (denominator 100; hero 50 + synthetic 50)

| method | exact | over-inclusive | incomplete | wrong | exact, hero /50 | exact, synthetic /50 | exact but F not required (S,N,M only) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T-D | 0 | 0 | 100 | 0 | 0 | 0 | 0 |
| T-F | 0 | 100 | 0 | 0 | 0 | 0 | 0 |
| T-F+G | 100 | 0 | 0 | 0 | 50 | 50 | 100 |
| T-F+DD | 99 | 0 | 0 | 1 | 49 | 50 | 100 |
| T-F+DDc | 100 | 0 | 0 | 0 | 50 | 50 | 100 |
| DD | 99 | 0 | 0 | 1 | 49 | 50 | 100 |
| DDc | 100 | 0 | 0 | 0 | 50 | 50 | 100 |
| LOO | 60 | 1 | 39 | 0 | 20 | 40 | 60 |
| G-full | 100 | 0 | 0 | 0 | 50 | 50 | 100 |

#### Exact per decision type (exact / decisions of that type)

| method | MERGE | MNL | CAP | ORDER |
| --- | --- | --- | --- | --- |
| T-D | 0/28 (0%) | 0/26 (0%) | 0/23 (0%) | 0/23 (0%) |
| T-F | 0/28 (0%) | 0/26 (0%) | 0/23 (0%) | 0/23 (0%) |
| T-F+G | 28/28 (100%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |
| T-F+DD | 27/28 (96%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |
| T-F+DDc | 28/28 (100%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |
| DD | 27/28 (96%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |
| DDc | 28/28 (100%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |
| LOO | 18/28 (64%) | 24/26 (92%) | 7/23 (30%) | 11/23 (48%) |
| G-full | 28/28 (100%) | 26/26 (100%) | 23/23 (100%) | 23/23 (100%) |

#### Full class breakdown per decision type

**T-D**: MERGE 0/0/28/0; MNL 0/0/26/0; CAP 0/0/23/0; ORDER 0/0/23/0   (order: exact/over-inclusive/incomplete/wrong)

**T-F**: MERGE 0/28/0/0; MNL 0/26/0/0; CAP 0/23/0/0; ORDER 0/23/0/0   (order: exact/over-inclusive/incomplete/wrong)

**T-F+G**: MERGE 28/0/0/0; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

**T-F+DD**: MERGE 27/0/0/1; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

**T-F+DDc**: MERGE 28/0/0/0; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

**DD**: MERGE 27/0/0/1; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

**DDc**: MERGE 28/0/0/0; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

**LOO**: MERGE 18/1/9/0; MNL 24/0/2/0; CAP 7/0/16/0; ORDER 11/0/12/0   (order: exact/over-inclusive/incomplete/wrong)

**G-full**: MERGE 28/0/0/0; MNL 26/0/0/0; CAP 23/0/0/0; ORDER 23/0/0/0   (order: exact/over-inclusive/incomplete/wrong)

#### Explanation size (facts named, subject excluded): median [min, max]

| method | hero | synthetic |
| --- | --- | --- |
| T-D | 0 [0, 0] | 0 [0, 0] |
| T-F | 70 [16, 79] | 438 [409, 475] |
| T-F+G | 2 [1, 6] | 2 [2, 7] |
| T-F+DD | 2 [1, 6] | 2 [2, 7] |
| T-F+DDc | 2 [1, 6] | 2 [2, 7] |
| DD | 2 [1, 6] | 2 [2, 7] |
| DDc | 2 [1, 6] | 2 [2, 7] |
| LOO | 1 [0, 6] | 2 [0, 7] |
| G-full | 2 [1, 6] | 2 [2, 7] |

#### Full-input necessity diagnostic (facts of E that flip D when deleted from the untouched input)

| method | exact explanations with every fact necessary in the full input | share of facts necessary in the full input (exact explanations) |
| --- | --- | --- |
| T-D | - | - |
| T-F | - | - |
| T-F+G | 61/100 (61%) | 202/265 (76%) |
| T-F+DD | 53/99 (54%) | 169/269 (63%) |
| T-F+DDc | 55/100 (55%) | 173/269 (64%) |
| DD | 53/99 (54%) | 169/269 (63%) |
| DDc | 55/100 (55%) | 173/269 (64%) |
| LOO | 60/60 (100%) | 135/135 (100%) |
| G-full | 61/100 (61%) | 202/265 (76%) |

#### Cost of producing the explanation (executor calls and wall clock; classification checks excluded)

| method | net runs per decision, hero median [max] | net runs per decision, synthetic median [max] | executor wall s (replayed sample of every 5th decision), hero median | same, synthetic median |
| --- | --- | --- | --- | --- |
| T-D | 0 [0] | 0 [0] | 0.0 | 0.0 |
| T-F | 0 [0] | 0 [0] | 0.0 | 0.0 |
| T-F+G | 0 [0] | 0 [0] | 0.0 | 0.0 |
| T-F+DD | 20 [174] | 70 [296] | 1.9 | 17.5 |
| T-F+DDc | 25 [174] | 70 [296] | 3.2 | 19.0 |
| DD | 20 [174] | 70 [296] | 1.9 | 17.5 |
| DDc | 25 [174] | 70 [296] | 3.2 | 19.0 |
| LOO | 71 [80] | 439 [476] | 0.0 | 0.0 |
| G-full | 0 [0] | 0 [0] | 0.0 | 0.0 |

Executor runs used to classify the explanations (sufficiency, every single-fact deletion, faithfulness): 3255; each decoded and compared with the reference implementation: 0 disagreements. Executor runs used to replay the search sequences of the timing sample: 5674. Search queries answered by the reference implementation: 53096.

#### Order sensitivity of exact explanations of refusals (swap the subject with one edge of E in the E-alone world)

* G-full, MNL: 14/26 (54%) of the exact explanations flip when the subject swaps priority with one of their edges.
* G-full, CAP: 23/23 (100%) of the exact explanations flip when the subject swaps priority with one of their edges.
* G-full, ORDER: 23/23 (100%) of the exact explanations flip when the subject swaps priority with one of their edges.
* DDc, MNL: 14/26 (54%) of the exact explanations flip when the subject swaps priority with one of their edges.
* DDc, CAP: 23/23 (100%) of the exact explanations flip when the subject swaps priority with one of their edges.
* DDc, ORDER: 23/23 (100%) of the exact explanations flip when the subject swaps priority with one of their edges.

#### Explanations that were sufficient but unfaithful (class wrong because F failed)

* DD on decision 13 (hero3 MERGE, records 20 and 29): returned facts [0, 1, 2, 3] ([(11, 19, 800), (4, 29, 800), (4, 11, 800), (19, 20, 800)]); D holds with only these rows, but not once the must-not-link rows and the cap that really exist are put back. Context-preserving DD returned [1, 4].
* T-F+DD on decision 13 (hero3 MERGE, records 20 and 29): returned facts [0, 1, 2, 3] ([(11, 19, 800), (4, 29, 800), (4, 11, 800), (19, 20, 800)]); D holds with only these rows, but not once the must-not-link rows and the cap that really exist are put back. Context-preserving DD returned [1, 4].

#### Tracing overhead (depth oracle vs the traced copy; same annotated book)

| problem | facts | untraced itrs / depth | traced itrs / depth | untraced oracle s | traced F s | traced D s | ratio F | ratio D | distinct sets F | unions F (memo hit %) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| hero1 | 61 | 574,145 / 2,919 | 574,145 / 2,919 | 0.6 | 0.9 | 0.5 | 1.54 | 0.86 | 230 | 212,246 (99.7) |
| hero2 | 63 | 611,857 / 3,128 | 611,857 / 3,128 | 0.5 | 0.6 | 0.8 | 1.24 | 1.57 | 242 | 240,014 (99.7) |
| hero3 | 17 | 194,572 / 947 | 194,572 / 947 | 0.4 | 0.3 | 0.1 | 0.70 | 0.41 | 58 | 57,066 (99.7) |
| hero4 | 71 | 772,765 / 3,357 | 772,765 / 3,357 | 0.7 | 0.9 | 1.2 | 1.37 | 1.75 | 272 | 348,627 (99.8) |
| hero5 | 79 | 884,253 / 2,419 | 884,253 / 2,419 | 0.9 | 1.1 | 0.9 | 1.21 | 1.00 | 389 | 438,576 (99.7) |
| syn9100 | 414 | 84,047,147 / 14,894 | 84,047,147 / 14,894 | 48.0 | 67.4 | 68.6 | 1.40 | 1.43 | 2,798 | 37,216,959 (100.0) |
| syn9101 | 447 | 92,764,088 / 16,352 | 92,764,088 / 16,352 | 59.3 | 75.3 | 76.4 | 1.27 | 1.29 | 3,138 | 41,108,482 (100.0) |
| syn9102 | 458 | 95,044,975 / 16,807 | 95,044,975 / 16,807 | 61.1 | 77.9 | 76.7 | 1.28 | 1.26 | 3,223 | 42,128,707 (100.0) |
| syn9103 | 451 | 92,992,984 / 16,549 | 92,992,984 / 16,549 | 68.1 | 66.2 | 60.7 | 0.97 | 0.89 | 3,131 | 41,210,485 (100.0) |
| syn9104 | 475 | 98,261,057 / 17,364 | 98,261,057 / 17,364 | 48.0 | 72.8 | 58.6 | 1.52 | 1.22 | 3,337 | 43,563,676 (100.0) |
| syn9105 | 439 | 89,097,756 / 15,837 | 89,097,756 / 15,837 | 43.0 | 67.7 | 57.3 | 1.57 | 1.33 | 3,060 | 39,470,657 (100.0) |
| syn9106 | 410 | 83,369,527 / 14,787 | 83,369,527 / 14,787 | 25.4 | 45.4 | 47.2 | 1.79 | 1.86 | 2,792 | 36,909,281 (100.0) |
| syn9107 | 433 | 88,401,043 / 15,607 | 88,401,043 / 15,607 | 29.6 | 54.8 | 54.1 | 1.85 | 1.83 | 2,883 | 39,160,818 (100.0) |
| syn9108 | 465 | 95,054,123 / 16,863 | 95,054,123 / 16,863 | 41.9 | 60.2 | 53.1 | 1.43 | 1.27 | 3,201 | 42,128,424 (100.0) |
| syn9109 | 461 | 95,280,727 / 17,079 | 95,280,727 / 17,079 | 47.8 | 63.1 | 53.7 | 1.32 | 1.12 | 3,137 | 42,232,738 (100.0) |
| syn9110 | 469 | 97,119,012 / 17,100 | 97,119,012 / 17,100 | 49.6 | 61.4 | 54.1 | 1.24 | 1.09 | 3,201 | 43,051,567 (100.0) |
| syn9111 | 463 | 96,199,636 / 17,063 | 96,199,636 / 17,063 | 49.6 | 59.1 | 50.8 | 1.19 | 1.02 | 3,181 | 42,642,010 (100.0) |
| syn9112 | 420 | 85,667,114 / 15,275 | 85,667,114 / 15,275 | 37.8 | 45.5 | 39.0 | 1.20 | 1.03 | 2,805 | 37,933,871 (100.0) |
| syn9113 | 428 | 88,412,389 / 15,781 | 88,412,389 / 15,781 | 35.8 | 45.5 | 42.8 | 1.27 | 1.20 | 3,017 | 39,163,344 (100.0) |
| syn9114 | 432 | 89,097,464 / 15,869 | 89,097,464 / 15,869 | 33.5 | 45.1 | 44.3 | 1.35 | 1.32 | 2,949 | 39,471,297 (100.0) |
| syn9115 | 436 | 89,790,075 / 15,911 | 89,790,075 / 15,911 | 35.9 | 40.7 | 37.8 | 1.13 | 1.05 | 2,966 | 39,777,756 (100.0) |
| syn9116 | 417 | 85,190,838 / 15,153 | 85,190,838 / 15,153 | 30.2 | 39.0 | 34.9 | 1.29 | 1.16 | 2,922 | 37,727,541 (100.0) |
| syn9117 | 474 | 98,034,410 / 17,347 | 98,034,410 / 17,347 | 36.7 | 44.6 | 38.0 | 1.22 | 1.04 | 2,982 | 43,462,003 (100.0) |
| syn9118 | 437 | 89,554,808 / 15,837 | 89,554,808 / 15,837 | 30.5 | 40.1 | 36.4 | 1.31 | 1.19 | 2,883 | 39,674,552 (100.0) |
| syn9119 | 437 | 89,999,050 / 15,914 | 89,999,050 / 15,914 | 30.5 | 41.0 | 36.1 | 1.34 | 1.18 | 3,036 | 39,875,989 (100.0) |
| syn9120 | 424 | 86,338,170 / 15,403 | 86,338,170 / 15,403 | 29.3 | 39.7 | 16.3 | 1.35 | 0.56 | 2,969 | 38,239,239 (100.0) |
| syn9121 | 445 | 92,518,441 / 16,478 | 92,518,441 / 16,478 | 16.4 | 38.6 | 34.7 | 2.35 | 2.11 | 2,920 | 41,004,256 (100.0) |
| syn9122 | 441 | 90,699,224 / 16,033 | 90,699,224 / 16,033 | 27.8 | 37.7 | 35.0 | 1.36 | 1.26 | 3,087 | 40,184,676 (100.0) |
| syn9123 | 415 | 84,045,090 / 14,886 | 84,045,090 / 14,886 | 26.4 | 35.4 | 31.4 | 1.34 | 1.19 | 2,854 | 37,214,893 (100.0) |
| syn9124 | 443 | 91,153,280 / 16,098 | 91,153,280 / 16,098 | 27.9 | 35.9 | 28.6 | 1.29 | 1.02 | 3,076 | 40,390,747 (100.0) |

Wall-clock ratio traced/untraced: policy F median 1.32 (range 0.70-2.35); policy D median 1.19 (range 0.41-2.11).

#### What the trace says (causal set sizes)

* policy F: the causal set equals the whole input (every fact) for 100 of 100 decisions; median share of the input 1.00.
* policy D: empty for 100 of 100 decisions; largest 0.

#### Example sentences (T-F+G, all exact; these are outputs of a game with the host's rules, not claims about the guests)

* [hero5 MERGE, 2 facts] Chamath Palihapitiya sits with David Sacks because each link in the chain was accepted and merged in priority order: Chamath Palihapitiya-Greg Brockman (score 750), Greg Brockman-David Sacks (score 750).
* [hero4 MERGE, 1 facts] Shyam Sankar sits with Alex Karp because each link in the chain was accepted and merged in priority order: Shyam Sankar-Alex Karp (score 1000).
* [hero2 MNL, 2 facts] Greg Brockman was kept out of Dario Amodei's section because the must-not-link rule forbids Greg Brockman with Dario Amodei: Greg Brockman is itself one end of that rule, and Dario Amodei is itself one end of that rule.
* [hero4 MNL, 2 facts] Satya Nadella was kept out of Elon Musk's section because the must-not-link rule forbids Satya Nadella with Elon Musk: Satya Nadella is itself one end of that rule, and Elon Musk is itself one end of that rule.
* [hero5 CAP, 7 facts] VPOTUS was kept out of Jared Isaacman's section because the size limit of 6 would be exceeded: 6 guests already with VPOTUS plus 1 already with Jared Isaacman is more than 6.
* [hero2 CAP, 7 facts] Speaker Johnson was kept out of Director Clayton's section because the size limit of 6 would be exceeded: 6 guests already with Speaker Johnson plus 1 already with Director Clayton is more than 6.
* [hero5 ORDER, 3 facts] Tom Brown was kept out of Brad Gerstner's section because the must-not-link rule forbids Tom Brown with Greg Brockman: Tom Brown is itself one end of that rule, and Greg Brockman was already seated with Brad Gerstner via Greg Brockman-Brad Gerstner (score 750). Those links were settled first (scores 750 against this pair's 750; equal scores go by id order).
* [hero3 ORDER, 3 facts] Dario Amodei was kept out of Sanjay Mehrotra's section because the must-not-link rule forbids Dario Amodei with Greg Brockman: Dario Amodei is itself one end of that rule, and Greg Brockman was already seated with Sanjay Mehrotra via Greg Brockman-Sanjay Mehrotra (score 800). Those links were settled first (scores 800 against this pair's 800; equal scores go by id order).
* [syn9100 MNL, 3 facts] record 544 was kept out of record 578's section because the must-not-link rule forbids record 544 with record 116: record 544 is itself one end of that rule, and record 116 was already seated with record 578 via record 116-record 578 (score 700). Those links were settled first (scores 700 against this pair's 700; equal scores go by id order).
* [syn9100 MERGE, 2 facts] record 1299 sits with record 1712 because each link in the chain was accepted and merged in priority order: record 281-record 1299 (score 850), record 281-record 1712 (score 1000).
* [syn9101 CAP, 6 facts] record 1337 was kept out of record 1700's section because the size limit of 5 would be exceeded: 2 records already with record 1337 plus 4 already with record 1700 is more than 5.
* [syn9102 ORDER, 3 facts] record 887 was kept out of record 1220's section because the must-not-link rule forbids record 887 with record 764: record 887 is itself one end of that rule, and record 764 was already seated with record 1220 via record 764-record 1220 (score 850). Those links were settled first (scores 850 against this pair's 700; equal scores go by id order).


## 4. Analysis

### 4.1 Tracer controls (`runs/hero5/tracer_tests.py`, all pass)

* Sum of two facts, with a third copied by a DUP and a fourth erased: the sum carries exactly the two operand facts, both
  copies carry the third, the erased fact is absent. (Both policies.)
* Keyed lookup in a 4-leaf tree of facts, all four keys: the answer carries exactly the one leaf that was read. (Both policies.)
  This is the positive control: where the net's data flow is local, the trace is exact.
* Maximum of four facts by comparisons: policy D returns the single fact the answer was copied from (exact); policy F returns
  all four (every fact that was compared). So policy F over-attributes even in a tiny net by design, which is the "naive tracing
  over-attributes" effect in its smallest form.
* A switch on a fact selecting a constant: policy D returns the empty set, policy F returns the fact.

### 4.2 Why delta debugging needs the context, and what "faithful" caught

Plain DD works in the E-alone world, exactly as the task's definition (ii) says. On decision 13 (hero rule set R3, a MERGE of two
chip makers) it returned four edge rows that connect the two guests through a chain that goes through an AI-lab pair which the
must-not-link rule forbids; alone they merge, but once the MNL rows that exist are put back the chain breaks. It is sufficient
and 1-minimal but not the reason the guests are together. The faithfulness test (F) caught it (class wrong), and DDc, which keeps
the blocking clauses in every test world during a MERGE, returned the two-row witness (one shared AI-lab guest) instead. With
F dropped, all nine methods' S,N,M-only exact counts are in the last column of the first table.

### 4.3 The trace on a different net (`runs/hero5/canon_probe.py`, `canon_probe.log`)

`runs/exp10/t5_cluster_canon.hvm` (label propagation over channels, a different algorithm from the sorted greedy) on
random cluster edge lists of 64 / 512 / 2,000 records with 44 / 242 / 581 edge facts, output = each record's canonical id, all
runs equal to union-find. Median components have 4-5 edges. Policy F: the causal set of a record's label is the whole input in
every case (44/44, 242/242, 581/581 median; a median of 40, 237 and 576 facts lie outside the record's own component). Policy D:
empty. So the saturation is not a property of the greedy alone. I did not test a net with tree-shaped input (which should
localise control state); RECON-REALDATA's tree-input nets are the obvious candidate.

### 4.4 What the trace could have bought

If the causal set had been small, T-F+DD would have been much cheaper than DD, because its search space would be the causal set
and not the input. On the synthetic problems the input has 409-475 facts and the exact explanations have 1-7, so the possible
saving was about two orders of magnitude in search space. The trace delivered none of it: the causal set equals the input, so
T-F+DD is the same search as DD (same answers, same rerun counts in the cost table).

### 4.5 Order

For refusals, the exact explanations are order sensitive: swapping the subject's priority with one of the explanation's own edges
flips D in 23 of 23 CAP and 23 of 23 ORDER decisions and in 14 of 26 MNL decisions (an MNL refusal where the forbidden pair is the subject
row itself does not depend on order). The English sentences for ORDER decisions state which links were settled first.

## 5. Tracing overhead

Table in section 3. In short: interactions and parallel depth are identical to the untraced oracle (the tracer is a passive
shadow; a real parallel runtime would pay for the set unions in every interaction); the annotated input costs at most +0.021%
interactions and +1 depth against the plain input because each fact row is one extra REF unfolding; the traced oracle is
1.32x the untraced oracle in wall-clock (median), 2.0x in resident memory (one measurement), and both traced policies are
single-threaded like the oracle. For scale: the plain verified net on the multi-threaded Rust interpreter takes a median 11 s
(range 3.7-26 s, loaded machine) on a 2,000-record problem, 0.2 s on the hero problems; the traced oracle takes a median 45 s
(hero: under 1.2 s).

## 6. Caveats

* **The kill-rule reading (K1) was fixed after I saw the dev-set traces** (1.7). The evaluation set and its hash were fixed first.
  If K2 (trace + generator) were the reading, the kill rule is not hit (100/100), but so is the same generator without a trace.
* **One net family plus one probe.** The nets are the verified `t5_conflict_greedy_cap` (100 decisions) and a label-propagation
  canon (a size probe, not classified). Nets written for locality (keyed lookups, tree input) were only tested on the toy controls.
* **Two tracer policies.** A value-sensitive or counterfactual tracer (a policy between D and F) was not tried, and the
  cause of the saturation (sequential greedy state, broadcast relabel, sorted-candidate stream, or the linked-list input walk) was
  not isolated. I did not test whether a list-free input changes the result.
* **Exactness is defined in the E-alone world** (1.3). Only 61 of 100 generator explanations have every fact necessary when
  deleted from the untouched input; the rest have redundant alternative evidence in the full input (hero cliques, synthetic bridges).
  A definition that demands necessity in the full input would leave those decisions with no exact explanation.
* **Excluded decisions.** Refusals blocked by both rules are excluded because the reason is ambiguous: 291 of 1,624 skips in the
  synthetic problems (18%) and 0 of 82 in the hero problems. Merge decisions are 1/3 direct-edge pairs (10 of 28), which are easy.
* **The generator is written for this kernel** (edge rows, MNL rows, cap). DD is generic. G-full and T-F+G use the reference
  semantics (one logged simulation), which is why they do not count as "from the reduction". Minimality was checked exhaustively
  with the reference; only S, N and F ran on the executor, plus the whole delta-debugging sequence for the replayed sample.
* **Hero rule sets are host's rules in a game**, built only from the printed org and coarse category on the chart; R3 uses cap 7
  (chosen so that its refusals are single-reason). Every sentence in this document is program output about those rules, not a claim about a guest.
  Six guests are unlabelled and carry no rule. Hero decisions come 6 each from R3 and R5 (ORDER), 10 from R4 and 2 from R2 (MNL).
* **Timing is noisy.** The machine was shared (load 25-40); the interaction and depth equalities are exact, wall-clock ratios are
  not. The replayed sample for cost is 10 + 10 decisions.
* Not modified: PHYSICS.md, the depth oracle (`physics/hvm2-depth` is untouched; the tracer is a copy in `genome/hero5/tracer`),
  the exp18 nets, the corpus.

## 7. Reproduce

```
python3 runs/hero5/tracer_tests.py
python3 -m genome.hero5.gen runs/hero5/eval_set.json          # sha256 3f477482...16c1d6 (frozen before any trace)
python3 -m genome.hero5.trace_all runs/hero5/eval_set.json runs/hero5/traces 3
python3 -m genome.hero5.run_eval runs/hero5/eval_set.json runs/hero5/traces runs/hero5/results.jsonl 4
python3 -m genome.hero5.report runs/hero5/eval_set.json runs/hero5/traces runs/hero5/results_all.jsonl runs/hero5/report.md
```
(Build the tracer once: `cd genome/hero5/tracer && cargo build --release --offline`, with `DEVELOPER_DIR=/Library/Developer/CommandLineTools`.)

