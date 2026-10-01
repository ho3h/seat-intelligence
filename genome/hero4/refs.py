"""HERO-4 seating domain: guest encoding, name tables and the PYTHON REFERENCE SEMANTICS of every seating word.

A guest is ONE u24 number:   idx (bits 0-5) | rank (bits 6-10) | category (bits 11-13) | company (bits 14-18)
  idx      the guest's position in the input chart (0..63); the output of the last word is expressed with it
  rank     a numeric RSVP-order field of the game (0..31), a host-side number, NOT a personal trait
  category coarse category from data/hero/luncheon.json: 1 ai_lab 2 big_tech 3 chips 4 software_security 5 investor 6 government 7 unlabelled
  company  printed company, 1..19, 0 = none printed
Only company / category (and the game's rank number) are ever used. Nothing personal.

A seating program is a list of ARRANGE words (list -> list, a permutation) followed by exactly one CLOSING word
(`sections S` or `captains S`). Every arrange word is defined here by its reference function; the net for it
(genome/hero4/words.py) must equal that reference on the hidden suite (genome.verify).
"""
from __future__ import annotations

CATS = {"ai_lab": 1, "big_tech": 2, "chips": 3, "software_security": 4, "investor": 5, "government": 6, "unlabelled": 7}
CAT_NAMES = {v: k for k, v in CATS.items()}
TASK_CATS = ["ai_lab", "big_tech", "chips", "software_security", "investor", "government"]  # used in rules (never `unlabelled`)
# company tokens (spaces -> underscores); 'X, Tesla, Space X' is left out of the rule vocabulary.
COMPANIES = ["AMD", "Altimeter", "Amazon", "Anthropic", "Broadcom", "Craft_Ventures", "Exiger", "Google", "Meta", "Micron",
             "Microsoft", "NASA", "Nvidia", "OpenAI", "Palantir", "Palo_Alto_Networks", "Service_Now", "Social_Capital",
             "X_Tesla_SpaceX"]
CO = {n: i + 1 for i, n in enumerate(COMPANIES)}
TASK_COS = [c for c in COMPANIES if c != "X_Tesla_SpaceX"]
M24 = (1 << 24) - 1


def pack(idx, rank, cat, comp): return (idx & 63) | (rank & 31) << 6 | (cat & 7) << 11 | (comp & 31) << 14
def f_idx(g): return g & 63
def f_rank(g): return (g >> 6) & 31
def f_cat(g): return (g >> 11) & 7
def f_comp(g): return (g >> 14) & 31


def stable(xs, key): return [x for _, _, x in sorted((key(x), i, x) for i, x in enumerate(xs))]


def occ_keys(xs, cls, f):
    """f(g, occ, cls_value, pos) with occ = number of EARLIER guests of the same class."""
    seen, out = {}, []
    for p, g in enumerate(xs):
        c = cls(g); o = seen.get(c, 0); seen[c] = o + 1
        out.append(f(g, o, c, p))
    return out


def by_keys(xs, keys): return [x for _, _, x in sorted((k, i, x) for i, (k, x) in enumerate(zip(keys, xs)))]


# ------------------------------------------------------------------ BASE arrange words
def w_group(xs, field):                         # affinity cluster: same company (or category) adjacent; id order; company 0 last
    if field == "company": return stable(xs, lambda g: (f_comp(g) - 1) & M24)
    return stable(xs, f_cat)


def w_spread(xs):                                # deal categories round-robin: k-th guest of each category before any (k+1)-th
    return by_keys(xs, occ_keys(xs, f_cat, lambda g, o, c, p: o))


def w_order(xs, mode, names):                    # priority order
    if mode == "rank": return stable(xs, f_rank)
    if mode == "rankdesc": return stable(xs, lambda g: 31 - f_rank(g))
    if mode == "category":
        codes = [CATS[n] for n in names]; return stable(xs, lambda g: codes.index(f_cat(g)) if f_cat(g) in codes else len(codes))
    if mode == "company":
        codes = [CO[n] for n in names]; return stable(xs, lambda g: codes.index(f_comp(g)) if f_comp(g) in codes else len(codes))
    raise KeyError(mode)


# ------------------------------------------------------------------ CLOSING words
def w_sections(xs, S): return [(i // S) * 64 + f_idx(g) for i, g in enumerate(xs)]


def w_captains(xs, S):                           # captain of a section = member with the smallest (rank, idx)
    out = []
    for b in range(0, len(xs), S):
        blk = xs[b:b + S]; m = min(g & 2047 for g in blk); out.append((b // S) * 64 + (m & 63))
    return out


# ------------------------------------------------------------------ NEW arrange words (the ten authored ones)
def w_limit(xs, cat, k, S):                      # at most k guests of `cat` per section of S seats (best effort when infeasible)
    if k >= S: return list(xs)
    c = CATS[cat]
    keys = occ_keys(xs, lambda g: 1 if f_cat(g) == c else 0,
                    lambda g, o, cl, p: (o // k) * 2 if cl else (o // (S - k)) * 2 + 1)
    return by_keys(xs, keys)


def w_pair(xs, a, b):                            # A_j immediately followed by B_j; everyone else after
    ca, cb = CATS[a], CATS[b]
    def cls(g): return 1 if f_cat(g) == ca else (2 if f_cat(g) == cb else 0)
    return by_keys(xs, occ_keys(xs, cls, lambda g, o, c, p: 2 * o if c == 1 else (2 * o + 1 if c == 2 else 4096)))


def w_apart(xs, x, y):                           # company x first, others, company y last
    cx, cy = CO[x], CO[y]
    return stable(xs, lambda g: 0 if f_comp(g) == cx else (2 if f_comp(g) == cy else 1))


def w_vip(xs, R): return stable(xs, lambda g: 0 if f_rank(g) <= R else 1)


def w_stagger(xs, m):                            # rounds: every company contributes at most m guests per round
    return by_keys(xs, occ_keys(xs, f_comp, lambda g, o, c, p: (o // m) if c else 0))


def w_headseat(xs):                              # the guest with the smallest (rank, idx) takes seat 1
    if not xs: return []
    m = min(g & 2047 for g in xs)
    return stable(xs, lambda g: 0 if (g & 2047) == m else 1)


def w_bigfirst(xs):                              # bigger company delegations first; ties by company id; no company last
    cnt = {}
    for g in xs: cnt[f_comp(g)] = cnt.get(f_comp(g), 0) + 1
    return stable(xs, lambda g: 3000 if f_comp(g) == 0 else (64 - cnt[f_comp(g)]) * 32 + f_comp(g))


def w_waitlist(xs, cat, k):                      # only the first k guests of `cat` keep their place; the rest go last
    c = CATS[cat]
    keys = occ_keys(xs, lambda g: 1 if f_cat(g) == c else 0, lambda g, o, cl, p: 1 if (cl and o >= k) else 0)
    return by_keys(xs, keys)


def w_snake(xs, S):                              # reverse the seat order inside every second section (2nd, 4th, ...)
    def key(p):
        b, r = divmod(p, S)
        return b * S + (S - 1 - r if b & 1 else r)
    return by_keys(xs, [key(p) for p in range(len(xs))])


def w_sectionlead(xs, S):                        # the smallest-(rank, idx) guest of each section moves to the section's first seat
    n = len(xs); mins = {}
    for p, g in enumerate(xs): b = p // S; mins[b] = min(mins.get(b, 1 << 30), g & 2047)
    return by_keys(xs, [(p // S) * 4096 + (0 if (g & 2047) == mins[p // S] else 2048) + p for p, g in enumerate(xs)])


ARRANGE = {
    "group": lambda xs, a: w_group(xs, a[0]), "spread": lambda xs, a: w_spread(xs),
    "order": lambda xs, a: w_order(xs, a[0], a[1:]),
    "limit": lambda xs, a: w_limit(xs, a[0], a[1], a[2]), "pair": lambda xs, a: w_pair(xs, a[0], a[1]),
    "apart": lambda xs, a: w_apart(xs, a[0], a[1]), "vip": lambda xs, a: w_vip(xs, a[0]),
    "stagger": lambda xs, a: w_stagger(xs, a[0]), "headseat": lambda xs, a: w_headseat(xs),
    "bigfirst": lambda xs, a: w_bigfirst(xs), "waitlist": lambda xs, a: w_waitlist(xs, a[0], a[1]),
    "snake": lambda xs, a: w_snake(xs, a[0]), "sectionlead": lambda xs, a: w_sectionlead(xs, a[0]),
}
CLOSING = {"sections": lambda xs, a: w_sections(xs, a[0]), "captains": lambda xs, a: w_captains(xs, a[0])}
BASE_WORDS = ["group", "spread", "order", "sections", "captains"]
NEW_WORDS = ["limit", "pair", "apart", "vip", "stagger", "headseat", "bigfirst", "waitlist", "snake", "sectionlead"]  # authoring order


def run_program(words, xs):
    """words: list of (name, *args) tuples; the last must be a closing word. Pure Python semantics."""
    xs = list(xs)
    for w in words[:-1]: xs = ARRANGE[w[0]](xs, w[1:])
    c = words[-1]
    return CLOSING[c[0]](xs, c[1:])


def gen_guests(rng, n, skew=True):
    """n random guests, idx = position. Company printed for ~60%; categories skewed; ranks 0..31 (with ties)."""
    xs = []
    ncomp = rng.choice([3, 6, 12, 19])
    for i in range(n):
        cat = rng.choice(list(range(1, 8)) if not skew else [1, 2, 2, 3, 4, 4, 5, 6, 6, 6, 7, 7])
        comp = rng.randrange(1, ncomp + 1) if rng.random() < 0.65 else 0
        xs.append(pack(i, rng.randrange(32), cat, comp))
    return xs
