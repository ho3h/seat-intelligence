"""Run one input on a net with the depth oracle. usage: python3 runs/exp10/run1.py <prog> <net> '<python literal input>'"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from genome.verify import assemble
from genome.executor import run_net
from genome.corpus import load_all
def run(prog, net, x, mode="depth"):
    p = load_all()[prog]
    r = run_net(assemble(p, open(net).read(), x), mode, 600)
    return r
if __name__ == "__main__":
    r = run(sys.argv[1], sys.argv[2], eval(sys.argv[3]))
    print("depth", r.depth, "itrs", r.itrs, "ok", r.ok, r.result[:200], r.error[:200])
