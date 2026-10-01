"""Synthetic guest lists (org, category) with a plausible company/category mix. Deterministic per (n, seed, mix)."""
import random
from .lang import CATS

MIXES = {
    "balanced":   [0.09, 0.13, 0.10, 0.12, 0.12, 0.22, 0.22],
    "gov_heavy":  [0.06, 0.08, 0.06, 0.08, 0.08, 0.44, 0.20],
    "tech_heavy": [0.18, 0.24, 0.16, 0.14, 0.10, 0.06, 0.12],
}
# company size distribution (guests per company at the event)
SIZES, SW = [1, 2, 3, 4, 5, 6, 8], [0.50, 0.20, 0.11, 0.07, 0.05, 0.04, 0.03]


def gen_guests(n, seed, mix="balanced"):
    """deterministic; for n >= 30 re-draws (attempt counter) until every category has at least 2 guests."""
    for attempt in range(200):
        g = _gen(n, seed, mix, attempt)
        if n < 30 or min(sum(1 for _, c in g if c == k) for k in range(7)) >= 2: return g
    return g


def _gen(n, seed, mix, attempt):
    r = random.Random(f"guests|{n}|{seed}|{mix}|{attempt}")
    w = MIXES[mix]; out = []; cid = 0
    while len(out) < n:
        c = r.choices(range(7), w)[0]
        if c >= 5:                                   # government / unlabelled: mostly no printed company
            if r.random() < 0.65:
                out.append((None, c)); continue
        s = r.choices(SIZES, SW)[0]
        org = f"{CATS[c][:3]}_co{cid}"; cid += 1
        out += [(org, c)] * s
    out = out[:n]
    r.shuffle(out)
    return out


# the three synthetic lists of the pipeline agreement test (frozen with the test set)
AGREE_LISTS = [(48, 101, "balanced"), (80, 202, "gov_heavy"), (120, 303, "tech_heavy")]
