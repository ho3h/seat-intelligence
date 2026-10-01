"""aggregate runs/hero1/scale.jsonl -> markdown table + runs/hero1/scale_summary.json"""
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import json, statistics as st, collections
rows = [json.loads(l) for l in open(_REPO + "/runs/hero1/scale.jsonl")]
key = lambda r: (r["policy"], r["n"])
by = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows: by[key(r)][r["mode"]].append(r)
out = {}; lines = ["| policy | guests | sections | rule violations (independent checker) | net = Python reference | depth (rounds) | interactions (bare net) | C runtime seconds (3 runs: min / median / max) | book load (gen-c serialise, s) | host prep + Python ref (s) |", "|---|---|---|---|---|---|---|---|---|---|"]
for (p, n) in sorted(by):
    m = by[(p, n)]
    d = m["depth"][0]; nat = m["native"]
    rt = [x["rt_secs"] for x in nat]; ser = [x["serialise_secs"] for x in nat]
    exact = all(x["digest_ok"] for x in nat) and all(x["digest_ok"] for x in m.get("rust", [])) and all(x.get("exact_full_decode", True) for x in m.get("full", []))
    full = " + full decode" if m.get("full") else ""
    v = nat[0]["violations"]
    rec = dict(policy=p, n=n, sections=nat[0]["sections"], violations=v, exact=exact, depth=d["depth"], itrs_bare=d["itrs"], itrs_with_digest=nat[0]["itrs"],
               rt_min=min(rt), rt_median=st.median(rt), rt_max=max(rt), serialise_median=st.median(ser), prep=nat[0]["prep_secs"], py_ref=nat[0]["py_ref_secs"],
               native_runs=len(nat), full_decode=bool(m.get("full")))
    out[f"{p}_{n}"] = rec
    lines.append(f"| {p} | {n:,} | {rec['sections']:,} | {sum(v[k] for k in ('cap','limit','apart','together','order'))} | {'yes' if exact else 'NO'} (digest{full}) | {d['depth']:,} | {d['itrs']:,} | {min(rt):.2f} / {st.median(rt):.2f} / {max(rt):.2f} | {st.median(ser):.1f} | {rec['prep']:.2f} + {rec['py_ref']:.2f} |")
open(_REPO + "/runs/hero1/scale_summary.json", "w").write(json.dumps(out, indent=1))
print("\n".join(lines))
