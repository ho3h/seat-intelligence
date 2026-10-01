"""Structure of OpenSanctions Pairs: what reconciliation on real analyst judgements looks like."""
import gzip, json, sys, collections, statistics as S
path = "data/opensanctions/pairs-20251209.json.gz"
pos, neg, uns = [], [], []
ids = {}; schema = collections.Counter(); keys = None
def nid(x):
    return ids.setdefault(x, len(ids))
with gzip.open(path, "rt") as f:
    for line in f:
        d = json.loads(line)
        if keys is None: keys = [k for k in d.keys()]; print("keys:", keys)
        a, b = nid(d["left"]["id"]), nid(d["right"]["id"])
        j = d.get("judgement")
        (pos if j == "positive" else neg if j == "negative" else uns).append((a, b))
        schema[(d["left"]["schema"], d["right"]["schema"])] += 1
n = len(ids)
print(f"entities {n}, positive {len(pos)}, negative {len(neg)}, unsure {len(uns)}")
print("top schema pairs:", schema.most_common(6))
par = list(range(n))
def find(x):
    while par[x] != x: par[x] = par[par[x]]; x = par[x]
    return x
for a, b in pos:
    ra, rb = find(a), find(b)
    if ra != rb: par[ra] = rb
sizes = collections.Counter(find(i) for i in range(n))
dist = collections.Counter(min(s, 10) for s in sizes.values())
print("clusters", len(sizes), "size histogram (10 = 10+):", dict(sorted(dist.items())), "largest", max(sizes.values()))
inconsistent = sum(1 for a, b in neg if find(a) == find(b))
print(f"negative judgements inside a positive-closure cluster (analyst inconsistency): {inconsistent}")
print(f"unsure inside a cluster: {sum(1 for a, b in uns if find(a) == find(b))}")
# how much transitive closure adds: implied pairs vs explicit positives
implied = sum(s * (s - 1) // 2 for s in sizes.values())
print(f"pairs implied by transitive closure {implied} vs explicit positive pairs {len(pos)} (x{implied/max(1,len(pos)):.2f})")
