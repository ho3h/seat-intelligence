"""Collect verified nets, split by TASK, write runs/exp4/dataset.json.

  python3 -m genome.exp4.data
Sources: datagen best.hvm (accepted + audit clean), g1/g1r1/probe2/g1esc best.hvm (accepted + audit clean, one per pid),
g0 passing attempts, data/compose/verified.json. Test = 20% of datagen tasks (stratified by family, seed 0). Composed nets that
contain a test task's net as a stage are dropped (they would leak the test wiring).
"""
import glob, json, os, random, re, sys, ast, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT); os.chdir(ROOT)
from genome.netast import parse_book
from genome.exp4.skel import canon, roundtrip_ok
from genome.compose import _rename_refs

ok = lambda s: str(s.get("accepted")) == "True" and str(s.get("audit")) in ("['pass', 'pass']",) or (s.get("accepted") is True and s.get("audit") == ["pass", "pass"])


def fam(pid):
    return pid[4:].rsplit("_", 1)[0] if pid.startswith("gen_") else pid.split("_")[0]


def collect():
    rows = []
    for f in sorted(glob.glob("runs/datagen/native/seed0/*/state.json")):
        s = json.load(open(f)); b = os.path.join(os.path.dirname(f), "best.hvm")
        if ok(s) and os.path.exists(b): rows.append({"src": "datagen", "task": s["pid"], "fam": fam(s["pid"]), "net": open(b).read()})
    g1 = {}
    for pat in ["runs/g1/native/seed0/*/state.json", "runs/g1r1/native/seed0/*/state.json", "runs/probe2/*/native/seed0/*/state.json", "runs/g1esc/native/seed0/*/state.json"]:
        for f in glob.glob(pat):
            s = json.load(open(f)); b = os.path.join(os.path.dirname(f), "best.hvm")
            if ok(s) and os.path.exists(b) and s["pid"] not in g1: g1[s["pid"]] = open(b).read()
    for pid, net in sorted(g1.items()): rows.append({"src": "g1", "task": pid, "fam": "corpus_" + pid[:2], "net": net})
    for d in sorted(glob.glob("runs/g0/t*")):
        s = json.load(open(os.path.join(d, "state.json"))); pid = os.path.basename(d)
        if pid in g1 or not ok(s): continue
        att = ast.literal_eval(s["attempts"]) if isinstance(s["attempts"], str) else s["attempts"]
        k = next((i + 1 for i, a in enumerate(att) if a["status"] == "pass"), None)
        if k and os.path.exists(os.path.join(d, f"attempt_{k}.hvm")):
            rows.append({"src": "g0", "task": pid, "fam": "corpus_" + pid[:2], "net": open(os.path.join(d, f"attempt_{k}.hvm")).read()})
    for r in json.load(open("data/compose/verified.json")):
        rows.append({"src": "compose", "task": r["id"], "fam": "compose", "net": r["net"]})
    return rows


def components(net):
    defs, order = parse_book(net); comps = collections.defaultdict(dict)
    for n in order:
        m = re.match(r"c(\d+)_(.*)", n)
        if m: comps[m.group(1)][n] = defs[n]
    out = []
    for i, ds in comps.items():
        pre = f"c{i}_"; mp = {n: n[len(pre):] for n in ds}
        d2 = {mp[n]: (_rename_refs(r, mp), [(p, _rename_refs(a, mp), _rename_refs(b, mp)) for p, a, b in reds]) for n, (r, reds) in ds.items()}
        o2 = [mp[n] for n in order if n in ds]
        out.append(canon(d2, o2))
    return out


def main():
    rows = collect(); good = []
    bad = 0
    for r in rows:
        try:
            eq, _ = roundtrip_ok(r["net"])
            if not eq: bad += 1; continue
        except Exception as e:
            bad += 1; continue
        good.append(r)
    print("rows", len(rows), "round-trip ok", len(good), "failed", bad, collections.Counter(r["src"] for r in good))
    rng = random.Random(0)
    byfam = collections.defaultdict(list)
    for r in good:
        if r["src"] == "datagen": byfam[r["fam"]].append(r["task"])
    test = set()
    for f, ts in sorted(byfam.items()):
        ts = sorted(ts); rng.shuffle(ts); test |= set(ts[:max(1, round(0.2 * len(ts)))])
    test_canon = {canon(*parse_book(r["net"])) for r in good if r["task"] in test}
    dropped = 0
    for r in good:
        if r["src"] == "compose":
            if any(c in test_canon for c in components(r["net"])): r["split"] = "drop"; dropped += 1
            else: r["split"] = "train"
        else: r["split"] = "test" if r["task"] in test else "train"
    # dev: 10% of non-test datagen/g tasks for early stopping
    tr = sorted({r["task"] for r in good if r["split"] == "train" and r["src"] != "compose"}); rng.shuffle(tr)
    dev = set(tr[:len(tr) // 10])
    for r in good:
        if r["task"] in dev: r["split"] = "dev"
    print("compose dropped for leakage:", dropped, "splits:", collections.Counter(r["split"] for r in good))
    print("test by family:", collections.Counter(r["fam"] for r in good if r["split"] == "test"))
    os.makedirs("runs/exp4", exist_ok=True)
    json.dump([r for r in good if r["split"] != "drop"], open("runs/exp4/dataset.json", "w"))


if __name__ == "__main__": main()
