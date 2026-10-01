"""HERO-2 demonstration: equivalence certificates for seating-stage pipelines (docs/HERO-2.md s.6).

Guest record = (company, category, key, alive, hint), five u24 fields. Stages are BRANCH-FREE per-guest words (a "filter" is a mask stage
that multiplies `alive` by a 0/1 test, a "group" stage writes the group key from the company); a single shared `compact` step at the end
drops guests whose `alive` is 0. A pipeline is compiled into ONE list walker whose per-guest body applies the stages in order
(map-fusion by construction). Two pipelines are compared by normalization with the interface (guest list in, seating out) left open.
All of this is a game about the host's rules; company and category are the printed fields of data/hero/luncheon.json (no opinions)."""
from __future__ import annotations
import hashlib, json, random, sys, os
from genome.hero2.prove import Prover
from genome.hero2.corpus import Case
from genome.hero2.harness import sample_pair
from genome.types import u24, list_of, tup, encode, decode
from genome.executor import run_net

REC = tup(u24, u24, u24, u24, u24)
LREC = list_of(REC)
GOV = 5  # category code of "government" in this demo's coding (see CATS)
CATS = ["ai_lab", "big_tech", "chips", "software_security", "investor", "government", "unlabelled"]


# ------------------------------------------------------------------------------------------ stage words (fragment builders)
def _f(w, n):
    return {k: f"{k}{n}" for k in w}


def st_group(w, n):          # key := company % 5              (reads co, writes key)
    a, b, k2 = f"co{n}a", f"co{n}b", f"key{n}"
    return ([f"  & {w['co']} ~ {{{a} {b}}}", f"  & {a} ~ $([%] $(5 {k2}))", f"  & {w['key']} ~ *"], {**w, "co": b, "key": k2})


def _mask(w, n, field, op, const):
    a, b, ok, al = f"{field}{n}a", f"{field}{n}b", f"ok{n}", f"alive{n}"
    return ([f"  & {w[field]} ~ {{{a} {b}}}", f"  & {a} ~ $([{op}] $({const} {ok}))", f"  & {w['alive']} ~ $([*] $({ok} {al}))"],
            {**w, field: b, "alive": al})


def st_mask_gov(w, n): return _mask(w, n, "cat", "!", GOV)       # alive *= (category != government)    (reads cat, alive)
def st_mask_bigco(w, n): return _mask(w, n, "co", "<", 50)         # alive *= (company < 50)              (reads co, alive)
def st_mask_key0(w, n): return _mask(w, n, "key", "!", 0)          # alive *= (key != 0)                  (reads key, alive)


def st_bump(w, n):           # company := company + 101       (reads and writes co)
    c2 = f"co{n}"
    return ([f"  & {w['co']} ~ $([+101] {c2})"], {**w, "co": c2})


def st_hint(w, n):           # hint := company * 3             (reads co, writes hint)
    a, b, h2 = f"co{n}a", f"co{n}b", f"hint{n}"
    return ([f"  & {w['co']} ~ {{{a} {b}}}", f"  & {a} ~ $([*3] {h2})", f"  & {w['hint']} ~ *"], {**w, "co": b, "hint": h2})


STAGES = {"hint": st_hint, "group": st_group, "mask_gov": st_mask_gov, "mask_bigco": st_mask_bigco, "mask_key0": st_mask_key0, "bump": st_bump}
DESC = {"group": "group key := company mod 5", "mask_gov": "mask out government guests", "mask_bigco": "mask out companies >= 50",
        "mask_key0": "mask out group key 0", "bump": "company := company + 101", "hint": "hint := company * 3"}


def chain_lines(stages):
    w = {"co": "co0", "cat": "cat0", "key": "key0", "alive": "alive0", "hint": "hint0"}
    lines = []
    for i, s in enumerate(stages, 1):
        ls, w = STAGES[s](w, i)
        lines += ls
    return lines, w


def fused_net(stages) -> str:
    lines, w = chain_lines(stages)
    return "\n".join([
        "@prog = (l out)", "  & @walk ~ (l out)", "",
        "@walk = ((?((@w_nil @w_cons) (pl out)) pl) out)", "@w_nil = (* (0 *))",
        "@w_cons = (* ((h t) out))", "  & h ~ (co0 (cat0 (key0 (alive0 hint0))))", *lines,
        f"  & {w['alive']} ~ ?((@w_drop @w_keep) ({w['co']} ({w['cat']} ({w['key']} ({w['hint']} (t out))))))",
        "@w_drop = (co (cat (key (hint (t out)))))", "  & co ~ *", "  & cat ~ *", "  & key ~ *", "  & hint ~ *", "  & @walk ~ (t out)",
        "@w_keep = (* (co (cat (key (hint (t out))))))", "  & out ~ (1 (rec tl))", "  & rec ~ (co (cat (key (1 hint))))", "  & @walk ~ (t tl)", ""])


def unfused_net(stages) -> str:
    """one list pass per stage, then the shared compact pass"""
    out = ["@prog = (l out)"]
    prev = "l"
    for i in range(len(stages)):
        out.append(f"  & @pass{i} ~ ({prev} m{i})"); prev = f"m{i}"
    out += [f"  & @compact ~ ({prev} out)", ""]
    for i, s in enumerate(stages):
        ls, w = STAGES[s]({"co": "co0", "cat": "cat0", "key": "key0", "alive": "alive0", "hint": "hint0"}, 1)
        out += [f"@pass{i} = ((?((@p{i}_nil @p{i}_cons) (pl out)) pl) out)", f"@p{i}_nil = (* (0 *))",
                f"@p{i}_cons = (* ((h t) out))", "  & h ~ (co0 (cat0 (key0 (alive0 hint0))))", *ls,
                "  & out ~ (1 (rec tl))", f"  & rec ~ ({w['co']} ({w['cat']} ({w['key']} ({w['alive']} {w['hint']}))))", f"  & @pass{i} ~ (t tl)", ""]
    out += ["@compact = ((?((@c_nil @c_cons) (pl out)) pl) out)", "@c_nil = (* (0 *))", "@c_cons = (* ((h t) out))",
            "  & h ~ (co (cat (key (alive hint))))", "  & alive ~ ?((@c_drop @c_keep) (co (cat (key (hint (t out))))))",
            "@c_drop = (co (cat (key (hint (t out)))))", "  & co ~ *", "  & cat ~ *", "  & key ~ *", "  & hint ~ *", "  & @compact ~ (t out)",
            "@c_keep = (* (co (cat (key (hint (t out))))))", "  & out ~ (1 (rec tl))", "  & rec ~ (co (cat (key (1 hint))))", "  & @compact ~ (t tl)", ""]
    return "\n".join(out)


# ------------------------------------------------------------------------------------------ python model (independent of the nets)
def py_stage(s, r):
    co, cat, key, al, hint = r
    M = (1 << 24) - 1
    if s == "group": key = co % 5
    elif s == "mask_gov": al = (al * (cat != GOV)) & M
    elif s == "mask_bigco": al = (al * (co < 50)) & M
    elif s == "mask_key0": al = (al * (key != 0)) & M
    elif s == "bump": co = (co + 101) & M
    elif s == "hint": hint = (co * 3) & M
    return (co, cat, key, al, hint)


def py_pipeline(stages, guests):
    out = []
    for g in guests:
        r = g
        for s in stages: r = py_stage(s, r)
        if r[3] != 0: out.append((r[0], r[1], r[2], 1, r[4]))
    return out


def gen_guests(rng, n=None):
    n = rng.choice([0, 1, 2, 3, 5, 8, 13, 20]) if n is None else n
    return [(rng.choice([rng.randrange(0, 120), rng.randrange(0, 1 << 24), 0, 49, 50]), rng.randrange(0, 7), rng.randrange(0, 9),
             rng.choice([1, 1, 1, 0, 2]), rng.randrange(0, 50)) for _ in range(n)]


def run_pipeline(net_text, guests):
    root, defs = encode(guests, LREC)
    r = run_net(f"@main = r\n  & @prog ~ ({root} r)\n\n" + "\n".join(defs) + "\n\n" + net_text, "run", 60)
    return decode(r.result, LREC) if r.ok else ("ERR", r.error[:100])


def check_model(stages, n=150, seed=1):
    """the compiled nets really compute the python model (so the demo is about the intended pipeline)"""
    rng = random.Random(seed)
    bad = 0
    for compile_ in (fused_net, unfused_net):
        text = compile_(stages)
        for _ in range(n):
            g = gen_guests(rng)
            if run_pipeline(text, g) != py_pipeline(stages, g): bad += 1
    return bad


def load_chart():
    d = json.load(open("data/hero/luncheon.json"))
    orgs = sorted({s["org"] for s in d["seats"] if s["org"]})
    guests, labels = [], []
    for s in d["seats"]:
        co = (orgs.index(s["org"]) + 1) if s["org"] else 0
        guests.append((co, CATS.index(s["category"]), 0, 1, 0))
        labels.append(f"{s['side']}{s['row']:>2} {s['name']} ({s['org'] or '-'}, {s['category']})")
    return d, orgs, guests, labels


# ------------------------------------------------------------------------------------------ certificate
def certificate(stagesA, stagesB, compile_=fused_net, n=300, seed=5):
    A, B = compile_(stagesA), compile_(stagesB)
    rng = random.Random(seed)
    agree = dis = 0; wit = None
    for _ in range(n):
        g = gen_guests(rng)
        a, b = run_pipeline(A, g), run_pipeline(B, g)
        if a == b: agree += 1
        else:
            dis += 1
            if wit is None or len(g) < len(wit[0]): wit = (g, a, b)
    pr = Prover(A, B)
    v = pr.prove()
    circuit = ""
    if v.equal:
        from genome.hero2 import inet as I
        tn = {"S": (False, True, False), "S~a": (False, False, False), "U": (True, True, False), "U~a": (True, False, False), "D": (True, False, True)}[v.tier]
        _, nf, _, _ = pr.normalize(*tn)
        for key in ("A:w_cons", "A:p0_cons"):
            if key in nf:
                net = nf[key]
                ops = sorted(o for o in (I.show_numb(net.val[net.p[i][1] // 3]) for i, k in enumerate(net.kind)
                             if k == "O" and net.p[i][1] >= 0 and net.kind[net.p[i][1] // 3] == "N") if o.startswith("["))
                cnt = I.ncount(net)
                circuit = (f"per-guest body (identical on both sides): operators {ops}, {cnt.get('D', 0)} copy nodes, "
                           f"{cnt.get('S', 0)} switch (on the alive flag), {cnt.get('E', 0)} erasers")
                break
    pl = lambda st: " ; ".join(st) if st else "(nothing)"
    head = "PROVED EQUAL" if v.equal else ("REFUTED (counterexample found)" if dis else "NO PROOF FOUND (they agree on every sample, which is evidence, not proof)")
    L = ["=" * 78, f"CERTIFICATE   {head}",
         f"  pipeline A : {pl(stagesA)}", f"  pipeline B : {pl(stagesB)}"]
    for s_ in dict.fromkeys(stagesA + stagesB): L.append(f"      {s_:11s}= {DESC[s_]}")
    L.append(f"      compact    = keep guests whose alive flag is nonzero (shared last step)   [compiled as: {compile_.__name__}]")
    if v.equal:
        L.append(f"  verdict    : equal for EVERY guest list (any length) and EVERY field value  [tier {v.tier}]")
        L.append("  how        : both nets normalised by the HVM2 rewrite rules with the interface (guest list in, seating out) left open;")
        L.append("               the residual nets are isomorphic (fingerprint %s)" % v.stats.get("code_sha256"))
        if circuit: L.append("               " + circuit)
        L.append(f"               {v.stats['defs']} definitions in {v.stats['classes']} classes; residual {sum(v.stats['residA'].values())} / {sum(v.stats['residB'].values())} nodes; "
                 f"{v.stats['itrsA']} / {v.stats['itrsB']} interactions spent")
        L.append("  assumption : " + {"S": "none beyond HVM2's own rewrite rules (exact)",
              "S~a": "neither net aborts with the 'clone a non-affine reference' error",
              "U": "reference unfolding (argued, not machine-checked)",
              "U~a": "reference unfolding and no non-affine-clone abort",
              "D": "the values that get copied are plain numbers (a duplicator never meets a duplicator); true for encoded guest records"}[v.tier])
        L.append("  not shown  : that either pipeline is the right seating rule; only that A and B are the same program.")
    elif dis:
        L.append(f"  verdict    : NOT equal: {dis}/{n} random guest lists give different seatings")
        g, a, b = wit
        L.append(f"  smallest   : guests {g}")
        L.append(f"               A -> {a}")
        L.append(f"               B -> {b}")
    else:
        L.append(f"  verdict    : no proof ({v.reason}); {agree}/{n} random guest lists agree on the real runtime")
    L.append(f"  executor   : {agree}/{n} random guest lists agree between A and B on the real HVM2 runtime")
    L.append("=" * 78)
    return v, agree, dis, "\n".join(L)


def main():
    out = {}
    text = []
    os.makedirs("runs/hero2", exist_ok=True)
    print("model check (fused and unfused nets vs python model):")
    for st in (["group", "mask_gov"], ["mask_gov", "group"], ["group", "mask_gov", "hint"], ["group", "mask_key0"], ["bump", "group"]):
        print("  ", st, "mismatches:", check_model(st, 60), flush=True)
    demos = [
        ("H1 group ; filter  vs  filter ; group (should commute)", ["group", "mask_gov"], ["mask_gov", "group"], fused_net),
        ("H2 three independent stages in a different order (should commute)", ["group", "mask_gov", "hint"], ["hint", "group", "mask_gov"], fused_net),
        ("H3 the filter reads the group key (should NOT commute)", ["group", "mask_key0"], ["mask_key0", "group"], fused_net),
        ("H4 the group key is made from a company that another stage changes (should NOT commute)", ["bump", "group"], ["group", "bump"], fused_net),
        ("H5 two filters, other order (equal, but needs commutativity of *, which normalization does not know)", ["mask_gov", "mask_bigco"], ["mask_bigco", "mask_gov"], fused_net),
        ("H6 as H1 but one list pass per stage (equal, but needs loop fusion, out of reach)", ["group", "mask_gov"], ["mask_gov", "group"], unfused_net),
    ]
    for title, a, b, comp in demos:
        v, agree, dis, cert = certificate(a, b, comp, n=300)
        print(f"\n### {title}\n{cert}", flush=True)
        text.append(f"### {title}\n{cert}\n")
        out[title] = {"proved": v.equal, "tier": v.tier, "reason": v.reason, "agree": agree, "disagree": dis, "stats": v.stats}
    d, orgs, guests, labels = load_chart()
    print(f"\n### real chart: {d['n']} seats, {len(orgs)} printed organisations")
    res = {}
    for name, st in (("group;mask_gov", ["group", "mask_gov"]), ("mask_gov;group", ["mask_gov", "group"])):
        res[name] = run_pipeline(fused_net(st), guests)
    same = res["group;mask_gov"] == res["mask_gov;group"]
    kept = len(res["group;mask_gov"]) if isinstance(res["group;mask_gov"], list) else None
    print(f"   group;mask_gov and mask_gov;group give the same seating on the real chart: {same}; {kept} of {d['n']} guests kept (non-government)")
    out["real_chart"] = {"n": d["n"], "same": same, "kept": kept}
    json.dump(out, open("runs/hero2/hero.json", "w"), indent=1)
    open("runs/hero2/certificates.txt", "w").write("\n".join(text))


if __name__ == "__main__":
    main()
