import sys
sys.path.insert(0, "<home>/Genome")
from genome.corpus import load_all
from genome import bend_io as B
from genome.verify import build_cases
from genome.executor import run_net
prog, path = sys.argv[1], sys.argv[2]
p = load_all()[prog]
book, err = B.compile_bend(B.bend_source(p, open(path).read()))
if err: print(err); sys.exit(1)
for kind, n, x in build_cases(p, 0):
    if kind != "big": continue
    r = run_net(B.assemble_bend(p, book, x, digest=False), "run", 120)
    d = run_net(B.assemble_bend(p, book, x, digest=False), "depth", 120)
    print(n, len(x[-1]), r.result[:60] if r.ok else r.error[:100], d.depth)
