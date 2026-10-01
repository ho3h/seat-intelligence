"""Vocabulary inducer (Lane B). Mines recurring subnets across accepted programs and promotes them to coined words.

A word is an ordinary HVM2 definition, so every word lowers to the physics by plain expansion and correctness never
depends on the vocabulary. A subtree S of a definition whose outside wires (and reference leaves) are E1..Ek becomes
  @w = (P1 (P2 ... (Pk r0)))   &  r0 ~ S[Ei := Pi]
and each occurrence is replaced by a fresh wire r with the call  `& @w ~ (E1 (E2 ... (Ek r)))`.
Names are opaque hashes assigned by the machine. Nothing here is human-named or human-designed.
"""
from __future__ import annotations
import hashlib
from collections import defaultdict
from .netast import parse_book, print_book, show, size, var_counts, tokens

MIN_SIZE, MAX_SIZE, MAX_PORTS, MIN_PROGRAMS, MIN_OCC = 4, 60, 7, 3, 3
KIDS = ("con", "dup", "opr", "swi")


def _walk(t, path=()):
    yield path, t
    if t[0] in KIDS:
        yield from _walk(t[1], path + (1,))
        yield from _walk(t[2], path + (2,))


def _get(t, path):
    for i in path: t = t[i]
    return t


def _put(t, path, new):
    if not path: return new
    i = path[0]
    kids = list(t); kids[i] = _put(t[i], path[1:], new); return tuple(kids)


def canon(sub, whole_counts):
    """-> (canonical string, ports) or None. ports: list of ('var', name) / ('ref', name) leaves in DFS order."""
    sub_counts = var_counts(sub)
    for v, c in sub_counts.items():
        if whole_counts.get(v, 0) - c < 0: return None
        if whole_counts.get(v, 0) == 1: return None  # dangling wire
    refs = defaultdict(int)
    def scan(t):
        if t[0] == "ref": refs[t[1]] += 1
        elif t[0] in KIDS: scan(t[1]); scan(t[2])
    scan(sub)
    ports, ivars, out = [], {}, []
    def go(t):
        k = t[0]
        if k in KIDS:
            out.append({"con": "(", "dup": "{", "opr": "$(", "swi": "?("}[k]); go(t[1]); out.append(" "); go(t[2])
            out.append({"con": ")", "dup": "}", "opr": ")", "swi": ")"}[k])
        elif k == "era": out.append("*")
        elif k == "num": out.append(t[1])
        elif k == "ref":
            if refs[t[1]] == 1:
                out.append(f"P{len(ports)}"); ports.append(t)
            else: out.append("@" + t[1])
        else:  # var
            if sub_counts[t[1]] == 2:
                out.append(f"i{ivars.setdefault(t[1], len(ivars))}")
            else:
                out.append(f"P{len(ports)}"); ports.append(t)
    go(sub)
    return "".join(out), ports


def mine(programs):
    """programs: {pid: (defs, order)} -> candidate table {canon: [(pid, defname, where, path, ports)]}"""
    table = defaultdict(list)
    for pid, (defs, order) in programs.items():
        for dn in order:
            root, reds = defs[dn]
            trees = [("root", -1, root)] + [(s, i, r[1 if s == "L" else 2]) for i, r in enumerate(reds) for s in ("L", "R")]
            whole = {}
            for _, _, t in trees: var_counts(t, whole)
            for where, idx, t in trees:
                for path, sub in _walk(t):
                    if sub[0] not in KIDS: continue
                    n = size(sub)
                    if n < MIN_SIZE or n > MAX_SIZE: continue
                    c = canon(sub, whole)
                    if c is None or len(c[1]) > MAX_PORTS or len(c[1]) == 0: continue
                    table[c[0]].append((pid, dn, where, idx, path, c[1], n))
    return table


def _tok(s): return len(tokens(s))


def choose(table):
    best, best_gain = None, 0
    for c, occ in table.items():
        progs = {o[0] for o in occ}
        if len(progs) < MIN_PROGRAMS or len(occ) < MIN_OCC: continue
        n, k = occ[0][6], len(occ[0][5])
        frag_tok = _tok(c.replace("P", "v").replace("i", "u"))
        call_tok = 4 + 2 * k
        # non-overlapping estimate: count occurrences as is (overlaps are dropped when applied)
        gain = len(occ) * (frag_tok - call_tok) - (frag_tok + 2 * k + 8)
        if gain > best_gain: best, best_gain = c, gain
    return best, best_gain


def word_name(c): return "w" + hashlib.sha256(c.encode()).hexdigest()[:7]


def apply_word(programs, c, occ, lib, stats):
    """Rewrite every non-overlapping occurrence of canonical form c. Returns number replaced."""
    name = word_name(c)
    by_loc = defaultdict(list)
    for o in occ: by_loc[(o[0], o[1], o[2], o[3])].append(o)
    replaced = 0; defined = False
    for (pid, dn, where, idx), items in by_loc.items():
        defs, order = programs[pid]
        root, reds = defs[dn]
        reds = list(reds)
        # apply deepest/last first is unnecessary: choose non-overlapping by path prefix, replace right-to-left
        items.sort(key=lambda o: o[4])
        chosen = []
        for o in items:
            if all(not (o[4][:len(p[4])] == p[4] or p[4][:len(o[4])] == o[4]) for p in chosen): chosen.append(o)
        for o in reversed(chosen):
            t = root if where == "root" else reds[idx][1 if where == "L" else 2]
            sub = _get(t, o[4]); ports = o[5]
            if not defined:
                # build the word definition from this occurrence
                pvars = [("var", f"p{j}") for j in range(len(ports))]
                body = _subst_ports(sub, ports, pvars)
                r0 = ("var", "r0")
                tree = r0
                for pv in reversed(pvars): tree = ("con", pv, tree)
                lib[name] = (tree, [(False, r0, _rename_internal(body, keep={"r0"} | {v[1] for v in pvars}))])
                defined = True; stats["size"][name] = size(sub); stats["ports"][name] = len(ports)
            fresh = ("var", f"{name}_{stats['n']}"); stats["n"] += 1
            args = fresh
            for p in reversed(ports): args = ("con", p, args)
            newt = _put(t, o[4], fresh)
            if where == "root": root = newt
            else:
                i = idx; par, a, b = reds[i]
                reds[i] = (par, newt, b) if where == "L" else (par, a, newt)
            reds.append((False, ("ref", name), args))
            replaced += 1; stats["mass"][name] = stats["mass"].get(name, 0) + size(sub)
        defs[dn] = (root, reds)
    return replaced


def _subst_ports(sub, ports, pvars):
    it = iter(zip(ports, pvars)); pend = {}
    seq = list(zip(ports, pvars)); pos = [0]
    def go(t):
        k = t[0]
        if k in KIDS: return (k, go(t[1]), go(t[2]))
        if k in ("var", "ref") and pos[0] < len(seq) and seq[pos[0]][0] == t:
            pv = seq[pos[0]][1]; pos[0] += 1; return pv
        return t
    return go(sub)


def _rename_internal(t, keep=()):
    m = {}
    def go(x):
        k = x[0]
        if k in KIDS: return (k, go(x[1]), go(x[2]))
        if k == "var" and x[1] not in keep:
            return ("var", m.setdefault(x[1], f"q{len(m)}"))
        return x
    return go(t)


def induce(nets: dict, max_words: int = 40):
    """nets: {pid: book_text}. -> (rewritten {pid: book_text}, library book_text, stats)"""
    programs = {pid: parse_book(t) for pid, t in nets.items()}
    lib, stats = {}, {"n": 0, "size": {}, "ports": {}, "mass": {}, "words": []}
    total_nodes = sum(size(r[0]) + sum(size(a) + size(b) for _, a, b in r[1]) for d, o in programs.values() for r in d.values())
    for _ in range(max_words):
        table = mine(programs)
        c, gain = choose(table)
        if c is None: break
        n = apply_word(programs, c, table[c], lib, stats)
        stats["words"].append((word_name(c), n, gain)); stats.setdefault("canon", {})[word_name(c)] = c
    out = {pid: print_book(d, o) for pid, (d, o) in programs.items()}
    libtxt = print_book(lib, list(lib)) if lib else ""
    stats["total_nodes"] = total_nodes
    return out, libtxt, stats


def lower(book_text: str, lib_text: str) -> str:
    """Expand every coined-word call back into the base physics. A call `& @w ~ (E1 (E2 ... (Ek r)))` becomes the link
    `& r ~ S[Pi := Ei]` with the word's internal wires renamed fresh. Exact: same net as before promotion."""
    defs, order = parse_book(book_text)
    lib, _ = parse_book(lib_text) if lib_text.strip() else ({}, [])
    counter = [0]

    def subst(t, m):
        k = t[0]
        if k in KIDS: return (k, subst(t[1], m), subst(t[2], m))
        if k == "var" and t[1] in m: return m[t[1]]
        return t

    def expand(name, args):
        root, reds = lib[name]
        # root = (p0 (p1 ... (pk-1 r0))); args = [E0..Ek-1, r]
        m = {}; node = root; i = 0
        while node[0] == "con":
            m[node[1][1]] = args[i]; i += 1; node = node[2]
        r0 = node[1]; m[r0] = args[i]
        body = reds[0][2]
        counter[0] += 1
        ren = {}
        def fresh(t):
            k = t[0]
            if k in KIDS: return (k, fresh(t[1]), fresh(t[2]))
            if k == "var" and t[1] not in m:
                return ("var", ren.setdefault(t[1], f"{t[1]}_x{counter[0]}"))
            return t
        return _subst_all(fresh(body), m)

    def _subst_all(t, m): return subst(t, m)

    for dn in order:
        root, reds = defs[dn]; new = []
        for par, a, b in reds:
            if a[0] == "ref" and a[1] in lib and b[0] == "con":
                args, node = [], b
                while node[0] == "con": args.append(node[1]); node = node[2]
                args.append(node)
                new.append((par, args[-1], expand(a[1], args)))
            else: new.append((par, a, b))
        defs[dn] = (root, new)
    return print_book(defs, order)


def apply_vocab(nets: dict, canons: dict):
    """Rewrite unseen nets with an already-learned vocabulary {word_name: canonical_form}. -> (rewritten, library_text, stats)"""
    programs = {pid: parse_book(t) for pid, t in nets.items()}
    lib, stats = {}, {"n": 0, "size": {}, "ports": {}, "mass": {}, "words": []}
    total = sum(size(r[0]) + sum(size(a) + size(b) for _, a, b in r[1]) for d, o in programs.values() for r in d.values())
    for name, c in canons.items():
        table = mine(programs)
        occ = table.get(c)
        if not occ: continue
        n = apply_word(programs, c, occ, lib, stats)
        stats["words"].append((name, n, 0))
    out = {pid: print_book(d, o) for pid, (d, o) in programs.items()}
    stats["total_nodes"] = total
    return out, (print_book(lib, list(lib)) if lib else ""), stats
