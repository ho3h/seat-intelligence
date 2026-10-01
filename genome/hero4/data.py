"""HERO-4 data: training prompts for the BASE-only tuning, the frozen test sets, and text rendering from templates.

  python3 -m genome.hero4.data build     -> runs/hero4/data/{train,valid}.jsonl (base only, alias names), runs/hero4/sets/*.json
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import hashlib, json, os, random, re, sys
from genome.hero4 import tasks as T, lang, refs
from genome.hero4.refs import BASE_WORDS, NEW_WORDS

ROOT = _REPO
SETS = f"{ROOT}/runs/hero4/sets"
DATA = f"{ROOT}/runs/hero4/data"
NUMW = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
HOLD = 8      # last 8 templates of each kind (per writer) are held out of training and used only for the iid test set

KIND_TMPL = {"group_company": "group_company", "group_category": "group_category", "spread": "spread", "order_rank": "order_rank",
             "order_rankdesc": "order_rankdesc", "order_category": "order_category", "order_company": "order_company"}


def num(rng, v):
    return NUMW[v] if (v <= 10 and rng.random() < 0.3) else str(v)


def listphrase(rng, names, kind):
    ph = [rng.choice(lang.CAT_SURFACE[n]) if kind == "cat" else lang.co_surface(n) for n in names]
    if len(ph) == 1: return ph[0]
    style = rng.choice(["then", "gt", "and", "first"])
    if style == "then": return ", then ".join(ph)
    if style == "gt": return " > ".join(ph)
    if style == "and": return ", ".join(ph[:-1]) + " and then " + ph[-1]
    return ", ".join(f"{p} {['first', 'second', 'third', 'fourth'][i]}" for i, p in enumerate(ph))


def load_templates(train):
    """-> {kind: [templates]} from writers A and B; train=True excludes the held-out tail of each writer's list"""
    out = {}
    for w in ("A", "B"):
        d = json.load(open(f"{SETS}/tmpl_out_base_{w}.json"))
        for k, v in d.items():
            v = v[:-HOLD] if train else v[-HOLD:]
            out.setdefault(k, []).extend(v)
    return out


def render_item(it, rng, tm):
    k = it["kind"]; t = rng.choice(tm[k])
    if k == "order_category": return t.replace("{LIST}", listphrase(rng, it["names"], "cat"))
    if k == "order_company": return t.replace("{LIST}", listphrase(rng, it["names"], "co"))
    return t


def render_closing(c, rng, tm):
    return rng.choice(tm[c["kind"]]).replace("{S}", num(rng, c["S"]))


def render_task(task, rng, tm):
    sents = [render_item(it, rng, tm) for it in task["items"]]
    c = render_closing(task["closing"], rng, tm)
    r = rng.random()
    if r < 0.2: sents = [c] + sents
    elif r < 0.3 and len(sents) >= 2: sents.insert(1, c)
    else: sents = sents + [c]
    return " ".join(sents)


def rand_base_task(rng, tid):
    n = rng.choices([0, 1, 2, 3], weights=[10, 40, 35, 15])[0]
    kinds = rng.sample(T.BASE_EXTRA, n)
    items = [T.rand_item(k, rng) for k in kinds]
    c = T.rand_closing(rng, p_captains=0.3)
    return {"id": tid, "family": "train", "items": items, "closing": c}


def make_example(task, text, rng, available=None, names=None, order=None):
    available = available or BASE_WORDS
    if names is None: names = lang.sample_names(rng, [w for w in available if w in lang.ALIASES])
    if order is None:
        order = list(available); rng.shuffle(order)
    prompt = lang.prompt(text, available, names, order)
    inv = {v: k for k, v in names.items()}
    lines = []
    for w in T.gold(task):
        line = lang.fmt_word(w); head, _, rest = line.partition(" ")
        lines.append((names.get(head, head) + (" " + rest if rest else "")))
    return prompt, "\n".join(lines), names


def build_train(n=6000, seed=1):
    rng = random.Random(seed); tm = load_templates(True); rows = []
    for i in range(n + 150):
        t = rand_base_task(rng, f"tr_{i}")
        text = render_task(t, rng, tm)
        prompt, target, names = make_example(t, text, rng)
        rows.append({"messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": target}], "prog": lang.to_text(T.gold(t))})
    return rows[:n], rows[n:]


def build_iid(seed=77):
    """5 x 30 base tasks whose text comes from the HELD-OUT templates (same params space, unseen templates)"""
    rng = random.Random(seed); tm = load_templates(False); out = []
    for f in ["group", "spread", "order", "sections", "captains"]:
        for t in T.base_family_tasks(f, 30, rng, tag="iid"):
            t["text"] = render_task(t, rng, tm); out.append(t)
    return out


def merge_test():
    specs = json.load(open(f"{SETS}/test_specs.json")); text = {}
    for i in range(5): text.update(json.load(open(f"{SETS}/writer_out_{i}.json")))
    out = []
    for t in specs:
        t = dict(t); t["text"] = text[t["id"]].strip(); out.append(t)
    return out


def check_numbers(t):
    """every number in the gold program must appear in the text (digit or word form); returns missing list"""
    txt = t["text"].lower(); miss = []
    nums = set()
    for w in T.gold(t):
        for a in w[1:]:
            if isinstance(a, int): nums.add(a)
    for v in nums:
        ok = re.search(rf"(?<!\d){v}(?!\d)", txt) or (v <= 10 and NUMW[v] in txt) or (v == 1 and ("single" in txt or "one" in txt or "a " in txt))
        if not ok: miss.append(v)
    return miss


def sha(obj): return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()


if __name__ == "__main__":
    if sys.argv[1] == "build":
        os.makedirs(DATA, exist_ok=True)
        tr, va = build_train()
        with open(f"{DATA}/train.jsonl", "w") as f:
            for r in tr: f.write(json.dumps({"messages": r["messages"]}) + "\n")
        with open(f"{DATA}/valid.jsonl", "w") as f:
            for r in va: f.write(json.dumps({"messages": r["messages"]}) + "\n")
        iid = build_iid(); test = merge_test()
        bad = [(t["id"], check_numbers(t)) for t in test if check_numbers(t)]
        print("train", len(tr), "valid", len(va), "iid", len(iid), "test", len(test), "texts missing a number:", len(bad), bad[:10])
        json.dump(iid, open(f"{SETS}/iid_base.json", "w"), indent=1)
        json.dump(test, open(f"{SETS}/test_final.json", "w"), indent=1)
        print("sha256 test_final", sha(test)); print("sha256 iid_base", sha(iid))
        progs = {r["prog"] for r in tr}
        print("distinct train programs", len(progs))


# ------------------------------------------------------------------ variants: ablation (constant names) and control (retrain with new words)
def render_new_item(it, rng, tnew):
    k = it["kind"]; t = rng.choice(tnew[k])
    cs = lambda c: rng.choice(lang.CAT_SURFACE[c])
    rep = {}
    if k in ("limit", "waitlist"): rep = {"{CAT}": cs(it["cat"]), "{K}": num(rng, it["k"]), "{S}": num(rng, it.get("S", 0))}
    elif k == "pair": rep = {"{CAT2}": cs(it["b"]), "{CAT}": cs(it["a"])}
    elif k == "apart": rep = {"{CO2}": lang.co_surface(it["y"]), "{CO}": lang.co_surface(it["x"])}
    elif k == "vip": rep = {"{R}": str(it["R"])}
    elif k == "stagger": rep = {"{M}": num(rng, it["m"])}
    elif k in ("snake", "sectionlead"): rep = {"{S}": num(rng, it["S"])}
    for a, b in rep.items(): t = t.replace(a, b)
    return t


def build_train_const(n=6000, seed=1):
    """ABLATION: identical tasks and texts, but shown names are always the canonical names (no alias training)"""
    rng = random.Random(seed); tm = load_templates(True); rows = []
    for i in range(n):
        t = rand_base_task(rng, f"tr_{i}"); text = render_task(t, rng, tm)
        names = {w: w for w in BASE_WORDS}
        prompt, target, _ = make_example(t, text, rng, names=names, order=list(BASE_WORDS))
        rows.append({"messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": target}]})
    return rows


def build_train_retrain(n=6000, seed=2):
    """CONTROL: the ten new words are in the training data (25 templates each from a third writer) and in the block"""
    rng = random.Random(seed); tm = load_templates(True); tnew = json.load(open(f"{SETS}/tmpl_out_new.json")); rows = []
    allw = BASE_WORDS + NEW_WORDS
    for i in range(n):
        if rng.random() < 0.55:
            w = rng.choice(NEW_WORDS); it = T.rand_item(w, rng); items = [it]
            for b in rng.sample(T.BASE_EXTRA, rng.choice([0, 0, 1, 1, 2])): items.insert(rng.randrange(len(items) + 1), T.rand_item(b, rng))
            c = T.rand_closing(rng, 0.3)
            if w in ("limit", "snake", "sectionlead"): c["S"] = it["S"]
            t = {"id": f"rt_{i}", "family": w, "items": items, "closing": c}
            sents = [render_new_item(x, rng, tnew) if x["kind"] in NEW_WORDS else render_item(x, rng, tm) for x in items]
            cs = render_closing(c, rng, tm); sents = sents + [cs] if rng.random() < 0.8 else [cs] + sents
            text = " ".join(sents)
        else:
            t = rand_base_task(rng, f"rt_{i}"); text = render_task(t, rng, tm)
        prompt, target, _ = make_example(t, text, rng, available=allw)
        rows.append({"messages": [{"role": "user", "content": prompt}, {"role": "assistant", "content": target}]})
    return rows


def write_jsonl(rows, d, valid=150):
    os.makedirs(d, exist_ok=True)
    with open(f"{d}/train.jsonl", "w") as f:
        for r in rows[:-valid]: f.write(json.dumps({"messages": r["messages"]}) + "\n")
    with open(f"{d}/valid.jsonl", "w") as f:
        for r in rows[-valid:]: f.write(json.dumps({"messages": r["messages"]}) + "\n")


if __name__ == "__main__" and sys.argv[1] == "variants":
    write_jsonl(build_train_const(6150), f"{ROOT}/runs/hero4/data_const")
    write_jsonl(build_train_retrain(6150), f"{ROOT}/runs/hero4/data_retrain")
    print("variants written")
