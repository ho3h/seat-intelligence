import sys
sys.path.insert(0, "<home>/Genome")
from genome.corpus import load_all
from genome import bend_io as B
from genome.executor import run_net
prog, path, expr = sys.argv[1], sys.argv[2], sys.argv[3]
p = load_all()[prog]
book, err = B.compile_bend(B.bend_source(p, open(path).read()))
if err: print(err); sys.exit(1)
x = eval(expr)
r = run_net(B.assemble_bend(p, book, x, digest=False), "depth", 120)
r2 = run_net(B.assemble_bend(p, book, x, digest=False), "run", 120)
print("depth", r.depth, "itrs", r.itrs, "ok", B.decode_bend(r2.result, p.out) == p.ref(x) if r2.ok else r2.error[:100])
