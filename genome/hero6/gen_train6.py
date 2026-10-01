"""HERO-6 training set: HERO-1 sentences (old words only, same generator, same held-out signatures excluded) mixed with
sentences that also name guests or companies (`avoid X Y`, `pair X Y`). Names come from the 34 real luncheon guests
(full names, surnames, a few first names, companies) AND from a large invented pool (so the model learns to copy names).
The HERO-6 independent test set (data/hero/policies_test6.json) is written by a separate subagent and is never read here.

Targets: the HERO-1 lines in canonical order, then the named lines in the order the sentence mentions them
(X = the first-mentioned side; a group "A, B and C together" = pair A B, pair A C).

  python3 -m genome.hero6.gen_train6 [n_train] [n_valid] [seed]   -> runs/hero6/data/{train,valid}.jsonl, runs/hero6/train_meta.json
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, os, random, sys, re, collections
sys.path.insert(0, _REPO)
from genome.hero1.lang import Policy, CATS, MAXCAP
from genome.hero1 import lang as L1
from genome.hero1.gen_train import (load_bank, sample_policy, cat_phrase, join_list, join_seq, pick, fill, NUMW, NONE_TEXTS,
                                    prompt, render as render_old)
from genome.hero6 import lang6 as L6

# ------------------------------------------------------------------ real guests: token -> surface forms
REAL_PEOPLE = {
    "Will_Scharf": ["Will Scharf", "Scharf"], "Shyam_Sankar": ["Shyam Sankar", "Sankar"],
    "Chamath_Palihapitiya": ["Chamath Palihapitiya", "Palihapitiya", "Chamath"], "Susie_Wiles": ["Susie Wiles", "Wiles"],
    "Greg_Brockman": ["Greg Brockman", "Brockman"], "Secretary_Lutnick": ["Secretary Lutnick", "Lutnick", "Howard Lutnick"],
    "Satya_Nadella": ["Satya Nadella", "Nadella", "Satya"], "Jeff_Bezos": ["Jeff Bezos", "Bezos"],
    "VPOTUS": ["VPOTUS", "the Vice President", "the VP"], "Speaker_Johnson": ["Speaker Johnson", "the Speaker"],
    "David_Sacks": ["David Sacks", "Sacks"], "Lisa_Su": ["Lisa Su", "Dr. Su"],
    "Secretary_Scott_Bessent": ["Secretary Scott Bessent", "Scott Bessent", "Bessent", "Secretary Bessent"],
    "Alex_Karp": ["Alex Karp", "Karp"], "Chairman_Andrew_Ferguson": ["Chairman Andrew Ferguson", "Andrew Ferguson", "Ferguson", "Chairman Ferguson"],
    "Michael_Kratsios": ["Michael Kratsios", "Kratsios"], "Tom_Brown": ["Tom Brown"],
    "Scott_Kupor": ["Scott Kupor", "Kupor"], "Brandon_Rahbar_Daniels": ["Brandon Rahbar Daniels", "Rahbar Daniels"],
    "Dario_Amodei": ["Dario Amodei", "Amodei", "Dario"], "Hock_Tan": ["Hock Tan"],
    "Richard_Walters": ["Richard Walters", "Walters"], "Brad_Gerstner": ["Brad Gerstner", "Gerstner"],
    "Mark_Zuckerberg": ["Mark Zuckerberg", "Zuckerberg", "Zuck"], "Jensen_Huang": ["Jensen Huang", "Huang", "Jensen"],
    "POTUS": ["POTUS", "the President"], "Elon_Musk": ["Elon Musk", "Musk", "Elon", "Tesla", "SpaceX"],
    "Sundar_Pichai": ["Sundar Pichai", "Pichai", "Sundar"], "Director_Clayton": ["Director Clayton", "Clayton"],
    "Sanjay_Mehrotra": ["Sanjay Mehrotra", "Mehrotra"], "Jared_Isaacman": ["Jared Isaacman", "Isaacman"],
    "Bill_McDermott": ["Bill McDermott", "McDermott"], "Nikesh_Arora": ["Nikesh Arora", "Arora"],
    "Sean_Cairncross": ["Sean Cairncross", "Cairncross"],
}
REAL_COMPANIES = {
    "OpenAI": ["OpenAI"], "Anthropic": ["Anthropic"], "Palantir": ["Palantir"], "Microsoft": ["Microsoft"], "Amazon": ["Amazon"],
    "Meta": ["Meta"], "Google": ["Google"], "Nvidia": ["Nvidia", "NVIDIA"], "AMD": ["AMD"], "Broadcom": ["Broadcom"], "Micron": ["Micron"],
    "Exiger": ["Exiger"], "Altimeter": ["Altimeter"], "Social_Capital": ["Social Capital"], "Craft_Ventures": ["Craft Ventures"],
    "NASA": ["NASA"], "Service_Now": ["Service Now", "ServiceNow"], "Palo_Alto_Networks": ["Palo Alto Networks"],
}
COMPANY_WRAP = ["{C}", "{C}", "{C}", "the {C} people", "the {C} folks", "anyone from {C}", "everyone from {C}", "the {C} team",
                "whoever is from {C}", "the {C} guests", "{C}'s people"]

# ------------------------------------------------------------------ invented pool (the model must copy these)
FIRST = """Amara Bogdan Chiara Dmitri Esperanza Farid Greta Hiroshi Ingrid Joaquin Kwame Leilani Mateus Nadia Oluwaseun Priya Quentin
Rosalind Soren Tamar Umberto Valentina Wojciech Ximena Yusuf Zanele Aiko Bartholomew Camille Declan Eun-ji Fatima Gideon Hana Ignatius
Jolene Kofi Ludmila Marisol Nikolai Odette Pradeep Rafaela Siddharth Thandiwe Ulrich Vesna Winifred Xavier Yara Zoltan Anouk Benedikt
Cosima Dagny Emeka Fionnuala Gaspard Hollis Imogen Jasper Katarzyna Lorenzo Meera Nnamdi Orla Paolo Rania Stellan Tobias Ursula Viggo
Wren Yevgenia Zubair Ahmad Beatriz Cormac Delphine Elif Florin Gulnara Hamid Isolde Jiro Kalani Lars Mireille Nour Osvaldo Petra Rashida
Saoirse Teodor Uma Vikram Wilhelmina Yosef Zofia Arjun Brigid Caspian Dilnoza Ezra Frida Grigori Hyun-woo Ilse Jean-Luc Kiri Lucia""".split()
LAST = """Abernathy Bergstrom Castellanos Dubois Eriksen Fontaine Gallagher Haddad Ibarra Jankowski Kowalczyk Lindqvist Moreau Nakamura
Okonkwo Petrov Quintero Rasmussen Szabo Takahashi Uzoma Vasquez Whitfield Xiong Yamamoto Zielinski Achebe Brennan Chowdhury Delacroix
Esposito Fairbanks Gonzaga Hartmann Iyer Jovanovic Kaminski Lemaire Mbeki Novak O'Sullivan Pereira Quarshie Rinaldi Sorensen Tanaka
Ugwu Villanueva Wexler Yilmaz Zapata Adeyemi Bianchi Carvalho Dimitriou Eklund Ferreira Grünewald Holloway Ishikawa Jaramillo Kuznetsov
Lachance Mwangi Nordin Oyelaran Pastore Radcliffe Sandoval Thorsen Underhill Valdez Winterbottom Yoshida Zaragoza Ansari Blackwood
Cienfuegos Dunleavy Ekwueme Fitzgerald-Ruiz Gutierrez Halvorsen Ivanova Juarez Kirkpatrick Lombardi MacAllister Nieminen Oduya Pham
Rourke Stavros Trevisan Umarov Vukovic Whitlock Ybarra Zhou Arceneaux Beaumont Coltrane Dasgupta""".split()
CO_A = """Brightwave Kestrel Norden Halcyon Tidewater Quillon Ferrous Lumen Verdant Cobalt Aster Blue Harbor Silverline Granite Polaris
Redwood Solace Juniper Meridian Obsidian Tessellate Nimbus Corvid Saffron Ironbark Lattice Pioneer Vantage Helix Orchard Sable Zephyr
Cascade Emberly Foxglove Glasswing Hawthorne Ivory Jetstream Kindling Lodestar Marlow Northwind Opaline Parallax Quarry Riverbend
Starling Thornfield Umbra Vireo Wildcard Yellowfin Zenith Arclight Bramble Copperleaf Driftwood""".split()
CO_B = ["Labs", "Capital", "Robotics", "Systems", "Ventures", "Analytics", "Partners", "Dynamics", "Semiconductor", "Health",
        "Energy", "AI", "Networks", "Bio", "Security", "Holdings", "Foundry", "Media", "Logistics", "Group", "", "", "", "Inc", "Research"]


def invented_person(r):
    return f"{r.choice(FIRST)} {r.choice(LAST)}"


def invented_company(r):
    b = r.choice(CO_B)
    a = r.choice(CO_A)
    return f"{a} {b}".strip() if b else (a if r.random() < 0.5 else a + r.choice(["ly", "io", "ware", "tech", "scale"]))


def entity(r):
    """-> (token, surface)"""
    u = r.random()
    if u < 0.34:
        tok = r.choice(list(REAL_PEOPLE)); forms = REAL_PEOPLE[tok]
        s = forms[0] if r.random() < 0.45 or len(forms) == 1 else r.choice(forms[1:])
        return tok, s
    if u < 0.50:
        tok = r.choice(list(REAL_COMPANIES)); c = r.choice(REAL_COMPANIES[tok])
        return tok, (c if r.random() < 0.6 else r.choice(COMPANY_WRAP).replace("{C}", c))
    if u < 0.85:
        s = invented_person(r); return L6.key(s), s
    c = invented_company(r)
    return L6.key(c), (c if r.random() < 0.6 else r.choice(COMPANY_WRAP).replace("{C}", c))


def entities(r, k):
    out, toks = [], set()
    while len(out) < k:
        t, s = entity(r)
        if t in toks or any(s.lower() == o[1].lower() for o in out): continue
        toks.add(t); out.append((t, s))
    return out


def names(ss, r, word="and"):
    return join_list(ss, r, word)


# ------------------------------------------------------------------ named clause templates
AVOID1 = ["Keep {X} away from {Y}.", "{X} and {Y} shouldn't sit together.", "Don't let {X} near {Y}.", "Never seat {X} with {Y}.",
          "{X} and {Y} in different sections.", "Separate {X} and {Y}.", "{X} can't be in the same section as {Y}.",
          "{X} nowhere near {Y}.", "Keep {X} and {Y} apart.", "{X} should not share a section with {Y}.",
          "Make sure {X} isn't seated with {Y}.", "Split up {X} and {Y}.", "No {X} near {Y}.", "{X} must not sit with {Y}.",
          "Please keep {X} far from {Y}.", "Don't put {X} and {Y} in the same section.", "{X} away from {Y}.",
          "{X} and {Y}: different sections.", "{X} is not to be seated in the same section as {Y}.", "Avoid seating {X} with {Y}.",
          "Under no circumstances should {X} end up in a section with {Y}.", "{X} goes nowhere near {Y}.",
          "Can you keep {X} away from {Y}?", "{X} should be kept apart from {Y}.", "{X} and {Y} must never share a section.",
          "Whatever you do, don't seat {X} next to {Y}.", "Keep {X} clear of {Y}.", "{X} not with {Y}.",
          "I don't want {X} and {Y} in one section.", "No section with both {X} and {Y}."]
AVOIDN = ["Keep {X} away from {YS}.", "{X} shouldn't sit with {YSOR}.", "Don't seat {X} near {YSOR}.", "{X} nowhere near {YS}.",
          "Keep {X} apart from {YS}.", "{YS} must all be kept away from {X}.", "Don't let {X} near {YSOR}.",
          "{X} must not share a section with {YSOR}.", "Separate {X} from {YS}.", "{X} should be kept away from {YS}.",
          "No {YSOR} anywhere near {X}.", "Make sure {X} isn't seated with {YSOR}.", "{X} away from {YS}.",
          "Keep {X} away from {YFROM}.", "{X} can't sit with {YSOR}."]
AVOID_MUTUAL = ["{XS} should all be in different sections.", "Keep {XS} apart from each other.", "No two of {XSOR} in the same section.",
                "{XS} must each sit in a different section.", "Split up {XS}."]
PAIR1 = ["Seat {X} with {Y}.", "{X} and {Y} together.", "Put {X} next to {Y}.", "{X} and {Y} in the same section.",
         "Keep {X} and {Y} together.", "{X} should sit with {Y}.", "Group {X} with {Y}.", "Make sure {X} is seated alongside {Y}.",
         "Don't split up {X} and {Y}.", "{X} sits with {Y}.", "Please seat {X} and {Y} together.", "{X} goes with {Y}.",
         "Put {X} and {Y} in one section.", "{X} needs to be in the same section as {Y}.", "Can {X} sit with {Y}?",
         "I'd like {X} seated with {Y}.", "{X} + {Y} together.", "Keep {X} with {Y}.", "{X} and {Y} share a section.",
         "Seat {X} in the same section as {Y}."]
PAIRN = ["Put {XS} in the same section.", "{XS} together.", "Seat {XS} together.", "Keep {XS} in one section.",
         "{XS} should all sit together.", "Group {XS}.", "Make sure {XS} share a section.", "{XS} all in the same section.",
         "Seat {X} with {YS}.", "Keep {X} together with {YS}.", "Put {X} alongside {YS}."]
PAIR_AVOID = ["Keep {A} and {B} together, and keep {C} away from both.", "{A} with {B}, but {C} away from them.",
              "Seat {A} next to {B}; {C} should sit with neither.", "{A} and {B} in one section, and {C} not near either of them.",
              "Put {A} and {B} together and don't let {C} near them."]


def named_clause(r):
    """-> (text, [(word, X, Y)])"""
    u = r.random()
    if u < 0.33:
        (x, xs), (y, ys) = entities(r, 2)
        return fill(r.choice(AVOID1), X=xs, Y=ys), [("avoid", x, y)]
    if u < 0.56:
        es = entities(r, r.choice([2, 2, 3, 3, 4])); (x, xs), rest = es[0], es[1:]
        yl = [s for _, s in rest]
        t = fill(r.choice(AVOIDN), X=xs, YS=names(yl, r, "and"), YSOR=names(yl, r, "or"),
                 YFROM=" and from ".join(yl) if len(yl) < 3 else ", from ".join(yl[:-1]) + " and from " + yl[-1])
        return t, [("avoid", x, y) for y, _ in rest]
    if u < 0.60:
        es = entities(r, 3)
        t = fill(r.choice(AVOID_MUTUAL), XS=names([s for _, s in es], r, "and"), XSOR=names([s for _, s in es], r, "or"))
        return t, [("avoid", es[0][0], es[1][0]), ("avoid", es[0][0], es[2][0]), ("avoid", es[1][0], es[2][0])]
    if u < 0.80:
        (x, xs), (y, ys) = entities(r, 2)
        return fill(r.choice(PAIR1), X=xs, Y=ys), [("pair", x, y)]
    if u < 0.94:
        es = entities(r, r.choice([3, 3, 3, 4])); x = es[0][0]
        t = fill(r.choice(PAIRN), XS=names([s for _, s in es], r, "and"), X=es[0][1], YS=names([s for _, s in es[1:]], r, "and"))
        return t, [("pair", x, y) for y, _ in es[1:]]
    (a, as_), (b, bs), (c, cs) = entities(r, 3)
    return fill(r.choice(PAIR_AVOID), A=as_, B=bs, C=cs), [("pair", a, b), ("avoid", c, a), ("avoid", c, b)]


def old_clauses(pol, r, B, voice):
    """the clause builder of genome/hero1/gen_train.render (copied), without the final shuffle/join."""
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
    return [(c, None) for c in cl]


def render_named(pol, r, B):
    voices = sorted({e["voice"] for v in B["bank"].values() for e in v})
    voice = r.choice(voices)
    cl = old_clauses(pol, r, B, voice) if pol.sig() else []
    for _ in range(r.choices([1, 2, 3], [0.68, 0.27, 0.05])[0]):
        t, words = named_clause(r); cl.append((t, words))
    r.shuffle(cl)
    words = [w for _, ws in cl if ws for w in ws]
    cl = [c.strip() for c, _ in cl]
    lines = r.random() < 0.15
    if lines:
        mk = r.choice(["- ", "* ", "• ", "NUM", "NUM)"])
        text = "\n".join((f"{i + 1}. " if mk == "NUM" else (f"{i + 1}) " if mk == "NUM)" else mk)) + c for i, c in enumerate(cl))
    else:
        text = cl[0]
        for c in cl[1:]:
            if re.search(r"[.!?]$", text):
                if r.random() < 0.35:       # glue as one sentence: "..., and keep X away from Y."
                    text = text[:-1] + r.choice([", and ", "; ", ", and also ", " and "]) + c[0].lower() + c[1:] if c[:1].isupper() and not _proper(c) else text[:-1] + r.choice([", and ", "; "]) + c
                else:
                    text += r.choice([" ", " ", " ", "\n", " " + r.choice([j for j in B["joiners"] if j[:1].isupper()] or ["Also,"]) + " "]) + c
            else:
                text += r.choice(["; ", ", ", " and ", ". "]) + c
    if r.random() < 0.25: text = r.choice(B["openers"]).strip() + ("\n" if lines else " ") + text
    if r.random() < 0.12:
        cz = r.choice(B["closers"]).strip()
        if cz: text += " " + cz
    return text.strip(), words


def _proper(c):
    w = c.split()[0].strip(",.:;")
    return w not in {"Keep", "Don't", "Never", "Separate", "Make", "Split", "No", "Please", "Avoid", "Under", "Can", "Whatever", "I",
                     "Seat", "Put", "Group", "Sits", "Put", "Seat", "I'd", "Kindly"}


def target(pol, words):
    base = L1.to_text(pol)
    lines = [] if base == "none" else base.split("\n")
    seen = set()
    for w, x, y in words:
        k = (w, min(x, y), max(x, y))
        if k in seen: continue
        seen.add(k); lines.append(f"{w} {x} {y}")
    return "\n".join(lines) if lines else "none"


def build(n_train=11000, n_valid=300, seed=6, p_named=0.62):
    r = random.Random(seed); B = load_bank(True)
    seen, rows = set(), []
    while len(rows) < n_train + n_valid:
        if r.random() < p_named:
            pol = sample_policy(r) if r.random() < 0.55 else Policy()
            text, words = render_named(pol, r, B)
            prog = target(pol, words)
            kind = "named"
        else:
            pol = sample_policy(r); text = render_old(pol, r, B); prog = L1.to_text(pol); kind = "old"
        if text in seen: continue
        L6.parse(prog)            # every target parses
        seen.add(text); rows.append((text, prog, kind, sorted(L6.parse(prog).sig())))
    return rows[:n_train], rows[n_train:]


if __name__ == "__main__":
    nt = int(sys.argv[1]) if len(sys.argv) > 1 else 11000; nv = int(sys.argv[2]) if len(sys.argv) > 2 else 300
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    tr, va = build(nt, nv, seed)
    out = _REPO + "/runs/hero6/data"; os.makedirs(out, exist_ok=True)
    for name, rows in (("train", tr), ("valid", va)):
        with open(f"{out}/{name}.jsonl", "w") as f:
            for text, prog, _, _ in rows:
                f.write(json.dumps({"messages": [{"role": "user", "content": prompt(text)}, {"role": "assistant", "content": prog}]}) + "\n")
    json.dump([dict(text=t, gold=p, kind=k) for t, p, k, _ in va], open(_REPO + "/runs/hero6/valid_set.json", "w"), indent=0)
    sigs = collections.Counter("+".join(s) for _, _, _, s in tr)
    kinds = collections.Counter(k for _, _, k, _ in tr)
    json.dump(dict(n_train=len(tr), n_valid=len(va), seed=seed, kinds=kinds, signatures=dict(sigs.most_common()),
                   n_avoid=sum("avd" in s for *_, s in tr), n_pair=sum("par" in s for *_, s in tr)),
              open(_REPO + "/runs/hero6/train_meta.json", "w"), indent=1)
    print(len(tr), len(va), kinds)
    rr = random.Random(1)
    for t, p, k, _ in rr.sample(tr, 14): print(repr(t), "->", repr(p))
