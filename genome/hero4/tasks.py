"""HERO-4 task specs: structured (kind, params) items -> gold stage program, and NEUTRAL descriptions handed to independent
wording writers (who never see the word signatures, glosses or examples of lang.py).

A task = {"id", "family", "items": [item, ...], "closing": {"kind": "sections"|"captains", "S": int}}
item = {"kind": "limit", "cat": "government", "k": 2, "S": 6} ...  Text order == program order; the closing statement may go anywhere.
"""
from __future__ import annotations
import hashlib, json, random
from genome.hero4.refs import TASK_CATS, TASK_COS
from genome.hero4.lang import CAT_SURFACE, co_surface, parse_line

CAT_PLAIN = {"ai_lab": "AI labs", "big_tech": "big tech firms", "chips": "chip makers", "software_security": "software and security firms",
             "investor": "investors", "government": "government officials"}


def item_words(it):
    k = it["kind"]
    if k == "group_company": return ("group", "company")
    if k == "group_category": return ("group", "category")
    if k == "spread": return ("spread",)
    if k == "order_rank": return ("order", "rank")
    if k == "order_rankdesc": return ("order", "rankdesc")
    if k == "order_category": return ("order", "category", *it["names"])
    if k == "order_company": return ("order", "company", *it["names"])
    if k in ("limit", "waitlist"): return (k, it["cat"], it["k"]) + ((it["S"],) if k == "limit" else ())
    if k == "pair": return ("pair", it["a"], it["b"])
    if k == "apart": return ("apart", it["x"], it["y"])
    if k == "vip": return ("vip", it["R"])
    if k == "stagger": return ("stagger", it["m"])
    if k in ("headseat", "bigfirst", "spread"): return (k,)
    if k in ("snake", "sectionlead"): return (k, it["S"])
    raise KeyError(k)


def gold(task):
    words = [item_words(it) for it in task["items"]]
    c = task["closing"]; words.append((c["kind"], c["S"]))
    return words


def neutral(it):
    """plain description of the host's wish in fixed English, for independent wording writers"""
    k = it["kind"]; C = lambda c: CAT_PLAIN[c]; O = co_surface
    if k == "group_company": return "Guests from the same company must sit together, each company forming one block."
    if k == "group_category": return "Guests of the same category must sit together, each category forming one block."
    if k == "spread": return "Guests of the same category must be spread out: hand the categories out in turn, one guest of each category, then the next round, instead of letting a category sit together."
    if k == "order_rank": return "Seat guests in order of their RSVP rank number, lowest number first."
    if k == "order_rankdesc": return "Seat guests in order of their RSVP rank number, highest number first."
    if k == "order_category": return "Seat categories in this priority order (categories not listed come afterwards): " + " > ".join(C(c) for c in it["names"]) + "."
    if k == "order_company": return "Seat companies in this priority order (other companies come afterwards): " + " > ".join(O(c) for c in it["names"]) + "."
    if k == "limit": return f"In every section of {it['S']} seats there may be at most {it['k']} guest(s) from the category {C(it['cat'])}."
    if k == "pair": return f"Every guest from the category {C(it['a'])} must sit right next to a guest from the category {C(it['b'])} (pair them up one to one)."
    if k == "apart": return f"Keep the guests of {O(it['x'])} and the guests of {O(it['y'])} away from each other: {O(it['x'])} at one end of the table and {O(it['y'])} at the other end, everyone else in between."
    if k == "vip": return f"Guests whose RSVP rank number is {it['R']} or lower (better) are moved to the first seats; everyone else keeps their relative order after them."
    if k == "stagger": return f"Seat guests in rounds: in each round a company may contribute at most {it['m']} guest(s); the remaining guests of that company wait for later rounds."
    if k == "headseat": return "The guest with the lowest RSVP rank number takes the very first seat of the table; everyone else keeps the current order."
    if k == "bigfirst": return "Companies that brought more guests are seated before companies that brought fewer (equal sizes: any fixed order); guests without a company come last."
    if k == "waitlist": return f"Only the first {it['k']} guest(s) of the category {C(it['cat'])} keep their place in the seating order; any further guests of that category are sent to the very end."
    if k == "snake": return f"With sections of {it['S']} seats, every second section (the 2nd, 4th, 6th, ...) is seated in reverse direction."
    if k == "sectionlead": return f"In every section of {it['S']} seats, the guest with the lowest RSVP rank number takes that section's first seat."
    raise KeyError(k)


def neutral_closing(c):
    if c["kind"] == "sections": return f"The table is divided into sections of {c['S']} seats; the answer is which section each guest is in."
    return f"The table is divided into sections of {c['S']} seats; the answer is only the captain of each section (the guest with the lowest RSVP rank number)."


def rand_item(kind, rng):
    cats = TASK_CATS; cos = TASK_COS
    S = rng.choice([3, 4, 5, 6, 6, 7, 8, 9, 10])
    if kind == "limit": return {"kind": kind, "cat": rng.choice(cats), "k": rng.choice([1, 2, 2, 3]), "S": rng.choice([4, 5, 6, 7, 8, 10])}
    if kind == "waitlist": return {"kind": kind, "cat": rng.choice(cats), "k": rng.choice([1, 2, 3, 4])}
    if kind == "pair": a, b = rng.sample(cats, 2); return {"kind": kind, "a": a, "b": b}
    if kind == "apart": x, y = rng.sample(cos, 2); return {"kind": kind, "x": x, "y": y}
    if kind == "vip": return {"kind": kind, "R": rng.choice([2, 3, 4, 5, 6, 8, 10, 12, 15])}
    if kind == "stagger": return {"kind": kind, "m": rng.choice([1, 2, 2, 3])}
    if kind in ("snake", "sectionlead"): return {"kind": kind, "S": S}
    if kind == "order_category": n = rng.choice([1, 2, 3, 3, 4]); return {"kind": kind, "names": rng.sample(cats, n)}
    if kind == "order_company": n = rng.choice([1, 2, 2, 3, 4]); return {"kind": kind, "names": rng.sample(cos, n)}
    return {"kind": kind}


def rand_closing(rng, p_captains=0.15):
    return {"kind": "captains" if rng.random() < p_captains else "sections", "S": rng.choice([3, 4, 5, 6, 6, 7, 8, 9, 10])}


BASE_EXTRA = ["group_company", "group_category", "order_rank", "order_rankdesc", "order_category", "order_company", "spread"]


def new_family_tasks(word, n, rng, tag="test"):
    out = []
    for i in range(n):
        it = rand_item(word, rng)
        items = [it]
        r = rng.random()
        if r < 0.3:                                          # add one base rule before or after
            b = rand_item(rng.choice(["group_company", "group_category", "order_rank", "order_rankdesc", "order_category", "order_company"]), rng)
            items = [b, it] if rng.random() < 0.5 else [it, b]
        c = rand_closing(rng)
        if word in ("limit", "snake", "sectionlead"): c["S"] = it["S"]           # the section size is stated once
        out.append({"id": f"{tag}_{word}_{i:02d}", "family": word, "items": items, "closing": c})
    return out


def base_family_tasks(fam, n, rng, tag="test"):
    out = []
    for i in range(n):
        if fam == "group": items = [rand_item(rng.choice(["group_company", "group_category"]), rng)]
        elif fam == "spread": items = [rand_item("spread", rng)]
        elif fam == "order": items = [rand_item(rng.choice(["order_rank", "order_rankdesc", "order_category", "order_company"]), rng)]
        else: items = []
        if fam in ("group", "spread", "order") and rng.random() < 0.4:
            other = rand_item(rng.choice([k for k in BASE_EXTRA if not k.startswith(fam)]), rng)
            items = [other] + items if rng.random() < 0.5 else items + [other]
        if fam == "sections" and rng.random() < 0.4: items = [rand_item(rng.choice(BASE_EXTRA), rng)]
        if fam == "captains" and rng.random() < 0.5: items = [rand_item(rng.choice(BASE_EXTRA), rng)]
        c = {"kind": "captains" if fam == "captains" else "sections", "S": rng.choice([3, 4, 5, 6, 6, 7, 8, 9, 10])}
        out.append({"id": f"{tag}_{fam}_{i:02d}", "family": fam, "items": items, "closing": c})
    return out


def agent_view(task):
    """what the wording writer sees for one task: neutral sentences in program order, then the closing sentence"""
    return {"id": task["id"], "rules_in_order": [neutral(it) for it in task["items"]], "table": neutral_closing(task["closing"])}


def sha(obj): return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()
