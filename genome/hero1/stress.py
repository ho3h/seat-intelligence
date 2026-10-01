"""Extra kernel stress beyond the hidden suite: N random inputs (sizes up to 300), net vs reference. python3 -m genome.hero1.stress [N] [seed]"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import random, sys, time
sys.path.insert(0, _REPO)
from concurrent.futures import ThreadPoolExecutor
from genome.hero1 import sectioner as S
from genome.verify import assemble
from genome.executor import run_net
from genome.types import decode


def main(N=2000, seed=100):
    p = S.make_program(); r = random.Random(seed)
    cases = [S._gen(r, r.choice([0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 100, 200, 300])) for _ in range(N)]
    def one(x):
        rr = run_net(assemble(p, S.net_text(), x), "run", 60)
        return rr.ok and decode(rr.result, S.OUT) == p.ref(x)
    t = time.time()
    with ThreadPoolExecutor(6) as ex: res = list(ex.map(one, cases))
    print(f"kernel stress: {sum(res)}/{N} match reference, seed {seed}, {time.time() - t:.0f}s")
    return sum(res), N


if __name__ == "__main__": main(int(sys.argv[1]) if len(sys.argv) > 1 else 2000, int(sys.argv[2]) if len(sys.argv) > 2 else 100)
