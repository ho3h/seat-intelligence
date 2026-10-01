"""Ground-truth shape of a generated task, parsed from its (deterministic) description, used ONLY for the coverage report
(the search never sees it). Returns (stages, reducer) in the word DSL, or (None, reason) when the library has no word for it.
CORE = the words named in the swing brief; EXT = CORE + scan/position words (runmax runmin runxor diff ind-map idx* argmax
cntgtfirst)."""
from __future__ import annotations
import re
from genome.exp13 import search as S

CORE_STAGES = {"map", "filter", "take", "drop", "reverse", "dedup", "runsum", "sort"}
CORE_RED = {"sum", "count", "max", "min", "xor", "first", "last"}


def _pred(d):
    d = d.strip()
    m = re.fullmatch(r"x (>|<|>=) (\d+)", d)
    if m: return ({">": "gt", "<": "lt", ">=": "ge"}[m.group(1)], int(m.group(2)))
    if d == "x is even": return ("even",)
    if d == "x is odd": return ("odd",)
    m = re.fullmatch(r"x mod (\d+) equals (\d+)", d)
    if m:
        mm, r = int(m.group(1)), int(m.group(2))
        return (("even",) if r == 0 else ("odd",)) if mm == 2 else ("modeq", mm, r)   # same predicate, canonical word
    raise ValueError(d)


def _expr(d):
    m = re.fullmatch(r"x\*(\d+)\+(\d+) \(mod 2\^24\)", d)
    if m: return ("lin", int(m.group(1)), int(m.group(2)))
    m = re.fullmatch(r"x (xor|and) (\d+)", d)
    if m: return (m.group(1), int(m.group(2)))
    m = re.fullmatch(r"x\+(\d+) \(mod 2\^24\)", d)
    if m: return ("add", int(m.group(1)))
    if d == "x*x (mod 2^24)": return ("sq",)
    m = re.fullmatch(r"x mod (\d+)", d)
    if m: return ("mod", int(m.group(1)))
    m = re.fullmatch(r"x integer-divided by (\d+)", d)
    if m: return ("div", int(m.group(1)))
    raise ValueError(d)


def _stage(d):
    if d.startswith("keep only the elements x for which "): return ("filter", _pred(d[len("keep only the elements x for which "):]))
    if d.startswith("replace every element x by "): return ("map", _expr(d[len("replace every element x by "):]))
    m = re.match(r"keep only the first (\d+) elements", d)
    if m: return ("take", int(m.group(1)))
    m = re.match(r"remove the first (\d+) elements", d)
    if m: return ("drop", int(m.group(1)))
    if d == "reverse the order": return ("reverse",)
    if d.startswith("collapse every run"): return ("dedup",)
    if d.startswith("replace the list by its running totals"): return ("runsum",)
    if d == "sort ascending": return ("sort",)
    raise ValueError(d)


RED_BY_DESC = {"the sum of all elements": "sum", "the number of elements that are greater": "cntgtfirst", "the number of elements": "count",
               "the largest element": "max", "the smallest element": "min", "the bitwise xor": "xor", "the last element": "last",
               "the first element": "first"}


def truth(p):
    fam = p.id.split("_")[1]; d = p.desc
    if fam in ("pipeline", "reduce"):
        stages = [_stage(line.split(". ", 1)[1]) for line in d.splitlines() if re.match(r"\d+\. ", line)]
        if fam == "pipeline": return stages, None
        last = d.splitlines()[-1]
        for k, v in RED_BY_DESC.items():
            if last.startswith("Output " + k): return stages, (v,)
        raise ValueError(last)
    if fam == "scan":
        if d.startswith("Output the running maximum"): return [("runmax",)], None
        if d.startswith("Output the running minimum"): return [("runmin",)], None
        if d.startswith("Output the list of differences"): return [("diff",)], None
        if d.startswith("Output the running bitwise xor"): return [("runxor",)], None
        m = re.search(r"satisfy: (.*) \(x is the element\)", d)
        return [("map", ("ind", _pred(m.group(1)))), ("runsum",)], None
    if fam == "position":
        if d.startswith("Output the index (counting from 0) of the first occurrence of the largest"): return [], ("argmax",)
        m = re.search(r"element x for which (.*); output", d)
        if d.startswith("Output the index (counting from 0) of the first element"): return [], ("idxfirst", _pred(m.group(1)))
        if d.startswith("Output the index (counting from 0) of the last element"): return [], ("idxlast", _pred(m.group(1)))
        m = re.search(r"elements x for which (.*?)(, mod 2\^24)?\.$", d)
        if d.startswith("Output the number of elements x"): return [("filter", _pred(m.group(1)))], ("count",)
        if d.startswith("Output the sum of the indices"): return [], ("idxsum", _pred(m.group(1)))
    raise ValueError(d)


def _in_grid(t):
    """is the term's hole inside the search grid?"""
    k = t[0]
    if k == "map": return t[1] in S.EXPRS
    if k == "filter": return t[1] in S.PREDS
    if k in ("take", "drop"): return t[1] in S.TAKES
    if k in ("idxfirst", "idxlast", "idxsum"): return t[1] in S.PREDS
    return True


def coverage(p):
    """-> dict(core, ext, in_search_space, shape)"""
    stages, red = truth(p)
    words = [s[0] if not (s[0] == "map" and s[1][0] == "ind") else "map_ind" for s in stages]
    core = all(w in CORE_STAGES for w in words) and (red is None or red[0] in CORE_RED)
    shape = "|".join(words + ([red[0]] if red else []))
    grid = all(_in_grid(s) for s in stages) and (red is None or _in_grid(red))
    n_ok = len(stages) <= 3 if red is None else (len(stages) <= 2 and (red[0] not in ("idxfirst", "idxlast", "idxsum") or len(stages) <= 1))
    return {"core": core, "ext": True, "in_space": grid and n_ok, "shape": shape, "truth": (stages, red)}
