"""exp8 results: verify every composed net on seeds 0,1,2 (3 worker processes), compare with the frozen author's
native and Bend nets (states combined exactly as genome/exp_quick.py does), count authoring lines.
usage: python3 runs/exp8/results.py  -> runs/exp8/results.json + a markdown table on stdout"""
import sys, os, json, glob, inspect
D = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, ROOT); sys.path.insert(0, D)
from genome.corpus import load_all
from genome.verify import verify
import build as B

ok = lambda s: s["accepted"] and s.get("audit") == ["pass", "pass"]


def layers(pats):
    out = {}
    for pat in pats:
        for f in glob.glob(os.path.join(ROOT, pat)):
            s = json.load(open(f))
            if s["pid"] not in out or (not ok(out[s["pid"]]) and ok(s)): out[s["pid"]] = s
    return out


NB = layers(["runs/g1/native/seed0/*/state.json", "runs/g1r1/native/seed0/*/state.json",
             "runs/probe2/dsv4/native/seed0/*/state.json", "runs/g1esc/native/seed0/*/state.json"])
BB = layers(["runs/g1/b1/seed0/*/state.json", "runs/g1r1/b1/seed0/*/state.json", "runs/g1esc/b1/seed0/*/state.json"])


def best(S, p):
    s = S.get(p)
    return s["best"] if s and ok(s) and s.get("best") else None


def authoring_lines(f):
    """Non-blank lines of the program function plus every module-level glue string/helper it uses (recursively)."""
    seen, total = set(), 0
    def walk(obj):
        nonlocal total
        src = inspect.getsource(obj) if callable(obj) else obj
        total += len([l for l in src.splitlines() if l.strip() and not l.strip().startswith("#")])
        if callable(obj):
            for name in obj.__code__.co_names:
                v = getattr(B, name, None)
                if name in seen or v is None or name in ("G", "Book", "K"): continue
                if isinstance(v, str) or (callable(v) and getattr(v, "__module__", "") == B.__name__):
                    seen.add(name); walk(v)
    walk(f)
    return total


def main():
    P = load_all(); res = {}
    for group, progs in (("main", B.PROGS), ("extra", B.EXTRAS)):
        for name, f in progs.items():
            book = open(os.path.join(D, name + ".hvm")).read()
            runs = {s: verify(P[name], book, s, 60.0, 3) for s in (0, 1, 2)}
            b = f(); nd, nl = b.size()
            res[name] = {"group": group, "status": {s: r["status"] for s, r in runs.items()}, "metrics0": runs[0].get("metrics"),
                         "prev_native": best(NB, name), "bend": best(BB, name), "authoring_lines": authoring_lines(f),
                         "net_defs": nd, "net_lines": nl}
            print(name, res[name]["status"], flush=True)
    json.dump(res, open(os.path.join(D, "results.json"), "w"), indent=1, default=str)
    fmt = lambda m: f"{m['depth_median_big']:,} / {m['itrs_median_big']:,}" if m else "no accepted net"
    for group in ("main", "extra"):
        print(f"\n| program | seeds 0-2 | authoring lines / emitted net lines | prev native depth / itrs | Bend depth / itrs | "
              f"**composed depth / itrs** | depth vs Bend | itrs vs Bend |\n|---|---|---|---|---|---|---|---|")
        for name, r in res.items():
            if r["group"] != group: continue
            m, bd = r["metrics0"], r["bend"]
            st = "pass" if all(v == "pass" for v in r["status"].values()) else str(r["status"])
            dr = f"{bd['depth_median_big'] / m['depth_median_big']:.1f}x shallower" if bd else "-"
            ir = (f"{bd['itrs_median_big'] / m['itrs_median_big']:.2f}x" if bd else "-")
            print(f"| {name} | {st} | {r['authoring_lines']} / {r['net_lines']} | {fmt(r['prev_native'])} | {fmt(bd)} | "
                  f"**{fmt(m)}** | {dr} | {ir} |")


if __name__ == "__main__":
    main()
