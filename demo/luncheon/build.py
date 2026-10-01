"""Builds demo/luncheon/index.html from template.html + seating.js + app.js + the real chart and recorded showcase."""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json
D = _REPO
seats = json.load(open(f"{D}/data/hero/luncheon.json"))["seats"]
show = json.load(open(f"{D}/runs/hero1/showcase.json"))["showcase"]
data = {"guests": [{"name": s["name"], "org": s["org"], "category": s["category"]} for s in seats],
        "shows": [{"id": s["id"], "sentence": s["policy"], "emitted": s["emitted_program"], "gold": s["gold_program"],
                   "tin": s["authoring"]["tokens_in"], "tout": s["authoring"]["tokens_out"], "secs": s["authoring"]["secs"]} for s in show]}
import re
from collections import Counter
raw = json.load(open(f"{D}/runs/hero1/baseline_samples.json"))["samples"]["ter02"]
scored = json.load(open(f"{D}/runs/hero1/baseline_scored.json"))["per_policy"]["ter02"]
gov = [s["category"] == "government" for s in seats]
answers = []
for r in raw:
    secs = json.loads(re.search(r"\{.*\}", r, re.S).group(0))["sections"]
    ids = [[int(g[1:]) - 1 for g in sec if re.fullmatch(r"G\d\d", g) and 1 <= int(g[1:]) <= 34] for sec in secs]
    c = Counter(i for s in ids for i in s)
    answers.append({"secs": ids, "dup": [i for i, n in c.items() if n > 1], "miss": [i for i in range(34) if i not in c],
                    "govOver": sum(max(0, sum(gov[i] for i in s) - 1) for s in ids), "capOver": sum(max(0, len(s) - 6) for s in ids)})
data["chat"] = {"sentence": "No two government officials in one section.", "program": "limit government 1",
                "model": "Qwen3-4B-Instruct (4-bit), untuned, temperature 0.7", "n": len(answers),
                "broke": sum(a["govOver"] + a["capOver"] > 0 for a in answers), "dup": sum(bool(a["dup"]) for a in answers),
                "miss": sum(bool(a["miss"]) for a in answers), "distinct": scored["distinct_answers"],
                "show": answers[3], "showGovMax": max(sum(gov[i] for i in s) for s in answers[3]["secs"]), "answers": [a["secs"] for a in answers], "govMin": min(a["govOver"] for a in answers), "govMax": max(a["govOver"] for a in answers)}
t = open(f"{D}/demo/luncheon/template.html").read()
t = t.replace("/*SEATING*/", open(f"{D}/demo/luncheon/seating.js").read())
t = t.replace("/*DATA*/", json.dumps(data, ensure_ascii=False))
t = t.replace("/*APP*/", open(f"{D}/demo/luncheon/app.js").read())
open(f"{D}/demo/luncheon/index.html", "w").write(t)
print(len(t), "bytes")

# artifact variant: the publish skeleton supplies doctype/html/head/body
import re as _re
a = open(f"{D}/demo/luncheon/index.html").read()
a = a.replace('<!doctype html>\n<html lang="en">\n<head>\n', '')
a = _re.sub(r'<meta charset="utf-8">\n<meta name="viewport"[^>]*>\n', '', a)
a = a.replace('<title>Who sits next to whom? The White House AI lunch</title>', '<title>Who Sits Next to Whom?</title>')
a = a.replace('</head>\n<body>\n', '').replace('</body>\n</html>\n', '')
open(f"{D}/demo/luncheon/artifact.html", "w").write(a)
