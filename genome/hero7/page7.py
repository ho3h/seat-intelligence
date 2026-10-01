"""Re-record the HERO-6 page sentences (runs/hero6/page_intended.json, intended programs written in HERO-6) with a HERO-7
configuration: greedy program (timed, one warm-up excluded), 20 samples at T=0.7, and (if vote) the 5-sample vote.
Fields as runs/hero6/page_outputs.json plus `config`.
  python -m genome.hero7.page7 <model> <adapter> <mode plain|cons> <vote 0|1> [out] [items json]"""
import json, sys, time, collections
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
sys.path.insert(0, _REPO)
from genome.hero6 import lang6 as L
from genome.hero6.judge6 import judge, judge_strict
from genome.hero7.sample7 import run
from genome.hero7.score7 import vote


def main(model_id, adapter, mode="cons", use_vote="0", out=_REPO + "/runs/hero7/page_outputs.json",
         items_path=_REPO + "/runs/hero6/page_intended.json"):
    from mlx_lm import load
    model, tok = load(model_id, adapter_path=adapter)
    G = L.load_real()[0]
    items = json.load(open(items_path))["items"]
    run(model, tok, ["Sections of 3."], G, 1, 0.0, 1.0, mode)          # warm-up
    from genome.hero1.gen_train import prompt
    rows = []
    for it in items:
        t0 = time.time(); o, r, _ = run(model, tok, [it["sentence"]], G, 1, 0.0, 1.0, mode); secs = time.time() - t0
        g = o[0][0]
        try: canon = L.to_text(L.parse(g))
        except L.ParseError as e: canon = f"PARSE ERROR: {e}"
        s20, _, _ = run(model, tok, [it["sentence"]], G, 20, 0.7, 0.95, mode, seed=6)
        cs = []
        for s in s20[0]:
            try: cs.append(L.to_text(L.parse(s)))
            except L.ParseError: cs.append("UNPARSABLE: " + s.strip())
        cnt = collections.Counter(cs)
        row = dict(id=it["id"], sentence=it["sentence"], greedy_program=g, canonical=canon, matches_intended=bool(judge(g, it["intended_program"])["passed"]),
                   matches_intended_strict=bool(judge_strict(g, it["intended_program"])), canonical_equals_intended=(canon == it["intended_canonical"]),
                   intended_program=it["intended_program"], distinct_programs_T07=len(cnt),
                   T07_samples_matching_intended=sum(judge(s, it["intended_program"])["passed"] for s in s20[0]),
                   T07_program_counts=dict(cnt.most_common()), secs=round(secs, 3),
                   tokens_in=len(tok.apply_chat_template([{"role": "user", "content": prompt(it["sentence"])}], add_generation_prompt=True, enable_thinking=False)),
                   tokens_out=len(tok.encode(g)))
        if use_vote == "1":
            t0 = time.time(); v5, _, _ = run(model, tok, [it["sentence"]], G, 5, 0.7, 0.95, mode, seed=7); vt, vs = vote(v5[0], G)
            row.update(vote_program=vt, vote_size=vs, vote_matches_intended=bool(judge(vt, it["intended_program"])["passed"]), vote_secs=round(time.time() - t0, 3))
        rows.append(row)
        print(it["id"], row["matches_intended"], repr(g), row["distinct_programs_T07"], row["secs"], flush=True)
    cfg = dict(model=model_id, adapter=adapter, decoding=mode, vote=use_vote == "1")
    json.dump(dict(model=model_id, adapter=adapter, config=cfg, note="greedy timing = one request on a shared machine, warm-up excluded; "
                   "matches_intended = same seating as the intended program on the real 34 and the two synthetic lists (genome/hero6/judge6.py); "
                   "guest list for the decoder = the 34-guest chart", outputs=rows), open(out, "w"), indent=1)


if __name__ == "__main__": main(*sys.argv[1:])
