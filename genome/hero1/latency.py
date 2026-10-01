"""Authoring cost, single request: tuned 1.7B (policy -> program) vs untuned 4B chatbot (policy + 34 guests -> sections) on the 5 showcase policies.
   python3 -m genome.hero1.latency   -> runs/hero1/latency.json   (machine shared; times are indicative)"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, sys, time, statistics as st
sys.path.insert(0, _REPO)
from genome.hero1.showcase import SHOW
from genome.hero1.gen_train import prompt
from genome.hero1.baseline import prompt as bprompt, MODEL as BMODEL
from mlx_lm import load, stream_generate
from mlx_lm.sample_utils import make_sampler


def run(model, tok, text, max_tokens, sampler, think=False):
    m = [{"role": "user", "content": text}]
    try: p = tok.apply_chat_template(m, add_generation_prompt=True, enable_thinking=False)
    except TypeError: p = tok.apply_chat_template(m, add_generation_prompt=True)
    t0 = time.time(); last = None
    for r in stream_generate(model, tok, p, max_tokens=max_tokens, sampler=sampler): last = r
    return dict(tokens_in=last.prompt_tokens, tokens_out=last.generation_tokens, secs=round(time.time() - t0, 3))


out = {}
sam = make_sampler(temp=0.0)
m1, t1 = load("mlx-community/Qwen3-1.7B-4bit", adapter_path=_REPO + "/adapters/hero1_1p7b")
run(m1, t1, prompt("warm up"), 8, sam)
out["pipeline_1p7b_tuned"] = {sid: run(m1, t1, prompt(text), 120, sam) for sid, text, _ in SHOW}
del m1
m2, t2 = load(BMODEL)
run(m2, t2, bprompt("warm up"), 8, sam)
out["chatbot_4b_direct"] = {sid: run(m2, t2, bprompt(text), 1100, sam) for sid, text, _ in SHOW}
for k, v in out.items():
    out[k]["mean"] = {f: round(st.mean(x[f] for x in v.values() if isinstance(x, dict) and f in x), 2) for f in ("tokens_in", "tokens_out", "secs")}
json.dump(out, open(_REPO + "/runs/hero1/latency.json", "w"), indent=1)
print(json.dumps({k: v["mean"] for k, v in out.items()}, indent=1))
