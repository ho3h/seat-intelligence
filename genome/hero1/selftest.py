"""Independent checks: (1) semantics: the next-fit reference has zero violations under the independent checker for random policies
and random guest lists; (2) net == reference on random pipelines end to end; run: python3 -m genome.hero1.selftest [n]"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import random, sys, time
sys.path.insert(0, _REPO)
from genome.hero1.lang import *
from genome.hero1.guests import gen_guests, MIXES
from genome.hero1.pipeline import run_net_assign


def rand_policy(r):
    cap = r.choice([6, 6, 5, 4, 3, 2, 1])
    tk = tuple(r.sample(range(7), r.choice([0, 0, 1, 2])))
    lim = tuple((tuple(r.sample(range(7), r.choice([1, 1, 2, 3]))), r.choice([1, 1, 2, 3])) for _ in range(r.choice([0, 1, 2])))
    apt = tuple(tuple(r.sample(range(7), 2)) for _ in range(r.choice([0, 1, 2, 3])))
    order = tuple(r.sample(range(7), r.choice([0, 0, 1, 2, 3])))
    return Policy(cap, r.random() < 0.5, tk, lim, apt, order).canon()


def main(N=300, seed=0):
    r = random.Random(seed); bad = 0; t = time.time(); netbad = 0; nnet = 0
    for it in range(N):
        pol = rand_policy(r)
        assert parse(to_text(pol)).canon() == pol.canon() or to_text(pol) == "none"
        n = r.choice([10, 34, 60, 150]); g = gen_guests(n, r.randrange(10**6), r.choice(list(MIXES)))
        a = assign_ref(g, pol)
        v = violations(g, pol, a)
        if v["total"]:
            bad += 1; print("VIOLATION", to_text(pol).replace("\n", "; "), n, v)
        assert v["total"] == violations_fast(g, pol, a)["total"] + order_inversions_fast(g, pol, a)
        if it % 5 == 0:
            nnet += 1
            a2, run = run_net_assign(g, pol)
            if a2 != a: netbad += 1; print("NET MISMATCH", to_text(pol).replace("\n", "; "), n)
    print(f"policies {N}: reference violations in {bad}; net==reference on {nnet - netbad}/{nnet}; {time.time() - t:.0f}s")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 300)
