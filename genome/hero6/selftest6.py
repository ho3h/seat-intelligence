"""Self-checks of lang6: (1) old words unchanged vs HERO-1 lang (assignment, order, canonical text, violations);
(2) tag-mask function (net reference) == JS-semantics reference on random policies with avoid/pair;
(3) the reference with avoid never leaves an avoid pair in one section unless forced by a unit (independent checker).
  python3 -m genome.hero6.selftest6 [N]"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import random, sys
sys.path.insert(0, _REPO)
from genome.hero1 import lang as L1
from genome.hero1.gen_train import sample_policy
from genome.hero6 import lang6 as L


def rand_guests(r, n):
    orgs = {c: [f"{L.CATS[c][:3]} co{k}" for k in range(4)] for c in range(7)}
    out = []
    for i in range(n):
        c = r.randrange(7)
        org = r.choice(orgs[c]) if c < 5 or r.random() < 0.3 else None
        out.append((org, c, f"Person {i % 23}" if r.random() < 0.9 else None))
    return out


def rand_names(r, g):
    pool = [L.key(x[2]) for x in g if x[2]] + [L.key(x[0]) for x in g if x[0]] + ["Nobody_Here"]
    return r.choice(pool)


def rand_pol(r, g):
    o = sample_policy(r, allow_held=True)
    av, pa = [], []
    for _ in range(r.choice([0, 1, 1, 2, 3])):
        a, b = rand_names(r, g), rand_names(r, g)
        if a != b: av.append((a, b))
    for _ in range(r.choice([0, 0, 1, 1, 2])):
        a, b = rand_names(r, g), rand_names(r, g)
        if a != b: pa.append((a, b))
    return L.Policy6(o.cap, o.tog_company, o.tog_cats, o.limits, o.aparts, o.order, tuple(av), tuple(pa)).canon()


def main(N=3000, seed=6):
    r = random.Random(seed); bad_old = bad_tag = bad_rt = forced = 0; tot_avd = 0
    for t in range(N):
        g = rand_guests(r, r.choice([1, 5, 12, 34, 60]))
        g2 = [(a, b) for a, b, _ in g]
        o = sample_policy(r, allow_held=True)
        p6 = L.parse(L1.to_text(o))
        if (L.assign_ref(g, p6) != L1.assign_ref(g2, o) or L.seat_order(g, p6) != L1.seat_order(g2, o) or L.to_text(p6) != L1.to_text(o)
                or {k: v for k, v in L.violations(g, p6, L1.assign_ref(g2, o)).items() if k not in ("avoid", "pair")} != L1.violations(g2, o, L1.assign_ref(g2, o))):
            bad_old += 1
        p = rand_pol(r, g)
        if L.parse(L.to_text(p)) != p: bad_rt += 1
        a = L.assign_ref(g, p)
        x, seq = L.tag_input(g, p)
        secs = L.ref_tags(*x); b = [None] * len(g)
        for (i, _, _), s in zip(seq, secs): b[i] = s
        if a != b: bad_tag += 1
        if p.avoids:
            tot_avd += 1
            v = L.violations(g, p, a)["avoid"]
            if v:
                # allowed only if some unit (company / category / pair) itself contains both sides
                seqs = L.prep(g, p); units = []; cur = None
                for i, c, s in seqs:
                    if s > 0: cur = [i]; units.append(cur)
                    else: cur.append(i)
                ok = any(any(L.is_who(g[i], X) for i in u) and any(L.is_who(g[j], Y) for j in u) for u in units for X, Y in p.avoids)
                if not ok: forced += 1
    print(f"old words unchanged: {N - bad_old}/{N}; canonical round-trip: {N - bad_rt}/{N}; tag-mask ref == reference: {N - bad_tag}/{N}; "
          f"avoid violated without a unit forcing it: {forced}/{tot_avd}")
    return bad_old + bad_tag + bad_rt + forced == 0


if __name__ == "__main__": sys.exit(0 if main(int(sys.argv[1]) if len(sys.argv) > 1 else 3000) else 1)
