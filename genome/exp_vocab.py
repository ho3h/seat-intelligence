"""G2 groundwork: learn a vocabulary on some verified nets, measure coverage and description length on nets it never saw."""
import glob, json, os, random, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, ROOT)
from genome.induce import induce, apply_vocab
from genome.netast import tokens
ok = lambda s: s["accepted"] and s.get("audit") == ["pass", "pass"]

def nets_from(pat):
    out = {}
    for f in sorted(glob.glob(pat)):
        s = json.load(open(f))
        b = os.path.join(os.path.dirname(f), "best.hvm")
        if ok(s) and os.path.exists(b): out[s["pid"]] = open(b).read()
    return out

def measure(orig, rew, lib, st):
    before = sum(len(tokens(t)) for t in orig.values()); after = sum(len(tokens(t)) for t in rew.values()) + len(tokens(lib))
    mass = sum(st["mass"].values()) / max(1, st["total_nodes"])
    return before, after, mass

if __name__ == "__main__":
    n_train = int(sys.argv[1]) if len(sys.argv) > 1 else 300
    train = nets_from("runs/datagen/native/seed0/*/state.json"); items = sorted(train.items()); random.Random(0).shuffle(items)
    fit, held_same = dict(items[:n_train]), dict(items[n_train:n_train + 150])
    corpus = nets_from("runs/g1/native/seed0/*/state.json")
    for extra in ("runs/g1r1/native/seed0/*/state.json", "runs/g1esc/native/seed0/*/state.json"): corpus.update({k: v for k, v in nets_from(extra).items() if k not in corpus})
    corpus = {k: v for k, v in corpus.items() if not k.startswith("gen_")}
    t0 = time.time()
    rew, lib, st = induce(fit, max_words=40)
    b, a, m = measure(fit, rew, lib, st)
    print(f"[fit on {len(fit)} generated nets] words {len(st['words'])}  description {b}->{a} tokens ({100*(1-a/b):.1f}% shorter)  mass in words {100*m:.1f}%  ({time.time()-t0:.0f}s)", flush=True)
    canons = st["canon"]
    for label, held in (("held-out generated nets (same families)", held_same), ("held-out CORPUS nets (never seen families)", corpus)):
        r2, l2, s2 = apply_vocab(held, canons)
        b, a, m = measure(held, r2, l2, s2)
        used = sum(1 for w in s2["words"] if w[1] > 0)
        print(f"[{label}: {len(held)} nets] words used {used}/{len(canons)}  description {b}->{a} tokens ({100*(1-a/b):.1f}% shorter)  mass in words {100*m:.1f}%", flush=True)
    json.dump({"canons": canons}, open("runs/vocab_v1.json", "w"))
