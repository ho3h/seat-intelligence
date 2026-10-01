"""OpenSanctions Pairs -> reconciliation slices (swing 20, G4 slice).

compact(): one pass over the 409 MB file -> integer pairs (entity index = order of first appearance), cached as a pickle
under data/opensanctions/ (gitignored, CC BY-NC).
slice_(N, seed): whole positive-closure clusters. The clusters that contain a gold conflict (a negative judgement inside a
positive-closure cluster) come first, then clusters in order of first appearance in the file, until N entities. Slice ids
0..N-1 are a seeded random permutation, so ids carry no cluster information. Returns
  n, accepted edges (u < v, score 1000), noise edges (negatives, score uniform in [0, tau)), must-not-link pairs.
Everything is a function of the edge list; the encoder never sees the components.
"""
from __future__ import annotations
import gzip, json, os, pickle, random, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "data/opensanctions/pairs-20251209.json.gz")
CACHE = os.path.join(ROOT, "data/opensanctions/pairs-compact.pkl")
TAU = 600


def compact():
    if os.path.exists(CACHE):
        return pickle.load(open(CACHE, "rb"))
    ids, pos, neg = {}, [], []
    nid = lambda x: ids.setdefault(x, len(ids))
    with gzip.open(SRC, "rt") as f:
        for line in f:
            d = json.loads(line)
            a, b = nid(d["left"]["id"]), nid(d["right"]["id"])
            (pos if d.get("judgement") == "positive" else neg).append((a, b))
    out = dict(n=len(ids), pos=pos, neg=neg)
    pickle.dump(out, open(CACHE, "wb"))
    return out


def uf_components(n, pairs):
    par = list(range(n))
    def find(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for a, b in pairs:
        ra, rb = find(a), find(b)
        if ra != rb: par[ra] = rb
    return [find(i) for i in range(n)]


_G = {}
def _global():
    if not _G:
        d = compact()
        root = uf_components(d["n"], d["pos"])
        members = collections.defaultdict(list)
        for i, r in enumerate(root): members[r].append(i)   # i ascending = first appearance
        order = sorted(members, key=lambda r: members[r][0])
        gold = [(a, b) for a, b in d["neg"] if root[a] == root[b]]
        _G.update(d=d, root=root, members=members, order=order, gold=gold)
    return _G


def slice_(N, seed=0, tau=TAU):
    g = _global(); d, root, members = g["d"], g["root"], g["members"]
    conf_roots = list(dict.fromkeys(root[a] for a, b in g["gold"]))
    chosen, seen, total = [], set(), 0
    for r in conf_roots + g["order"]:
        if r in seen: continue
        if total + len(members[r]) > N and total > 0 and r not in conf_roots:
            if total >= N: break
            continue            # skip a cluster that would overshoot; keep filling with smaller ones
        seen.add(r); chosen.append(r); total += len(members[r])
        if total >= N: break
    ents = [e for r in chosen for e in members[r]]
    rng = random.Random(1_000_003 * seed + N)
    perm = list(range(len(ents))); rng.shuffle(perm)
    sid = {e: perm[i] for i, e in enumerate(ents)}
    n = len(ents)
    acc = sorted({(min(sid[a], sid[b]), max(sid[a], sid[b])) for a, b in d["pos"] if a in sid and b in sid})
    mnl = sorted({(min(sid[a], sid[b]), max(sid[a], sid[b])) for a, b in d["neg"] if a in sid and b in sid})
    noise = [(u, v, rng.randrange(0, tau)) for u, v in mnl]
    edges = sorted([(u, v, 1000) for u, v in acc] + noise)
    gold_in = [(min(sid[a], sid[b]), max(sid[a], sid[b])) for a, b in g["gold"] if a in sid]
    return dict(n=n, tau=tau, edges=edges, mnl=mnl, gold=gold_in, clusters=len(chosen))


if __name__ == "__main__":
    import sys, time
    t = time.time(); g = _global()
    print("entities", g["d"]["n"], "pos", len(g["d"]["pos"]), "neg", len(g["d"]["neg"]), "gold conflicts", len(g["gold"]),
          "conflict clusters", len(set(g["root"][a] for a, b in g["gold"])),
          "sizes", sorted(len(g["members"][r]) for r in set(g["root"][a] for a, b in g["gold"])), f"{time.time()-t:.0f}s")
    for N in map(int, sys.argv[1:]):
        s = slice_(N)
        print(N, "n", s["n"], "edges", len(s["edges"]), "accepted", sum(1 for e in s["edges"] if e[2] >= s["tau"]),
              "mnl", len(s["mnl"]), "gold in slice", len(s["gold"]), "clusters", s["clusters"])
