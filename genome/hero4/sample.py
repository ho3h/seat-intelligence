"""Sample n stage programs per task from a local MLX model (+ optional LoRA adapter) under one PROMPT ARM.
  arms: without (base block only) | own (base + the family's own new entry) | all (base + all ten new entries)
  python -m genome.hero4.sample --model mlx-community/Qwen3-1.7B-4bit --adapter adapters/hero4_main --set runs/hero4/sets/FROZEN/test_final.json --arm own --n 4 --out runs/hero4/samples/main_own.json
"""
import argparse, json, os, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from genome.hero4 import lang
from genome.hero4.refs import BASE_WORDS, NEW_WORDS


def available_for(task, arm, idx=0):
    if arm == "without": return list(lang.BASE_ORDER)
    if arm == "own": return list(lang.BASE_ORDER) + ([task["family"]] if task["family"] in NEW_WORDS else [])
    if arm == "all": return list(lang.BASE_ORDER) + list(lang.NEW_ORDER)
    if arm == "one": return list(lang.BASE_ORDER) + [lang.NEW_ORDER[idx % 10]]      # base tasks with ONE (rotating) new entry added
    raise KeyError(arm)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--adapter", default=None); ap.add_argument("--set", required=True)
    ap.add_argument("--arm", required=True); ap.add_argument("--n", type=int, default=4); ap.add_argument("--temp", type=float, default=0.7)
    ap.add_argument("--top-p", type=float, default=0.95); ap.add_argument("--max-tokens", type=int, default=120); ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", required=True); ap.add_argument("--only", default=None)
    a = ap.parse_args()
    import mlx.core as mx
    from mlx_lm import load, batch_generate
    from mlx_lm.sample_utils import make_sampler
    mx.random.seed(a.seed)
    tasks = json.load(open(a.set))
    if a.only: tasks = [t for t in tasks if t["family"] in a.only.split(",")]
    model, tok = load(a.model, adapter_path=a.adapter) if a.adapter else load(a.model)
    def chat(text):
        m = [{"role": "user", "content": text}]
        try: return tok.apply_chat_template(m, add_generation_prompt=True, enable_thinking=False)
        except TypeError: return tok.apply_chat_template(m, add_generation_prompt=True)
    jobs = []
    for i, t in enumerate(tasks):
        p = lang.prompt(t["text"], available_for(t, a.arm, i))
        for _ in range(a.n): jobs.append((t["id"], chat(p)))
    sampler = make_sampler(temp=a.temp, top_p=a.top_p)
    samples = {t["id"]: [] for t in tasks}; t0 = time.time()
    for s in range(0, len(jobs), a.batch):
        chunk = jobs[s:s + a.batch]
        r = batch_generate(model, tok, [c[1] for c in chunk], max_tokens=a.max_tokens, sampler=sampler, verbose=False)
        for (pid, _), txt in zip(chunk, r.texts): samples[pid].append(txt)
        print(f"generated {min(s + a.batch, len(jobs))}/{len(jobs)}  {time.time() - t0:.0f}s", flush=True)
    meta = {k: v for k, v in vars(a).items()}; meta["seconds"] = round(time.time() - t0, 1)
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump({"meta": meta, "tasks": tasks, "samples": samples}, open(a.out, "w"))


if __name__ == "__main__": main()
