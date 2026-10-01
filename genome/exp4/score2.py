"""Step 2 scoring: LM skeleton samples (genome.exp.sample output) -> wiring model -> genome.verify (seed 0, 10 s).

  <venv python> -m genome.exp4.score2 runs/exp4/skel_iid.json --ckpt runs/exp4/wire.pt
Per sample: noblock | badskel (unparseable or odd blank count in a definition) | static | fail | pass. Writes <file>.scored.json in the
genome.exp.score format so genome.exp.metrics.summarize / paired work unchanged.
"""
import argparse, collections, json, os, sys
from concurrent.futures import ThreadPoolExecutor
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); os.chdir(ROOT)
from genome.netast import parse_book, print_book
from genome.exp4.skel import refill, n_slots
from genome.exp4 import wire as W
from genome.exp.score import extract, reason_class
from genome.taskgen import task
from genome.verify import verify


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--ckpt", default="runs/exp4/wire.pt")
    ap.add_argument("--method", default="model", choices=["model", "hybrid"])
    ap.add_argument("--repair", action="store_true", help="odd-blank definitions: the matcher leaves its weakest slot unmatched, which becomes `*`")
    a = ap.parse_args()
    L = None
    if a.method == "hybrid":
        from genome.exp4.evalwire import build_lookup, lookup
        L = build_lookup([r for r in json.load(open("runs/exp4/dataset.json")) if r["split"] in ("train", "dev")])
    d = json.load(open(a.file)); progs = {task(f, i).id: task(f, i) for f, i in d["tasks"]}
    model, V, dev = W.load(a.ckpt, device="cpu")
    books = {}
    for pid, texts in d["samples"].items():
        for j, txt in enumerate(texts):
            sk = extract(txt)
            if not sk: books[(pid, j)] = {"status": "noblock"}; continue
            try:
                defs, order = parse_book(sk)
                odd = [n for n in order if n_slots(defs[n]) % 2]
                if odd and not a.repair: books[(pid, j)] = {"status": "badskel", "why": f"odd blanks in @{odd[0]}"}; continue
                M = W.predict(model, V, dev, defs, order)
                if L is not None:
                    for n in order:
                        lk = lookup(L, defs[n])
                        if lk and n_slots(defs[n]) % 2 == 0 and max((max(p) for p in lk), default=-1) < n_slots(defs[n]): M[n] = lk
                books[(pid, j)] = {"book": print_book(refill(defs, order, M, erase_unmatched=a.repair), order), "repaired": bool(odd)}
            except Exception as e:
                books[(pid, j)] = {"status": "badskel", "why": repr(e)[:120]}
    def one(key):
        x = books[key]
        if "book" not in x: return key, x
        from genome.verify import check_book
        from genome.exp4.evalwire import quick_reject
        bad = check_book(x["book"])
        if bad: return key, {"status": "static", "cls": reason_class(bad), "why": bad[:300]}
        if quick_reject(progs[key[0]], x["book"]): return key, {"status": "fail", "why": "quick pre-screen: wrong on an early small case", "net": x["book"]}
        r = verify(progs[key[0]], x["book"], seed=0, timeout=10.0, workers=4)
        if r["status"] == "pass": return key, {"status": "pass", "net": x["book"], "repaired": x.get("repaired")}
        if r["status"] == "reject": return key, {"status": "static", "cls": reason_class(r["reason"]), "why": r["reason"][:300]}
        return key, {"status": "fail", "why": r["counterexample"]["why"][:120], "net": x["book"]}
    res = {}
    with ThreadPoolExecutor(6) as ex:
        for k, v in ex.map(one, list(books)): res[k] = v
    out = {pid: [res[(pid, j)] for j in range(len(texts))] for pid, texts in d["samples"].items()}
    sp = a.file.replace(".json", f".{a.method}{'.repair' if a.repair else ''}.scored.json")
    json.dump({"meta": d["meta"], "tasks": d["tasks"], "scored": out}, open(sp, "w"))
    from genome.exp.metrics import summarize
    print(json.dumps(summarize(sp), indent=1)); print(collections.Counter(s["status"] for v in out.values() for s in v))


if __name__ == "__main__": main()
