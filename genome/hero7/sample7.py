"""HERO-7 sampler: same prompt as HERO-1/HERO-6 (genome/hero1/gen_train.prompt). Modes:
  plain  unconstrained (exactly genome/hero1/sample.py)
  cons   grammar + guest-name constrained decoding (genome/hero7/constrain7.py); alias names mapped to full guest keys
The guest list of a request = the 34-guest chart + the set's `extra_guests` (test sets 6 and 7 list the invented guests their
authors added); sets 1 and 2 have none.
  python -m genome.hero7.sample7 --model M --adapter A --set S --n 5 --temp 0.7 --mode cons --out X.json
"""
import argparse, json, os, sys, time
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
sys.path.insert(0, _REPO)


def request_guests(set_path):
    from genome.hero6 import lang6 as L
    d = json.load(open(set_path))
    real, _ = L.load_real()
    ex = d.get("extra_guests", []) if isinstance(d, dict) else []
    return real + [(g["org"], L.CID[g["category"]], g["name"]) for g in ex]


def run(model, tok, prompts_text, guests, n, temp, top_p, mode, seed=0, max_tokens=120, batch=64):
    import mlx.core as mx
    import importlib
    G = importlib.import_module("mlx_lm.generate")
    from mlx_lm.sample_utils import make_sampler
    from genome.hero1.gen_train import prompt
    from genome.hero7 import constrain7 as C
    mx.random.seed(seed)
    def chat(text):
        return tok.apply_chat_template([{"role": "user", "content": prompt(text)}], add_generation_prompt=True, enable_thinking=False)
    jobs = [(i, chat(t)) for i, t in enumerate(prompts_text) for _ in range(n)]
    names, alias = C.name_table(guests)
    gram = C.Grammar(names); pcs = C.pieces(tok) if mode == "cons" else None
    eos = set(tok.eos_token_ids)
    sampler = make_sampler(temp=temp, top_p=top_p)
    out = [[] for _ in prompts_text]; raw = [[] for _ in prompts_text]; scans = 0
    for s in range(0, len(jobs), batch):
        chunk = jobs[s:s + batch]
        gen = G.BatchGenerator(model, stop_tokens=[[t] for t in tok.eos_token_ids], sampler=sampler)
        procs = [C.Processor(gram, pcs, eos) for _ in chunk] if mode == "cons" else None
        uids = gen.insert([c[1] for c in chunk], [max_tokens] * len(chunk), logits_processors=[[p] for p in procs] if procs else None)
        res = {u: [] for u in uids}
        while rs := gen.next_generated():
            for r in rs:
                if r.finish_reason != "stop": res[r.uid].append(r.token)
        gen.close()
        for (i, _), u in zip(chunk, uids):
            t = tok.decode(res[u]).strip()
            raw[i].append(t); out[i].append(C.map_aliases(t, alias) if mode == "cons" else t)
        if procs: scans += sum(p.full_scans for p in procs)
    return out, raw, scans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--adapter", default=None); ap.add_argument("--set", required=True)
    ap.add_argument("--n", type=int, default=5); ap.add_argument("--temp", type=float, default=0.7); ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--mode", default="plain", choices=["plain", "cons"]); ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--batch", type=int, default=64); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    from mlx_lm import load
    model, tok = load(a.model, adapter_path=a.adapter) if a.adapter else load(a.model)
    d = json.load(open(a.set)); pols = d["policies"] if isinstance(d, dict) else d
    t0 = time.time()
    out, raw, scans = run(model, tok, [p["text"] for p in pols], request_guests(a.set), a.n, a.temp, a.top_p, a.mode, a.seed, batch=a.batch)
    meta = dict(vars(a)); meta["seconds"] = round(time.time() - t0, 1); meta["full_vocab_scans"] = scans
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(dict(meta=meta, samples={p["id"]: o for p, o in zip(pols, out)}, raw={p["id"]: r for p, r in zip(pols, raw)}), open(a.out, "w"))
    print("done", a.out, meta["seconds"], "s", "scans", scans, flush=True)


if __name__ == "__main__": main()
