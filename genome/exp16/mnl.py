"""Must-not-link handling for swing 20 (RECONCILIATION-SPEC step 4, no size cap).

Route: unconstrained label propagation in the net (canon + the list of must-not-link pairs whose ends share a component,
both checked exactly against Python), then the ordered greedy ONLY inside the conflicted components. Exactness argument:
merges only ever happen inside an LP component; a merge in a component without a violated must-not-link pair can never
be blocked (a blocking pair would have both ends in that component), so those components are final as LP left them, and
components are independent, so the greedy can run per conflicted component. The greedy itself is a host-side step here
(sequential by specification); it consumes the net's conflict list, which the digest check proved equal to the reference.
We check the composed result against the full greedy over the whole slice.
usage: python3 -m genome.exp16.mnl N..."""
import json, os, sys, collections
from .data import slice_
from .run import reference, greedy_mnl, RUNS


def restricted_greedy(s, canon, conflicts):
    tau = s["tau"]; bad = {c for a, b, c in conflicts}
    out = list(canon)
    edges = collections.defaultdict(list); mnl = collections.defaultdict(list); verts = collections.defaultdict(list)
    for u, v, sc in s["edges"]:
        if sc >= tau and canon[u] in bad: edges[canon[u]].append((u, v, sc))
    for a, b in s["mnl"]:
        if canon[a] in bad and canon[a] == canon[b]: mnl[canon[a]].append((a, b))
    for i, c in enumerate(canon):
        if c in bad: verts[c].append(i)
    skipped, work = [], 0
    for c in bad:
        vs = verts[c]; sub = dict(n=len(vs), tau=tau)
        idx = {x: i for i, x in enumerate(vs)}               # vs ascending, so local order = global order
        sub["edges"] = [(idx[u], idx[v], sc) for u, v, sc in edges[c]]
        sub["mnl"] = [(idx[a], idx[b]) for a, b in mnl[c]]
        lc, sk = greedy_mnl(sub); work += len(sub["edges"])
        for i, x in enumerate(vs): out[x] = vs[lc[i]]
        skipped += [(vs[u], vs[v]) for u, v in sk]
    return out, sorted(skipped), work


if __name__ == "__main__":
    for N in map(int, sys.argv[1:]):
        s = slice_(N); canon, conf = reference(s)
        full, full_sk = greedy_mnl(s)
        rc, rsk, work = restricted_greedy(s, canon, conf)
        gold = s["gold"]; gold_n = [(min(a, b), max(a, b)) for a, b in gold]
        det = {(a, b) for a, b, c in conf}
        clusters = {canon[a] for a, b in gold_n}
        res_pairs = sum(1 for a, b in gold_n if rc[a] != rc[b])
        res_clusters = sum(1 for c in clusters if all(rc[a] != rc[b] for a, b in gold_n if canon[a] == c))
        rec = dict(N=N, gold_pairs=len(gold_n), gold_detected=sum(1 for p in gold_n if p in det),
                   conflict_clusters=len(clusters), self_pairs=sum(1 for a, b in gold_n if a == b),
                   gold_pairs_resolved=res_pairs, clusters_fully_resolved=res_clusters,
                   skipped_merges=len(rsk), greedy_edges_processed=work,
                   accepted_edges=sum(1 for e in s["edges"] if e[2] >= s["tau"]),
                   equals_full_greedy=(rc == full and rsk == sorted(full_sk)))
        print(json.dumps(rec), flush=True)
        with open(os.path.join(RUNS, "mnl.jsonl"), "a") as f: f.write(json.dumps(rec) + "\n")
