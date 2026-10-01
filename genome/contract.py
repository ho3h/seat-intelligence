"""Builds the author prompt: primer + task contract. The template is frozen per gate."""
from __future__ import annotations
import os
from .corpus import Program
from .types import describe

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

HEADER = """You are an author in the Genome experiment. You write a net directly in HVM2's textual net IR.

Rules of this experiment:
- Use no tools beyond the one read that gave you this file. Do not read any other file, do not run anything, do not search. Answer from this prompt alone.
- Your submission must be a net. Do not submit Bend, Python, or pseudo-code as the answer. Your private reasoning is yours.
- After each submission you may receive feedback from a hidden test suite. Fix the net and resubmit the complete book.

"""

FORMAT = """
## Reply format

Reply with exactly one fenced code block containing your complete book of definitions (it must define `@prog`),
optionally preceded by a few words. Nothing after the code block.
"""


def _adt_note(p: Program) -> str:
    from .bend_io import bend_type_decls  # reuse the walker only for detecting variant types
    from .types import Adt, List, Tup
    found = []
    def walk(t):
        if isinstance(t, List): walk(t.elem)
        elif isinstance(t, Tup): [walk(e) for e in t.elems]
        elif isinstance(t, Adt) and t not in found:
            found.append(t)
            for c in t.ctors:
                for f in c: walk(f)
    walk(p.inp); walk(p.out)
    if not found: return ""
    lines = []
    for a in found:
        cs = "; ".join(f"variant {i} has {len(c)} field(s)" for i, c in enumerate(a.ctors))
        lines.append(f"- Variant type `{a.name}`: {cs}. Encoded as `(i payload)` per the primer (fields in the order listed in the task text).")
    return "\n".join(lines) + "\n"


def contract(p: Program) -> str:
    lo, hi = min(p.sizes), max(p.sizes)
    return f"""## Task `{p.id}`

{p.desc}

- Input type:  `{describe(p.inp)}`
- Output type: `{describe(p.out)}`
{_adt_note(p)}- `@prog` has root `(input output)`. The input is delivered in the encoding described in the primer; the output must be the canonical encoding of the output type.
- While you author, imagine inputs of size parameter {lo} to {hi}. The verifier also runs inputs up to 16x larger than that, edge cases, and fresh random inputs. One wrong answer, crash or hang fails the program.
"""


def prompt(p: Program) -> str:
    primer = open(os.path.join(ROOT, "PHYSICS.md")).read()
    return HEADER + "# PRIMER\n\n" + primer + "\n\n# YOUR TASK\n\n" + contract(p) + FORMAT


# ---------------------------------------------------------------- B1: same author, Bend route
HEADER_B1 = """You are an author in the Genome experiment. You write a program in Bend (a functional language that compiles to HVM2 nets).

Rules of this experiment:
- Use no tools beyond the one read that gave you this file. Do not read any other file, do not run anything, do not search. Answer from this prompt alone.
- Your submission must be Bend code defining `def prog(x)` (plus helpers). Do not define `main`.
- After each submission you may receive feedback from a hidden test suite. Fix the code and resubmit the complete program.

"""

FORMAT_B1 = """
## Reply format

Reply with exactly one fenced code block containing your complete Bend code (it must define `prog`), optionally preceded by a
few words. Nothing after the code block.
"""


def contract_b1(p: Program) -> str:
    from .bend_io import bend_type_decls
    lo, hi = min(p.sizes), max(p.sizes)
    decls = "\n\n".join(x for x in (bend_type_decls(p.inp), bend_type_decls(p.out)) if x)
    decl_txt = ""
    if decls:
        decl_txt = ("\n- These types are already declared for you (the constructors are numbered in the order the task text lists its variants, "
                    "so the first variant is `C0`, the second `C1`, and so on; fields are `f0`, `f1`, ...). Do not redeclare them:\n\n```\n"
                    + decls + "\n```\n")
    return f"""## Task `{p.id}`

{p.desc}

- Input type:  `{describe(p.inp)}`
- Output type: `{describe(p.out)}`
- `prog` takes the input (a tuple if there are several inputs) and returns the output. Lists are Bend lists; numbers are u24.{decl_txt}
- While you author, imagine inputs of size parameter {lo} to {hi}. The verifier also runs inputs up to 16x larger than that, edge cases, and fresh random inputs. One wrong answer, crash or hang fails the program.
"""


def prompt_b1(p: Program) -> str:
    primer = open(os.path.join(ROOT, "BEND_PRIMER.md")).read()
    return HEADER_B1 + "# PRIMER\n\n" + primer + "\n\n# YOUR TASK\n\n" + contract_b1(p) + FORMAT_B1


# ---------------------------------------------------------------- short prompts (no primer): for models that learned the medium
SHORT_HEADER = "Write a net in HVM2's textual net IR that solves the task below. Define `@prog` with root `(input output)`.\n\n"
SHORT_HEADER_B1 = "Write Bend code that solves the task below. Define `def prog(x)` (plus helpers, no `main`).\n\n"


def prompt_short(p: Program) -> str:
    return SHORT_HEADER + contract(p) + FORMAT


def prompt_short_b1(p: Program) -> str:
    return SHORT_HEADER_B1 + contract_b1(p) + FORMAT_B1
