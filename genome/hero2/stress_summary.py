import json, glob, collections
rows = [json.loads(l) for f in sorted(glob.glob("runs/hero2/stress_*.jsonl")) for l in open(f)]
print("candidates:", len(rows), "programs:", len({r["pid"] for r in rows}))
c = collections.Counter()
for r in rows:
    op = r["op"].split("#")[0]
    truth = "differs" if r["disagree"] else "equal-on-samples"
    c[(op, "proved" if r["proved"] else "unproved", truth)] += 1
ops = sorted({k[0] for k in c})
print(f"{'operator':16s} {'n':>4s} {'proved&equal':>13s} {'FALSE PROOF':>12s} {'unproved&equal':>15s} {'unproved&differs':>17s}")
tot = collections.Counter()
for op in ops:
    pe = c[(op, "proved", "equal-on-samples")]; pd = c[(op, "proved", "differs")]
    ue = c[(op, "unproved", "equal-on-samples")]; ud = c[(op, "unproved", "differs")]
    n = pe + pd + ue + ud
    print(f"{op:16s} {n:4d} {pe:13d} {pd:12d} {ue:15d} {ud:17d}")
    tot.update({"n": n, "pe": pe, "pd": pd, "ue": ue, "ud": ud})
print(f"{'ALL':16s} {tot['n']:4d} {tot['pe']:13d} {tot['pd']:12d} {tot['ue']:15d} {tot['ud']:17d}")
eq = tot["pe"] + tot["ue"]
print(f"of the {eq} candidates that agree with the original on every sample, the normalizer proved {tot['pe']} ({100*tot['pe']/max(eq,1):.0f}%); "
      f"of the {tot['ud']+tot['pd']} that the executor separates, it proved {tot['pd']}")
print("tiers of proofs:", collections.Counter(r["tier"] for r in rows if r["proved"]))
print("proved-candidate inputs: min", min((r["n"] for r in rows if r["proved"]), default=None))
print("equal-but-unproved by op:", collections.Counter(r["op"].split("#")[0] for r in rows if not r["proved"] and not r["disagree"]))
