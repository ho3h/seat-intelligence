"""HERO-5 problem and decision generation (ground truth from the reference implementation only; no tracer output)."""
from __future__ import annotations
import json, random, itertools, hashlib, os, sys
from .core import Problem, greedy_log, ROOT

HERO_JSON = os.path.join(ROOT, "data", "hero", "luncheon.json")


# ------------------------------------------------------------------ hero: 5 rule sets over the real 34-guest chart
def _guests():
    return json.load(open(HERO_JSON))["seats"]


def _pairs(idx):
    return [(a, b) for a, b in itertools.combinations(sorted(idx), 2)]


def hero_problem(k: int) -> Problem:
    """Game rules only.  Inputs to a rule: the printed org and the coarse category (no guesses, no personal claims)."""
    g = _guests()
    n = len(g)
    cat = {}
    for i, s in enumerate(g): cat.setdefault(s["category"], []).append(i)
    org = {}
    for i, s in enumerate(g):
        if s["org"]: org.setdefault(s["org"], []).append(i)
    edges = {}
    def add(a, b, s):
        a, b = min(a, b), max(a, b)
        if a != b: edges[(a, b)] = max(edges.get((a, b), 0), s)
    def same_org(s):
        for o, m in org.items():
            for a, b in _pairs(m): add(a, b, s)
    def clique(c, s):
        for a, b in _pairs(cat.get(c, [])): add(a, b, s)
    def cross(c1, c2, s):
        for a in cat.get(c1, []):
            for b in cat.get(c2, []): add(a, b, s)
    def rival(c):   # "no two guests of category c from different orgs in one section"
        return [(a, b) for a, b in _pairs(cat.get(c, [])) if g[a]["org"] != g[b]["org"]]
    cats = [c for c in cat if c != "unlabelled"]
    cap, mnl, name = 6, [], ""
    if k == 1:
        name = "R1 colleagues+peers, cap 6"
        same_org(1000)
        for c in cats: clique(c, 600)
    elif k == 2:
        name = "R2 R1 + no rival AI labs, cap 6"
        same_org(1000)
        for c in cats: clique(c, 600)
        mnl = rival("ai_lab")
    elif k == 3:
        name = "R3 chips beside AI labs + no rival AI labs, cap 7"
        cap = 7
        same_org(1000); cross("chips", "ai_lab", 800)
        mnl = rival("ai_lab")
    elif k == 4:
        name = "R4 peers at small tables (cap 4), no two big-tech firms together"
        cap = 4
        same_org(1000)
        for c in cats: clique(c, 700)
        mnl = rival("big_tech")
    elif k == 5:
        name = "R5 house mix, cap 6"
        same_org(1000); clique("software_security", 900); cross("investor", "ai_lab", 750)
        clique("chips", 650); clique("government", 600)
        mnl = sorted(set(rival("ai_lab") + rival("big_tech") + [tuple(sorted((a, b))) for a in cat["investor"] for b in cat["chips"]]))
    else:
        raise ValueError(k)
    rows = sorted(edges.items())
    r = random.Random(1000 + k)
    r.shuffle(rows)                       # list order is arbitrary in the contract
    pr = Problem(n=n, cap=cap, mnl=sorted(set(mnl)), edges=[(a, b, s) for (a, b), s in rows], name=name)
    pr.names = {i: s["name"] for i, s in enumerate(g)}
    return pr


# ------------------------------------------------------------------ synthetic 2,000-record reconciliation problems
def synth_problem(seed: int, n=2000, groups=100) -> Problem:
    r = random.Random(seed)
    ids = list(range(n)); r.shuffle(ids)
    pos = 0
    edges = {}
    def add(a, b, s):
        a, b = min(a, b), max(a, b)
        if a != b and (a, b) not in edges: edges[(a, b)] = s
    members = []
    for _ in range(groups):
        sz = r.choices([2, 3, 4, 5, 6, 7, 8], [22, 24, 18, 14, 10, 7, 5])[0]
        grp = ids[pos:pos + sz]; pos += sz
        members.append(grp)
        for j in range(1, sz):
            add(grp[j], grp[r.randrange(j)], r.choice([1000, 950, 900, 850, 800, 750]))
        for _ in range(r.choice([0, 0, 1, 2])):
            a, b = r.sample(grp, 2); add(a, b, r.choice([900, 800, 700, 600, 500]))
    mnl = set()
    def addm(a, b):
        a, b = min(a, b), max(a, b)
        if a != b: mnl.add((a, b))
    # bridges between groups (noise that causes conflicts) and MNL between records of the bridged groups
    for _ in range(30):
        g1, g2 = r.sample(range(groups), 2)
        a, b = r.choice(members[g1]), r.choice(members[g2])
        add(a, b, r.choice([800, 700, 700, 600, 500, 450]))
        if r.random() < 0.6: addm(r.choice(members[g1]), r.choice(members[g2]))
    for _ in range(15):
        g1, g2 = r.sample(range(groups), 2)
        addm(r.choice(members[g1]), r.choice(members[g2]))
    # order gadgets on fresh records: x -z- y with MNL(x,y); equal or close scores
    for _ in range(14):
        x, z, y = ids[pos:pos + 3]; pos += 3
        s1 = r.choice([900, 800, 700]); s2 = s1 if r.random() < 0.4 else s1 - r.choice([50, 100])
        add(x, z, s1); add(z, y, s2); addm(x, y)
    cap = r.choice([4, 5, 5, 6, 7])
    rows = sorted(edges.items()); r.shuffle(rows)
    ml = sorted(mnl); r.shuffle(ml)
    return Problem(n=n, cap=cap, mnl=ml, edges=[(a, b, s) for (a, b), s in rows], name=f"syn{seed}")


# ------------------------------------------------------------------ ground truth for decisions
def _components(pr: Problem):
    p = list(range(pr.n))
    def f(x):
        while p[x] != x: p[x] = p[p[x]]; x = p[x]
        return x
    for u, v, _ in pr.edges: p[f(u)] = f(v)
    for a, b in pr.mnl: p[f(a)] = f(b)
    return f


def _outcome_with_order(pr, order):
    """Greedy with an explicit processing order; returns kind per edge idx."""
    n, cap = pr.n, pr.cap
    p = {}; mem = {}
    def find(x):
        while p.get(x, x) != x: x = p[x]
        return x
    out = {}
    for i in order:
        u, v, _ = pr.edges[i]
        a, b = find(u), find(v)
        if a == b: out[i] = "noop"; continue
        A, B = mem.get(a, {a}), mem.get(b, {b})
        bad = any((x in A and y in B) or (x in B and y in A) for x, y in pr.mnl)
        if bad or len(A) + len(B) > cap: out[i] = "skip"; continue
        out[i] = "merge"; p[a] = b; mem[b] = A | B; mem.pop(a, None)
    return out


def analyse(pr: Problem):
    """Per-edge ground truth: kind, single reason, order dependence (swap of processing positions with one other edge in the
    same conflict component flips this edge's outcome), plus the labels."""
    labels, log, order = greedy_log(pr.n, pr.cap, pr.mnl, pr.edges)
    f = _components(pr)
    comp = {}
    for i, (u, v, _) in enumerate(pr.edges): comp.setdefault(f(u), []).append(i)
    pos = {i: k for k, i in enumerate(order)}
    res = {}
    for c, idxs in comp.items():
        sub_order = sorted(idxs, key=lambda i: pos[i])
        # restrict the MNL / cap semantics to this component: components never interact, so a sub-problem is exact
        sub = Problem(pr.n, pr.cap, [m for m in pr.mnl if f(m[0]) == c], pr.edges)
        base = _outcome_with_order(sub, sub_order)
        for i in idxs:
            info = log[i]
            dep = False   # STRICT: swapping processing positions with ONE adjacent edge of a different score flips this edge
            if info["kind"] == "skip" and len(idxs) <= 60:
                ui, vi = pr.edges[i][0], pr.edges[i][1]
                for j in idxs:
                    if j == i: continue
                    uj, vj = pr.edges[j][0], pr.edges[j][1]
                    if not ({ui, vi} & {uj, vj}) or pr.edges[j][2] == pr.edges[i][2]: continue
                    o2 = list(sub_order); a, b = o2.index(i), o2.index(j); o2[a], o2[b] = o2[b], o2[a]
                    if _outcome_with_order(sub, o2)[i] != base[i]: dep = True; break
            res[i] = dict(kind=info["kind"], mnl_bad=info.get("mnl_bad"), cap_bad=info.get("cap_bad"), order_dep=dep,
                          blocker=info.get("blocker"))
    return labels, log, res


def decision_pools(pr: Problem, tag: str):
    """All eligible decisions per bin, from the reference analysis only."""
    labels, log, res = analyse(pr)
    pools = {"MERGE": [], "MNL": [], "CAP": [], "ORDER": []}
    clusters = {}
    for i, l in enumerate(labels): clusters.setdefault(l, []).append(i)
    direct = {(u, v) for u, v, _ in pr.edges}
    for l, mem in clusters.items():
        if len(mem) < 2: continue
        for a, b in itertools.combinations(sorted(mem), 2):
            pools["MERGE"].append(dict(kind="MERGE", a=a, b=b, subject=None, polarity="same", direct=(a, b) in direct, src=tag))
    for i, (u, v, s) in enumerate(pr.edges):
        r_ = res[i]
        if r_["kind"] != "skip": continue
        if r_["mnl_bad"] == r_["cap_bad"]: continue          # both or neither: ambiguous reason, excluded (stated in the doc)
        reason = "mnl" if r_["mnl_bad"] else "cap"
        # bins: CAP = capacity refusal; ORDER = MNL refusal that flips under a priority swap with one adjacent edge of a
        # different score; MNL = the other MNL refusals.  (Many CAP refusals are also order dependent: flag kept.)
        kind = "CAP" if reason == "cap" else ("ORDER" if r_["order_dep"] else "MNL")
        pools[kind].append(dict(kind=kind, a=u, b=v, subject=i, polarity="refused", reason=reason, order_dep=r_["order_dep"], src=tag))
    return pools


def _pick(pool, q, rng):
    if q <= 0: return []
    pool = list(pool); rng.shuffle(pool); return pool[:q]


def _pick_merge(pool, q, rng):
    multi = [d for d in pool if not d["direct"]]; dire = [d for d in pool if d["direct"]]
    rng.shuffle(multi); rng.shuffle(dire)
    nd = q // 3
    take = multi[:q - nd] + dire[:nd]
    if len(take) < q: take += (multi[q - nd:] + dire[nd:])[:q - len(take)]
    return take


def select_decisions(pr, quotas, rng, tag):
    pools = decision_pools(pr, tag)
    out = []
    for kind, q in quotas.items():
        out += (_pick_merge if kind == "MERGE" else _pick)(pools[kind], q, rng)
    return out, {k: len(v) for k, v in pools.items()}


def select_global(pools_by_set, quotas, rng):
    """Balanced across rule sets: round-robin over the sets, taking one random decision at a time."""
    out = []
    for kind, q in quotas.items():
        sets = [t for t in pools_by_set if pools_by_set[t][kind]]
        rng.shuffle(sets)
        pools = {t: list(pools_by_set[t][kind]) for t in sets}
        for t in sets: rng.shuffle(pools[t])
        took = 0
        while took < q and any(pools[t] for t in sets):
            for t in sets:
                if took >= q: break
                if not pools[t]: continue
                # merge pools: prefer multi-hop (2 of every 3 picks)
                if kind == "MERGE":
                    want_direct = (took % 3 == 2)
                    cand = [d for d in pools[t] if d["direct"] == want_direct] or pools[t]
                    d = cand[0]; pools[t].remove(d)
                else:
                    d = pools[t].pop()
                out.append(d); took += 1
    return out


def freeze(path, dev=False):
    """Build the evaluation set.  hero: 50 decisions over the 5 rule sets; synthetic: 25 problems x 2 decisions."""
    rng = random.Random(555 if not dev else 777)
    out = {"problems": {}, "decisions": [], "pools": {}}
    hero_ks = [1, 2, 3, 4, 5] if not dev else [1, 3, 5]
    hq = {"MERGE": 14, "MNL": 12, "CAP": 12, "ORDER": 12} if not dev else {"MERGE": 3, "MNL": 1, "CAP": 3, "ORDER": 3}
    pb = {}
    for k in hero_ks:
        pr = hero_problem(k); tag = f"hero{k}"
        out["problems"][tag] = pr.__dict__ | {"names": pr.names}
        pb[tag] = decision_pools(pr, tag)
        out["pools"][tag] = {kk: len(v) for kk, v in pb[tag].items()}
    out["decisions"] += select_global(pb, hq, rng)
    nsyn = 25 if not dev else 4
    base = 9100 if not dev else 8100
    kinds = (["MERGE"] * 14 + ["MNL"] * 14 + ["CAP"] * 11 + ["ORDER"] * 11) if not dev else ["MERGE", "MNL", "CAP", "ORDER", "MERGE", "CAP", "ORDER", "MNL"]
    # pair the kinds so that the two decisions of one problem differ
    seqs = [[kinds[2 * i], kinds[2 * i + 1]] for i in range(nsyn)]
    if not dev:
        rr = random.Random(12); ks = list(kinds); rr.shuffle(ks)
        seqs = [ks[2 * i:2 * i + 2] for i in range(nsyn)]
    for j in range(nsyn):
        seed = base + j
        pr = synth_problem(seed); tag = f"syn{seed}"
        out["problems"][tag] = pr.__dict__ | {"names": {}}
        pools = decision_pools(pr, tag)
        out["pools"][tag] = {kk: len(v) for kk, v in pools.items()}
        picks = []
        used = set()
        for kd in seqs[j]:
            pool = [d for d in pools[kd] if (d["a"], d["b"]) not in used]
            got = (_pick_merge if kd == "MERGE" else _pick)(pool, 1, rng)
            for d in got: used.add((d["a"], d["b"])); picks.append(d)
        out["decisions"] += picks
    for i, d in enumerate(out["decisions"]):
        d["id"] = i
    json.dump(out, open(path, "w"), indent=0, sort_keys=True)
    return out


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


if __name__ == "__main__":
    dev = "--dev" in sys.argv
    path = sys.argv[1]
    o = freeze(path, dev)
    from collections import Counter
    print(len(o["decisions"]), Counter((d["src"][:4], d["kind"]) for d in o["decisions"]))
    print(sha(path))
