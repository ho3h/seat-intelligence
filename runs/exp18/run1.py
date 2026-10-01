"""Run one input on a net. usage: python3 runs/exp18/run1.py <prog> <net> '<python literal input>' [depth|run]"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genome.verify import assemble
from genome.executor import run_net
from genome.corpus import load_all
from genome.types import decode
p = load_all()[sys.argv[1]]
x = eval(sys.argv[3])
r = run_net(assemble(p, open(sys.argv[2]).read(), x), sys.argv[4] if len(sys.argv) > 4 else "run", 600)
print("ok", r.ok, "depth", r.depth, "itrs", r.itrs, r.error[:300])
try: print("got", decode(r.result, p.out))
except Exception as e: print("raw", r.result[:300], e)
print("exp", p.ref(x))
