"""Sample n stage programs per task from a local MLX model + LoRA adapter (GPU; run with the MLX venv). Prompt: lang.prompt_stage.

  python -m genome.exp15.sample --model mlx-community/Qwen3-1.7B-4bit --adapter adapters/exp15_1p7b \
      --set runs/exp15/sets/iid.json --n 4 --out runs/exp15/samples/1p7b_iid.json
"""
import argparse, json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--adapter", default=None); ap.add_argument("--set", required=True)
    ap.add_argument("--n", type=int, default=4); ap.add_argument("--temp", type=float, default=0.7); ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-tokens", type=int, default=160); ap.add_argument("--batch", type=int, default=64)
    ap.add_argument("--vocab", action="store_true", help="zero-shot control: document the vocabulary in the prompt")
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import mlx.core as mx
    from mlx_lm import load, batch_generate
    from mlx_lm.sample_utils import make_sampler
    from genome.exp15.lang import prompt_stage, prompt_stage_vocab
    mk = prompt_stage_vocab if a.vocab else prompt_stage
    from genome.exp15.data import load_task
    mx.random.seed(a.seed)
    specs = json.load(open(a.set)); tasks = [load_task(s) for s in specs]
    model, tok = load(a.model, adapter_path=a.adapter) if a.adapter else load(a.model)
    def chat(text):
        m = [{"role": "user", "content": text}]
        try: return tok.apply_chat_template(m, add_generation_prompt=True, enable_thinking=False)
        except TypeError: return tok.apply_chat_template(m, add_generation_prompt=True)
    jobs = [(p.id, chat(mk(p))) for p in tasks for _ in range(a.n)]
    sampler = make_sampler(temp=a.temp, top_p=a.top_p)
    samples = {p.id: [] for p in tasks}; t0 = time.time()
    for s in range(0, len(jobs), a.batch):
        chunk = jobs[s:s + a.batch]
        r = batch_generate(model, tok, [c[1] for c in chunk], max_tokens=a.max_tokens, sampler=sampler, verbose=False)
        for (pid, _), txt in zip(chunk, r.texts): samples[pid].append(txt)
        print(f"generated {min(s + a.batch, len(jobs))}/{len(jobs)}  {time.time() - t0:.0f}s", flush=True)
    meta = {k: v for k, v in vars(a).items()}; meta["seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"meta": meta, "specs": specs, "samples": samples}, open(a.out, "w"))


if __name__ == "__main__": main()
