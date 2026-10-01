"""HERO-7 paraphrase augmentation: a larger LOCAL model (Qwen3-30B-A3B-Instruct-2507, MLX 4-bit) rewrites training sentences
(from the HERO-6 training set, never from any test set) in another style. Filtering (names/numbers kept, dedupe against
every test set) happens in gen_train7.py.
  python -m genome.hero7.para7 [n_named] [n_old] -> runs/hero7/para_raw.json"""
import json, random, sys, time
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
sys.path.insert(0, _REPO)
STYLES = ["a very terse note made of clipped fragments (drop articles and verbs where possible)",
          "a chatty, rambling message with filler words, as if typed quickly to an assistant",
          "a formal written instruction from an event office",
          "a polite question to the seating planner",
          "a short bulleted list, one rule per bullet",
          "unusual wording: avoid the most obvious verbs and phrases of the original, use idioms or roundabout phrasing",
          "lowercase text-message style with abbreviations"]
PROMPT = """Rewrite this seating instruction for a lunch in the following style: {style}.

Rules for the rewrite:
- Keep EVERY rule and its exact meaning. Do not add, drop, merge or weaken any rule.
- Keep every person and company name exactly as written (same spelling, same form).
- Keep every number (you may write it as a digit or a word).
- "in the same section"/"together" must stay a request to seat them together; "apart"/"not in the same section" must stay a request to keep them apart.

Instruction:
{text}

Reply with the rewritten instruction only."""


def main(n_named=1100, n_old=500, out=_REPO + "/runs/hero7/para_raw.json"):
    from mlx_lm import load, batch_generate
    from mlx_lm.sample_utils import make_sampler
    import mlx.core as mx
    rows = [json.loads(l) for l in open(_REPO + "/runs/hero6/data/train.jsonl")]
    data = []
    for r in rows:
        u = r["messages"][0]["content"]; t = u.split("## Policy\n\n", 1)[1].split("\n\n## Reply format", 1)[0]
        data.append((t, r["messages"][1]["content"]))
    rng = random.Random(7)
    named = [d for d in data if "avoid " in d[1] or "pair " in d[1]]; old = [d for d in data if d not in named]
    pick = rng.sample(named, n_named) + rng.sample(old, n_old)
    model, tok = load("mlx-community/Qwen3-30B-A3B-Instruct-2507-4bit")
    mx.random.seed(7)
    jobs = []
    for t, p in pick:
        st = rng.choice(STYLES)
        jobs.append(dict(src=t, prog=p, style=st,
                         prompt=tok.apply_chat_template([{"role": "user", "content": PROMPT.format(style=st, text=t)}], add_generation_prompt=True)))
    t0 = time.time(); res = []
    for s in range(0, len(jobs), 48):
        ch = jobs[s:s + 48]
        r = batch_generate(model, tok, [j["prompt"] for j in ch], max_tokens=160, sampler=make_sampler(temp=0.8, top_p=0.95), verbose=False)
        for j, txt in zip(ch, r.texts):
            res.append(dict(src=j["src"], prog=j["prog"], style=j["style"], para=txt.strip()))
        print(f"{len(res)}/{len(jobs)} {time.time() - t0:.0f}s", flush=True)
        json.dump(dict(model="mlx-community/Qwen3-30B-A3B-Instruct-2507-4bit", items=res), open(out, "w"), indent=0)


if __name__ == "__main__": main(*[int(x) for x in sys.argv[1:]])
