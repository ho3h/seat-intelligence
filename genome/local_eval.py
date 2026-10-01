"""Evaluate a local MLX model as the author. Runs in a Python with mlx_lm installed.
  python -m genome.local_eval --model mlx-community/Qwen3-4B-Instruct-2507-4bit --arm native --split holdout --n 2
Reports pass@1 (mean over samples) and pass@n, overall and per family, plus how many samples fail static checks."""
import argparse, collections, json, os, sys, time
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--arm", choices=["native", "b1"], default="native")
    ap.add_argument("--split", default="holdout"); ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--max-tokens", type=int, default=900); ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--temp", type=float, default=0.7); ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--adapter", default=None); ap.add_argument("--short-prompt", action="store_true")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    from mlx_lm import load, batch_generate
    from mlx_lm.sample_utils import make_sampler
    from genome.contract import prompt, prompt_b1, prompt_short, prompt_short_b1
    from genome.verify import verify, verify_b1
    from genome.g0 import extract_net as _strict
    import re
    def extract_net(t, arm=a.arm):
        b = _strict(t)
        if b: return b
        m = re.search(r'```[a-zA-Z]*\n(.*)$', t, re.S)          # unclosed fence
        if m: t = m.group(1)
        key = r'^\s*(@\w|def\s)' 
        lines = t.split('\n'); st = next((i for i, l in enumerate(lines) if re.match(key, l)), None)
        if st is None: return None
        body = '\n'.join(lines[st:]).split('```')[0].strip()
        return body + '\n' if body else None
    from genome import taskset
    from genome.corpus import load_all
    tasks = list(load_all().values()) if a.split == "corpus" else taskset.load(a.split)
    if a.limit: tasks = tasks[:a.limit]
    model, tok = load(a.model, adapter_path=a.adapter) if a.adapter else load(a.model)
    def chat(text):
        m = [{"role": "user", "content": text}]
        try: return tok.apply_chat_template(m, add_generation_prompt=True, enable_thinking=False)
        except TypeError: return tok.apply_chat_template(m, add_generation_prompt=True)
    mk = (prompt_short if a.short_prompt else prompt) if a.arm == "native" else (prompt_short_b1 if a.short_prompt else prompt_b1)
    jobs = [(i, j, chat(mk(p))) for i, p in enumerate(tasks) for j in range(a.n)]
    jobs.sort(key=lambda t: len(t[2]))
    sampler = make_sampler(temp=a.temp, top_p=0.95)
    outs = {}
    t0 = time.time()
    for s in range(0, len(jobs), a.batch):
        chunk = jobs[s:s + a.batch]
        r = batch_generate(model, tok, [c[2] for c in chunk], max_tokens=a.max_tokens, sampler=sampler, verbose=False)
        for (i, j, _), txt in zip(chunk, r.texts): outs[(i, j)] = txt
        print(f"generated {len(outs)}/{len(jobs)}  {time.time() - t0:.0f}s", flush=True)
    ver = verify if a.arm == "native" else verify_b1
    def score(key):
        i, j = key; p = tasks[i]; net = extract_net(outs[key])
        if not net: return key, "noblock"
        r = ver(p, net, seed=0, timeout=4.0, workers=4)
        if r["status"] == "pass": return key, "pass"
        return key, ("static" if r["status"] == "reject" else "fail")
    with ThreadPoolExecutor(4) as ex: res = dict(ex.map(score, list(outs)))
    fam = collections.defaultdict(lambda: [0, 0, 0]); tot = collections.Counter(res.values())
    for (i, j), v in res.items():
        f = tasks[i].id.split("_")[1] if tasks[i].id.startswith("gen_") else tasks[i].tier
        fam[f][0] += v == "pass"; fam[f][1] += 1
    solved = {i for (i, j), v in res.items() if v == "pass"}
    summary = {"model": a.model, "adapter": a.adapter, "arm": a.arm, "split": a.split, "n": a.n, "tasks": len(tasks), "samples": len(res),
               "pass@1": tot["pass"] / len(res), f"pass@{a.n}": len(solved) / len(tasks), "outcomes": dict(tot),
               "per_family_pass1": {k: v[0] / v[1] for k, v in fam.items()}, "seconds": time.time() - t0}
    json.dump({"summary": summary, "raw": {f"{i}_{j}": outs[(i, j)] for (i, j) in outs}}, open(a.out, "w"))
    print(json.dumps(summary, indent=1))


if __name__ == "__main__": main()
