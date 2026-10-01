# Methodology review: can a small local model learn the net medium? (2026-09-29/30)

Scope: the local-model lane (Qwen3-4B-Instruct-2507-4bit, MLX, LoRA SFT on Luna-authored data) as it stood after `runs/local/*`.
Nothing frozen was changed (corpus, primers, `contract.py`, `verify.py`, `gates/*` except one appended STATUS bullet).
New code: `genome/exp/` (sets, sample, score, metrics, repair, build_ei, trainset_probe). New manifests: `data/tasksets/{iid_test,ei_pool,train_probe}.json`.
Runs: `runs/exp/` (`*.json` raw samples, `*.scored.json` per-sample verdicts, `*.metrics.txt`). New adapter: `adapters/native_ei1`. Paid API spend: $0.

## Part 1. Problems, ranked

**1. The held-out test measures transfer to unseen data types, not learning of the medium.** 131 of 144 held-out tasks have an
(input, output) type signature that never occurs in training: tree to tree (30), tuple of lists (30), `(n, list of triples)` (47).
Training has 0 tree-output tasks and 12 tuple-input tasks (all `(u24, u24)`). The short prompt leaves out the primer, so the tuple
and variant encodings are never stated. The native contract even says "per the primer" when no primer is given. Checked in
`runs/local/c_native_holdout.json`: 0 of 154 outputs for tuple-input tasks take the input tuple apart at `@prog`. 95 of 288 outputs
reuse the primer's list-accumulator skeleton (`(* (a a))`) whatever the task. Bend fails the same way, for example
`def prog(xs, ys)` for a single tuple argument. Both routes are at the floor (2/288 and 1/288), so that result says nothing about
nets. The difficulty of held-out tasks for a model that knows the types was not measured: the calibration run was dropped for time.

**2. The recipe is too thin: the native adapter cannot reproduce its own training tasks.** On training tasks it was fitted on,
native_v1 gets pass@1 30.9% (123 tasks x 4 samples, 95% CI 24.6-37.2%). bend_v1 gets 87.6% (125 x 2, 82.4-92.4%). The native
validation loss bottoms out at 0.28 (Bend 0.10). The recipe is one teacher solution per task, positives only, rank-8 LoRA on 16 of
36 layers, about 3 epochs, a 4-bit base, and no verifier signal during training. So Bend has mainly a generalization problem, and
the native route has an underfitting problem first. Theo's reading is right. For scale: Luna solves 785 of 824 native tasks, but
only 51% on the first attempt (Bend 97%), so native targets are hard even for the teacher. The 39 tasks Luna never solved (25 of
them pipeline) are simply missing from the native SFT set.

**3. The training distribution is narrow and the generator has run out of new tasks.** 82% of train tasks are pipeline, reduce or
position, all list to number or list. Six of the eight train families have no unused variants left (sortlike 11, arith 23,
rangefn 22, treefold 45, scan 48, position 177), so "824 tasks" is really 2 combinatorial families plus about 330 near-templates.
The old in-distribution test is 30 pipeline/reduce tasks plus 2 position tasks.

**4. The route comparison is confounded.**
- Pretraining familiarity: Bend reads like Python.
- Length: a net is about 2.3x the tokens of the Bend program (median 208 vs 90).
- Prompts are not matched: the Bend prompt declares the types, the native prompt points to a primer it does not include.
- Unlike the API arms, the local model gets one shot, with no linter feedback.

On a fair test the gap is mostly composition. Native pass@1 falls from 62% to 16% to 1% on 1-, 2- and 3-stage pipelines. Bend
falls from 98% to 54% to 36%.

**5. Samples are small and reporting has holes.**
- The old in-distribution test is 32 tasks x 2 samples at temperature 0.7, so 12/64 has a task-level CI of roughly ±15 points.
- `local_eval` merges recon_count and recon_uf into one "recon" family (`id.split("_")[1]`).
- Run metadata does not record whether the short prompt was used.
- The exhaustive sweep for recon tasks only builds invalid, all-below-threshold inputs (u = v = 0, score ≤ 2): harmless, but it tests nothing.

**Checked and fine:**
- Descriptions match the references in all 14 generator families. Some internal kind labels are misnamed (for example `maxs` is "distinct nodes"), but not the descriptions.
- The 4 s verify timeout: 0 of 41 in-distribution failures change at 30 s.
- Output truncation: 11 of 288 held-out outputs, 0 of 64 in-distribution.
- The empty `<think></think>` the model emits is harmless.

## How much of the failure is "wire appears only once"?
native_v1 on the fair test (960 samples):
- 62% fail the static check, and 490 samples (51% of all) contain a wire that appears only once.
- Only 38% pass the static check (Bend compiles 90%). Of the nets that pass it, 38% are correct (Bend 53%).

A mechanical repair that erases each lone wire (`genome/exp/repair.py`) makes only 16 of those 490 nets correct (3%). So the lone
wire is mostly a symptom of dataflow the model does not know how to route, not a forgotten `*`.

Would a per-line edge-list interface remove it? It would turn this error class into a syntax impossibility. The upper bound is
+20 points of pass@1 (490 samples passing at the current 38%), but the repair result points to a gain in the low single digits,
with longer outputs further from pretraining. A cheaper test of the same idea is constrained decoding that tracks open wires. It
matters only once composition is learnable.

## Part 2. Next step options, ranked
1. **(chosen) Fair test plus a free static filter plus one round of expert iteration.** Zero dollars, about 2.5 GPU-hours. It tests self-improvement from exact reward.
2. **Stronger SFT, measured on a train-set probe first.** Rank 32-64 on all layers, more epochs, bf16 base, 2-4 solutions per task. About 1-2 hours. After this run, I now rank it first.
3. **Learning curves for both routes (N = 100/300/746).** About 1.5 hours. Separates familiarity from the medium.
4. **Bend-X control with renamed keywords.** About 1 hour.
5. **Constrained or open-wire-aware decoding.** About half a day of development.
6. **Stage vocabulary (the G2 words) to make composition shallow.**
7. **Re-split the held-out set by type coverage, with encodings in the prompt.**

## Part 3. Results
Fair test `iid_test`: 120 unseen pipeline and reduce tasks, temperature 0.7, top_p 0.95. CIs are 95% task-bootstrap.

| Adapter | Samples/task | pass@1 | pass@k | Static filter, best of n | Static-clean rate |
|---|---|---|---|---|---|
| native_v1 | 8 | 14.4% [9.9, 19.1] | pass@8 37.5% | 25.8% | 37.6% |
| bend_v1 | 8 | 47.4% [40.9, 54.4] | pass@8 81.7% | 47.5% | 90.1% |
| native_ei1 (EI round 1) | 4 | 10.2% [6.0, 14.8] | pass@4 17.5% | 16.7% | 27.5% |

Expert iteration: native_v1 sampled 4 times on 428 pool tasks and 153 tasks had a pass. That gave 260 verified rows, plus an
equal replay of the original rows, trained for 130 iterations resumed from v1. On the same tasks the change is **−4.2 points**
(95% CI −6.9 to −1.7). The self-generated data solved only 4 of 90 three-stage pipelines, so it reinforced easy cases.

These runs were not done because the coordinator stopped the session: the control run (same iterations, original data), the
Bend expert-iteration round, the greedy-decoding run and the base-model calibration. So "expert iteration hurts" cannot be told
apart from "more training at a constant 1e-4 learning rate hurts".

## What I would do next
1. Fix the native recipe until the train-set probe (`data/tasksets/train_probe.json`) is at least 80%.
2. Then run learning curves for both routes, plus Bend-X.
3. Use expert iteration only with a curriculum over stage count, with each stage as its own definition. This fits the vocabulary lane.
4. Rebuild the held-out split so its types are covered in training and its encodings are in the prompt.
