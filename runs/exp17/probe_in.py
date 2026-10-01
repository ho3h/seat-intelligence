"""Depth/itrs of a Bend file on a python-literal input: probe_in.py prog path 'expr' """
import sys
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.corpus import load_all
from genome import bend_io as B
from genome.executor import run_net
prog, path = sys.argv[1], sys.argv[2]
p = load_all()[prog]
book, err = B.compile_bend(B.bend_source(p, open(path).read()))
if err: print(err); sys.exit(1)
for ex in sys.argv[3:]:
    x = eval(ex)
    r = run_net(B.assemble_bend(p, book, x, digest=False), "depth", 120)
    r2 = run_net(B.assemble_bend(p, book, x, digest=False), "run", 120)
    try: got = B.decode_bend(r2.result, p.out)
    except Exception as e: got = f"ERR {e}"
    print(ex[:60], "depth", r.depth, "itrs", r.itrs, "ok" if got == p.ref(x) else f"WRONG got {str(got)[:80]} want {str(p.ref(x))[:80]}")
