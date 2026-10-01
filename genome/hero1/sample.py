"""Sample stage programs for seating policies from a local MLX model + LoRA adapter.
  python -m genome.hero1.sample --model mlx-community/Qwen3-1.7B-4bit --adapter adapters/hero1_1p7b --set data/hero/policies_test.json --n 5 --out runs/hero1/samples/test_t07.json
"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import argparse, json, os, sys, time
sys.path.insert(0, _REPO)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--adapter", default=None); ap.add_argument("--set", required=True)
    ap.add_argument("--n", type=int, default=5); ap.add_argument("--temp", type=float, default=0.7); ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-tokens", type=int, default=120); ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--vocab", action="store_true", help="zero-shot control: vocabulary in the prompt")
    ap.add_argument("--ids", default=None, help="comma-separated policy ids to keep")
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import mlx.core as mx
    from mlx_lm import load, batch_generate
    from mlx_lm.sample_utils import make_sampler
    from genome.hero1.gen_train import prompt, prompt_vocab
    mk = prompt_vocab if a.vocab else prompt
    mx.random.seed(a.seed)
    d = json.load(open(a.set)); pols = d["policies"] if isinstance(d, dict) else d
    if a.ids: keep = set(a.ids.split(",")); pols = [p for p in pols if p["id"] in keep]
    model, tok = load(a.model, adapter_path=a.adapter) if a.adapter else load(a.model)

    def chat(text):
        m = [{"role": "user", "content": mk(text)}]
        try: return tok.apply_chat_template(m, add_generation_prompt=True, enable_thinking=False)
        except TypeError: return tok.apply_chat_template(m, add_generation_prompt=True)
    jobs = [(p["id"], chat(p["text"])) for p in pols for _ in range(a.n)]
    sampler = make_sampler(temp=a.temp, top_p=a.top_p)
    samples = {p["id"]: [] for p in pols}; t0 = time.time()
    for s in range(0, len(jobs), a.batch):
        chunk = jobs[s:s + a.batch]
        r = batch_generate(model, tok, [c[1] for c in chunk], max_tokens=a.max_tokens, sampler=sampler, verbose=False)
        for (pid, _), txt in zip(chunk, r.texts): samples[pid].append(txt)
        print(f"generated {min(s + a.batch, len(jobs))}/{len(jobs)}  {time.time() - t0:.0f}s", flush=True)
    meta = {k: v for k, v in vars(a).items()}; meta["seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"meta": meta, "samples": samples}, open(a.out, "w"))


if __name__ == "__main__": main()
