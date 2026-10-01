"""Over-constraint check (run FIRST, CPU only): teacher-force known nets token by token through NetFSM.

  $MLXPY -m genome.exp2.teacher_force     -> runs/exp2/teacher_force.json

Positives (every token must be allowed, and EOS at the end): every lint-clean net in runs/g0, runs/datagen/native,
runs/g1/native (*.hvm), the SFT rows (data/sft*/), and the lint-clean baseline samples (runs/exp/A_native_v1_iid.json, raw text as
generated). Each positive is forced three ways: the tokenizer's own segmentation of the SFT-style response, char by char, and
random 1-6 char chunks. Negatives: baseline samples the linter rejected for wires/brackets must be blocked somewhere (recall),
and any baseline text the automaton accepts end-to-end must be lint-clean for wires/brackets (soundness).
"""
import glob, json, os, random, re, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, ROOT)
from genome.verify import lint_net
from genome.exp.score import extract
from genome.exp2.netfsm import NetFSM

WIRE_BRACKET = re.compile(r"appears only once|appears \d+ times|brackets do not balance|exactly one `~`|text outside")


def force(pieces):
    """Returns None if all pieces and EOS are allowed, else (index, piece, reason)."""
    s = NetFSM()
    for i, p in enumerate(pieces):
        c = s.clone()
        if not c.feed(p): return (i, p, c.why)
        s = c
    c = s.clone()
    if not c.end(): return (len(pieces), "<EOS>", c.why)
    return None


def main():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("mlx-community/Qwen3-4B-Instruct-2507-4bit")
    from genome.exp2.vocab import token_strings
    strs, special = token_strings(tok)
    enc = lambda t: [strs[i] for i in tok.encode(t, add_special_tokens=False)]
    rng = random.Random(0)
    def chunks(t):
        out, i = [], 0
        while i < len(t): k = rng.randint(1, 6); out.append(t[i:i + k]); i += k
        return out

    nets = []  # (source, net)
    for pat in ("runs/g0/*/*.hvm", "runs/datagen/native/*/*/*.hvm", "runs/g1/native/*/*/*.hvm"):
        for f in sorted(glob.glob(os.path.join(ROOT, pat))): nets.append((pat.split("/")[1] + ":" + os.path.basename(f), open(f).read()))
    for f in sorted(glob.glob(os.path.join(ROOT, "data/sft*/*.jsonl"))):
        if "bend" in f: continue
        for l in open(f):
            m = json.loads(l)["messages"][-1]["content"]; n = extract(m)
            if n: nets.append(("sft:" + os.path.basename(os.path.dirname(f)), n))
    res = {"positives": collections.Counter(), "blocked": [], "lint_dirty_skipped": collections.Counter()}
    seen = set()
    for src, net in nets:
        key = net.strip()
        if key in seen: continue
        seen.add(key)
        if lint_net(net) is not None: res["lint_dirty_skipped"][src.split(":")[0]] += 1; continue
        resp = "```\n" + net.strip() + "\n```"
        for how, pieces in (("tok", enc(resp)), ("char", list(resp)), ("chunk", chunks(resp)),
                            ("think", enc("<think>\n\n</think>\n\n" + resp))):
            r = force(pieces); res["positives"][how] += 1
            if r: res["blocked"].append({"src": src, "how": how, "at": r[0], "piece": r[1], "why": r[2],
                                         "context": "".join(pieces[max(0, r[0] - 12):r[0] + 1])[-160:]})
    # baseline samples (raw text as generated)
    base = json.load(open(os.path.join(ROOT, "runs/exp/A_native_v1_iid.json")))["samples"]
    neg = collections.Counter(); pos_raw = collections.Counter(); unsound = []
    for pid, texts in base.items():
        for t in texts:
            net = extract(t); lint = lint_net(net) if net else "noblock"
            r = force(enc(t))
            wb = bool(lint and lint != "noblock" and WIRE_BRACKET.search(lint))
            if lint is None:
                pos_raw["clean"] += 1
                if r: pos_raw["clean_but_blocked"] += 1; res["blocked"].append({"src": "baseline:" + pid, "how": "raw", "at": r[0], "piece": r[1], "why": r[2],
                                                                                   "context": "".join(enc(t)[max(0, r[0] - 12):r[0] + 1])[-160:]})
            elif wb:
                neg["wire_bracket_lint_fail"] += 1; neg["blocked" if r else "NOT_blocked"] += 1
                if r: neg["why:" + (r[2] or "?").split(" ")[0] + " " + " ".join((r[2] or "").split(" ")[1:3])] += 1
            if r is None and wb: unsound.append({"pid": pid, "lint": lint[:300]})
    res["baseline_lint_clean"] = pos_raw; res["baseline_negatives"] = neg; res["unsound"] = unsound[:20]; res["n_unsound"] = len(unsound)
    out = {"n_distinct_positive_nets": sum(1 for _ in seen), **{k: v for k, v in res.items()}}
    os.makedirs(os.path.join(ROOT, "runs/exp2"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "runs/exp2/teacher_force.json"), "w"), indent=1, default=str)
    print(json.dumps({k: v for k, v in out.items() if k != "blocked"}, indent=1, default=str))
    print("n_blocked_positive_forcings:", len(res["blocked"]))
    for b in res["blocked"][:15]: print(json.dumps(b))


if __name__ == "__main__": main()
