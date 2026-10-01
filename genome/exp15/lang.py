"""exp15 stage language: the text a model emits instead of a net. One verified parametric word per line (the words are the
exp13 net templates, genome/exp13/words.py, unit-tested through genome.verify: 65/65 instances pass seeds 0-1).

  map lin 3 7        x*3+7 (mod 2^24)        filter gt 5         take 3      reverse     runsum    runmax    diff
  map xor 255 | map and 15 | map add 9       filter lt 10        drop 2      dedup       sort      runmin
  map sq | map mod 6 | map div 3             filter ge 3 | filter even | filter odd | filter modeq 3 1     runxor
  map ind gt 20      (predicate as 0/1)
  reduce sum|count|max|min|xor|first|last|cntgtfirst|argmax      reduce idxfirst|idxlast|idxsum <pred>

A program is zero or more list stages, optionally ended by one `reduce` line. `assemble` lowers it to ONE net with the fixed glue
of genome/compose.py (exp13.words.net_program); nothing is trusted, the assembled net is verified by genome.verify.
"""
from __future__ import annotations
import re
from genome.types import u24
from genome.contract import describe

PRED0 = {"even", "odd"}; PRED1 = {"gt", "lt", "ge"}
EXPR1 = {"xor", "and", "add", "mod", "div"}
STAGE0 = {"reverse", "dedup", "runsum", "sort", "runmax", "runmin", "runxor", "diff"}
RED0 = {"sum", "count", "max", "min", "xor", "first", "last", "cntgtfirst", "argmax"}
REDP = {"idxfirst", "idxlast", "idxsum"}
MAXV = (1 << 24) - 1


class ParseError(ValueError):
    pass


def fmt(t):
    return " ".join(fmt(a) if isinstance(a, tuple) else str(a) for a in t)


def to_text(stages, reducer=None):
    lines = [fmt(s) for s in stages] + (["reduce " + fmt(reducer)] if reducer else [])
    return "\n".join(lines) if lines else "id"


def _int(tok, lo=0):
    if not re.fullmatch(r"\d+", tok): raise ParseError(f"not a number: {tok}")
    v = int(tok)
    if not lo <= v <= MAXV: raise ParseError(f"out of range: {v}")
    return v


def _pred(toks):
    if not toks: raise ParseError("missing predicate")
    k = toks[0]
    if k in PRED0 and len(toks) == 1: return (k,)
    if k in PRED1 and len(toks) == 2: return (k, _int(toks[1]))
    if k == "modeq" and len(toks) == 3:
        m = _int(toks[1], 1); return (k, m, _int(toks[2]))
    raise ParseError(f"bad predicate: {' '.join(toks)}")


def _expr(toks):
    if not toks: raise ParseError("missing expression")
    k = toks[0]
    if k == "sq" and len(toks) == 1: return (k,)
    if k == "lin" and len(toks) == 3: return (k, _int(toks[1]), _int(toks[2]))
    if k in EXPR1 and len(toks) == 2: return (k, _int(toks[1], 1 if k in ("mod", "div") else 0))
    if k == "ind": return (k, _pred(toks[1:]))
    raise ParseError(f"bad expression: {' '.join(toks)}")


def parse(text):
    """-> (stages, reducer or None). Raises ParseError. Tolerates code fences and blank lines, nothing else."""
    lines = [l.strip() for l in text.strip().splitlines()]
    lines = [l for l in lines if l and not l.startswith("```")]
    if lines == ["id"]: return [], None
    if not lines: raise ParseError("empty")
    stages, red = [], None
    for i, l in enumerate(lines):
        toks = l.split()
        if red is not None: raise ParseError("stage after reduce")
        w = toks[0]
        if w == "map": stages.append(("map", _expr(toks[1:])))
        elif w == "filter": stages.append(("filter", _pred(toks[1:])))
        elif w in ("take", "drop") and len(toks) == 2: stages.append((w, _int(toks[1])))
        elif w in STAGE0 and len(toks) == 1: stages.append((w,))
        elif w == "reduce" and len(toks) >= 2:
            r = toks[1]
            if r in RED0 and len(toks) == 2: red = (r,)
            elif r in REDP: red = (r, _pred(toks[2:]))
            else: raise ParseError(f"bad reducer: {l}")
        else: raise ParseError(f"unknown word: {l}")
    return stages, red


def assemble(stages, reducer=None):
    from genome.exp13.words import net_program
    return net_program(stages, reducer)


HEADER = ("Write a stage program that solves the task below. A stage program is a sequence of verified words, one per line; "
          "it is compiled to a net by fixed composition.\n\n")
FORMAT = "\n## Reply format\n\nReply with the stage program only, one word per line.\n"


def prompt_stage(p):
    """prompt_short-style: task text and types only (no primer, no vocabulary list, no task id)."""
    return HEADER + f"## Task\n\n{p.desc}\n\n- Input type:  `{describe(p.inp)}`\n- Output type: `{describe(p.out)}`\n" + FORMAT


VOCAB = """## Stage words (one per line; list stages run top to bottom, an optional final `reduce` turns the list into one number)

- `map E` replaces every element x by E(x). E is one of: `lin a b` (x*a+b mod 2^24), `xor m`, `and m`, `add c` (x+c mod 2^24),
  `sq` (x*x mod 2^24), `mod m` (x mod m), `div a` (x integer-divided by a), `ind P` (1 if P(x) else 0).
- `filter P` keeps the elements x with P(x). P is one of: `gt k` (x > k), `lt k` (x < k), `ge k` (x >= k), `even`, `odd`,
  `modeq m r` (x mod m equals r).
- `take k` keeps the first k elements; `drop k` removes the first k elements.
- `reverse`; `dedup` (collapse runs of equal consecutive elements); `runsum` (running totals mod 2^24); `sort` (ascending);
  `runmax`; `runmin`; `runxor`; `diff` (adjacent differences).
- `reduce R` with R one of: `sum` (mod 2^24, 0 if empty), `count`, `max` (0 if empty), `min` (16777215 if empty), `xor`,
  `first` (0 if empty), `last` (0 if empty), `cntgtfirst` (number of elements greater than the first), `argmax`,
  `idxfirst P`, `idxlast P`, `idxsum P`.

Example: "keep the numbers above 7, triple each one and add 1, then output their sum" is
```
filter gt 7
map lin 3 1
reduce sum
```

"""


def prompt_stage_vocab(p):
    """zero-shot control: the same prompt with the vocabulary documented (for an un-tuned instruct model)."""
    return HEADER + VOCAB + prompt_stage(p)[len(HEADER):]
