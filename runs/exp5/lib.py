"""Tiny text-macro library for the GRAPH-SWING nets (runs/exp5). Emits hand-designed HVM2 templates; nothing here is
learned or searched. Each function returns HVM2 text.

stream(p, k, step, fin): a k-cell blocked list walker. It matches k cells of the list speculatively (2 rounds per cell,
no switch in the way), puts one SWI per cell on the cell's tag, and threads a state S through a chain of pre-expanded
@step calls. When a Nil is met, @fin receives the state and the output wire. Cells beyond the Nil receive erasers and
their whole sub-net is erased, so no separate end-of-list test is needed.
  @step ~ (S_in (elem S_out))       @fin ~ (S out)
Entry: @<p>_blk ~ (list (S0 out)).
"""


def stream(p, k, step, fin):
    pat = f"t{k}"
    for i in range(k, 0, -1):
        pat = f"(T{i} (E{i} {pat}))"
    lines = [f"@{p}_blk = (t (S0 o0))", f"  & t ~ {pat}"]
    for i in range(1, k):
        lines.append(f"  & T{i} ~ ?((@{p}_nil @{p}_cons) (S{i-1} (o{i-1} (E{i} (S{i} o{i})))))")
    lines.append(f"  & T{k} ~ ?((@{p}_nil @{p}_last) (S{k-1} (o{k-1} (E{k} t{k}))))")
    lines += [
        f"@{p}_nil = (S (o *))",
        f"  & @{fin} ~ (S o)",
        f"@{p}_cons = (* (S (o (E (S2 o)))))",
        f"  & @{step} ~ (S (E S2))",
        f"@{p}_last = (* (S (o (E t))))",
        f"  & @{step} ~ (S (E S2))",
        f"  & @{p}_blk ~ (t (S2 o))",
    ]
    return "\n".join(lines) + "\n"


def build(parts, out):
    open(out, "w").write("\n".join(parts))


def nav(X, act):
    """Keyed update of a depth-L complete binary trie: @X ~ (t (k (L (P o)))) rebuilds the path to leaf k and runs
    @act ~ (leaf (P leaf')) there. P is an opaque payload. Control flow depends only on k and L, so the whole update
    expands before t exists; a chain of updates collapses in O(L) rounds once the keys are known."""
    return f"""@{X} = (t (k (L (P o))))
  & L ~ ?((@{X}_leaf @{X}_node) (t (k (P o))))
@{X}_leaf = (t (* (P o)))
  & @{act} ~ (t (P o))
@{X}_node = (lm (t (k (P o))))
  & k ~ {{k1 k2}}
  & lm ~ {{l1 l2}}
  & k1 ~ $([>>] $(l1 sh))
  & sh ~ $([&] $(1 b))
  & b ~ ?((@{X}_L @{X}_R) (t (k2 (l2 (P o)))))
@{X}_L = ((l r) (k (L (P (l2 r)))))
  & @{X} ~ (l (k (L (P l2))))
@{X}_R = (* ((l r) (k (L (P (l r2))))))
  & @{X} ~ (r (k (L (P r2))))
"""
