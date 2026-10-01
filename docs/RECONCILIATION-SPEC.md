# Reconciliation core: the swing workload, specified

**Finding (2026-09-28).** The PRD calls G4's workload "the reconciliation core of Orbweaver: taking scored match decisions and
applying merges, clustering and conflict checks across a live graph". A read of the Orbweaver repo found no such core.
Orbweaver decides pair by pair (blocker -> frozen-LLM head -> conformal singleton test -> staged `SUGGESTED_SAME_AS` edge ->
human accept writes `SAME_AS`). It has no union-find, no components, no must-not-link check, no property merge, and never
collapses nodes. Merges are independent per pair, so ordering matters only via the stage cap.

**Decision (Claude, on Theo's delegation).** The swing must not shrink and must be a real system, so the workload is the
function Orbweaver's pipeline implies but never implements: **reconciliation** of a graph given a matcher's scored pair
decisions. The matcher stays a model at the edge (pillar 4). The core is what the model's decisions are applied to. Semantics
that Orbweaver does fix are kept exactly: `dup_id=left`, `canonical_id=right` with left<right, so the canonical id of a merged
pair is the larger id; a decision needs a singleton prediction set (top probability >= tau); staging is idempotent per target;
merges are additive `SAME_AS` facts, never destructive. Everything else below is new and is defined here, once, in advance.

## The function

Input: a graph of `n` nodes (ids 0..n-1) with edges, per-node attributes, candidate pairs `(u, v, score)` with `u < v` and
`score` an integer per-mille in 0..1000 (a matcher's confidence), a threshold `tau`, a set of must-not-link pairs, and an
optional already-known SAME_AS set. Output: the resolved graph.

1. **Decide.** A candidate is accepted if `score >= tau`. Pairs already in SAME_AS or already implied are dropped. Duplicate
   candidates for one pair keep the highest score (ties: first occurrence).
2. **Order.** Accepted pairs are processed by descending score, ties by ascending `(u, v)`. (Deterministic; matters for 4.)
3. **Cluster.** Transitive closure of accepted merges: connected components under union-find. The canonical id of a cluster
   is its largest member id (Orbweaver's rule).
4. **Conflict-aware clustering.** A merge is skipped if it would put both ends of a must-not-link pair in one cluster, or push
   a cluster past a size cap. Skipped merges are reported as conflicts. (Order dependent, hence step 2.)
5. **Properties.** Each node has attributes `(key, value)`. A cluster's merged value per key is the majority value, ties to
   the smallest value; a key with more than one distinct value in a cluster is a property conflict.
6. **Rewrite.** Edges `(a, b)` become `(canon(a), canon(b))`, self loops are dropped, duplicates collapsed (edge weights
   summed when present). Node set becomes the canonical ids.
7. **Emit.** The new `SAME_AS` facts as `(dup, canonical)` pairs for every non-canonical member, idempotent against existing ones.

The 50 T5 kernels are these steps and the metrics around them, piece by piece; `t5_reconcile_*` compose them. G4 runs the
composed function at 100,000 nodes or more on replayed real data with a real matcher's scores.

## Real data for G4
Orbweaver's own decision data is synthetic (LLM-teacher scenarios, tiny graphs, no live pilot on disk). The best replayable
real source found is UCI record linkage (`orbweaver/external_data/uci_record_linkage`, CC BY 4.0): 99,788 records, 5,749,132
blocked candidate pairs with ground truth (20,931 positives). Scores come from a frozen matcher over the comparison
patterns. It is just under 100,000 nodes; whether attribute-value nodes count is open, and G4 may add a second real source
(OpenEA alignment, 15k x 2) if a strict 100,000-record floor is wanted. Flagged for Theo, not silently decided.
