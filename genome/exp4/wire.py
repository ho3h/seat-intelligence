"""The wiring model: given a skeleton book, score pairs of blank slots (same definition) and decode a perfect matching.

  python -m genome.exp4.wire train  --out runs/exp4/wire.pt           (MLX venv python: needs torch)
Model: a small transformer over the skeleton token sequence of the whole book (definition names replaced by per-book indices,
randomly permuted during training, so a call `@f ~ (_ (_ _))` can attend to f's definition). Per-token extra embeddings: slot role
(parent node kind x port, or top of root/redex side), depth, statement index. Pair score s_ij = <q_i,k_j> + <q_j,k_i>, trained with
a per-slot softmax over the other slots of its definition. Decoding: max-weight perfect matching (Blossom, networkx) on
w_ij = logp_i(j) + logp_j(i), so every wire has exactly two ends by construction.
"""
from __future__ import annotations
import json, math, os, random, sys, time, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)
from genome.netast import parse_book
from genome.exp4.skel import to_skeleton, KIDS

SPECIAL = ["<pad>", "DEF", "=", "&", "&!", "~", "(", "{", "$(", "?(", ")", "*", "_", "REF_UNK", "NUM_UNK"]
NID = 128  # max definitions per book (indices)
ROLE = {"root": 1, "redL": 2, "redR": 3}
for i, k in enumerate(KIDS): ROLE[k + "0"] = 4 + 2 * i; ROLE[k + "1"] = 5 + 2 * i
OPEN = {"con": "(", "dup": "{", "opr": "$(", "swi": "?("}


def num_vocab(rows, minc=3):
    c = collections.Counter()
    def walk(t):
        if t[0] == "num": c[t[1]] += 1
        elif t[0] in KIDS: walk(t[1]); walk(t[2])
    for r in rows:
        d, o = parse_book(r["net"])
        for n in o:
            root, reds = d[n]; walk(root); [walk(a) or walk(b) for _, a, b in reds]
    return sorted(k for k, v in c.items() if v >= minc)


class Vocab:
    def __init__(self, nums):
        self.itos = SPECIAL + [f"ID{i}" for i in range(NID)] + ["N:" + x for x in nums]
        self.stoi = {s: i for i, s in enumerate(self.itos)}

    def __len__(self): return len(self.itos)


def encode_book(skdefs, order, V: Vocab, perm=None):
    """Token ids + features for a skeleton book. Returns dict of lists; slot entries carry (def index, slot index in def)."""
    idx = {n: (perm[i] if perm else i) for i, n in enumerate(order)}
    tok, role, depth, stmt, sdef, sidx = [], [], [], [], [], []
    def emit(t, r, dp, st, di): tok.append(V.stoi[t]); role.append(r); depth.append(min(dp, 31)); stmt.append(min(st, 31)); sdef.append(di)
    for di, n in enumerate(order):
        root, reds = skdefs[n]; counter = [0]
        def tree(t, r, dp, st):
            k = t[0]
            if k == "var":
                emit("_", r, dp, st, di); sidx.append((len(tok) - 1, di, counter[0])); counter[0] += 1
            elif k in KIDS:
                emit(OPEN[k], r, dp, st, di); tree(t[1], ROLE[k + "0"], dp + 1, st); tree(t[2], ROLE[k + "1"], dp + 1, st); emit(")", 0, dp, st, di)
            elif k == "era": emit("*", r, dp, st, di)
            elif k == "ref": emit(f"ID{idx[t[1]]}" if t[1] in idx and idx[t[1]] < NID else "REF_UNK", r, dp, st, di)
            else: emit("N:" + t[1] if ("N:" + t[1]) in V.stoi else "NUM_UNK", r, dp, st, di)
        emit("DEF", 0, 0, 0, di); emit(f"ID{idx[n]}" if idx[n] < NID else "REF_UNK", 0, 0, 0, di); emit("=", 0, 0, 0, di)
        tree(root, ROLE["root"], 0, 0)
        for s, (p, a, b) in enumerate(reds):
            emit("&!" if p else "&", 0, 0, s + 1, di); tree(a, ROLE["redL"], 0, s + 1); emit("~", 0, 0, s + 1, di); tree(b, ROLE["redR"], 0, s + 1)
    return {"tok": tok, "role": role, "depth": depth, "stmt": stmt, "slots": sidx}


def example(net_text, V, perm_rng=None):
    d, o = parse_book(net_text); sk, m = to_skeleton(d, o)
    perm = None
    if perm_rng is not None:
        perm = list(range(max(len(o), NID))); perm_rng.shuffle(perm); perm = perm[:len(o)]
    e = encode_book(sk, o, V, perm)
    # partner targets per slot (in book slot order)
    base, off = {}, 0
    for di, n in enumerate(o): base[di] = off; off += sum(1 for s in e["slots"] if s[1] == di) if False else 0
    part = {}
    for di, n in enumerate(o):
        for i, j in m[n]: part[(di, i)] = j; part[(di, j)] = i
    e["target"] = [part[(di, si)] for _, di, si in e["slots"]]
    e["order"] = o; e["sk"] = sk; e["gold"] = m
    return e


# ------------------------------------------------------------------------------------------------ model (torch)
def build_model(nvocab, d=128, layers=3, heads=4, maxlen=4096):
    import torch, torch.nn as nn

    class WireNet(nn.Module):
        def __init__(self):
            super().__init__()
            self.tok = nn.Embedding(nvocab, d); self.pos = nn.Embedding(maxlen, d); self.role = nn.Embedding(16, d)
            self.depth = nn.Embedding(32, d); self.stmt = nn.Embedding(32, d)
            el = nn.TransformerEncoderLayer(d, heads, 4 * d, dropout=0.1, batch_first=True, norm_first=True)
            self.enc = nn.TransformerEncoder(el, layers); self.norm = nn.LayerNorm(d)
            self.q = nn.Linear(d, d); self.k = nn.Linear(d, d); self.d = d

        def forward(self, tok, role, depth, stmt, pad):
            L = tok.shape[1]; pos = torch.arange(L, device=tok.device)[None]
            h = self.tok(tok) + self.pos(pos) + self.role(role) + self.depth(depth) + self.stmt(stmt)
            return self.norm(self.enc(h, src_key_padding_mask=pad))

        def pair_logits(self, hs):  # hs: [S, d] slot states of one book -> [S, S]
            q, k = self.q(hs), self.k(hs); a = q @ k.T
            return (a + a.T) / math.sqrt(self.d)
    return WireNet()


def batchify(exs, dev):
    import torch
    L = max(len(e["tok"]) for e in exs); B = len(exs)
    T = torch.zeros(B, L, dtype=torch.long); R = torch.zeros_like(T); D = torch.zeros_like(T); S = torch.zeros_like(T)
    P = torch.ones(B, L, dtype=torch.bool)
    for b, e in enumerate(exs):
        n = len(e["tok"]); T[b, :n] = torch.tensor(e["tok"]); R[b, :n] = torch.tensor(e["role"]); D[b, :n] = torch.tensor(e["depth"])
        S[b, :n] = torch.tensor(e["stmt"]); P[b, :n] = False
    return T.to(dev), R.to(dev), D.to(dev), S.to(dev), P.to(dev)


def slot_tensors(exs, dev):
    import torch
    B = len(exs); Sm = max(1, max(len(e["slots"]) for e in exs))
    pos = torch.zeros(B, Sm, dtype=torch.long); dd = torch.full((B, Sm), -1, dtype=torch.long); tg = torch.full((B, Sm), -100, dtype=torch.long)
    for b, e in enumerate(exs):
        first = {}
        for g, (_, d_, si) in enumerate(e["slots"]):
            if si == 0: first[d_] = g
        for g, (p, d_, si) in enumerate(e["slots"]):
            pos[b, g] = p; dd[b, g] = d_
            if "target" in e: tg[b, g] = first[d_] + e["target"][g]
    return pos.to(dev), dd.to(dev), tg.to(dev)


def batch_logprobs(model, exs, dev):
    """[B, S, S] log-probs of partner (masked to same definition), plus def ids and targets."""
    import torch
    T, R, D, S, P = batchify(exs, dev); H = model(T, R, D, S, P)
    pos, dd, tg = slot_tensors(exs, dev)
    hs = torch.gather(H, 1, pos[..., None].expand(-1, -1, H.shape[-1]))
    q, k = model.q(hs), model.k(hs); A = q @ k.transpose(1, 2); A = (A + A.transpose(1, 2)) / math.sqrt(model.d)
    Sm = pos.shape[1]
    mask = (dd[:, :, None] != dd[:, None, :]) | torch.eye(Sm, dtype=torch.bool, device=dev)[None] | (dd[:, None, :] < 0)
    A = A.masked_fill(mask, -1e9)
    return torch.log_softmax(A, -1), dd, tg


def slot_logprobs(model, exs, dev):
    LP, dd, _ = batch_logprobs(model, exs, dev); out = []
    for b, e in enumerate(exs):
        n = len(e["slots"]); out.append((LP[b, :n, :n], dd[b, :n]))
    return out


def loss_on(model, exs, dev):
    import torch
    LP, dd, tg = batch_logprobs(model, exs, dev)
    return torch.nn.functional.nll_loss(LP.reshape(-1, LP.shape[-1]), tg.reshape(-1), ignore_index=-100)


def decode(LP, di, e):
    """Max-weight perfect matching per definition. Returns {def name: [(i,j),...]}."""
    import networkx as nx
    LP = LP.detach().float().cpu().numpy(); di = di.cpu().numpy(); res = {}
    for dn, n in enumerate(e["order"]):
        g = [i for i in range(len(di)) if di[i] == dn]
        if not g: res[n] = []; continue
        sub = LP[g][:, g]; k = len(g)
        W = sub + sub.T
        G = nx.Graph()
        for i in range(k):
            for j in range(i + 1, k): G.add_edge(i, j, weight=float(W[i, j]) + 1e4)
        M = nx.max_weight_matching(G, maxcardinality=True)
        res[n] = sorted(tuple(sorted(p)) for p in M)
    return res


def chunks(rows, V, rng, maxtok=2000):
    """Examples; books longer than maxtok are dropped from training (rare)."""
    out = []
    for r in rows:
        e = example(r["net"], V, rng)
        if len(e["tok"]) <= maxtok: out.append(e)
    return out


def train(out, epochs=30, bs=16, lr=1e-3, seed=0, device=None, max_compose=400, max_minutes=35):
    import torch
    torch.manual_seed(seed); rng = random.Random(seed); torch.set_num_threads(8)
    D = json.load(open(os.path.join(ROOT, "runs/exp4/dataset.json")))
    comp = [r for r in D if r["split"] == "train" and r["src"] == "compose"]; rng.shuffle(comp)
    tr = [r for r in D if r["split"] == "train" and r["src"] != "compose"] + comp[:max_compose]; dv = [r for r in D if r["split"] == "dev"]
    V = Vocab(num_vocab(tr)); dev = device or "cpu"
    model = build_model(len(V)).to(dev); opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    dvx = [example(r["net"], V) for r in dv]
    print(f"train books {len(tr)} dev {len(dv)} vocab {len(V)} params {sum(p.numel() for p in model.parameters())/1e6:.2f}M dev={dev}", flush=True)
    steps_per = math.ceil(len(tr) / bs); total = epochs * steps_per; step = 0; best = (-1, None); t0 = time.time()
    for ep in range(epochs):
        exs = chunks(tr, V, rng, maxtok=1500); exs.sort(key=lambda e: len(e["tok"]) + rng.random() * 200)
        batches = [exs[i:i + bs] for i in range(0, len(exs), bs)]; rng.shuffle(batches)
        model.train(); tl = 0
        for b in batches:
            for g in opt.param_groups: g["lr"] = lr * min(1, step / 200) * 0.5 * (1 + math.cos(math.pi * step / total))
            loss = loss_on(model, b, dev); opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); step += 1; tl += loss.item()
        acc = evaluate_defs(model, dvx, dev)
        print(f"ep {ep} loss {tl/len(batches):.4f} dev def-exact {acc:.4f} {time.time()-t0:.0f}s", flush=True)
        if acc > best[0]:
            best = (acc, ep); torch.save({"state": model.state_dict(), "nums": V.itos}, out)
        if time.time() - t0 > max_minutes * 60: print("time cap"); break
    print("best dev", best)


def evaluate_defs(model, exs, dev, bs=8):
    import torch
    model.eval(); right = tot = 0
    with torch.no_grad():
        for i in range(0, len(exs), bs):
            b = exs[i:i + bs]
            for e, (LP, di) in zip(b, slot_logprobs(model, b, dev)):
                pred = decode(LP, di, e)
                for n in e["order"]: right += pred[n] == e["gold"][n]; tot += 1
    return right / tot


def load(path, device=None):
    import torch
    ck = torch.load(path, map_location="cpu"); V = Vocab([]); V.itos = ck["nums"]; V.stoi = {s: i for i, s in enumerate(V.itos)}
    dev = device or ("mps" if torch.backends.mps.is_available() else "cpu")
    m = build_model(len(V)); m.load_state_dict(ck["state"]); m.to(dev).eval()
    return m, V, dev


def predict_scores(model, V, dev, skdefs, order):
    """Skeleton -> (matching, {def: symmetric pair-weight matrix w_ij = logp_i(j) + logp_j(i)} as numpy)."""
    import torch
    e = encode_book(skdefs, order, V); e["order"] = order
    with torch.no_grad():
        LP, di = slot_logprobs(model, [e], dev)[0]
    M = decode(LP, di, e); L = LP.float().cpu().numpy(); d = di.cpu().numpy(); Ws = {}
    for dn, n in enumerate(order):
        g = [i for i in range(len(d)) if d[i] == dn]; sub = L[g][:, g]; Ws[n] = sub + sub.T
    return M, Ws


def predict(model, V, dev, skdefs, order):
    """Skeleton -> matching dict (and per-def log-prob matrices)."""
    import torch
    e = encode_book(skdefs, order, V); e["order"] = order
    with torch.no_grad():
        LP, di = slot_logprobs(model, [e], dev)[0]
    return decode(LP, di, e)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(); ap.add_argument("cmd"); ap.add_argument("--out", default="runs/exp4/wire.pt")
    ap.add_argument("--epochs", type=int, default=30); ap.add_argument("--device", default=None)
    a = ap.parse_args()
    if a.cmd == "train": train(os.path.join(ROOT, a.out) if not os.path.isabs(a.out) else a.out, epochs=a.epochs, device=a.device)
