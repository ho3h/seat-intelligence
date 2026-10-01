# exp20 plan (swing 26, recipes), frozen 2026-09-30 before any recipe code or author run

## Held-out programs (16)
Eligible pool: T3/T5 corpus programs never mentioned anywhere under runs/exp5, exp8, exp9, exp10, exp14, exp18,
exp19 (file names and file text scanned): 20 programs. Only 2 are T3 (t3_bfs_order, t3_bridges).
Excluded (no recipe plausibly applies):
- t3_bridges: needs DFS lowpoint / cycle-space reasoning; no recipe.
- t3_bfs_order: FIFO order with sorted neighbour scan; a layered BFS gives levels, not the order within a level.
- t5_prop_distinct_per_key: values are arbitrary 24-bit numbers (edge case 16777215): no bounded key space.
- t5_metric_purity: per-group max over a 2-D (pred, truth) histogram with labels up to ~1000: judged the
  weakest fit of the remaining metric programs (chosen before any run).
Chosen (all T5):
| program | recipes that plausibly apply | judgement |
| --- | --- | --- |
| t5_decide_normalise | reduce_by_key(max, pair key) + select_sorted (+ list_length/max for L) | covered |
| t5_decide_drop_known | reduce_by_key(set1, pair key) + lookup_many + filter_in_order | covered |
| t5_decide_order | filter_in_order + sort_by | covered |
| t5_decide_top_k | sort_by + take_first | covered |
| t5_decide_stage_cap | filter_in_order + sort_by + take_first | covered |
| t5_decide_stage_idem | reduce_by_key (blocked set, first index) + lookup_many + filter_in_order | covered, 2-3 recipes chained |
| t5_conflict_pairs | list_to_trie + lookup_many + reduce_by_key(set1, pair key) + select_sorted | covered |
| t5_prop_conflicts | list_to_trie + lookup_many + reduce_by_key(min and max) + count_where_trie | covered, 4 recipes |
| t5_prop_majority | list_to_trie + lookup_many + reduce_by_key(add, value) + argmax_first_trie | partial (value range) |
| t5_rewrite_edges | list_to_trie + lookup_many + reduce_by_key(set1, pair key) + select_sorted | covered |
| t5_rewrite_weighted | as rewrite_edges, reduce_by_key(add) + presence flag | covered |
| t5_rewrite_collapsed | as rewrite_edges + count_where_trie | covered |
| t5_rewrite_degrees | as rewrite_edges + reduce_by_key(inc per endpoint) + select_sorted over canonical ids | covered, long chain |
| t5_rewrite_sameas_cycle | pointer_jump + lookup_many + count_where | covered |
| t5_metric_pairwise | reduce_by_key(inc) x3 (pred, truth, joint key) + reductions | partial (label range ~1000, joint key 18 bits) |
| t5_metric_rand | as metric_pairwise | partial |
Prediction (before running): recipes cover 13/16 fully, 3 partially. The hard part left to the author is choosing
and chaining 2-4 recipes and packing pair keys.

## Recipe list (frozen before seeing any author output)
Required by the brief: lookup_many, pointer_jump, layered_bfs_count, argmax_first (list and trie),
filter_in_order, list_length_and_copy, frontier_relax (hole: combine/update), reduce_by_key (hole: combiner).
Recurring in exp8/exp9/exp10/exp14 and the T5 corpus: list_to_trie (conflict_*, sameas: T[i] = c[i]),
count_where (decide_count, reach_count), count_where_trie (reach_count, cluster_count), select_sorted
(cc_label to_list, conflict_flags fold-to-list, LEX outputs everywhere in T5), sort_by (the T5 ORDER
"descending score, ties by u then v" in 6 decide/pipeline programs), take_first (take/drop words of swing 22),
pack/unpack helpers for pair keys.
NOTE (honesty): the held-out contracts were read before this list was frozen (to pick the 16). sort_by and
take_first were added because the ORDER sentence recurs across T5, which includes held-out programs.

## Protocol
One fresh Haiku subagent per (program, condition), identical instructions except the API file list; at most 6
verify attempts through runs/exp20/attempt.py (unmodified genome.verify.verify, seed 0); randomized launch order
(seed 26); A = checked glue + primitives (exp14 checked brief), B = A + genome/lib/recipes.py + docs/RECIPES.md.
Passing nets re-verified on seeds 1, 2. Kill rule: B - A < 20 points of pass rate (seeds 0-2) -> clean negative.
