"""Chatbot baseline: untuned local Qwen3-4B-Instruct-2507 (MLX, 4-bit) assigns the real 34 guests to sections directly.
20 policies x 20 samples at temperature 0.7 = 400 samples.  Selection of the 20 policies (fixed before running): the first 3 of each
voice (ids xxx01-xxx03) + ter11 + for11.   usage: python3 -m genome.hero1.baseline sample|score
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, os, re, sys, time, collections
sys.path.insert(0, _REPO)
from genome.hero1.lang import parse, to_text, violations, load_real, CATS, Policy

ROOT = _REPO
TEST = os.path.join(ROOT, "data/hero/policies_test.json")
# defaults = the specified baseline (untuned Qwen3-4B-Instruct-2507, direct answer). Extras via env: BASE_MODEL, BASE_OUT, BASE_N, BASE_COT=1
MODEL = os.environ.get("BASE_MODEL", "mlx-community/Qwen3-4B-Instruct-2507-4bit")
OUT = os.path.join(ROOT, os.environ.get("BASE_OUT", "runs/hero1/baseline_samples.json"))
COT = os.environ.get("BASE_COT") == "1"


def selected():
    pols = json.load(open(TEST))["policies"]
    ids = [p["id"] for p in pols if p["id"][3:] in ("01", "02", "03")] + ["ter11", "for11"]
    return [p for p in pols if p["id"] in ids]


def guest_table():
    guests, seats = load_real()
    return guests, [f"G{i + 1:02d}" for i in range(len(guests))]


def prompt(policy_text, cap_default=6):
    guests, ids = guest_table()
    rows = "\n".join(f"{gid} | {org or '-'} | {CATS[c]}" for gid, (org, c) in zip(ids, guests))
    return ("You are seating guests at a long banquet table. The table is split into SECTIONS: a section is a run of adjacent seats. "
            f"A section holds at most {cap_default} guests unless the host's rule below says otherwise.\n\n"
            f"Guests (id | company ('-' = none) | category):\n{rows}\n\n"
            f"Host's seating rule:\n{policy_text}\n\n"
            "Assign every guest to exactly one section. Sections are numbered 1, 2, 3, ... in the order they run along the table. "
            'Reply with JSON only, in the form {"sections": [["G01", "G05"], ["G02", ...], ...]} where the k-th list holds the ids of section k. '
            "Every guest must appear exactly once." + (" First think step by step: list the sections, check every rule of the host and that all 34 guests appear exactly once. "
             "Then give the final JSON as the last thing in your reply." if COT else ""))


def sample(n=int(os.environ.get('BASE_N', 20)), temp=0.7, seed=0):
    import mlx.core as mx
    from mlx_lm import load, batch_generate
    from mlx_lm.sample_utils import make_sampler
    mx.random.seed(seed)
    model, tok = load(MODEL)
    sampler = make_sampler(temp=temp, top_p=0.95)
    res = {}
    if os.path.exists(OUT): res = json.load(open(OUT))["samples"]
    t0 = time.time()
    for p in selected():
        if p["id"] in res: continue
        m = [{"role": "user", "content": prompt(p["text"])}]
        pr = tok.apply_chat_template(m, add_generation_prompt=True)
        r = batch_generate(model, tok, [pr] * n, max_tokens=(4000 if COT else 1100), sampler=sampler, verbose=False)
        res[p["id"]] = list(r.texts)
        json.dump({"model": MODEL, "temp": temp, "n": n, "samples": res}, open(OUT, "w"))
        print(p["id"], f"{time.time() - t0:.0f}s", flush=True)


def parse_answer(text, ids):
    """-> (sections list[list[id]] or None, note)"""
    t = re.sub(r"```(?:json)?", "", text)
    d = None
    starts = [m.start() for m in re.finditer(r"\{\s*\"sections\"", t)]
    for st in reversed(starts):
        try: d, _ = json.JSONDecoder().raw_decode(t[st:]); break
        except Exception: continue
    if d is None:
        m = re.search(r"\{.*\}", t, re.S)
        if not m: return None, "no json"
        try: d = json.loads(m.group(0))
        except Exception: return None, "bad json"
    secs = d.get("sections") if isinstance(d, dict) else None
    if not isinstance(secs, list) or not all(isinstance(s, list) for s in secs): return None, "bad shape"
    return [[str(x).strip() for x in s] for s in secs], ""


def score_sample(text, policy_text_gold):
    guests, ids = guest_table(); pol = parse(policy_text_gold)
    secs, note = parse_answer(text, ids)
    if secs is None: return dict(parsed=False, note=note)
    seen = collections.Counter(x for s in secs for x in s)
    known = set(ids)
    missing = [g for g in ids if g not in seen]; dup = [g for g, c in seen.items() if c > 1 and g in known]; unknown = [g for g in seen if g not in known]
    assign = {}
    for k, s in enumerate(secs):
        for x in s:
            if x in known and x not in assign: assign[x] = k
    placed = [g for g in ids if g in assign]
    sub = [guests[ids.index(g)] for g in placed]; a = [assign[g] for g in placed]
    v = violations(sub, pol, a) if placed else {"total": 0}
    part = frozenset(frozenset(s) for s in secs if s)
    v_pol = v["total"] - (v.get("cap", 0) if pol.cap == 6 else 0) if placed else 0     # excludes the default size-6 cap unless the policy sets a size
    return dict(parsed=True, violates_policy=v_pol > 0, missing=len(missing), dup=len(dup), unknown=len(unknown), bad_cover=bool(missing or dup or unknown),
                viol=v, violates=v["total"] > 0, partition=sorted(sorted(s) for s in part), exact=json.dumps(secs))


def score():
    data = json.load(open(OUT))["samples"]; pols = {p["id"]: p for p in selected()}
    rows = {}
    for pid, texts in data.items():
        rows[pid] = [score_sample(t, pols[pid]["gold"]) for t in texts]
    tot = sum(len(v) for v in rows.values())
    parsed = [r for v in rows.values() for r in v if r["parsed"]]
    summ = dict(samples=tot, unparsed=tot - len(parsed),
                violates=sum(r["violates"] for r in parsed), violates_policy=sum(r["violates_policy"] for r in parsed), bad_cover=sum(r["bad_cover"] for r in parsed),
                any_problem=sum((r["violates"] or r["bad_cover"]) for r in parsed) + (tot - len(parsed)),
                clean=sum((not r["violates"] and not r["bad_cover"]) for r in parsed))
    by_rule = collections.Counter()
    for r in parsed:
        for k in ("cap", "limit", "apart", "together", "order"):
            if r["viol"].get(k): by_rule[k] += 1
    summ["violating_samples_by_rule"] = dict(by_rule)
    per = {}
    for pid, v in rows.items():
        ps = [r for r in v if r["parsed"]]
        per[pid] = dict(n=len(v), parsed=len(ps), violates=sum(r["violates"] for r in ps), bad_cover=sum(r["bad_cover"] for r in ps),
                        clean=sum((not r["violates"] and not r["bad_cover"]) for r in ps),
                        distinct_partitions=len({json.dumps(r["partition"]) for r in ps}), distinct_answers=len({r["exact"] for r in ps}),
                        mean_viol=round(sum(r["viol"]["total"] for r in ps) / max(1, len(ps)), 2))
    summ["mean_distinct_partitions"] = round(sum(x["distinct_partitions"] for x in per.values()) / len(per), 2)
    summ["mean_distinct_answers"] = round(sum(x["distinct_answers"] for x in per.values()) / len(per), 2)
    out = dict(summary=summ, per_policy=per)
    json.dump(out, open(OUT.replace("_samples", "_scored"), "w"), indent=1)
    print(json.dumps(summ, indent=1))
    return out


if __name__ == "__main__":
    if sys.argv[1] == "sample": sample()
    else: score()
