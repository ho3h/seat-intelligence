"""Author channel over the Anthropic Messages API (stdlib only). Frozen models, no tools, the executor as verifier.

Per (arm, program, seed): up to MAX_ATTEMPTS submissions with feedback until a pass, then IMPROVE_ROUNDS rounds asking
for fewer interactions / shallower depth while staying correct; the best passing submission is kept (selection).
Every call is logged with token counts; a hard token cap per run stops spending.

  ANTHROPIC_API_KEY=... python -m genome.author_api run --arm native --seed 0 --ids all --model claude-opus-5-5
"""
from __future__ import annotations
import argparse, json, os, re, sys, threading, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from .corpus import load_all
from .contract import prompt, prompt_b1
from .verify import verify, verify_b1, feedback_text

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_ATTEMPTS, IMPROVE_ROUNDS, MAX_FREE_REJECTS = 5, 2, 4
API = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/") + "/v1/messages"


class Budget:
    def __init__(self, cap_tokens, cap_usd=None):
        self.cap, self.used, self.usd, self.cap_usd, self.lock = cap_tokens, 0, 0.0, cap_usd, threading.Lock()
    def add(self, n, usd=0.0):
        with self.lock: self.used += n; self.usd += usd
    def exhausted(self): return self.used >= self.cap or (self.cap_usd is not None and self.usd >= self.cap_usd)


def load_env():
    """Read KEY=VALUE lines from Genome/.env (gitignored) without printing them."""
    p = os.path.join(ROOT, ".env")
    if os.path.exists(p):
        for line in open(p):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


OR_API = "https://openrouter.ai/api/v1/chat/completions"


def call_openrouter(model, messages, key, max_tokens=32000, reasoning="medium", temperature=1.0, retries=6):
    """OpenAI-compatible chat via OpenRouter. Returns {"text", "tokens", "usd"}; reasoning tokens are billed as output."""
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "usage": {"include": True}}
    if reasoning: body["reasoning"] = {"effort": reasoning}
    else: body["temperature"] = temperature
    req = urllib.request.Request(OR_API, data=json.dumps(body).encode(), method="POST", headers={
        "content-type": "application/json", "authorization": f"Bearer {key}",
        "x-title": "Genome"})
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=900) as r: d = json.load(r)
            if "error" in d: raise urllib.error.HTTPError(OR_API, d["error"].get("code", 500), str(d["error"])[:200], {}, None)
            u = d.get("usage", {})
            return {"text": d["choices"][0]["message"].get("content") or "",
                    "tokens": u.get("prompt_tokens", 0) + u.get("completion_tokens", 0), "usd": float(u.get("cost", 0) or 0)}
        except urllib.error.HTTPError as e:
            if e.code in (408, 429, 500, 502, 503, 529): time.sleep(min(60, 2 ** i * 3)); continue
            raise RuntimeError(f"OpenRouter {e.code}: {getattr(e, 'msg', '')[:300]}")
        except (urllib.error.URLError, TimeoutError, KeyError): time.sleep(min(60, 2 ** i * 3))
    raise RuntimeError("OpenRouter unavailable after retries")


def call(model, messages, key, max_tokens=12000, thinking=0, temperature=1.0, retries=6):
    body = {"model": model, "max_tokens": max_tokens, "messages": messages, "temperature": temperature}
    if thinking: body["thinking"] = {"type": "enabled", "budget_tokens": thinking}; body.pop("temperature")
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method="POST", headers={
        "content-type": "application/json", "x-api-key": key, "anthropic-version": "2023-06-01"})
    for i in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=600) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 529): time.sleep(min(60, 2 ** i * 3)); continue
            raise RuntimeError(f"API {e.code}: {e.read().decode()[:300]}")
        except (urllib.error.URLError, TimeoutError): time.sleep(min(60, 2 ** i * 3))
    raise RuntimeError("API unavailable after retries")


def extract(text):
    blocks = re.findall(r"```[a-zA-Z]*\n(.*?)```", text, re.S)
    return blocks[-1].strip() + "\n" if blocks else None


def score(res):
    """Lower is better: (median big interactions, median big depth)."""
    m = res["metrics"]; return (m.get("itrs_median_big") or 1 << 60, m.get("depth_median_big") or 1 << 60)


MAX_OUT = 32000


def chat(provider, model, messages, key, thinking=0, reasoning="medium"):
    """-> {"text","tokens","usd"} for either provider."""
    if provider == "openrouter": return call_openrouter(model, messages, key, max_tokens=MAX_OUT, reasoning=reasoning)
    r = call(model, messages, key, thinking=thinking, max_tokens=12000 + thinking)
    u = r.get("usage", {})
    return {"text": "".join(b.get("text", "") for b in r["content"] if b["type"] == "text"),
            "tokens": u.get("input_tokens", 0) + u.get("output_tokens", 0), "usd": 0.0}


def get_program(pid):
    if pid.startswith("gen_"):
        from .taskgen import task
        fam, idx = pid[4:].rsplit("_", 1)
        return task(fam, int(idx))
    return load_all()[pid]


def run_program(arm, pid, seed, model, key, budget, outdir, thinking=0, log=print, provider="anthropic", reasoning="medium", improve=None):
    p = get_program(pid)
    ver = verify if arm == "native" else verify_b1
    ext = "hvm" if arm == "native" else "bend"
    d = os.path.join(outdir, arm, f"seed{seed}", pid); os.makedirs(d, exist_ok=True)
    messages = [{"role": "user", "content": (prompt if arm == "native" else prompt_b1)(p)}]
    state = {"pid": pid, "arm": arm, "seed": seed, "attempts": [], "accepted": False, "tokens": 0, "best": None}
    best_res, best_net = None, None
    def submit(k, kind):
        if budget.exhausted(): raise RuntimeError("token budget exhausted")
        r = chat(provider, model, messages, key, thinking, reasoning)
        budget.add(r["tokens"], r["usd"]); state["tokens"] += r["tokens"]; state["usd"] = state.get("usd", 0.0) + r["usd"]
        text = r["text"]
        if not text.strip(): text = "(your previous reply was empty: it ran out of output budget while thinking; think less and answer with the code block)"
        messages.append({"role": "assistant", "content": text})
        net = extract(text)
        open(os.path.join(d, f"{kind}_{k}.{ext}"), "w").write(net or "")
        res = ver(p, net, seed=0) if net else {"status": "reject", "reason": "no fenced code block in reply"}
        state["attempts"].append({"kind": kind, "status": res["status"], "metrics": res.get("metrics")})
        return net, res
    try:
        k, free = 0, 0
        while k < MAX_ATTEMPTS:
            net, res = submit(k + 1 + free, "attempt")
            if res["status"] == "pass": best_res, best_net = res, net; state["accepted"] = True; break
            # static / compile rejections are free (capped): they never reached the executor, same rule in both arms
            if res["status"] == "reject" and free < MAX_FREE_REJECTS: free += 1
            else: k += 1
            messages.append({"role": "user", "content": feedback_text(p, res) + "\n\nFix it and reply with the complete corrected code in one fenced block."})
        state["free_rejects"] = free
        if state["accepted"]:
            for k in range(1, (IMPROVE_ROUNDS if improve is None else improve) + 1):
                m = best_res["metrics"]
                messages.append({"role": "user", "content": (
                    f"{feedback_text(p, best_res)}\n\nImprove it: same task, fewer interactions and shallower dependent chains at the largest sizes "
                    f"(currently median {m['itrs_median_big']} interactions, depth {m.get('depth_median_big')}). It must stay correct. "
                    "Reply with the complete code in one fenced block.")})
                net, res = submit(k, "improve")
                if res["status"] == "pass" and score(res) < score(best_res): best_res, best_net = res, net
        if best_net:
            open(os.path.join(d, f"best.{ext}"), "w").write(best_net)
            state["best"] = best_res["metrics"]
            state["audit"] = [ver(p, best_net, seed=s)["status"] for s in (1, 2)]
    except RuntimeError as e:
        state["error"] = str(e)
    json.dump(state, open(os.path.join(d, "state.json"), "w"), indent=1)
    log(f"{arm} seed{seed} {pid}: {'PASS' if state['accepted'] else 'FAIL'} attempts={len(state['attempts'])} tokens={state['tokens']} usd={state.get('usd', 0):.4f}")
    return state


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["run"]); ap.add_argument("--arm", choices=["native", "b1"], required=True)
    ap.add_argument("--seed", type=int, default=0); ap.add_argument("--ids", default="all")
    ap.add_argument("--provider", choices=["anthropic", "openrouter"], default="anthropic")
    ap.add_argument("--model", default="claude-opus-5-5"); ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--usd-cap", type=float, default=None); ap.add_argument("--reasoning", default="medium")
    ap.add_argument("--max-out", type=int, default=32000); ap.add_argument("--improve", type=int, default=None)
    ap.add_argument("--token-cap", type=int, default=20_000_000); ap.add_argument("--thinking", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(ROOT, "runs", "g1"))
    a = ap.parse_args(argv)
    global MAX_OUT
    MAX_OUT = a.max_out
    load_env()
    envname = "OPENROUTER_API_KEY" if a.provider == "openrouter" else "ANTHROPIC_API_KEY"
    key = os.environ.get(envname)
    if not key: sys.exit(f"{envname} not set (export it, or put {envname}=... in {os.path.join(ROOT, '.env')})")
    ids = sorted(load_all()) if a.ids == "all" else (open(a.ids[1:]).read().split() if a.ids.startswith("@") else a.ids.split(","))
    b = Budget(a.token_cap, a.usd_cap)
    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(lambda pid: run_program(a.arm, pid, a.seed, a.model, key, b, a.out, a.thinking,
                                            provider=a.provider, reasoning=a.reasoning, improve=a.improve), ids))
    print(f"tokens used: {b.used} / cap {a.token_cap}; usd spent: {b.usd:.2f}" + (f" / cap {a.usd_cap}" if a.usd_cap else ""))


if __name__ == "__main__": main(sys.argv[1:])
