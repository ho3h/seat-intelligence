"""Stage 3: tables for docs/HERO-5.md.  usage: python3 -m genome.hero5.report <set.json> <tracedir> <results.jsonl> <out.md>"""
import sys, json, os, statistics as st
from collections import Counter, defaultdict
from .run_eval import load_problem
from .evalx import Oracle, greedy_log

METHODS = ["T-D", "T-F", "T-F+G", "T-F+DD", "T-F+DDc", "DD", "DDc", "LOO", "G-full"]
CLS = ["exact", "over-inclusive", "incomplete", "wrong"]
KINDS = ["MERGE", "MNL", "CAP", "ORDER"]


def order_sensitive(pr, dec, E):
    """For a refusal: does swapping the subject's processing position with one edge of E flip D in the E-alone world?"""
    if dec["polarity"] != "refused": return None
    orc = Oracle(pr, dec, use_net=False)
    x, a, b = orc.world(E)
    n, cap, mnl, edges = x
    subj = [i for i, e in enumerate(edges) if (e[0], e[1]) == (a, b)][0]
    order = sorted(range(len(edges)), key=lambda i: (-edges[i][2], edges[i][0], edges[i][1]))
    def run(order):
        p = {}; mem = {}
        def find(z):
            while p.get(z, z) != z: z = p[z]
            return z
        res = {}
        for i in order:
            u, v, _ = edges[i]; ra, rb = find(u), find(v)
            if ra == rb: res[i] = "noop"; continue
            A, B = mem.get(ra, {ra}), mem.get(rb, {rb})
            if any((q in A and r in B) or (q in B and r in A) for q, r in mnl) or len(A) + len(B) > cap: res[i] = "skip"; continue
            res[i] = "merge"; p[ra] = rb; mem[rb] = A | B; mem.pop(ra, None)
        return res
    base = run(order)[subj]
    for j in range(len(edges)):
        if j == subj: continue
        o2 = list(order); i1, i2 = o2.index(subj), o2.index(j); o2[i1], o2[i2] = o2[i2], o2[i1]
        if run(o2)[subj] != base: return True
    return False


def main(setpath, tracedir, resp, outp):
    o = json.load(open(setpath))
    rows = [json.loads(l) for l in open(resp)]
    decs = {d["id"]: d for d in o["decisions"]}
    by = defaultdict(dict)
    for r in rows: by[r["method"]][r["id"]] = r
    L = []
    def pct(a, b): return f"{a}/{b} ({100 * a / b:.0f}%)" if b else "0/0"
    hero = lambda i: decs[i]["src"].startswith("hero")

    L.append("### Class counts, all 100 decisions (denominator 100; hero 50 + synthetic 50)\n")
    L.append("| method | exact | over-inclusive | incomplete | wrong | exact, hero /50 | exact, synthetic /50 | exact but F not required (S,N,M only) |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
    for m in METHODS:
        rs = list(by[m].values()); c = Counter(r["cls"] for r in rs)
        eh = sum(1 for r in rs if r["cls"] == "exact" and hero(r["id"])); es = sum(1 for r in rs if r["cls"] == "exact" and not hero(r["id"]))
        lit = sum(1 for r in rs if r.get("S") and r.get("N") and r.get("M"))
        L.append(f"| {m} | " + " | ".join(str(c.get(k, 0)) for k in CLS) + f" | {eh} | {es} | {lit} |")
    L.append("")
    L.append("### Exact per decision type (exact / decisions of that type)\n")
    L.append("| method | " + " | ".join(KINDS) + " |"); L.append("| --- |" + " --- |" * len(KINDS))
    for m in METHODS:
        cells = []
        for k in KINDS:
            rs = [r for r in by[m].values() if r["kind"] == k]
            cells.append(pct(sum(1 for r in rs if r["cls"] == "exact"), len(rs)))
        L.append(f"| {m} | " + " | ".join(cells) + " |")
    L.append("")
    L.append("### Full class breakdown per decision type\n")
    for m in METHODS:
        L.append(f"**{m}**: " + "; ".join(
            f"{k} " + "/".join(str(Counter(r['cls'] for r in by[m].values() if r['kind'] == k).get(c, 0)) for c in CLS)
            for k in KINDS) + "   (order: exact/over-inclusive/incomplete/wrong)\n")
    # explanation sizes
    L.append("### Explanation size (facts named, subject excluded): median [min, max]\n")
    L.append("| method | hero | synthetic |"); L.append("| --- | --- | --- |")
    for m in METHODS:
        h = [r["size"] for r in by[m].values() if hero(r["id"])]; s = [r["size"] for r in by[m].values() if not hero(r["id"])]
        L.append(f"| {m} | {st.median(h):.0f} [{min(h)}, {max(h)}] | {st.median(s):.0f} [{min(s)}, {max(s)}] |")
    L.append("")
    # exact explanation sizes for the exact ones
    ex = [r["size"] for r in by["DDc"].values() if r["cls"] == "exact"]
    # full-input necessity
    L.append("### Full-input necessity diagnostic (facts of E that flip D when deleted from the untouched input)\n")
    L.append("| method | exact explanations with every fact necessary in the full input | share of facts necessary in the full input (exact explanations) |")
    L.append("| --- | --- | --- |")
    for m in METHODS:
        rs = [r for r in by[m].values() if r["cls"] == "exact" and r.get("N_full")]
        if not rs: L.append(f"| {m} | - | - |"); continue
        allnec = sum(1 for r in rs if r["N_full"][0] == r["N_full"][1]); a = sum(r["N_full"][0] for r in rs); b = sum(r["N_full"][1] for r in rs)
        L.append(f"| {m} | {pct(allnec, len(rs))} | {pct(a, b)} |")
    L.append("")
    # cost
    L.append("### Cost of producing the explanation (executor calls and wall clock; classification checks excluded)\n")
    L.append("| method | net runs per decision, hero median [max] | net runs per decision, synthetic median [max] | executor wall s (replayed sample of every 5th decision), hero median | same, synthetic median |")
    L.append("| --- | --- | --- | --- | --- |")
    for m in METHODS:
        h = [r["cost"]["net_calls"] for r in by[m].values() if hero(r["id"])]; s = [r["cost"]["net_calls"] for r in by[m].values() if not hero(r["id"])]
        hw = [r["cost"].get("net_replay_secs") for r in by[m].values() if hero(r["id"]) and r["cost"].get("net_replay_secs") is not None] or [0]
        sw = [r["cost"].get("net_replay_secs") for r in by[m].values() if not hero(r["id"]) and r["cost"].get("net_replay_secs") is not None] or [0]
        L.append(f"| {m} | {st.median(h):.0f} [{max(h)}] | {st.median(s):.0f} [{max(s)}] | {st.median(hw):.1f} | {st.median(sw):.1f} |")
    L.append("")
    chk = sum(r["check_calls"] for rs in by.values() for r in rs.values())
    mm = sum(r["check_mismatch"] for rs in by.values() for r in rs.values())
    rep = sum(r["cost"].get("net_replay_calls", 0) for rs in by.values() for r in rs.values())
    srch = sum(r["cost"]["net_calls"] for rs in by.values() for r in rs.values())
    L.append(f"Executor runs used to classify the explanations (sufficiency, every single-fact deletion, faithfulness): {chk}; each decoded "
             f"and compared with the reference implementation: {mm} disagreements. Executor runs used to replay the search sequences of the "
             f"timing sample: {rep}. Search queries answered by the reference implementation: {srch}.\n")
    # order sensitivity of exact ORDER explanations
    L.append("### Order sensitivity of exact explanations of refusals (swap the subject with one edge of E in the E-alone world)\n")
    for m in ["G-full", "DDc"]:
        for kind in ["MNL", "CAP", "ORDER"]:
            tot = ok = 0
            for r in by[m].values():
                if r["cls"] == "exact" and r["polarity"] == "refused" and r["kind"] == kind and "E" in r:
                    d = decs[r["id"]]; pr = load_problem(o, d["src"])
                    v = order_sensitive(pr, d, set(r["E"]))
                    if v is not None: tot += 1; ok += bool(v)
            L.append(f"* {m}, {kind}: {pct(ok, tot)} of the exact explanations flip when the subject swaps priority with one of their edges.")
    L.append("")
    # unfaithful DD witnesses
    L.append("### Explanations that were sufficient but unfaithful (class wrong because F failed)\n")
    for m in ["DD", "T-F+DD"]:
        for r in by[m].values():
            if r["cls"] == "wrong":
                d = decs[r["id"]]; pr = load_problem(o, d["src"])
                good = by["DDc"][r["id"]]
                L.append(f"* {m} on decision {r['id']} ({r['src']} {r['kind']}, records {d['a']} and {d['b']}): returned facts {r.get('E')} "
                         f"({[pr.edges[k][:3] if k < pr.E else ('MNL', pr.mnl[k - pr.E]) if k < pr.E + pr.M else 'cap' for k in r.get('E', [])]}); "
                         f"D holds with only these rows, but not once the must-not-link rows and the cap that really exist are put back. "
                         f"Context-preserving DD returned {good.get('E')}.")
    L.append("")
    # tracing overhead
    L.append("### Tracing overhead (depth oracle vs the traced copy; same annotated book)\n")
    L.append("| problem | facts | untraced itrs / depth | traced itrs / depth | untraced oracle s | traced F s | traced D s | ratio F | ratio D | distinct sets F | unions F (memo hit %) |")
    L.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    tot = defaultdict(list)
    for tag in sorted({d["src"] for d in o["decisions"]}):
        t = json.load(open(os.path.join(tracedir, tag + ".json")))
        u = t["same_book_depth"]; f = t["mode2"]["stats"]; d_ = t["mode1"]["stats"]
        rf = f["wall"] / u["wall"]; rd = d_["wall"] / u["wall"]
        tot["F"].append(rf); tot["D"].append(rd)
        assert f["itrs"] == u["itrs"] and f["depth"] == u["depth"] and d_["itrs"] == u["itrs"], tag
        L.append(f"| {tag} | {t['F']} | {u['itrs']:,} / {u['depth']:,} | {f['itrs']:,} / {f['depth']:,} | {u['wall']:.1f} | {f['wall']:.1f} | {d_['wall']:.1f} | {rf:.2f} | {rd:.2f} | {f['tsets']:,} | {f['tunions']:,} ({100 * f['tmemohits'] / max(1, f['tunions']):.1f}) |")
    L.append("")
    L.append(f"Wall-clock ratio traced/untraced: policy F median {st.median(tot['F']):.2f} (range {min(tot['F']):.2f}-{max(tot['F']):.2f}); policy D median {st.median(tot['D']):.2f} (range {min(tot['D']):.2f}-{max(tot['D']):.2f}).\n")
    # causal set sizes
    L.append("### What the trace says (causal set sizes)\n")
    fsz = []; dsz = []
    for d in o["decisions"]:
        t = json.load(open(os.path.join(tracedir, d["src"] + ".json")))
        pr = load_problem(o, d["src"])
        a, b = str(d["a"]), str(d["b"])
        fsz.append((len(set(t["mode2"]["sets"][a]) | set(t["mode2"]["sets"][b])), pr.F))
        dsz.append(len(set(t["mode1"]["sets"][a]) | set(t["mode1"]["sets"][b])))
    L.append(f"* policy F: the causal set equals the whole input (every fact) for {sum(1 for x, y in fsz if x >= y - (1 if True else 0))} of {len(fsz)} decisions; median share of the input {st.median([x / y for x, y in fsz]):.2f}.")
    L.append(f"* policy D: empty for {sum(1 for x in dsz if x == 0)} of {len(dsz)} decisions; largest {max(dsz)}.")
    L.append("")
    # example sentences (re-rendered from the stored fact sets with the final renderer)
    from .evalx import extract, render
    L.append("### Example sentences (T-F+G, all exact; these are outputs of a game with the host's rules, not claims about the guests)\n")
    seen = Counter()
    for r in sorted(by["T-F+G"].values(), key=lambda r: r["id"]):
        want = 2 if r["src"].startswith("hero") else 1
        key = (r["src"][:4], r["kind"])
        if r["cls"] == "exact" and seen[key] < want:
            d = decs[r["id"]]; pr = load_problem(o, d["src"])
            E_, why, roles = extract(pr, d, set(range(pr.F)) - ({d["subject"]} if d["subject"] is not None else set()))
            seen[key] += 1; L.append(f"* [{r['src']} {r['kind']}, {len(E_)} facts] {render(pr, d, E_, roles)}")
    L.append("")
    open(outp, "w").write("\n".join(L))
    print("\n".join(L))


if __name__ == "__main__":
    main(*sys.argv[1:5])
