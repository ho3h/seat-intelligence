"""HERO-1 training set: (English seating policy -> stage program). Policies are sampled from the program space (all stage-word
combinations EXCEPT the 6 held-out signatures H1-H6 of data/hero/policies_test.json) and rendered by a template engine over two
phrase banks: genome/hero1/phrasebank_agent.json (written by a separate subagent that never saw the test set) and a small core
bank below (my own, deliberately plain). The test set was written by hand before this file existed and is never read here except
to take the six held-out signatures (a fixed constant, HELD, copied from make_test_set.py).

  python3 -m genome.hero1.gen_train [n_train] [n_valid] [seed]   -> runs/hero1/data/{train,valid}.jsonl, runs/hero1/train_meta.json
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, os, random, sys, re, collections
sys.path.insert(0, _REPO)
from genome.hero1.lang import Policy, CATS, MAXCAP, to_text

HELD = [{"tc", "apt", "ord"}, {"size", "tk", "lim"}, {"lim", "apt", "ord"}, {"size", "tc", "tk", "ord"}, {"tk", "apt"},
        {"size", "lim", "apt", "ord"}]
HERE = os.path.dirname(os.path.abspath(__file__))
NUMW = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}

CORE_NAMES = {
    "ai_lab": ["AI labs", "the AI labs", "AI lab guests", "AI companies", "the frontier AI developers", "model labs"],
    "big_tech": ["big tech", "the big tech companies", "big tech guests", "tech giants", "the large tech platforms"],
    "chips": ["chip makers", "the chip makers", "semiconductor companies", "chip companies", "the silicon people"],
    "software_security": ["software and security companies", "the software and security firms", "software firms", "cybersecurity companies"],
    "investor": ["investors", "the investors", "VCs", "the investment guests", "funds and investors"],
    "government": ["government officials", "the government officials", "officials", "the government guests", "public officials"],
    "unlabelled": ["unlabelled guests", "the guests with no listed affiliation", "guests without an organisation", "the unaffiliated guests"],
}
# core bank: (template, voice)
CORE = {
    "SIZE": [("Sections of at most {N}.", "terse"), ("Max {N} per section.", "terse"), ("No section may have more than {N} guests.", "negative_first"),
             ("Each section holds up to {NW} guests.", "formal"), ("Keep sections to {NW} people or fewer.", "chatty"), ("Section size cap: {N}.", "list"),
             ("Never more than {NW} in a section.", "negative_first"), ("Let's cap every section at {N}.", "chatty")],
    "TOGETHER_COMPANY": [("Colleagues sit together.", "terse"), ("People from the same company go in the same section.", "chatty"),
                         ("Guests of one company are to be seated together.", "formal"), ("Never split up a company.", "negative_first"),
                         ("Keep each company together.", "terse"), ("Seat everyone with their colleagues.", "chatty")],
    "TOGETHER_CAT": [("Keep {CAT} together.", "terse"), ("Seat {CAT} in one section.", "instruction"), ("{CAT} should all sit together.", "chatty"),
                     ("Do not split up {CAT}.", "negative_first"), ("{CAT} are to be grouped together.", "formal")],
    "LIMIT": [("At most {K} of {CATS} per section.", "terse"), ("No section may hold more than {KW} guests from {CATS}.", "negative_first"),
              ("Limit {CATS} to {K} per section.", "list"), ("No more than {KW} from {CATS} in any one section.", "chatty")],
    "LIMIT_ONE": [("No two of {CATS} in one section.", "terse"), ("Never seat two of {CATS} together.", "negative_first"),
                  ("At most one from {CATS} per section.", "list")],
    "LIMIT_TWO": [("Two of {CATS} per section at most.", "terse"), ("No third guest from {CATS} in a section.", "negative_first")],
    "APART": [("{A} and {B} apart.", "terse"), ("Keep {A} away from {B}.", "chatty"), ("Never put {A} and {B} in one section.", "negative_first"),
              ("{A} shall not share a section with {B}.", "formal"), ("Separate {A} from {B}.", "instruction")],
    "ORDER": [("Seat {SEQ} first.", "instruction"), ("{SEQ} come first.", "terse"), ("Priority order: {SEQ}.", "list"),
              ("Start with {SEQ}.", "chatty")],
    "ORDER_ONE": [("{CAT} first.", "terse"), ("Seat {CAT} first.", "instruction"), ("Put {CAT} at the head of the table.", "chatty")],
}
CORE_OPENERS = ["Seating policy:", "Rules:", "Here is what I want.", "Please follow these seating rules.", "Host's rules:"]
CORE_JOINERS = ["Also,", "And", "Additionally,", "Plus,", "Then,"]
CORE_CLOSERS = ["", "", "", "Thanks!", "That's all."]
NONE_TEXTS = ["No special rules, just fill the sections in order.", "Just seat everyone, no restrictions.", "No rules this time.",
              "Seat the guests in the order listed, nothing special.", "No constraints, thanks."]


def load_bank(agent=True):
    bank = {k: [dict(t=t, voice=v, src="core") for t, v in vs] for k, vs in CORE.items()}
    names = {c: [dict(t=x, src="core") for x in v] for c, v in CORE_NAMES.items()}
    ops, jns, cls = list(CORE_OPENERS), list(CORE_JOINERS), list(CORE_CLOSERS)
    path = os.path.join(HERE, "phrasebank_agent.json")
    if agent and os.path.exists(path):
        a = json.load(open(path))
        for k in bank:
            for e in a.get(k, []): bank[k].append(dict(t=e["t"], voice=e.get("voice", "x"), src="agent"))
        for c in names:
            for x in a.get("CATEGORY_NAMES", {}).get(c, []): names[c].append(dict(t=x, src="agent"))
        ops += a.get("OPENERS", []); jns += a.get("JOINERS", []); cls += a.get("CLOSERS", [])
    return dict(bank=bank, names=names, openers=ops, joiners=jns, closers=cls)


def sample_policy(r, allow_held=False):
    while True:
        cap = MAXCAP
        if r.random() < 0.45: cap = r.choice([1, 2, 2, 3, 3, 3, 4, 4, 4, 5, 5])
        tc = r.random() < 0.35
        tk = tuple(r.sample(range(7), 1 if r.random() < 0.22 else 0)) if r.random() < 0.3 else ()
        if r.random() < 0.05 and tk: tk = tuple(sorted(set(tk) | {r.randrange(7)}))
        lim = []
        for _ in range(r.choices([0, 1, 2], [0.58, 0.32, 0.10])[0]):
            cs = tuple(sorted(r.sample(range(6 if r.random() < 0.97 else 7), r.choices([1, 2, 3], [0.66, 0.28, 0.06])[0])))
            lim.append((cs, r.choices([1, 2, 3], [0.55, 0.30, 0.15])[0]))
        apt = []
        for _ in range(r.choices([0, 1, 2], [0.64, 0.28, 0.08])[0]):
            a, b = r.sample(range(6 if r.random() < 0.97 else 7), 2); apt.append((min(a, b), max(a, b)))
        order = tuple(r.sample(range(6 if r.random() < 0.97 else 7), r.choices([1, 2, 3], [0.55, 0.33, 0.12])[0])) if r.random() < 0.3 else ()
        pol = Policy(cap, tc, tk, tuple(lim), tuple(apt), order).canon()
        if len(set(pol.limits)) < len(pol.limits) or len(set(pol.aparts)) < len(pol.aparts): continue
        if not pol.sig() and r.random() > 0.03: continue
        if not allow_held and set(pol.sig()) in HELD: continue
        return pol


def cat_phrase(c, r, B):
    return r.choice(B["names"][CATS[c]])["t"]


def join_list(ps, r, word=None):
    if len(ps) == 1: return ps[0]
    w = word or r.choice(["or", "or", "and"])
    if len(ps) == 2: return f"{ps[0]} {w} {ps[1]}"
    return ", ".join(ps[:-1]) + f" {w} " + ps[-1]


def join_seq(ps, r):
    if len(ps) == 1: return ps[0]
    style = r.choice(["then", "then", "followed", "arrow", "firstthen", "order"])
    if style == "then": return ", then ".join(ps)
    if style == "followed": return ps[0] + "".join(f", followed by {p}" for p in ps[1:])
    if style == "arrow": return " > ".join(ps)
    if style == "firstthen": return f"{ps[0]} first, then " + " and then ".join(ps[1:])
    return join_list(ps, r, "and") + ", in that order"


def pick(B, kind, r, voice):
    cand = [e for e in B["bank"][kind] if e["voice"] == voice]
    if not cand or r.random() < 0.12: cand = B["bank"][kind]
    return r.choice(cand)["t"]


def fill(t, **kw):
    for k, v in kw.items(): t = t.replace("{" + k + "}", str(v))
    return t


def render(pol, r, B):
    if not pol.sig():
        return r.choice(NONE_TEXTS)
    voices = sorted({e["voice"] for v in B["bank"].values() for e in v})
    voice = r.choice(voices)
    cl = []
    if pol.cap != MAXCAP or r.random() < 0.05:
        cl.append(fill(pick(B, "SIZE", r, voice), N=pol.cap, NW=NUMW[pol.cap]))
    if pol.tog_company: cl.append(pick(B, "TOGETHER_COMPANY", r, voice))
    for c in pol.tog_cats: cl.append(fill(pick(B, "TOGETHER_CAT", r, voice), CAT=cat_phrase(c, r, B)))
    for cs, k in pol.limits:
        phr = join_list([cat_phrase(c, r, B) for c in cs], r)
        if k == 1 and r.random() < 0.5: t = fill(pick(B, "LIMIT_ONE", r, voice), CATS=phr)
        elif k == 2 and r.random() < 0.4: t = fill(pick(B, "LIMIT_TWO", r, voice), CATS=phr)
        else: t = fill(pick(B, "LIMIT", r, voice), CATS=phr, K=k, KW=NUMW[k])
        cl.append(t)
    for a, b in pol.aparts:
        if r.random() < 0.5: a, b = b, a
        cl.append(fill(pick(B, "APART", r, voice), A=cat_phrase(a, r, B), B=cat_phrase(b, r, B)))
    if pol.order:
        ps = [cat_phrase(c, r, B) for c in pol.order]
        if len(ps) == 1 and r.random() < 0.5: cl.append(fill(pick(B, "ORDER_ONE", r, voice), CAT=ps[0]))
        else: cl.append(fill(pick(B, "ORDER", r, voice), SEQ=join_seq(ps, r)))
    r.shuffle(cl)
    cl = [c.strip() for c in cl]
    lines = r.random() < 0.18 or voice == "list"
    if lines:
        mk = r.choice(["- ", "* ", "• ", "NUM", "NUM)", "  "])
        out = []
        for i, c in enumerate(cl):
            m = f"{i + 1}. " if mk == "NUM" else (f"{i + 1}) " if mk == "NUM)" else mk)
            out.append(m + c if not re.match(r"^\s*([-*•]|\d+[.)])\s", c) else c)
        text = "\n".join(out)
    else:
        text = cl[0]
        for c in cl[1:]:
            if re.search(r"[.!?]$", text):
                sep = r.choice([" ", " ", " ", "\n", " " + r.choice([j for j in B["joiners"] if j[:1].isupper()] or ["Also,"]) + " "])
                text += sep + c
            else:
                text += r.choice(["; ", ", ", " and ", ". ", " / ", " + "]) + c
    if r.random() < 0.3: text = r.choice(B["openers"]).strip() + ("\n" if lines else " ") + text
    if r.random() < 0.18:
        cz = r.choice(B["closers"]).strip()
        if cz: text += " " + cz
    if r.random() < 0.04: text = text.lower()
    return text.strip()


def prompt(text):
    return ("Convert the seating policy into a stage program (one word per line), or `none` if it states no rules.\n\n"
            f"## Policy\n\n{text}\n\n## Reply format\n\nReply with the stage program only.\n")


VOCAB = """## Stage words (one per line; any subset, in this order; reply `none` if the policy states no rules)

- `size N`  at most N guests per section (N = 1..6; the default of 6 needs no line)
- `together company`  guests of the same company are seated in one section
- `together CAT`  all guests of category CAT are seated together (one line per category)
- `limit CAT [CAT ...] K`  at most K guests from the listed categories (counted together) in any section
- `apart CATA CATB`  no guest of CATA shares a section with a guest of CATB
- `order CAT [CAT ...]`  seat the listed categories first, in this order

CAT is one of: ai_lab (AI labs), big_tech, chips (chip makers), software_security (software and security firms), investor, government (government officials), unlabelled.

Example: "Keep colleagues together, at most 4 per section, and never two investors in one section." is
```
size 4
together company
limit investor 1
```

"""


def prompt_vocab(text):
    """zero-shot control: the same prompt with the vocabulary documented (for an un-tuned instruct model)."""
    p = prompt(text)
    return p.replace("## Policy", VOCAB + "## Policy", 1)


def build(n_train=9000, n_valid=200, seed=0, agent=True):
    r = random.Random(seed); B = load_bank(agent)
    seen, rows = set(), []
    while len(rows) < n_train + n_valid:
        pol = sample_policy(r); text = render(pol, r, B)
        if text in seen: continue
        seen.add(text); rows.append((text, to_text(pol), sorted(pol.sig())))
    return rows[:n_train], rows[n_train:]


if __name__ == "__main__":
    nt = int(sys.argv[1]) if len(sys.argv) > 1 else 9000; nv = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 0
    tr, va = build(nt, nv, seed)
    out = _REPO + "/runs/hero1/data"; os.makedirs(out, exist_ok=True)
    for name, rows in (("train", tr), ("valid", va)):
        with open(f"{out}/{name}.jsonl", "w") as f:
            for text, prog, _ in rows:
                f.write(json.dumps({"messages": [{"role": "user", "content": prompt(text)}, {"role": "assistant", "content": prog}]}) + "\n")
    sigs = collections.Counter(tuple(s) for _, _, s in tr)
    json.dump(dict(n_train=len(tr), n_valid=len(va), seed=seed, signatures={"+".join(k): v for k, v in sigs.items()}, held_out=[sorted(h) for h in HELD]),
              open(_REPO + "/runs/hero1/train_meta.json", "w"), indent=1)
    print(len(tr), len(va), len(sigs), "signatures")
    for t, p, _ in tr[:6]: print(repr(t), "->", repr(p))
