"""Swing 27 comparison tables: Bend (runs/exp21/results.jsonl) vs native (runs/exp16/*.log for the depth oracle, and the
same-session native reruns in runs/exp21/native_rerun.jsonl for the C runtime). The latest record per key wins.
usage: python3 -m genome.exp21.report [K]"""
import json, math, os, sys, glob
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NS = [2000, 8000, 32000, 100000]


def load(paths):
    out = []
    for p in paths:
        if not os.path.exists(p): continue
        for l in open(p):
            l = l.strip()
            if l.startswith("{"):
                try: out.append(json.loads(l))
                except json.JSONDecodeError: pass
    return out


def pick(recs, **kw):
    r = [x for x in recs if all(x.get(k) == v for k, v in kw.items())]
    return r[-1] if r else None


def expo(a, b, na, nb):
    return math.log(b / a) / math.log(nb / na) if a and b else float("nan")


def fmt(x, d=0):
    return "-" if x is None else f"{x:,.{d}f}"


def ratio(a, b):
    return "-" if not a or not b else f"{a / b:.2f}x"


def g(r, k):
    return r.get(k) if r else None


def main():
    K = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    bend = load([os.path.join(ROOT, "runs/exp21/results.jsonl")])
    nat = [x for x in load(glob.glob(os.path.join(ROOT, "runs/exp16/*.log"))) if x.get("depth") or x.get("mode") != "depth"]
    rer = load([os.path.join(ROOT, "runs/exp21/native_rerun.jsonl")])
    crep = load([os.path.join(ROOT, "runs/exp21/crepeat.jsonl")])

    def cstats(arm, var, N):
        """C runtime: all runs of this arm/program/N (matrix, timing reruns, crepeat). -> (min, median, runs, wrong, hung, rss)"""
        if arm == "bend":
            rs = [(x["rt_secs"], x["correct"], False, x.get("max_rss_mb")) for x in bend
                  if x.get("var") == var and x.get("k") == K and x.get("mode") == "native" and x.get("N") == N]
        else:
            rs = [(x["rt_secs"], x["correct"], False, x.get("max_rss_mb")) for x in rer if x.get("net") == var and x.get("N") == N]
        rs += [(x["rt_secs"], x["correct"], x["hung"], None) for x in crep if x["arm"] == arm and x["var"] == var and x["N"] == N]
        ok = sorted(t for t, c, h, r in rs if c and t is not None)
        if not ok: return None
        return (ok[0], ok[len(ok) // 2] if len(ok) % 2 else (ok[len(ok) // 2 - 1] + ok[len(ok) // 2]) / 2, len(rs),
                sum(1 for t, c, h, r in rs if not c and not h), sum(1 for t, c, h, r in rs if h), max(r for t, c, h, r in rs if r))

    def ncount(recs, **kw):
        return len([x for x in recs if all(x.get(k) == v for k, v in kw.items())])

    for bvar, nvar in (("recon_cps", "fan"), ("full", "full")):
        dvar = "full_sumout" if bvar == "full" else bvar
        print(f"\n### Bend `{bvar}` (K={K}) vs native `{nvar}` (same slices, same input text)\n")
        if bvar == "full":
            print("Bend depth / interactions are for the program with its output folded to one number inside Bend "
                  "(genome/exp21/sumout.py; see the text); the bare-output figure is in brackets.\n")
        print("| N | depth Bend / native | ratio | interactions Bend / native (oracle) | ratio | C runtime s, min / median: Bend; native "
              "| C runs (wrong, hung): Bend; native | peak RSS MB Bend / native (C) | Rust interp s Bend / native | exact Bend: Rust / oracle+digest |")
        print("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        rows = []
        for N in NS:
            bd = pick(bend, var=dvar, k=K, mode="depth", N=N)
            bb = pick(bend, var=bvar, k=K, mode="depth", N=N)
            bdd = pick(bend, var=bvar, k=K, mode="depthd", N=N)
            nd = pick(nat, net=nvar, mode="depth", N=N)
            br = pick(bend, var=bvar, k=K, mode="rust", N=N)
            bs, ns = cstats("bend", bvar, N), cstats("native", nvar, N)
            nr = pick(nat, net=nvar, mode="rust", N=N)
            rows.append((N, g(bd, "depth"), g(nd, "depth"), g(bd, "itrs"), g(nd, "itrs"), bs and bs[0], ns and ns[0]))
            bare = f" [{fmt(g(bb,'depth'))}]" if bvar == "full" else ""
            cs = lambda x: "-" if not x else f"{x[0]:.2f} / {x[1]:.2f}"
            cr = lambda x: "-" if not x else f"{x[2]} ({x[3]}, {x[4]})"
            print(f"| {N:,} | {fmt(g(bd,'depth'))}{bare} / {fmt(g(nd,'depth'))} | {ratio(g(bd,'depth'), g(nd,'depth'))} | "
                  f"{fmt(g(bd,'itrs'))} / {fmt(g(nd,'itrs'))} | {ratio(g(bd,'itrs'), g(nd,'itrs'))} | "
                  f"{cs(bs)}; {cs(ns)} | {cr(bs)}; {cr(ns)} | {fmt(bs and bs[5])} / {fmt(ns and ns[5])} | "
                  f"{fmt(g(br,'rt_secs'),2)} / {fmt(g(nr,'rt_secs'),2)} | {g(br,'correct')} / {g(bdd,'correct') if bdd else '-'} |")
        full = [r for r in rows if all(r[1:5])]
        if len(full) >= 2:
            a, b = full[0], full[-1]
            print(f"\nExponents {a[0]:,} -> {b[0]:,}: depth Bend {expo(a[1], b[1], a[0], b[0]):.2f}, native {expo(a[2], b[2], a[0], b[0]):.2f}; "
                  f"interactions Bend {expo(a[3], b[3], a[0], b[0]):.2f}, native {expo(a[4], b[4], a[0], b[0]):.2f}")
            if all(r[5] and r[6] for r in (a, b)):
                print(f"C runtime min seconds: Bend {expo(a[5], b[5], a[0], b[0]):.2f}, native {expo(a[6], b[6], a[0], b[0]):.2f}")
    print("\n### Bend iterations (depth / interactions on the oracle, K=4 unless noted; K=-1 = setup and output only)\n")
    print("| N | recon (plain ropes, list flags) | recon_bal (weight-balanced ropes) | recon_cps (+ CPS flag streams) | recon_cps setup only (K=-1 on recon) |")
    print("| --- | --- | --- | --- | --- |")
    for N in NS:
        cells = []
        for v in ("recon", "recon_bal", "recon_cps"):
            r = pick(bend, var=v, k=K, mode="depth", N=N)
            cells.append(f"{r['depth']:,} / {r['itrs']/1e6:.1f}M" if r else "-")
        r = pick(bend, var="recon", k=-1, mode="depth", N=N)
        cells.append(f"{r['depth']:,} / {r['itrs']/1e6:.1f}M" if r else "-")
        print(f"| {N:,} | " + " | ".join(cells) + " |")
    print("\n### K sweep, recon_cps (depth / interactions)\n")
    for N in NS:
        cells = []
        for kk in sorted({x["k"] for x in bend if x.get("var") == "recon_cps" and x.get("mode") == "depth"}):
            r = pick(bend, var="recon_cps", k=kk, mode="depth", N=N)
            if r and r.get("depth"): cells.append(f"K={kk}: {r['depth']:,} / {r['itrs']/1e6:.1f}M")
        if cells: print(f"- N={N:,}: " + "; ".join(cells))


if __name__ == "__main__":
    main()
