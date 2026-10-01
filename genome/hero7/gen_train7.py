"""HERO-7 training data (recipe R7). Sources, all generated without reading any test set except for the final overlap filter:
  hero6   the 11,000 HERO-6 training rows (runs/hero6/data/train.jsonl)
  replay  HERO-1 training rows (runs/hero1/data/train.jsonl), so old wordings are not forgotten
  terse   new terse/clipped renderings of old-word policies (own clause bank below), 35% with a terse named clause
  cover   new named sentences: HERO-6 generator with every surname / first name / title of the 34 guests (from the guest list
          only), more avoid/pair wordings (own), honorifics, invented guests mentioned by surname only (target = the surname)
  para    paraphrases of HERO-6 training sentences by a local Qwen3-30B-A3B-Instruct (runs/hero7/para_raw.json), kept only if
          every name surface form and every number of the source survives
Overlap filter (after the test sets were frozen): any row whose normalized text equals a test text, or which shares a word
6-gram with any text of test sets 1, 2, 6 or 7, is dropped; counts in runs/hero7/data_meta.json.
  python -m genome.hero7.gen_train7 [out_dir] [n_replay] [n_terse] [n_cover] [n_para_max]
"""
from __future__ import annotations
import json, os, random, re, sys, collections
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
sys.path.insert(0, _REPO)
from genome.hero1.lang import Policy, CATS, MAXCAP
from genome.hero1 import lang as L1
from genome.hero1.gen_train import load_bank, sample_policy, prompt, NUMW, fill, join_list
from genome.hero6 import gen_train6 as G6
from genome.hero6 import lang6 as L6

ROOT = _REPO
TESTS = [f"{ROOT}/data/hero/policies_test.json", f"{ROOT}/data/hero/policies_test2.json", f"{ROOT}/data/hero/policies_test6.json",
         f"{ROOT}/data/hero/policies_test7.json"]

# ---------------------------------------------------------------- coverage of the guest list (derived from luncheon.json only)
EXTRA_FORMS = {
    "Lisa_Su": ["Su", "Lisa", "Ms. Su"], "Hock_Tan": ["Tan", "Hock", "Mr. Tan"],
    "Brandon_Rahbar_Daniels": ["Daniels", "Brandon Daniels", "Rahbar", "Brandon"], "Tom_Brown": ["Brown", "Mr. Brown"],
    "Speaker_Johnson": ["Johnson", "the Speaker of the House"], "Will_Scharf": ["Will", "Mr. Scharf"], "Susie_Wiles": ["Susie", "Ms. Wiles"],
    "Greg_Brockman": ["Greg"], "Alex_Karp": ["Alex"], "Jeff_Bezos": ["Jeff"], "Mark_Zuckerberg": ["Mark"], "David_Sacks": ["David"],
    "Brad_Gerstner": ["Brad"], "Bill_McDermott": ["Bill"], "Nikesh_Arora": ["Nikesh"], "Sanjay_Mehrotra": ["Sanjay"],
    "Jared_Isaacman": ["Jared", "Administrator Isaacman"], "Michael_Kratsios": ["Michael", "Mr. Kratsios"], "Sean_Cairncross": ["Sean"],
    "Richard_Walters": ["Richard"], "Shyam_Sankar": ["Shyam"], "Scott_Kupor": ["Mr. Kupor"], "Director_Clayton": ["the Director"],
    "Chairman_Andrew_Ferguson": ["the Chairman"], "Secretary_Lutnick": ["Mr. Lutnick"], "Secretary_Scott_Bessent": ["Mr. Bessent"],
    "VPOTUS": ["Vice President", "the veep", "VP"], "POTUS": ["President", "the boss"], "Dario_Amodei": ["Mr. Amodei"],
    "Jensen_Huang": ["Mr. Huang"], "Elon_Musk": ["Mr. Musk"], "Satya_Nadella": ["Mr. Nadella"], "Sundar_Pichai": ["Mr. Pichai"],
}
AVOID_MORE = ["{X} and {Y} must be seated in separate sections.", "Don't seat {X} anywhere {Y} is.", "{X} should be kept out of {Y}'s section.",
              "Whichever section {X} is in, {Y} is not.", "{X} and {Y} can't be in one group.", "No overlap between {X} and {Y}.",
              "{X} ≠ {Y}.", "{X} / {Y}: split.", "{X} vs {Y}: different sections.", "Keep {X} from sitting with {Y}.",
              "{X} shouldn't end up with {Y}.", "Give {X} a section without {Y}.", "Seat {X} and {Y} far apart.",
              "Make sure {X} and {Y} don't share a table.", "No {X} with {Y}.", "{X} not near {Y}.", "{X}, {Y}: separate.",
              "{X} must be kept from {Y}.", "Don't pair {X} with {Y}.", "{X} and {Y} should not be paired up.", "{X} apart from {Y}.",
              "Please don't put {X} together with {Y}.", "{X} and {Y} are not to sit together.", "Not {X} with {Y}.",
              "{X} gets a different section than {Y}.", "Don't let {X} and {Y} end up together."]
AVOIDN_MORE = ["Keep {X} from sitting with {YS}.", "{X} must not end up with {YSOR}.", "{X} gets a section without {YSOR}.",
               "{X} away from {YS}, please.", "Don't put {X} together with {YSOR}.", "{X} ≠ {YS}."]
PAIR_MORE = ["{X} and {Y}: same section.", "{X} w/ {Y}.", "{X} + {Y}.", "Pair {X} with {Y}.", "Pair {X} and {Y}.", "{X} next to {Y}, please.",
             "Can {X} and {Y} be in one section?", "Put {X} in {Y}'s section.", "{X} joins {Y}.", "Keep {X} beside {Y}.",
             "{X} should be paired with {Y}.", "Seat {X} alongside {Y}.", "{X} and {Y} sit together."]


def install_cover():
    for k, v in EXTRA_FORMS.items(): G6.REAL_PEOPLE[k] = G6.REAL_PEOPLE[k] + [f for f in v if f not in G6.REAL_PEOPLE[k]]
    G6.AVOID1 += AVOID_MORE; G6.AVOIDN += AVOIDN_MORE; G6.PAIR1 += PAIR_MORE
    old_entity = G6.entity
    def entity(r):
        u = r.random()
        if u < 0.07:                                      # invented guest mentioned by surname only: copy the surname
            s = r.choice(G6.LAST); return L6.key(s), s
        if u < 0.12:                                      # honorific + invented surname
            s = r.choice(G6.LAST); return L6.key(s), r.choice(["Mr.", "Ms.", "Dr."]) + " " + s
        return old_entity(r)
    G6.entity = entity


# ---------------------------------------------------------------- terse / clipped bank (own)
TCAT = {"ai_lab": ["labs", "AI labs", "AI", "the labs", "AI cos", "model labs"],
        "big_tech": ["big tech", "bigtech", "tech giants", "megacaps", "big tech cos"],
        "chips": ["chips", "chip makers", "chipmakers", "semis", "chip cos", "chip people"],
        "software_security": ["software", "security", "software/security", "software & security", "cyber", "sec + software", "software cos"],
        "investor": ["investors", "VCs", "funds", "money people", "investor guests"],
        "government": ["gov", "govt", "officials", "gov't", "government", "gov folks"],
        "unlabelled": ["staff", "unaffiliated", "no-affiliation guests", "advisers", "unlabelled"]}
TSIZE = ["Cap {N}.", "Cap of {N}.", "Max {N}.", "{N} max.", "{N} per section.", "{N}/section.", "Sections of {N}.", "Groups of {N}.",
         "Tables of {N}.", "Size {N}.", "≤{N} per section.", "{NW} per section max.", "Max {NW}.", "Cap at {N}.", "{N} a section.",
         "Section cap {N}.", "{NW} max per section."]
TSIZE_SP = {1: ["Singles.", "One per section.", "Solo sections."], 2: ["Pairs only.", "Twos.", "In pairs.", "Seat in pairs.", "Pairs.",
            "Sections of two.", "Pairs, please."], 3: ["Trios.", "Threes.", "In threes."], 4: ["Fours.", "Foursomes."]}
TTC = ["Cos together.", "Companies together.", "Same co together.", "Colleagues together.", "Keep cos together.", "By company.",
       "Group by company.", "Together company.", "Company groups intact.", "Don't split companies."]
TTK = ["{CAT} together.", "{CAT} in one block.", "Group {CAT}.", "All {CAT} together.", "{CAT}: one section.", "Keep {CAT} together."]
TLIM = ["{CATS} max {K}/section.", "≤{K} {CATS} per section.", "{CATS} cap {K}.", "Max {K} {CATS}.", "{K} {CATS} per section max.",
        "Limit {CATS} {K}.", "{CATS}: {K} per section.", "{CATS} {K} max."]
TLIM1 = ["One {CATS} per section.", "{CATS}: 1 per section.", "No two {CATS} together.", "Max one {CATS}.", "Single {CATS} per section."]
TAPT = ["{A} and {B} apart.", "{A}/{B} apart.", "{A} ≠ {B}.", "{A} away from {B}.", "No {A} with {B}.", "{A} vs {B}: split.",
        "Split {A} and {B}.", "{A}, {B} apart.", "{A} not with {B}.", "Keep {A} off {B}."]
TORD = ["{SEQ} first.", "Order: {SEQ}.", "Lead with {SEQ}.", "Seat {SEQ} first.", "{SEQ} up front.", "First {SEQ}."]
TNAMED_AVOID = ["{X} ≠ {Y}.", "{X}/{Y} apart.", "No {X} + {Y}.", "{X} away from {Y}.", "{X} not w/ {Y}.", "Split {X}, {Y}.",
                "{X} vs {Y}: split.", "{X} off {Y}."]
TNAMED_PAIR = ["{X} w/ {Y}.", "{X} + {Y}.", "{X} with {Y}.", "Pair {X}/{Y}.", "{X} & {Y} together.", "{X}, {Y} same section."]


def tcat(c, r): return r.choice(TCAT[CATS[c]])


def render_terse(pol, r):
    cl = []
    if pol.cap != MAXCAP:
        sp = TSIZE_SP.get(pol.cap, [])
        t = r.choice(sp) if sp and r.random() < 0.35 else r.choice(TSIZE)
        cl.append(fill(t, N=pol.cap, NW=NUMW[pol.cap]))
    if pol.tog_company: cl.append(r.choice(TTC))
    for c in pol.tog_cats: cl.append(fill(r.choice(TTK), CAT=tcat(c, r)))
    for cs, k in pol.limits:
        phr = join_list([tcat(c, r) for c in cs], r, r.choice(["or", "+", "/", "and"]))
        cl.append(fill(r.choice(TLIM1 if k == 1 and r.random() < 0.45 else TLIM), CATS=phr, K=k))
    for a, b in pol.aparts:
        if r.random() < 0.5: a, b = b, a
        cl.append(fill(r.choice(TAPT), A=tcat(a, r), B=tcat(b, r)))
    if pol.order:
        ps = [tcat(c, r) for c in pol.order]
        seq = r.choice([" > ".join(ps), ", ".join(ps), ", then ".join(ps), " then ".join(ps), " → ".join(ps)])
        cl.append(fill(r.choice(TORD), SEQ=seq))
    words = []
    if r.random() < 0.35:
        k = r.choice(["a", "p"]); (x, xs), (y, ys) = G6.entities(r, 2)
        cl.append(fill(r.choice(TNAMED_AVOID if k == "a" else TNAMED_PAIR), X=xs, Y=ys)); words.append(("avoid" if k == "a" else "pair", x, y))
    r.shuffle(cl)
    sep = r.choice([" ", " ", " / ", "; ", "\n", ", ", " | "])
    text = sep.join(cl if sep == " " or sep == "\n" else [c.rstrip(".") for c in cl])
    if r.random() < 0.2: text = text.lower()
    if r.random() < 0.15: text = r.choice(["Notes:", "Rules:", "Seating:", "fyi", "Quick notes -"]) + (" " if "\n" not in sep else "\n") + text
    return text.strip(), words


# ---------------------------------------------------------------- overlap filter
def norm(t): return " ".join(re.findall(r"[a-z0-9]+", t.lower()))


def test_texts():
    out = []
    for p in TESTS:
        d = json.load(open(p)); ps = d["policies"] if isinstance(d, dict) else d
        out += [norm(x["text"]) for x in ps]
    return out


def grams(t, n=6):
    w = t.split(); return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def read_rows(path):
    rows = []
    for l in open(path):
        m = json.loads(l)["messages"]
        rows.append((m[0]["content"].split("## Policy\n\n", 1)[1].split("\n\n## Reply format", 1)[0], m[1]["content"]))
    return rows


NUMRE = re.compile(r"\b([1-6]|one|two|three|four|five|six)\b", re.I)


def para_rows(maxn):
    path = f"{ROOT}/runs/hero7/para_raw.json"
    if not os.path.exists(path): return [], dict(raw=0)
    items = json.load(open(path))["items"]; keep = []; why = collections.Counter()
    for it in items:
        src, para = it["src"], it["para"].strip().strip('"')
        if not para or len(para) > 400 or "\n\n\n" in para: why["empty/long"] += 1; continue
        if not re.search(r"[.!?)]\s*$", para): why["truncated"] += 1; continue
        # every word of a named token (avoid/pair argument) that the source spells out must survive in the paraphrase
        toks = [x for l in it["prog"].splitlines() if l.split()[0] in ("avoid", "pair") for x in l.split()[1:]]
        need = {w for x in toks for w in x.split("_") if re.search(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", src)}
        if any(not re.search(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", para) for w in need): why["name lost"] += 1; continue
        ns = sorted(NUMW.get(int(x), x).lower() if x.isdigit() else x.lower() for x in NUMRE.findall(src))
        np_ = sorted(NUMW.get(int(x), x).lower() if x.isdigit() else x.lower() for x in NUMRE.findall(para))
        if collections.Counter(ns) - collections.Counter(np_): why["number lost"] += 1; continue
        keep.append((para, it["prog"]))
    return keep[:maxn], dict(raw=len(items), kept=len(keep[:maxn]), dropped=dict(why))


def main(out=f"{ROOT}/runs/hero7/data", n_replay=4000, n_terse=1800, n_cover=1800, n_para=1500, seed=7):
    n_replay, n_terse, n_cover, n_para = int(n_replay), int(n_terse), int(n_cover), int(n_para)
    r = random.Random(seed); B = load_bank(True)
    src = collections.OrderedDict()
    src["hero6"] = read_rows(f"{ROOT}/runs/hero6/data/train.jsonl")
    h1 = read_rows(f"{ROOT}/runs/hero1/data/train.jsonl"); r.shuffle(h1); src["replay"] = h1[:n_replay]
    terse = []
    while len(terse) < n_terse:
        pol = sample_policy(r)
        t, w = render_terse(pol, r); terse.append((t, G6.target(pol, w)))
    src["terse"] = terse
    install_cover()
    cover = []
    while len(cover) < n_cover:
        pol = sample_policy(r) if r.random() < 0.4 else Policy()
        t, w = G6.render_named(pol, r, B); cover.append((t, G6.target(pol, w)))
    src["cover"] = cover
    src["para"], pmeta = para_rows(n_para)
    T = test_texts(); Tset = set(T); TG = set().union(*[grams(t) for t in T])
    seen, rows, meta = set(), [], dict(sources={}, para=pmeta, filter="drop if normalized text equals a test text (sets 1,2,6,7) or shares a word 6-gram with one")
    for name, rs in src.items():
        c = collections.Counter()
        for t, p in rs:
            L6.parse(p); nt = norm(t)
            if nt in Tset: c["exact_test"] += 1; continue
            if grams(nt) & TG: c["6gram_test"] += 1; continue
            if nt in seen: c["dup"] += 1; continue
            seen.add(nt); rows.append((t, p, name)); c["kept"] += 1
        meta["sources"][name] = dict(c)
    r.shuffle(rows)
    nv = 300; va, tr = rows[:nv], rows[nv:]
    os.makedirs(out, exist_ok=True)
    for nm, rs in (("train", tr), ("valid", va)):
        with open(f"{out}/{nm}.jsonl", "w") as f:
            for t, p, _ in rs:
                f.write(json.dumps({"messages": [{"role": "user", "content": prompt(t)}, {"role": "assistant", "content": p}]}) + "\n")
    meta["n_train"], meta["n_valid"] = len(tr), len(va)
    meta["train_by_source"] = dict(collections.Counter(s for *_, s in tr))
    json.dump(meta, open(f"{ROOT}/runs/hero7/data_meta.json", "w"), indent=1)
    print(json.dumps(meta, indent=1))
    rr = random.Random(1)
    for t, p, s in rr.sample(tr, 16): print(s, repr(t), "->", repr(p))


if __name__ == "__main__": main(*sys.argv[1:])
