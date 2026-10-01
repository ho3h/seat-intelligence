"""Side probe: does a different net (label-propagation cluster canon, runs/exp10) give informative provenance?"""
import sys, random, json, os, time
sys.path.insert(0, '/Users/tedsandtads/Genome')
from genome.hero5.core import *
from genome.hero5 import core
NET = '/Users/tedsandtads/Genome/runs/exp10/t5_cluster_canon.hvm'
book = open(NET).read()

def mk(n, comps, seed):
    r = random.Random(seed); ids = list(range(n)); r.shuffle(ids); pos = 0; pairs = set()
    for _ in range(comps):
        sz = r.choice([2, 3, 4, 5, 6, 8]); g = ids[pos:pos+sz]; pos += sz
        for j in range(1, sz): pairs.add(tuple(sorted((g[j], g[r.randrange(j)]))))
        if sz > 3 and r.random() < .5:
            a, b = r.sample(g, 2); pairs.add(tuple(sorted((a, b))))
    pairs = sorted(pairs); r.shuffle(pairs); return pairs

def main_text(n, pairs):
    defs = [f"@fact_{k} = ({u} {v})" for k, (u, v) in enumerate(pairs)]
    body = "".join(f"(1 (@fact_{k} " for k in range(len(pairs))) + "(0 *)" + "))" * len(pairs)
    # chunk to stay inside the definition node budget
    CH = 1000; chunks = [list(range(i, min(i + CH, len(pairs)))) for i in range(0, len(pairs), CH)] or [[]]
    tail = "(0 *)"
    for i in range(len(chunks) - 1, -1, -1):
        b = "".join(f"(1 (@fact_{k} " for k in chunks[i]) + tail + "))" * len(chunks[i])
        if i == 0: root = b
        else: defs.append(f"@__cc_{i} = {b}"); tail = f"@__cc_{i}"
    return f"@main = r\n  & @prog ~ (({n} {root}) r)\n\n" + "\n".join(defs) + "\n\n" + book + "\n"

def labels_ref(n, pairs):
    p = list(range(n))
    def f(x):
        while p[x] != x: p[x] = p[p[x]]; x = p[x]
        return x
    for u, v in pairs: p[f(u)] = f(v)
    top = {}
    for i in range(n): top[f(i)] = max(top.get(f(i), 0), i)
    return [top[f(i)] for i in range(n)], f

out = []
for n, comps, seed in [(64, 12, 1), (512, 60, 2), (2000, 150, 3)]:
    pairs = mk(n, comps, seed)
    text = main_text(n, pairs)
    for mode in (2, 1):
        path = core._tmp(text)
        env = dict(core.ENV, GENOME_TR=str(mode), GENOME_TR_F=str(len(pairs)))
        t0 = time.time()
        p = subprocess.run([core.TRACER, "run", path], capture_output=True, text=True, env=env); wall = time.time() - t0
        os.unlink(path)
        st = parse_stats(p.stdout)
        import re
        toks = re.search(r"^TOKENS (.*)$", p.stdout, re.M).group(1).split()
        sets = {int(m.group(1)): frozenset(int(x) for x in m.group(2).split(",") if x) for m in re.finditer(r"^SET (\d+) ?(.*)$", p.stdout, re.M)}
        tree = parse_tokens(toks); els = list_elems(tree, sets)
        labels = [tree[1][h] for h, _ in els]
        ref, f = labels_ref(n, pairs)
        # component edge counts
        comp_edges = {}
        for k, (u, v) in enumerate(pairs): comp_edges.setdefault(f(u), set()).add(k)
        sizes = []
        for i in range(n):
            if not comp_edges.get(f(i)): continue
            sizes.append((len(els[i][1]), len(comp_edges[f(i)]), len(els[i][1] - comp_edges[f(i)])))
        import statistics as s
        print(f"n={n} facts={len(pairs)} mode={mode} ok={labels==ref} itrs={st.get('itrs')} depth={st.get('depth')} wall={wall:.1f}s  "
              f"|C| median={s.median(x[0] for x in sizes)} max={max(x[0] for x in sizes)}  component edges median={s.median(x[1] for x in sizes)}  "
              f"facts outside own component: median {s.median(x[2] for x in sizes)} max {max(x[2] for x in sizes)}  (of {len(pairs)})", flush=True)
