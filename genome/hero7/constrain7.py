"""HERO-7 constrained decoding for the seating language.

The request is (sentence, guest list). The guest list is an INPUT of the request (the host supplies it with the sentence: the
34-guest chart plus any guests the test set's author added); it is not read from any gold program. From it we build the allowed
NAME tokens: every guest's full key, every company key, and unambiguous aliases (name without title, surname, first name, last
two words of a three-word name). Aliases are mapped back to the full guest key after decoding (`map_aliases`).

Decoding is restricted to the grammar of the language with an MLX logits processor:
  program := none | line (\n line)*      line := size N | together (company|CAT) | limit CAT+ K | apart CAT CAT | order CAT+
                                                  | avoid NAME NAME | pair NAME NAME        N, K in 1..6; CAT = 7 category ids
At each step the processor looks at the TOP_K most likely next tokens (by the model's logits), keeps those whose text keeps the
output a prefix of some program in the grammar (EOS only when the output is a complete program), and masks every other token;
if none of the TOP_K is allowed it tries the top 2,000, then the whole vocabulary. Sampling (temperature, top_p) then runs on the masked logits.
So greedy = the most likely allowed token; sampling = the model's distribution restricted to {top-K} ∩ grammar.
"""
from __future__ import annotations
import re, sys
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
sys.path.insert(0, _REPO)
import numpy as np
from genome.hero6 import lang6 as L
from genome.hero1.lang import CATS

HEADS = ["size", "together", "limit", "apart", "order", "avoid", "pair"]
NUMS = ["1", "2", "3", "4", "5", "6"]
TITLES = {"Secretary", "Speaker", "Chairman", "Director", "Mr.", "Ms.", "Dr.", "Administrator", "Mrs."}
TOP_K = 40


def name_table(guests):
    """-> (allowed tokens set, alias -> full key)."""
    full, comp = set(), set()
    for g in guests:
        if L.name_of(g): full.add(L.key(L.name_of(g)))
        if g[0]: comp.add(L.key(g[0]))
    cand = {}
    for g in guests:
        nm = L.name_of(g)
        if not nm: continue
        k = L.key(nm); w = nm.split()
        forms = set()
        core = [x for x in w if x not in TITLES]
        if core and core != w: forms.add("_".join(core))
        if len(core) >= 1: forms.add(core[-1])
        if len(core) >= 2: forms.add(core[0])
        if len(core) >= 3: forms.add("_".join(core[-2:]))
        for f in forms:
            f = L.key(f)
            if f and f != k: cand.setdefault(f, set()).add(k)
    alias = {a: next(iter(ks)) for a, ks in cand.items() if len(ks) == 1 and a not in full and a not in comp}
    return full | comp | set(alias), alias


def map_aliases(text, alias):
    out = []
    for l in text.strip().splitlines():
        t = l.split()
        if t and t[0] in ("avoid", "pair") and len(t) == 3:
            t = [t[0], alias.get(t[1], t[1]), alias.get(t[2], t[2])]
        out.append(" ".join(t))
    return "\n".join(out)


class Grammar:
    def __init__(self, names):
        self.names = sorted(names)

    def _opts_prefix(self, opts, p):
        return any(o.startswith(p) for o in opts)

    def _line(self, line, final):
        """final: the line must be complete. -> True if `line` is a (complete if final) prefix of a valid line."""
        tk = line.split(" ")
        if len(tk) == 1:
            return (tk[0] in HEADS and False) if final else any(h.startswith(tk[0]) for h in HEADS)
        h = tk[0]
        if h not in HEADS: return False
        args, part = tk[1:-1], tk[-1]
        if any(a == "" for a in args): return False
        if final: args, part = tk[1:], None
        if h == "size": slots = [NUMS]
        elif h == "together": slots = [["company"] + CATS]
        elif h == "apart": slots = [CATS, CATS]
        elif h in ("avoid", "pair"): slots = [self.names, self.names]
        elif h == "limit":
            cats = []
            for i, a in enumerate(args):
                if a in CATS and a not in cats and not (cats and False): cats.append(a); continue
                if a in NUMS and cats and i == len(args) - 1:
                    return part is None or False   # nothing may follow K
                return False
            if part is None: return False          # complete limit needs K last
            opts = [c for c in CATS if c not in cats] + (NUMS if cats else [])
            return self._opts_prefix(opts, part)
        elif h == "order":
            seen = []
            for a in args:
                if a not in CATS or a in seen: return False
                seen.append(a)
            if part is None: return len(seen) >= 1
            return self._opts_prefix([c for c in CATS if c not in seen], part)
        if len(args) > len(slots): return False
        for a, s in zip(args, slots):
            if a not in s: return False
        if h in ("apart", "avoid", "pair") and len(args) == 2 and args[0] == args[1]: return False
        if part is None: return len(args) == len(slots)
        if len(args) >= len(slots): return False
        opts = slots[len(args)]
        if h in ("apart", "avoid", "pair") and args: opts = [o for o in opts if o != args[0] or o.startswith(part) and o != part]
        return self._opts_prefix(opts, part)

    def viable(self, text, final=False):
        if "�" in text or "\r" in text or "\t" in text: return False
        if text.startswith("n") or text == "":
            if "none".startswith(text) and not final: return True
            if text in ("none", "none\n"): return True
            if text.startswith("n") : return False
        lines = text.split("\n")
        if final and lines[-1] == "": lines = lines[:-1]
        if not lines: return False
        heads = []
        for i, l in enumerate(lines):
            last = i == len(lines) - 1
            if l == "" and not last: return False
            if not self._line(l, final or not last): return False
            heads.append(l.split(" ")[0])
        done = heads if final else heads[:-1]
        if done.count("size") > 1 or done.count("order") > 1: return False
        if not final and len(lines) > 1 and lines[-1] and heads[-1] in ("size", "order") and heads[-1] in heads[:-1]: return False
        return True


class Processor:
    """MLX logits processor for one sequence (BatchGenerator passes (token_context, logits[1, V]); token_context = the prompt
    followed by the generated tokens; the context length at the first call marks where generation starts)."""
    def __init__(self, gram, pieces, eos):
        self.g, self.pieces, self.eos = gram, pieces, eos
        self.full_scans = 0; self.n0 = None

    def __call__(self, ctx, logits):
        import mlx.core as mx
        ids = ctx.tolist() if hasattr(ctx, "tolist") else list(ctx)
        if self.n0 is None: self.n0 = len(ids)
        ids = ids[self.n0:]
        text = "".join(self.pieces[i] for i in ids)
        lg = logits[0]
        top = mx.argpartition(-lg, TOP_K)[:TOP_K].tolist()
        ok = [t for t in top if self._ok(text, t)]
        if not ok:
            top = mx.argpartition(-lg, 2000)[:2000].tolist()
            ok = [t for t in top if self._ok(text, t)]
        if not ok:
            self.full_scans += 1
            ok = [t for t in range(len(self.pieces)) if self._ok(text, t)]
            if not ok: ok = list(self.eos)
        m = np.full(lg.shape[0], -np.inf, dtype=np.float32); m[ok] = 0.0
        return logits + mx.array(m)[None]

    def _ok(self, text, t):
        if t in self.eos: return self.g.viable(text, final=True)
        p = self.pieces[t] if t < len(self.pieces) else ""
        if not p: return False
        return self.g.viable(text + p)


_PIECES = {}


def pieces(tok):
    k = id(tok)
    if k not in _PIECES:
        V = len(tok.vocab) if hasattr(tok, "vocab") else tok.vocab_size
        _PIECES[k] = [tok.decode([i]) for i in range(V)]
    return _PIECES[k]


def selftest():
    names, alias = name_table(L.load_real()[0])
    g = Grammar(names)
    good = ["size 3", "together company\nlimit government 1", "limit ai_lab chips 2", "order chips ai_lab", "avoid Elon_Musk OpenAI",
            "pair Su Hock_Tan", "none", "apart ai_lab chips\n"]
    bad = ["size 7", "limit 2", "apart chips chips", "order chips chips", "avoid Elon_Musk Elon_Musk", "pair Bill_Daniels Su",
           "together software", "apart chips software", "size 3\nsize 4", "none\nsize 3", "limit chips 2 3", "pair Su"]
    assert all(g.viable(x, final=True) for x in good), [x for x in good if not g.viable(x, final=True)]
    assert not any(g.viable(x, final=True) for x in bad), [x for x in bad if g.viable(x, final=True)]
    assert g.viable("pair Su") and g.viable("lim") and g.viable("limit chips ") and not g.viable("pair Bill_D")
    assert map_aliases("pair Su Tan\nsize 3", alias) == "pair Lisa_Su Hock_Tan\nsize 3"
    print("aliases:", len(alias), sorted(alias.items())[:12], "... allowed names:", len(names))


if __name__ == "__main__": selftest()
