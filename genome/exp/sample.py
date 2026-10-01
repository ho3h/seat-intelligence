"""Sample k completions per task from a local MLX model (optionally with a LoRA adapter). GPU; run with the MLX venv.

  python -m genome.exp.sample --arm native --set data/tasksets/iid_test.json --n 8 --adapter adapters/native_v1 --out runs/exp/x.json

Writes {"meta", "tasks": [[family, index], ...], "samples": {pid: [text, ...]}}. Scoring is separate (genome.exp.score).
"""
import argparse, json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mlx-community/Qwen3-4B-Instruct-2507-4bit"); ap.add_argument("--adapter", default=None)
    ap.add_argument("--arm", choices=["native", "b1"], required=True); ap.add_argument("--set", required=True)
    ap.add_argument("--n", type=int, default=8); ap.add_argument("--temp", type=float, default=0.7); ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-tokens", type=int, default=1200); ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--primer", action="store_true", help="full primer prompt instead of the short (task-only) prompt")
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import mlx.core as mx
    from mlx_lm import load, batch_generate
    from mlx_lm.sample_utils import make_sampler
    from genome.contract import prompt, prompt_b1, prompt_short, prompt_short_b1
    from genome.taskgen import task
    mx.random.seed(a.seed)
    man = json.load(open(a.set)); tasks = [task(f, i) for f, i in man]
    model, tok = load(a.model, adapter_path=a.adapter) if a.adapter else load(a.model)
    mk = {("native", False): prompt_short, ("native", True): prompt, ("b1", False): prompt_short_b1, ("b1", True): prompt_b1}[(a.arm, a.primer)]
    def chat(text):
        m = [{"role": "user", "content": text}]
        try: return tok.apply_chat_template(m, add_generation_prompt=True, enable_thinking=False)
        except TypeError: return tok.apply_chat_template(m, add_generation_prompt=True)
    jobs = [(p.id, chat(mk(p))) for p in tasks for _ in range(a.n)]
    jobs.sort(key=lambda t: len(t[1]))
    sampler = make_sampler(temp=a.temp, top_p=a.top_p)
    samples = {p.id: [] for p in tasks}; t0 = time.time()
    for s in range(0, len(jobs), a.batch):
        chunk = jobs[s:s + a.batch]
        r = batch_generate(model, tok, [c[1] for c in chunk], max_tokens=a.max_tokens, sampler=sampler, verbose=False)
        for (pid, _), txt in zip(chunk, r.texts): samples[pid].append(txt)
        print(f"generated {min(s + a.batch, len(jobs))}/{len(jobs)}  {time.time() - t0:.0f}s", flush=True)
    meta = {k: v for k, v in vars(a).items()}; meta["seconds"] = time.time() - t0
    json.dump({"meta": meta, "tasks": man, "samples": samples}, open(a.out, "w"))


if __name__ == "__main__": main()
