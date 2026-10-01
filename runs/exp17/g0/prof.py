"""Per-case depth profile on the big cases: python3 prof.py prog [path] [seed]"""
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.corpus import load_all
from genome.verify import build_cases
from genome import bend_io as B
from genome.executor import run_net
prog = sys.argv[1]
path = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else f"/Users/tedsandtads/Genome/runs/exp17/{prog}.bend"
seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
p = load_all()[prog]
book, err = B.compile_bend(B.bend_source(p, open(path).read()))
if err: print(err); sys.exit(1)
def sz(x):
    if isinstance(x, list): return len(x)
    if isinstance(x, tuple): return "/".join(str(sz(e)) for e in x)
    return x
for k, n, x in build_cases(p, seed):
    if k != "big": continue
    m = run_net(B.assemble_bend(p, book, x, digest=False), "depth", 240)
    print(n, sz(x), "depth", m.depth, "itrs", m.itrs, flush=True)
