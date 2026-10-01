"""Composition of verified nets into deeper pipelines. The glue is fixed and dumb (function composition by wiring the output of one
`@prog` into the next); the parts are machine-authored and were verified. Every composed net is re-verified by the executor before it
is kept, so nothing here is trusted. This is how a growing vocabulary of verified parts is reused.
   python -m genome.compose build 1500
"""
import glob, json, os, random, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from concurrent.futures import ThreadPoolExecutor
from .netast import parse_book, print_book
from .taskgen import task, pipeline_from_steps
from .verify import verify

KIDS = ("con", "dup", "opr", "swi")


def _rename_refs(t, m):
    if t[0] == "ref": return ("ref", m.get(t[1], t[1]))
    if t[0] in KIDS: return (t[0], _rename_refs(t[1], m), _rename_refs(t[2], m))
    return t


def prefixed(book, pre):
    defs, order = parse_book(book)
    m = {n: pre + n for n in order}
    out = {}
    for n in order:
        root, reds = defs[n]
        out[m[n]] = (_rename_refs(root, m), [(p, _rename_refs(a, m), _rename_refs(b, m)) for p, a, b in reds])
    return out, [m[n] for n in order]


def compose_nets(books):
    """books: nets each defining @prog = (in out). Returns a book whose @prog pipes them in sequence."""
    defs, order = {}, []
    for i, b in enumerate(books):
        d, o = prefixed(b, f"c{i}_"); defs.update(d); order += o
    k = len(books)
    reds = [(False, ("ref", f"c{i}_prog"), ("con", ("var", "m0" if i == 0 else f"m{i}"), ("var", f"m{i + 1}" if i < k - 1 else "output"))) for i in range(k)]
    # input feeds m0: root is (input output) with input wired to m0
    root = ("con", ("var", "m0"), ("var", "output"))
    defs["prog"] = (root, reds); order.append("prog")
    return print_book(defs, order)


def load_parts():
    parts = []
    for f in sorted(glob.glob("runs/datagen/native/seed0/gen_pipeline_*/state.json")):
        s = json.load(open(f))
        if not (s["accepted"] and s.get("audit") == ["pass", "pass"]): continue
        pid = s["pid"]; idx = int(pid.rsplit("_", 1)[1]); p = task("pipeline", idx)
        parts.append((idx, p.steps, open(os.path.join(os.path.dirname(f), "best.hvm")).read()))
    return parts


def build(n, seed=0, max_stages=6):
    parts = load_parts(); rng = random.Random(seed); cand = []
    seen = set()
    while len(cand) < n and len(seen) < 100000:
        k = rng.choice([2, 2, 3])
        chosen = [rng.choice(parts) for _ in range(k)]
        if sum(len(c[1]) for c in chosen) > max_stages: continue
        key = tuple(c[0] for c in chosen)
        if key in seen: continue
        seen.add(key); cand.append(chosen)
    def one(i_chosen):
        i, chosen = i_chosen
        steps = [st for c in chosen for st in c[1]]
        p = pipeline_from_steps(steps, f"comp_{i:05d}")
        net = compose_nets([c[2] for c in chosen])
        r = verify(p, net, seed=0, timeout=10.0, workers=4)
        return i, steps, net, r["status"] == "pass", p
    rows = []
    with ThreadPoolExecutor(4) as ex:
        for i, steps, net, ok, p in ex.map(one, list(enumerate(cand))):
            if ok: rows.append({"id": f"comp_{i:05d}", "desc": p.desc, "net": net, "stages": len(steps)})
    os.makedirs("data/compose", exist_ok=True)
    json.dump(rows, open("data/compose/verified.json", "w"))
    from collections import Counter
    print(f"candidates {len(cand)}, verified {len(rows)}, stages {dict(Counter(r['stages'] for r in rows))}")


if __name__ == "__main__" and sys.argv[1:2] == ["build"]: build(int(sys.argv[2]))
