"""Record the page sentences with the HERO-6 adapter: greedy program (timed, one warm-up excluded), and 20 samples at T=0.7
(determinism). Intended programs were written first: runs/hero6/page_intended.json.
  python -m genome.hero6.page6 [adapter] [out]"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, sys, time, collections
sys.path.insert(0, _REPO)
from genome.hero1.gen_train import prompt
from genome.hero6 import lang6 as L
from genome.hero6.judge6 import judge, judge_strict


def main(adapter="adapters/hero6_1p7b", out="runs/hero6/page_outputs.json"):
    import mlx.core as mx
    from mlx_lm import load, generate, batch_generate
    from mlx_lm.sample_utils import make_sampler
    mx.random.seed(6)
    model, tok = load("mlx-community/Qwen3-1.7B-4bit", adapter_path=adapter)
    chat = lambda t: tok.apply_chat_template([{"role": "user", "content": prompt(t)}], add_generation_prompt=True, enable_thinking=False)
    items = json.load(open(_REPO + "/runs/hero6/page_intended.json"))["items"]
    generate(model, tok, chat("Sections of 3."), max_tokens=40, sampler=make_sampler(temp=0.0))   # warm-up
    rows = []
    for it in items:
        p = chat(it["sentence"])
        t0 = time.time(); g = generate(model, tok, p, max_tokens=120, sampler=make_sampler(temp=0.0)); secs = time.time() - t0
        g = g.strip()
        try: canon = L.to_text(L.parse(g))
        except L.ParseError as e: canon = f"PARSE ERROR: {e}"
        j = judge(g, it["intended_program"])
        r = batch_generate(model, tok, [p] * 20, max_tokens=120, sampler=make_sampler(temp=0.7, top_p=0.95), verbose=False)
        cs = []
        for s in r.texts:
            try: cs.append(L.to_text(L.parse(s)))
            except L.ParseError: cs.append("UNPARSABLE: " + s.strip())
        cnt = collections.Counter(cs)
        rows.append(dict(id=it["id"], sentence=it["sentence"], greedy_program=g, canonical=canon, matches_intended=bool(j["passed"]),
                         matches_intended_strict=bool(judge_strict(g, it["intended_program"])), canonical_equals_intended=(canon == it["intended_canonical"]),
                         intended_program=it["intended_program"], distinct_programs_T07=len(cnt),
                         T07_samples_matching_intended=sum(judge(s, it["intended_program"])["passed"] for s in r.texts),
                         T07_program_counts=dict(cnt.most_common()), secs=round(secs, 3),
                         tokens_in=len(tok.encode(p)) if isinstance(p, str) else len(p), tokens_out=len(tok.encode(g))))
        print(it["id"], rows[-1]["matches_intended"], repr(g), rows[-1]["distinct_programs_T07"], rows[-1]["secs"], flush=True)
    json.dump(dict(model="mlx-community/Qwen3-1.7B-4bit", adapter=adapter, note="greedy timing = one request on a shared machine, warm-up excluded; "
                   "matches_intended = same seating as the intended program on the real 34 and the two synthetic lists (genome/hero6/judge6.py)",
                   outputs=rows), open(out, "w"), indent=1)


if __name__ == "__main__": main(*sys.argv[1:])
