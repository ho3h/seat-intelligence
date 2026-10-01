"""HERO-3 net generators: the original sequential walker, the tree-fold rewrite, controls, and the list->tree ingest.

Tree-shaped input format ("rope"): an ADT  Nil | One(x) | Cat(l, r)  encoded with the interface rule of PHYSICS.md:
    Nil = (0 *)      One(x) = (1 x)      Cat(l, r) = (2 (l r))
A caller may supply ANY shape (balanced, skewed, with empty subtrees). The rewrite is correct for every shape; depth is
proportional to the height of the tree the caller supplies, so a balanced rope gives the logarithmic bound.
"""
from __future__ import annotations
from ..types import adt, REC, list_of, u24
from .folds import Fold


def rope_t(elem_t):
    return adt("rope", (), (elem_t,), (REC, REC))


def step_def(f: Fold) -> str:
    if f.step_txt: return f.step_txt
    return "@step = (acc (x out))\n  & @lift ~ (x hl)\n  & @comb ~ (acc (hl out))\n"


def helpers(f: Fold, need_step=True, need_lift=True, need_comb=True) -> str:
    parts = []
    if need_step: parts.append(step_def(f))
    if need_lift: parts.append(f.lift_txt)
    if need_comb: parts.append(f.comb_txt)
    if f.fin_txt: parts.append(f.fin_txt)
    return "\n".join(p.rstrip() + "\n" for p in parts)


def _finish(f: Fold, call: str) -> str:
    """@prog body: call produces state wire `s` or, with no fin, writes straight to out."""
    return call


def seq_net(f: Fold, all_defs: bool = False) -> str:
    """The ORIGINAL: a one-cell-at-a-time list walker over `step`, then fin."""
    u = f.unit_txt
    if f.fin_txt:
        prog = f"@prog = (l out)\n  & @sw ~ (l ({u} s))\n  & @fin ~ (s out)\n"
    else:
        prog = f"@prog = (l out)\n  & @sw ~ (l ({u} out))\n"
    walker = """@sw = ((?((@sw_nil @sw_cons) (pl (acc out))) pl) (acc out))

@sw_nil = (* (a a))

@sw_cons = (* ((h t) (acc out)))
  & @step ~ (acc (h acc2))
  & @sw ~ (t (acc2 out))
"""
    return prog + "\n" + walker + "\n" + helpers(f, need_lift=all_defs or f.step_txt is None, need_comb=all_defs or f.step_txt is None)


def tree_net(f: Fold) -> str:
    """The REWRITE: balanced-tree reduction over a rope, lift at the leaves, comb at the nodes, unit for Nil."""
    u = f.unit_txt
    if f.fin_txt:
        prog = "@prog = (t out)\n  & @tf ~ (t s)\n  & @fin ~ (s out)\n"
    else:
        prog = "@prog = (t out)\n  & @tf ~ (t out)\n"
    walker = f"""@tf = ((?((@tf_nil @tf_1) (pl out)) pl) out)

@tf_nil = (* {u})

@tf_1 = (m (pl out))
  & m ~ ?((@lift @tf_2) (pl out))

@tf_2 = (* ((l r) out))
  & @tf ~ (l lv)
  & @tf ~ (r rv)
  & @comb ~ (lv (rv out))
"""
    return prog + "\n" + walker + "\n" + helpers(f, need_step=False)


def seqtree_net(f: Fold) -> str:
    """CONTROL: the same rope input folded in sequential in-order (accumulator threaded through the tree). Shows that the
    depth win comes from using associativity, not from the input being a tree."""
    u = f.unit_txt
    if f.fin_txt:
        prog = f"@prog = (t out)\n  & @sf ~ (t ({u} s))\n  & @fin ~ (s out)\n"
    else:
        prog = f"@prog = (t out)\n  & @sf ~ (t ({u} out))\n"
    walker = """@sf = ((?((@sf_nil @sf_1) (pl (acc out))) pl) (acc out))

@sf_nil = (* (a a))

@sf_1 = (m (pl (acc out)))
  & m ~ ?((@sf_leaf @sf_2) (pl (acc out)))

@sf_leaf = (x (acc out))
  & @step ~ (acc (x out))

@sf_2 = (* ((l r) (acc out)))
  & @sf ~ (l (acc mid))
  & @sf ~ (r (mid out))
"""
    return prog + "\n" + walker + "\n" + helpers(f, need_lift=f.step_txt is None, need_comb=f.step_txt is None)


L2T = """@l2t = (l out)
  & @mapone ~ (l l1)
  & @red ~ (l1 out)

@mapone = ((?((@mo_nil @mo_cons) (pl out)) pl) out)

@mo_nil = (* (0 *))

@mo_cons = (* ((h t) (1 ((1 h) tl))))
  & @mapone ~ (t tl)

@pp = ((?((@pp_nil @pp_c) (pl out)) pl) out)

@pp_nil = (* (0 *))

@pp_c = (* ((h t) out))
  & @pp2 ~ (h (t out))

@pp2 = (h ((?((@pp2_nil @pp2_c) (h (pl out))) pl) out))

@pp2_nil = (h (* (1 (h (0 *)))))

@pp2_c = (* (h ((h2 t2) (1 ((2 (h h2)) tl)))))
  & @pp ~ (t2 tl)

@red = ((?((@red_nil @red_c) (pl out)) pl) out)

@red_nil = (* (0 *))

@red_c = (* ((h t) out))
  & @red2 ~ (h (t out))

@red2 = (h ((?((@red2_nil @red2_c) (h (pl out))) pl) out))

@red2_nil = (h (* h))

@red2_c = (* (h ((h2 t2) out)))
  & @pp ~ ((1 (h (1 (h2 t2)))) l2)
  & @red ~ (l2 out)
"""


def all_defs(f: Fold) -> str:
    """Every helper def (step, lift, comb, fin) plus the sequential walker @sw and the tree walker @tf, no @prog:
    used by the tester's driver nets."""
    sq = seq_net(f, all_defs=True); tr = tree_net(f)
    sq_body = sq[sq.index("@sw = "):]
    tr_body = tr[tr.index("@tf = "):tr.index("@lift ") if "@lift " in tr else None]
    # tree_net body = walker + helpers; strip helpers that seq_net already includes
    tf_walker = tr[tr.index("@tf = "):]
    cut = min([i for i in (tf_walker.find("\n@lift"), tf_walker.find("\n@comb"), tf_walker.find("\n@fin"), tf_walker.find("\n@step")) if i >= 0] or [len(tf_walker)])
    return sq_body + "\n" + tf_walker[:cut] + "\n"


def ingest_net(f: Fold) -> str:
    """Whole pipeline on LIST input: build a balanced rope from the list (measured cost), then the tree fold."""
    if f.fin_txt:
        prog = "@prog = (l out)\n  & @l2t ~ (l t)\n  & @tf ~ (t s)\n  & @fin ~ (s out)\n"
    else:
        prog = "@prog = (l out)\n  & @l2t ~ (l t)\n  & @tf ~ (t out)\n"
    tf = tree_net(f)
    tf_body = tf[tf.index("@tf = "):]
    return prog + "\n" + tf_body + "\n" + L2T
