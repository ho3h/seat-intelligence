"""HERO-4 stage language: the text the small model emits (one word per line), its strict parser, and the prompt with the WORD BLOCK.

  group company | group category            spread                 order rank | order rank desc | order category <c>... | order company <Co>...
  sections S | captains S    (closing; exactly one, last)
  limit <cat> <k> <S>   pair <catA> <catB>   apart <CoX> <CoY>   vip <R>   stagger <m>   headseat   bigfirst
  waitlist <cat> <k>    snake <S>            sectionlead <S>

A word's SHOWN NAME may differ from its canonical name (alias training, see docs/HERO-4.md): the prompt's word block defines the
names in force for that prompt, and `parse(text, names)` maps shown names back to canonical words.
"""
from __future__ import annotations
import re
from genome.hero4.refs import CATS, CO, TASK_CATS, TASK_COS, ARRANGE, CLOSING

CLOSERS = {"sections", "captains"}
ARITY = {  # canonical word -> (min args, max args) after the word token
    "group": (1, 1), "spread": (0, 0), "order": (1, 40), "sections": (1, 1), "captains": (1, 1),
    "limit": (3, 3), "pair": (2, 2), "apart": (2, 2), "vip": (1, 1), "stagger": (1, 1), "headseat": (0, 0), "bigfirst": (0, 0),
    "waitlist": (2, 2), "snake": (1, 1), "sectionlead": (1, 1)}


class ParseError(ValueError): pass


def _int(tok, lo, hi):
    if not re.fullmatch(r"\d+", tok): raise ParseError(f"not a number: {tok}")
    v = int(tok)
    if not lo <= v <= hi: raise ParseError(f"out of range: {v}")
    return v


def _cat(tok):
    if tok not in TASK_CATS: raise ParseError(f"unknown category: {tok}")
    return tok


def _co(tok):
    if tok not in TASK_COS: raise ParseError(f"unknown company: {tok}")
    return tok


def parse_line(w, args):
    """canonical word + raw arg tokens -> word tuple (raises ParseError)"""
    lo, hi = ARITY[w]
    if not lo <= len(args) <= hi: raise ParseError(f"{w}: wrong number of arguments")
    if w == "group":
        if args[0] not in ("company", "category"): raise ParseError("group: company or category")
        return ("group", args[0])
    if w == "order":
        if args[0] == "rank":
            if len(args) == 1: return ("order", "rank")
            if args[1:] == ["desc"]: return ("order", "rankdesc")
            raise ParseError("order rank [desc]")
        if args[0] == "category": names = [_cat(a) for a in args[1:]]
        elif args[0] == "company": names = [_co(a) for a in args[1:]]
        else: raise ParseError("order: rank, category or company")
        if not names or len(set(names)) != len(names): raise ParseError("order: list of distinct names")
        return ("order", args[0], *names)
    if w in ("sections", "captains", "snake", "sectionlead"): return (w, _int(args[0], 1, 40))
    if w == "limit": return ("limit", _cat(args[0]), _int(args[1], 1, 40), _int(args[2], 2, 40))
    if w == "pair":
        a, b = _cat(args[0]), _cat(args[1])
        if a == b: raise ParseError("pair: two different categories")
        return ("pair", a, b)
    if w == "apart":
        a, b = _co(args[0]), _co(args[1])
        if a == b: raise ParseError("apart: two different companies")
        return ("apart", a, b)
    if w == "vip": return ("vip", _int(args[0], 0, 31))
    if w == "stagger": return ("stagger", _int(args[0], 1, 40))
    if w == "waitlist": return ("waitlist", _cat(args[0]), _int(args[1], 0, 40))
    if w in ("spread", "headseat", "bigfirst"): return (w,)
    raise ParseError(f"unknown word {w}")


def fmt_word(t):
    if t[0] == "order" and t[1] == "rankdesc": return "order rank desc"
    return " ".join(str(a) for a in t)


def to_text(words): return "\n".join(fmt_word(w) for w in words)


def parse(text, names=None):
    """text -> list of word tuples; the last is a closing word and no other line is. `names`: shown name -> canonical."""
    names = names or {}
    lines = [l.strip() for l in text.strip().splitlines()]
    lines = [l for l in lines if l and not l.startswith("```")]
    if not lines: raise ParseError("empty")
    words = []
    for l in lines:
        toks = l.split()
        w = names.get(toks[0], toks[0])
        if w not in ARITY: raise ParseError(f"unknown word: {toks[0]}")
        words.append(parse_line(w, toks[1:]))
    for i, w in enumerate(words):
        if (w[0] in CLOSERS) != (i == len(words) - 1): raise ParseError("exactly one closing word, last")
    return words


def assemble(words):
    """ONE net for the whole program: every word's verified template net, piped by genome.compose.compose_nets."""
    from genome.compose import compose_nets
    from genome.hero4.words import BUILD
    from genome.hero4.newwords import BUILD_NEW
    B = {**BUILD, **BUILD_NEW}
    return compose_nets([B[w[0]](list(w[1:])) for w in words])


# ------------------------------------------------------------------ the word block (signature + gloss + ONE worked example)
CAT_SURFACE = {
    "ai_lab": ["AI labs", "frontier AI labs", "AI companies", "AI lab guests"],
    "big_tech": ["big tech firms", "big tech", "large technology companies", "tech giants"],
    "chips": ["chip makers", "semiconductor companies", "chip companies", "silicon firms"],
    "software_security": ["software and security firms", "cybersecurity and software companies", "security software vendors", "software and security guests"],
    "investor": ["investors", "investment firms", "venture and investment guests", "funds"],
    "government": ["government officials", "administration officials", "government guests", "public officials"],
}


def co_surface(c): return c.replace("_", " ")


# word entries: canonical name -> (signature with {N} for the shown name, gloss, example rule text, example program line(s) with {N})
ENTRIES = {
    "group": ("{N} company|category", "Seat guests with the same company (or the same category) next to each other, as one block per company (or category).",
              "Colleagues from one company should sit together.", "{N} company"),
    "spread": ("{N}", "Deal the categories round-robin so that guests of one category are spread out instead of sitting together.",
               "Please keep guests of the same category apart from each other.", "{N}"),
    "order": ("{N} rank|rank desc|category <cat>...|company <Co>...",
              "Priority order: by the numeric rank (lowest number first, or highest first with desc), or by a listed sequence of categories or companies (unlisted ones after).",
              "Seat government officials first, then investors.", "{N} category government investor"),
    "sections": ("{N} <S>", "CLOSING word. Cut the seating order into sections of S seats each and output every guest's section.",
                 "Each table seats 8.", "{N} 8"),
    "captains": ("{N} <S>", "CLOSING word. Cut the seating order into sections of S seats and output only each section's captain (the lowest rank number).",
                 "Sections have 5 seats; I only want each section's captain.", "{N} 5"),
    # ---- the ten NEW words (their entries are what a frontier author adds to the prompt; see docs/HERO-4.md section 4)
    "limit": ("{N} <cat> <k> <S>", "In each section of S seats, seat at most k guests of category <cat>.",
              "No table of 7 may have more than 3 investors.", "{N} investor 3 7"),
    "pair": ("{N} <catA> <catB>", "Seat every guest of category <catA> directly next to a guest of category <catB> (A, B, A, B, ...).",
             "Put each AI lab guest right beside a chip maker.", "{N} ai_lab chips"),
    "apart": ("{N} <CoX> <CoY>", "Keep the guests of company X as far from company Y's guests as the table allows (X at the head, Y at the foot).",
              "Keep Meta and Amazon at opposite ends of the table.", "{N} Meta Amazon"),
    "vip": ("{N} <R>", "Guests whose rank number is R or lower take the first seats; the rest keep their order after them.",
            "Anyone with rank 4 or better goes to the front.", "{N} 4"),
    "stagger": ("{N} <m>", "Seat in rounds: each round takes at most m guests from every company; later guests of a company wait for later rounds.",
                "Bring guests in waves, no more than 2 from any one company per wave.", "{N} 2"),
    "headseat": ("{N}", "The guest with the lowest rank number takes seat 1; everyone else keeps their order.",
                 "Whoever has the smallest rank number gets the first seat.", "{N}"),
    "bigfirst": ("{N}", "Larger company delegations are seated before smaller ones (ties by company); guests without a company go last.",
                 "Companies that brought the most people are seated first.", "{N}"),
    "waitlist": ("{N} <cat> <k>", "Only the first k guests of category <cat> keep their place; further ones of that category go to the very end.",
                 "Only the first 3 chip makers get regular seats; the rest wait at the end.", "{N} chips 3"),
    "snake": ("{N} <S>", "Reverse the seat order inside every second section (the 2nd, 4th, ...) of S seats.",
              "Every other table of 6 runs in the opposite direction.", "{N} 6"),
    "sectionlead": ("{N} <S>", "In each section of S seats, the guest with the lowest rank number moves to the section's first seat.",
                    "At each table of 5, the lowest-ranked guest takes the head seat.", "{N} 5"),
}
BASE_ORDER = ["group", "spread", "order", "sections", "captains"]
NEW_ORDER = ["limit", "pair", "apart", "vip", "stagger", "headseat", "bigfirst", "waitlist", "snake", "sectionlead"]

ALIASES = {  # shown-name pools for BASE words (alias training); canonical name is one of each pool. New words have fixed names.
    "group": ["group", "cluster", "bunch", "huddle", "tie"],
    "spread": ["spread", "deal", "sprinkle", "fan", "disperse"],
    "order": ["order", "prioritize", "queue", "rankby", "line_up"],
    "sections": ["sections", "tables", "pods", "chunk", "split"],
    "captains": ["captains", "leads", "chairs", "anchors", "heads"],
}


def _entries():
    """ENTRIES, with revised entries (round 2) overlaid when env HERO4_ENTRIES_FILE names a JSON {word: [sig, gloss, ex_text, ex_line]}"""
    import json, os
    f = os.environ.get("HERO4_ENTRIES_FILE")
    if not f: return ENTRIES
    e = dict(ENTRIES); e.update({k: tuple(v) for k, v in json.load(open(f)).items()}); return e


def word_block(available, names=None, order=None):
    """The vocabulary block of the prompt. available: canonical words in the library; names: canonical -> shown name."""
    names = names or {}
    ENTRIES = _entries()
    order = order or list(available)
    lines = []
    for w in order:
        sig, gloss, ex_text, ex_line = ENTRIES[w]; N = names.get(w, w)
        lines.append(f"- `{sig.format(N=N)}` : {gloss}\n    Example: \"{ex_text}\" -> `{ex_line.format(N=N)}`")
    return "\n".join(lines)


CATS_LINE = "Category tokens: " + "; ".join(f"{k} ({v[0]})" for k, v in CAT_SURFACE.items()) + "."
COS_LINE = "Company tokens (spelled with underscores): " + ", ".join(TASK_COS) + "."

HEADER = ("You turn a host's seating rules into a program made of WORDS, one word per line. The words available are listed below. "
          "Use only these words. Write the arrangement words in the order the rules are stated, and end with exactly one CLOSING word. "
          "Reply with the program only.\n\n")


def prompt(text, available, names=None, order=None):
    return (HEADER + "## Words\n\n" + word_block(available, names, order) + "\n\n" + CATS_LINE + "\n" + COS_LINE
            + "\n\n## Host's rules\n\n" + text.strip() + "\n\n## Program\n")


def sample_names(rng, available_base):
    """alias assignment for one training prompt: shown name of each BASE word drawn from its pool"""
    return {w: rng.choice(ALIASES[w]) for w in available_base}
