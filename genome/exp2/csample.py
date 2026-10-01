"""Constrained (or, with --off, unconstrained control) sampling through a hand-written batched decode loop. GPU; MLX venv.

  $MLXPY -m genome.exp2.csample --adapter adapters/native_v1 --set data/tasksets/iid_test.json --n 8 --out runs/exp2/C_native_v1_iid.json
  $MLXPY -m genome.exp2.csample ... --off --out runs/exp2/U_native_v1_iid.json      (same loop, no constraints)

Output format = genome.exp.sample (so genome.exp.score works unchanged) plus per-sample decode stats in "stats".

Sampling = mlx_lm make_sampler(temp, top_p) semantics applied AFTER masking illegal tokens (as a logits processor would):
nucleus on the untempered, renormalised legal distribution, then tempered categorical inside the nucleus. For speed, only the
top-K (default 256) tokens by logit are candidates; they are checked against NetFSM in descending order until the legal nucleus is
certain (legal mass >= top_p * (legal mass + all unchecked mass)). If no top-K token is legal, the whole vocabulary is scanned
in order (slow path, counted). RNG: numpy, seeded per batch from --seed (cannot reproduce MLX's RNG stream of the baseline).
"""
import argparse, json, os, sys, time
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from genome.exp2.netfsm import NetFSM, PRE, CODE, POST


def choose(state, ids, probs, strs, special, eos, top_p, temp, rng, constrained, stats, full_row=None):
    """ids/probs: candidates sorted by prob desc (untempered). Returns chosen token id."""
    leg_ids, leg_p = [], []
    legal_mass = 0.0; checked = 0.0; masked = 0.0
    for t, p in zip(ids, probs):
        t = int(t); p = float(p)
        ok = True
        if constrained:
            if t in eos: ok = state.allows_end()
            elif t in special: ok = state.mode == PRE
            else: ok = state.allows(strs[t])
        checked += p
        if ok:
            leg_ids.append(t); leg_p.append(p); legal_mass += p
            if legal_mass >= top_p * (legal_mass + max(0.0, 1.0 - checked)): break
        else: masked += p
    if not leg_ids and full_row is not None:          # slow path: scan the whole vocabulary by probability
        stats["slow"] += 1
        order = np.argsort(-full_row)
        for t in order[:40000]:
            t = int(t)
            if t in eos: ok = state.allows_end()
            elif t in special: ok = state.mode == PRE
            else: ok = state.allows(strs[t])
            if ok: leg_ids.append(t); leg_p.append(float(full_row[t])); break
    if not leg_ids:
        if full_row is None: return None
        stats["dead"] += 1; return next(iter(eos))
    stats["masked_mass"] += masked
    if masked > 0.5: stats["steps_masked_gt50"] += 1
    if masked > 0: stats["steps_masked"] += 1
    p = np.array(leg_p, dtype=np.float64)
    # nucleus over the renormalised legal distribution (HF rule: keep the token that crosses top_p)
    q = p / p.sum(); c = np.cumsum(q); k = int(np.searchsorted(c, top_p) + 1); k = min(k, len(q))
    w = q[:k] ** (1.0 / temp); w /= w.sum()
    return leg_ids[int(rng.choice(k, p=w))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="mlx-community/Qwen3-4B-Instruct-2507-4bit"); ap.add_argument("--adapter", default=None)
    ap.add_argument("--set", required=True); ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--temp", type=float, default=0.7); ap.add_argument("--top-p", type=float, default=0.95)
    ap.add_argument("--max-tokens", type=int, default=1200); ap.add_argument("--batch", type=int, default=48)
    ap.add_argument("--topk", type=int, default=256); ap.add_argument("--off", action="store_true", help="no constraints (control)")
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--seed", type=int, default=0); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    import mlx.core as mx
    from mlx_lm import load
    from mlx_lm.generate import _make_cache, _left_pad_prompts
    from genome.contract import prompt_short
    from genome.taskgen import task
    from genome.exp2.vocab import token_strings
    man = json.load(open(a.set))
    if a.limit: man = man[:a.limit]
    tasks = [task(f, i) for f, i in man]
    model, tok = load(a.model, adapter_path=a.adapter) if a.adapter else load(a.model)
    strs, special = token_strings(tok._tokenizer)
    eos = set(tok.eos_token_ids) | {tok.eos_token_id}
    special = special - eos

    def chat(text):
        m = [{"role": "user", "content": text}]
        try: return tok.apply_chat_template(m, add_generation_prompt=True, enable_thinking=False)
        except TypeError: return tok.apply_chat_template(m, add_generation_prompt=True)
    jobs = [(p.id, chat(prompt_short(p))) for p in tasks for _ in range(a.n)]
    jobs.sort(key=lambda t: len(t[1]))
    samples = {p.id: [] for p in tasks}; stats_all = {p.id: [] for p in tasks}
    t0 = time.time(); gen_tokens = 0; gen_time = 0.0
    for s in range(0, len(jobs), a.batch):
        chunk = jobs[s:s + a.batch]; B = len(chunk)
        rng = np.random.default_rng([a.seed, s])
        prompts = [c[1] for c in chunk]; L = max(len(p) for p in prompts)
        cache = _make_cache(model, [L - len(p) for p in prompts], None)
        x = _left_pad_prompts(prompts)
        for i in range(0, L - 1, 2048):
            model(x[:, i:min(i + 2048, L - 1)], cache=cache); mx.eval([c.state for c in cache])
        logits = model(x[:, L - 1:], cache=cache)[:, -1, :]
        states = [NetFSM() for _ in range(B)]; outs = [[] for _ in range(B)]
        st = [{"slow": 0, "dead": 0, "masked_mass": 0.0, "steps_masked": 0, "steps_masked_gt50": 0} for _ in range(B)]
        active = list(range(B)); tg = time.time()
        for step in range(a.max_tokens):
            logits = logits.astype(mx.float32)
            logp = logits - mx.logsumexp(logits, axis=-1, keepdims=True)
            K = min(a.topk, logp.shape[-1])
            idx = mx.argpartition(-logp, K - 1, axis=-1)[:, :K]
            val = mx.exp(mx.take_along_axis(logp, idx, axis=-1))
            mx.eval(idx, val)
            idx_n = np.array(idx); val_n = np.array(val)
            nxt, keep = [], []
            for r, b in enumerate(active):
                o = np.argsort(-val_n[r]); ids = idx_n[r][o]; ps = val_n[r][o]
                t = choose(states[b], ids, ps, strs, special, eos, a.top_p, a.temp, rng, not a.off, st[b])
                if t is None:  # no legal token among the top-K: slow path over the full row
                    full = np.array(mx.exp(logp[r]))
                    t = choose(states[b], np.array([], dtype=np.int64), np.array([]), strs, special, eos, a.top_p, a.temp, rng, True, st[b], full)
                if t in eos: continue
                outs[b].append(t)
                if t not in special: states[b].feed(strs[t])  # in --off mode the state is tracked for stats only
                nxt.append(t); keep.append(r)
            gen_tokens += len(active)
            if not keep: break
            if len(keep) < len(active):
                ki = mx.array(keep)
                for c in cache: c.filter(ki)
                active = [active[r] for r in keep]
            logits = model(mx.array(nxt)[:, None], cache=cache)[:, -1, :]
        gen_time += time.time() - tg
        for b, (pid, _) in enumerate(chunk):
            samples[pid].append(tok.decode(outs[b]))
            s_ = st[b]; s_["tokens"] = len(outs[b]); s_["hit_max"] = len(outs[b]) >= a.max_tokens
            s_["final_mode"] = states[b].mode; s_["final_clean"] = states[b].clone().end()
            stats_all[pid].append(s_)
        print(f"generated {min(s + a.batch, len(jobs))}/{len(jobs)}  {time.time() - t0:.0f}s  gen_tok/s {gen_tokens / max(gen_time, 1e-9):.0f}", flush=True)
        mx.clear_cache()
    meta = dict(vars(a)); meta.update(arm="native", seconds=time.time() - t0, gen_tokens=gen_tokens, gen_seconds=gen_time,
                                       tok_per_s=gen_tokens / gen_time, constrained=not a.off, primer=False)
    json.dump({"meta": meta, "tasks": man, "samples": samples, "stats": stats_all}, open(a.out, "w"))


if __name__ == "__main__": main()
