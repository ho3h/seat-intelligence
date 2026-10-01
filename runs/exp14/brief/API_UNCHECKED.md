# API: graphprims + raw HVM glue

Import:

```python
import sys, os
sys.path.insert(0, "/Users/tedsandtads/Genome")
from genome.lib import graphprims as G
from genome.lib.graphprims import Book, INF
```

A `Book` collects HVM definitions. Every primitive is a function `G.<prim>(b, name, ...)` that ADDS its definitions to
the book and returns the name of its entry definition. You connect primitives by writing HVM text yourself:

* the `@prog` root (and any helper definitions such as a `@p_pos` branch), added with `b.add("""...""")`;
* the bodies passed to primitives as strings (walker `step`/`fin`, leaf bodies of `reduce`/`fold`/`zip2`,
  key bodies of `scatter`, `act`/`msg` of `frontier`, ...).

Each primitive's docstring gives its signature as the tree its entry REF must meet, e.g. `update`:
`@name ~ (t (k (L (P t2))))` = "trie t, key k, depth L, payload P; result trie t2". You call it with a redex such as
`& @hadd ~ (H0 (key (L6 (1 H1))))`. See `docs/GRAPH-LIB.md` for every signature and body shape.

Glue rules (PHYSICS.md): every wire name appears exactly twice in its definition; a value needed k times must go
through a DUP chain `x ~ {x1 {x2 x3}}`; an unused value must be erased with `*`; brackets must balance; a primitive
that ignores its payload (acts inc, dec, set1) still needs a `*` in the payload position; outputs of a switch branch
must be delivered in every branch.

Write the net with `open(path, "w").write(b.text())`.

Worked examples: `runs/exp14/examples_raw.py` (t3_degrees and t3_cc_largest, as the library's author wrote them).
