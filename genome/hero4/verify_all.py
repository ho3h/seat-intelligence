"""Re-verify every word instance (5 base words incl. variants, 10 new words) at seeds 0,1,2 -> runs/hero4/word_verify.json"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, time
from genome.hero4 import wordtests, newwords
from genome.hero4.words import BUILD
from genome.hero4.author import INSTANCES
BASE = [("group", ["company"]), ("group", ["category"]), ("spread", []), ("order", ["rank"]), ("order", ["rankdesc"]),
        ("order", ["category", "government", "ai_lab", "chips"]), ("order", ["company", "Palantir", "OpenAI"]),
        ("sections", [6]), ("sections", [1]), ("sections", [10]), ("captains", [6]), ("captains", [1]), ("captains", [4]), ("captains", [7])]
rows = []; t0 = time.time()
for w, a in BASE:
    r = wordtests.run(w, a, BUILD[w](a), seeds=(0, 1, 2), workers=4)
    rows.append({"word": w, "args": a, "kind": "base", "seeds_pass": sum(x["status"] == "pass" for x in r), "cases": r[0].get("cases")})
for w, insts in INSTANCES.items():
    for a in insts:
        r = wordtests.run(w, list(a), newwords.BUILD_NEW[w](list(a)), seeds=(0, 1, 2), workers=4, tag="new")
        rows.append({"word": w, "args": list(a), "kind": "new", "seeds_pass": sum(x["status"] == "pass" for x in r), "cases": r[0].get("cases")})
tot = sum(x["seeds_pass"] for x in rows); n = 3 * len(rows)
json.dump({"instances": len(rows), "seed_runs": n, "seed_runs_pass": tot, "rows": rows, "secs": round(time.time() - t0)}, open(_REPO + "/runs/hero4/word_verify.json", "w"), indent=1)
print(len(rows), "instances,", tot, "/", n, "seed-runs pass")
