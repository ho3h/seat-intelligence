"""probe.py <prog> <bend file> : depth/itrs on each big case of seed 0 (no correctness check)."""
import sys
sys.path.insert(0, "<home>/Genome")
from genome.corpus import load_all
from genome.verify import build_cases
from genome import bend_io as B
from genome.executor import run_net
p = load_all()[sys.argv[1]]
book, err = B.compile_bend(B.bend_source(p, open(sys.argv[2]).read()))
if err: print(err); sys.exit(1)
for kind, n, x in build_cases(p, 0):
    if kind != "big": continue
    m = run_net(B.assemble_bend(p, book, x, digest=False), "depth", 120)
    print(n, len(x[-1]), m.ok, m.itrs, m.depth, (m.result or "")[:60] if m.ok else m.error[:200])
