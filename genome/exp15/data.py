"""exp15 data: (task text -> stage program) pairs generated from genome/taskgen.py's own stage objects (the pipeline stages ARE
the ground truth; no LLM). Split by TASK: no training task has the same program (hence the same description) as any test task.

  python3 -m genome.exp15.data            -> runs/exp15/data/{train,valid}.jsonl, runs/exp15/sets/{iid,deep,para}.json

Task specs (JSON-able, deterministic):
  ["gen", family, idx]   genome.taskgen.task(family, idx)  (iid_test = data/tasksets/iid_test.json)
  ["s15", split, idx]    fresh pipeline / reduce task built from taskgen._stage and taskgen.REDUCERS with its own seed;
                         split "train" (pipelines 1-6 stages, reduce 0-4 stages + reducer) or "deepK" (a K-stage pipeline)
  ["para", family, idx]  the iid_test task with the SAME reference but a reworded description (templates never seen in training)
"""
from __future__ import annotations
import hashlib, json, os, random, sys
from collections import Counter
from genome import taskgen as TG
from genome.taskgen import task, _mk, L, SIZES_L, TEST_L, EDGE_L, _num_prefix, pipeline_from_steps
from genome.types import u24
from genome.exp13.truth import truth
from genome.exp13.words import program_py
from genome.exp15.lang import to_text, prompt_stage

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "runs", "exp15")
N_TRAIN, N_VALID = 6000, 150
DEEP = {3: 40, 4: 40, 5: 40, 7: 30, 8: 30}


def _r(*key):
    return random.Random(int.from_bytes(hashlib.sha256("|".join(map(str, ("s15",) + key)).encode()).digest()[:8], "big"))


NOVEL_K = [4, 7, 12, 15, 25, 37, 64, 75, 150, 250, 999]; NOVEL_M = [6, 8, 9, 11]; NOVEL_A = [4, 6, 8, 9, 11, 13]


def _novel_stage(r):
    """a taskgen-worded stage whose constant lies OUTSIDE taskgen's constant sets (never seen in training)."""
    k = r.choice(NOVEL_K); m = r.choice(NOVEL_M); a = r.choice(NOVEL_A)
    preds = [f"x > {k}", f"x < {k}", f"x >= {k}", f"x mod {m} equals {r.randrange(1, m)}"]
    maps = [f"x*{a}+{r.choice([3, 5, 9, 42])} (mod 2^24)", f"x xor {r.choice([5, 31, 127, 1023])}", f"x and {r.choice([5, 31, 127, 1023])}",
            f"x+{r.choice([3, 4, 7, 11])} (mod 2^24)", f"x mod {r.choice([5, 7, 9, 10, 12, 13])}", f"x integer-divided by {a}"]
    kt = r.choice([4, 6, 7, 10, 12])
    return r.choice([f"keep only the elements x for which {r.choice(preds)}", f"replace every element x by {r.choice(maps)}",
                     f"keep only the first {kt} elements (all of them if there are fewer)",
                     f"remove the first {kt} elements (nothing is removed if there are fewer)"])


def _novel_task(idx):
    from genome.exp13.truth import _stage as parse_stage
    r = _r("novel", idx); pipe = idx % 2 == 0
    n = r.randint(1, 3) if pipe else r.randint(1, 2)
    ds = [_novel_stage(r) if j == 0 else r.choice([_novel_stage(r), TG._stage(r)[0]]) for j in range(n)]
    steps = [(d, None) for d in ds]; terms = [parse_stage(d) for d in ds]
    if pipe:
        f = program_py(terms)
        return _mk(f"x15_pipeline_novel_{idx:05d}", _num_prefix(steps) + "\nOutput the resulting list.", L, L, f,
                   lambda rng, n: [rng.randrange(1000) for _ in range(n)], SIZES_L, TEST_L, EDGE_L)
    rd, rf = r.choice(TG.REDUCERS); fs = program_py(terms)
    pre = _num_prefix(steps) + "\n" if steps else "Use the input list as it is.\n"
    return _mk(f"x15_reduce_novel_{idx:05d}", pre + f"Output {rd}.", L, u24, lambda xs, fs=fs, rf=rf: rf(fs(xs)),
               lambda rng, n: [rng.randrange(1000) for _ in range(n)], SIZES_L, TEST_L, EDGE_L)


def s15_task(split, idx):
    if split == "novel": return _novel_task(idx)
    r = _r(split, idx)
    if split.startswith("deep"):
        steps = [TG._stage(r) for _ in range(int(split[4:]))]
        return pipeline_from_steps(steps, f"x15_pipeline_{split}_{idx:05d}")
    if r.random() < 0.5:
        steps = [TG._stage(r) for _ in range(r.randint(1, 6))]
        return pipeline_from_steps(steps, f"x15_pipeline_{split}_{idx:05d}")
    steps = [TG._stage(r) for _ in range(r.randint(0, 4))]; rd, rf = r.choice(TG.REDUCERS)
    def ref(xs, steps=steps, rf=rf):
        for _, f in steps: xs = f(xs)
        return rf(xs)
    pre = _num_prefix(steps) + "\n" if steps else "Use the input list as it is.\n"
    return _mk(f"x15_reduce_{split}_{idx:05d}", pre + f"Output {rd}.", L, u24, ref, lambda rng, n: [rng.randrange(100) for _ in range(n)],
               SIZES_L, TEST_L, EDGE_L)


# ------------------------------------------------------------------ paraphrase (wording never seen in training)
def _pp(P):
    k = P[0]
    if k == "gt": return f"discard every value that is not greater than {P[1]}"
    if k == "lt": return f"discard every value that is {P[1]} or more"
    if k == "ge": return f"retain only the values that are at least {P[1]}"
    if k == "even": return "throw away the odd values"
    if k == "odd": return "throw away the even values"
    return f"retain only the values whose remainder on division by {P[1]} is {P[2]}"


def _pe(E):
    k = E[0]
    if k == "lin": return f"multiply each value by {E[1]} and then add {E[2]}, modulo 16777216"
    if k == "xor": return f"xor each value with {E[1]}"
    if k == "and": return f"bitwise-and each value with {E[1]}"
    if k == "add": return f"add {E[1]} to each value, modulo 16777216"
    if k == "sq": return "square each value, modulo 16777216"
    if k == "mod": return f"take each value modulo {E[1]}"
    if k == "div": return f"divide each value by {E[1]}, rounding down"
    raise KeyError(E)


def _ps(S):
    k = S[0]
    if k == "filter": return _pp(S[1])
    if k == "map": return _pe(S[1])
    if k == "take": return f"truncate the list to its first {S[1]} values"
    if k == "drop": return f"skip the first {S[1]} values"
    return {"reverse": "flip the list back to front", "dedup": "delete each value that equals the value right before it",
            "runsum": "turn the list into its prefix sums, modulo 16777216", "sort": "order the values from smallest to largest"}[k]


PRED_RED = {"sum": "the total of the values modulo 16777216 (0 if there are none)", "count": "how many values there are",
            "max": "the maximum value, or 0 if there are none", "min": "the minimum value, or 16777215 if there are none",
            "xor": "the xor of all the values (0 if there are none)", "first": "the value at the front (0 if there are none)",
            "last": "the value at the back (0 if there are none)",
            "cntgtfirst": "how many of the values after the first one exceed the first one (0 if there are none)"}


def para_task(fam, idx):
    p = task(fam, idx); stages, red = truth(p)
    body = "".join(f"- {_ps(s)}\n" for s in stages)
    if red is None: d = "Take the list of numbers and do the following, in this order:\n" + body + "Return the list you end up with."
    elif stages: d = "Take the list of numbers and do the following, in this order:\n" + body + f"Return {PRED_RED[red[0]]}."
    else: d = f"Return {PRED_RED[red[0]]}, for the input list."
    p.id = f"para_{fam}_{idx:05d}"; p.desc = d
    return p


def load_task(spec):
    k = spec[0]
    if k == "gen": return task(spec[1], spec[2])
    if k == "s15": return s15_task(spec[1], spec[2])
    if k == "para": return para_task(spec[1], spec[2])
    raise KeyError(spec)


def gold(p):
    """ground-truth word program, parsed from the (templated) description by exp13.truth."""
    if p.id.startswith("para_"):
        fam, idx = p.id.split("_")[1], int(p.id.split("_")[2]); return truth(task(fam, idx))
    return truth(p)


def depth(stages, red):
    return len(stages) + (1 if red else 0)


def _check(p, n=12):
    """gold program semantics == task reference on random + edge inputs (cheap sanity, Python only)."""
    st, rd = gold(p); f = program_py(st, rd); rng = random.Random(1)
    xs_all = EDGE_L + [[rng.randrange(hi) for _ in range(rng.randrange(0, 17))] for hi in (10, 100, 1000) for _ in range(n)]
    return all(f(list(x)) == p.ref(list(x)) for x in xs_all)


def row(p):
    st, rd = gold(p)
    return {"messages": [{"role": "user", "content": prompt_stage(p)}, {"role": "assistant", "content": to_text(st, rd)}]}


def build():
    os.makedirs(os.path.join(OUT, "data"), exist_ok=True); os.makedirs(os.path.join(OUT, "sets"), exist_ok=True)
    iid = [["gen", f, i] for f, i in json.load(open(os.path.join(ROOT, "data/tasksets/iid_test.json")))]
    para = [["para", f, i] for _, f, i in iid]
    deep = []
    for k, n in DEEP.items():
        seen, i = set(), 0
        while len([s for s in deep if s[1] == f"deep{k}"]) < n:
            p = s15_task(f"deep{k}", i); key = to_text(*gold(p))
            if key not in seen: seen.add(key); deep.append(["s15", f"deep{k}", i])
            i += 1
    test_keys = {to_text(*gold(load_task(s))) for s in iid + deep}
    train, i, dropped = [], 0, 0
    tr_keys = set()
    while len(train) < N_TRAIN + N_VALID:
        p = s15_task("train", i); key = to_text(*gold(p)); i += 1
        if key in test_keys: dropped += 1; continue
        if key in tr_keys: continue
        tr_keys.add(key); train.append(["s15", "train", i - 1])
    bad = [s for s in iid + deep + para + train[:300] if not _check(load_task(s))]
    assert not bad, bad[:5]
    for name, specs in (("iid", iid), ("deep", deep), ("para", para), ("train", train)):
        json.dump(specs, open(os.path.join(OUT, "sets", f"{name}.json"), "w"))
    with open(os.path.join(OUT, "data", "train.jsonl"), "w") as f:
        for s in train[:N_TRAIN]: f.write(json.dumps(row(load_task(s))) + "\n")
    with open(os.path.join(OUT, "data", "valid.jsonl"), "w") as f:
        for s in train[N_TRAIN:]: f.write(json.dumps(row(load_task(s))) + "\n")
    shape = lambda s: tuple(x[0] for x in gold(load_task(s))[0]) + ((gold(load_task(s))[1][0],) if gold(load_task(s))[1] else ())
    tr_shapes = {shape(s) for s in train[:N_TRAIN]}
    stats = {"train": N_TRAIN, "valid": N_VALID, "train_dropped_as_test_program": dropped,
             "train_depth": dict(sorted(Counter(depth(*gold(load_task(s))) for s in train[:N_TRAIN]).items())),
             "iid_depth": dict(sorted(Counter(depth(*gold(load_task(s))) for s in iid).items())),
             "deep_depth": dict(sorted(Counter(depth(*gold(load_task(s))) for s in deep).items())),
             "iid_shape_seen_in_train": sum(shape(s) in tr_shapes for s in iid), "deep_shape_seen_in_train": {
                 k: sum(shape(s) in tr_shapes for s in deep if s[1] == f"deep{k}") for k in DEEP}}
    json.dump(stats, open(os.path.join(OUT, "sets", "stats.json"), "w"), indent=1); print(json.dumps(stats, indent=1))


def build_novel(n=120):
    """unseen-constant set: taskgen wording, constants outside taskgen's sets (the model never saw these numbers)."""
    specs = [["s15", "novel", i] for i in range(n)]
    bad = [s for s in specs if not _check(load_task(s))]; assert not bad, bad[:5]
    json.dump(specs, open(os.path.join(OUT, "sets", "novel.json"), "w"))
    print("novel", n, dict(sorted(Counter(depth(*gold(load_task(s))) for s in specs).items())))





# ------------------------------------------------------------------ wording augmentation (control): two MORE wordings (B, C) mixed
# with taskgen's (A) in training; the paraphrase test wording (D, above) stays unseen. Tests whether the model can learn to read
# varied language rather than one template.
def _wb(S, v):
    k = S[0]; P = S[1] if len(S) > 1 else None
    if k == "filter":
        c = P[0]; kk = P[-1]; m = P[1] if c == "modeq" else None
        if v == "B":
            if c == "gt": return f"keep the elements that are greater than {kk}"
            if c == "lt": return f"keep the elements that are smaller than {kk}"
            if c == "ge": return f"keep the elements that are greater than or equal to {kk}"
            if c in ("even", "odd"): return f"keep the {c} elements"
            return f"keep the elements congruent to {kk} modulo {m}"
        if c == "gt": return f"remove all elements less than or equal to {kk}"
        if c == "lt": return f"remove all elements greater than or equal to {kk}"
        if c == "ge": return f"remove all elements below {kk}"
        if c == "even": return "remove all odd elements"
        if c == "odd": return "remove all even elements"
        return f"remove all elements whose residue mod {m} is not {kk}"
    if k == "map":
        E = P; e = E[0]
        B = {"lin": lambda: f"map each element x to {E[1]}*x + {E[2]} modulo 2^24", "xor": lambda: f"map each element x to x XOR {E[1]}",
             "and": lambda: f"map each element x to x AND {E[1]}", "add": lambda: f"increase each element by {E[1]} modulo 2^24",
             "sq": lambda: "square every element modulo 2^24", "mod": lambda: f"reduce each element modulo {E[1]}",
             "div": lambda: f"map each element x to floor(x / {E[1]})"}
        C = {"lin": lambda: f"replace each element by {E[1]} times itself plus {E[2]} (wrapping at 2^24)",
             "xor": lambda: f"flip the bits of each element selected by the mask {E[1]}", "and": lambda: f"mask each element with {E[1]} (bitwise and)",
             "add": lambda: f"replace each element x by x plus {E[1]}, wrapping at 2^24", "sq": lambda: "replace each element by its square, wrapping at 2^24",
             "mod": lambda: f"replace each element by its remainder after division by {E[1]}",
             "div": lambda: f"replace each element by the quotient of dividing it by {E[1]}"}
        return (B if v == "B" else C)[e]()
    B = {"take": f"keep at most {P} elements from the front", "drop": f"discard the first {P} elements", "reverse": "reverse the list",
         "dedup": "remove consecutive duplicates", "runsum": "compute the cumulative sums (mod 2^24)", "sort": "sort the list in non-decreasing order"}
    C = {"take": f"retain the leading {P} elements (or all, if shorter)", "drop": f"keep everything after the first {P} elements",
         "reverse": "put the elements in the opposite order", "dedup": "squeeze each block of repeated adjacent elements down to one element",
         "runsum": "replace each element by the total of itself and all elements before it, mod 2^24", "sort": "arrange the elements in increasing order"}
    return (B if v == "B" else C)[k]


RED_B = {"sum": "the sum of the elements modulo 2^24 (0 if empty)", "count": "the length of the list", "max": "the largest element in the list (0 if empty)",
         "min": "the minimum element (16777215 if empty)", "xor": "the XOR of all elements (0 if empty)", "first": "the head of the list (0 if empty)",
         "last": "the final element (0 if empty)", "cntgtfirst": "the count of elements strictly larger than the head (0 if empty)"}
RED_C = {"sum": "the elements added together, mod 2^24 (an empty list gives 0)", "count": "the number of elements left",
         "max": "the biggest element, or 0 when the list is empty", "min": "the least element, or 16777215 when the list is empty",
         "xor": "all elements combined with bitwise xor, or 0 when the list is empty", "first": "the element at index 0, or 0 when the list is empty",
         "last": "the element at the end, or 0 when the list is empty", "cntgtfirst": "how many later elements beat the first one (0 when the list is empty)"}


def aug_desc(p, r):
    st, rd = gold(p); a_lines = [l.split(". ", 1)[1] for l in p.desc.splitlines() if __import__("re").match(r"\d+\. ", l)]
    words = [a if (v := r.choice("ABC")) == "A" else _wb(s, v) for s, a in zip(st, a_lines)]
    fr = r.choice("ABC")
    if fr == "A":
        if not words: return p.desc
        return "Start with the input list. Apply these steps in order:\n" + "\n".join(f"{i + 1}. {w}" for i, w in enumerate(words)) + "\n" + p.desc.splitlines()[-1]
    red = None if rd is None else (RED_B if fr == "B" else RED_C)[rd[0]]
    if fr == "B":
        if not words: return f"Given a list of u24 numbers, return {red}."
        return "Given a list of u24 numbers, transform it step by step:\n" + "\n".join(f"({i + 1}) {w}" for i, w in enumerate(words)) + (
            "\nReturn the final list." if red is None else f"\nThen return {red}.")
    if not words: return f"The answer is {red} of the input list."
    return "Process the input list with this pipeline: " + "; then ".join(words) + (". The answer is the resulting list." if red is None else f". The answer is {red}.")


def build_aug():
    out = os.path.join(OUT, "data_aug"); os.makedirs(out, exist_ok=True)
    train = json.load(open(os.path.join(OUT, "sets", "train.json")))
    for name, specs in (("train", train[:N_TRAIN]), ("valid", train[N_TRAIN:])):
        with open(os.path.join(out, f"{name}.jsonl"), "w") as f:
            for i, s in enumerate(specs):
                p = load_task(s); st, rd = gold(p); p.desc = aug_desc(p, _r("aug", name, i))
                f.write(json.dumps({"messages": [{"role": "user", "content": prompt_stage(p)}, {"role": "assistant", "content": to_text(st, rd)}]}) + "\n")
    print("aug written")


if __name__ == "__main__":
    {"novel": build_novel, "aug": build_aug}.get((sys.argv[1:] or [""])[0], build)()
