"""Corpus self-check. Run: python -m genome.corpus.check [prefix]
Every program must be well formed: preconditions hold, references are pure and deterministic, outputs are valid and
non-degenerate, sizes stay affordable. This is the definition of done for a corpus module."""
import copy, random, sys, time
from . import load_all

def inc(xs, strict=False): return all((a < b) if strict else (a <= b) for a, b in zip(xs, xs[1:]))

PRE = {
    "t2_dedup_sorted": lambda x: inc(x),
    "t2_merge": lambda x: inc(x[0]) and inc(x[1]),
    "t2_merge3": lambda x: all(inc(l) for l in x),
    "t2_merge_dedup": lambda x: inc(x[0]) and inc(x[1]),
    "t2_search": lambda x: inc(x[0], True),
    "t2_lower_bound": lambda x: inc(x[0]),
    "t2_upper_bound": lambda x: inc(x[0]),
    "t2_intersect": lambda x: inc(x[0], True) and inc(x[1], True),
    "t2_union": lambda x: inc(x[0], True) and inc(x[1], True),
    "t2_histogram": lambda x: all(0 <= v < 16 for v in x),
    "t1_powmod": lambda x: 1 <= x[2] <= 4096,
    "t1_collatz": lambda x: x >= 1,
    "t1_bignum_add": lambda x: all(not l or (l[-1] != 0 and all(0 <= d < 4096 for d in l)) for l in x),
    "t1_bignum_mul": lambda x: all(not l or (l[-1] != 0 and all(0 <= d < 4096 for d in l)) for l in x),
    "t1_bignum_mul_small": lambda x: (not x[0] or x[0][-1] != 0) and 0 <= x[1] < 4096,
}

# size parameter is a bit-width, not a count, so 16x is not meaningful; boolean outputs have only 2 values
SIZE_EXEMPT = {"t1_gcd", "t1_powmod", "t1_popcount", "t1_collatz"}
BOOL_OK = {"t2_is_sorted", "t5_rewrite_sameas_cycle"}
MAX_REF_SECS = 2.0
MAX_ENC_CHARS = 3_000_000


def main(argv=()):
    from ..types import encode
    R = load_all(); bad = []
    def fail(pid, msg): bad.append((pid, msg)); print("FAIL", pid, msg)
    prefix = argv[0] if argv else ""
    for pid, p in R.items():
        if not pid.startswith(prefix): continue
        if not pid.startswith(p.tier.lower() + "_"): fail(pid, f"id must start with {p.tier.lower()}_")
        if len(p.desc) < 20: fail(pid, "desc too short to be a contract")
        pre = p.pre or PRE.get(pid) or (lambda x: True)
        rng = random.Random(11)
        inputs = [("edge", None, e) for e in p.edges]
        inputs += [("gen", n, p.gen(rng, n)) for n in p.sizes + p.test_sizes for _ in range(6)]
        if not p.edges: fail(pid, "no edge cases")
        if pid not in SIZE_EXEMPT and max(p.test_sizes) < 8 * max(p.sizes) and max(p.test_sizes) < 16 * max(p.sizes) // 2:
            fail(pid, "test_sizes should reach about 16x the authoring sizes")
        outs = set()
        for kind, n, x in inputs:
            try:
                if not pre(x): fail(pid, f"precondition violated by {kind} input {repr(x)[:80]}"); break
                snap = copy.deepcopy(x)
                t0 = time.time(); y = p.ref(x); dt = time.time() - t0
                if x != snap: fail(pid, "ref mutated its input"); break
                if dt > MAX_REF_SECS: fail(pid, f"ref took {dt:.1f}s on size {n}"); break
                if p.ref(copy.deepcopy(x)) != y: fail(pid, "ref not deterministic"); break
                txt, defs = encode(x, p.inp); ytxt, ydefs = encode(y, p.out)
                if len(txt) + sum(map(len, defs)) > MAX_ENC_CHARS: fail(pid, f"input too large at size {n}"); break
                outs.add(repr(y))
            except Exception as e:
                fail(pid, f"{kind} input {repr(x)[:80]} -> {type(e).__name__}: {e}"); break
        if len(outs) < (2 if pid in BOOL_OK else 4) and not any(b[0] == pid for b in bad):
            fail(pid, f"degenerate: only {len(outs)} distinct outputs over {len(inputs)} inputs")
    n = sum(1 for k in R if k.startswith(prefix))
    print(f"corpus check: {'FAIL' if bad else 'ok'} ({n} programs checked, {len(bad)} problems)")
    return 1 if bad else 0

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
