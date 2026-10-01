"""Per-big-case depth/itrs of a Bend file at seed 0 (no correctness check beyond small digest-less run).
usage: probe.py prog path [seed]"""
import sys, json
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.corpus import load_all
from genome import bend_io as B
from genome.verify import build_cases
from genome.executor import run_net
prog, path = sys.argv[1], sys.argv[2]
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
p = load_all()[prog]
book, err = B.compile_bend(B.bend_source(p, open(path).read()))
if err: print(err); sys.exit(1)
for kind, n, x in build_cases(p, seed):
    if kind != "big": continue
    r = run_net(B.assemble_bend(p, book, x, digest=False), "depth", 120)
    ok = None
    if r.ok:
        try: ok = B.decode_bend(r.result, p.out) == p.ref(x)
        except Exception as e: ok = f"decode {e}"
    m = len(x[-1]) if isinstance(x, tuple) and isinstance(x[-1], list) else len(x) if isinstance(x, list) else '?'
    print(f"n={n} m={m} ok={ok} depth={r.depth if r.ok else r.error[:200]} itrs={r.itrs}")
