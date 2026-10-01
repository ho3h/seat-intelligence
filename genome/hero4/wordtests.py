"""Word-level unit tests: every word instance as a corpus Program (hidden suite = genome.verify: edge + random + big + exhaustive
small, v2) with the Python reference of refs.py.   python -m genome.hero4.wordtests <word> [seeds]"""
from __future__ import annotations
import json, random, sys, time
from genome.corpus import Program as CP
from genome.types import u24, list_of
from genome.verify import verify
from genome.hero4 import refs
from genome.hero4.refs import gen_guests, pack

L_ = list_of(u24)


def edges():
    e = [[], [pack(0, 3, 1, 1)], [pack(0, 3, 1, 1), pack(1, 3, 1, 1)], [0, 1, 2], [2, 2, 2, 2]]
    r = random.Random(7)
    e.append([pack(i, 5, 6, 3) for i in range(8)])                   # all same everything
    e.append([pack(i, 31 - i, 1 + i % 7, i % 5) for i in range(10)]) # descending ranks, mixed
    e.append(gen_guests(r, 34, skew=True))                            # luncheon size
    e.append(gen_guests(r, 12, skew=False))
    return e


def program_for(word, args, tag=""):
    """corpus Program for one word instance"""
    def ref(xs):
        if word in refs.ARRANGE: return refs.ARRANGE[word](list(xs), list(args))
        return refs.CLOSING[word](list(xs), list(args))
    return CP(f"h4_{word}{tag}_" + "_".join(map(str, args)), "H4", f"hero4 word {word} {args}", L_, L_, ref,
              lambda rng, n: gen_guests(rng, n), [0, 1, 2, 3, 5, 8, 12, 20], [34, 48], edges(), None)


def run(word, args, net, seeds=(0, 1, 2), workers=4, tag=""):
    p = program_for(word, args, tag); out = []
    for sd in seeds:
        t0 = time.time(); r = verify(p, net, sd, 30.0, workers)
        out.append({"seed": sd, "status": r["status"], "cases": r.get("cases"), "failed": r.get("failed"),
                    "secs": round(time.time() - t0, 1), "metrics": r.get("metrics"), "cx": r.get("counterexample"), "reason": r.get("reason")})
        if r["status"] != "pass": break
    return out


if __name__ == "__main__":
    from genome.hero4.words import BUILD
    w = sys.argv[1]; args = []
    for a in sys.argv[2:]:
        args.append(int(a) if a.isdigit() else a)
    net = BUILD[w](args)
    for r in run(w, args, net): print(json.dumps(r, default=str)[:900])
