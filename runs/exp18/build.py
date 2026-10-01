"""Builds the RECON-SWING-2 nets (runs/exp18) from graphprims + runs/exp18/lib_ext.py templates plus glue.
usage: python3 runs/exp18/build.py <prog|all>"""
import sys, os
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from lib_ext import *  # noqa
CORE = os.environ.get("CORE", "5")  # 1: greedy_core, 2..5: greedy_core2..5 (see lib_ext.py)
if CORE == "2": greedy_core = greedy_core2  # noqa
if CORE == "3": greedy_core = greedy_core3  # noqa
if CORE == "4": greedy_core = greedy_core4  # noqa
if CORE == "5": greedy_core = greedy_core5  # noqa

NETS = {}
def prog(name):
    def deco(f): NETS[name] = f; return f
    return deco

def book(): return Book()

# n = 0 guard; ctx names the remaining input wires
def guard(pattern, rest, zero, body):
    """@prog = ((n rest_pattern) out); n == 0 -> zero output (rest erased); else body with n, L."""
    return f"""@prog = ((n {pattern}) out)
  & n ~ ?((@pz @pp) ({rest} out))
@pz = ({' '.join('*' for _ in [0])} {zero})
@pp = (nm1 ({rest} out))
  & nm1 ~ {{na nb}}
  & na ~ $([+1] n)
  & @lg ~ (nb L)
{body}"""

def ers(k):  # erase k nested context wires then the output
    return "(* " * k

@prog("t5_conflict_greedy")
def _():
    b = book(); greedy_core(b); out_labels(b)
    b.add("""
@prog = ((n (mnl cs)) out)
  & n ~ ?((@pz @pp) (mnl (cs out)))
@pz = (* (* (0 *)))
@pp = (nm1 (mnl (cs out)))
  & nm1 ~ {na nb}
  & na ~ $([+1] n)
  & @lg ~ (nb L)
  & L ~ {L1 L2}
  & @gr ~ (L1 (0 (16777215 (mnl (cs (T *))))))
  & @gout ~ (T (L2 (0 (n ((0 *) out)))))
""")
    return b.text()

@prog("t5_conflict_greedy_cap")
def _():
    b = book(); greedy_core(b); out_labels(b)
    b.add("""
@prog = ((n (cap (mnl cs))) out)
  & n ~ ?((@pz @pp) (cap (mnl (cs out))))
@pz = (* (* (* (0 *))))
@pp = (nm1 (cap (mnl (cs out))))
  & nm1 ~ {na nb}
  & na ~ $([+1] n)
  & @lg ~ (nb L)
  & L ~ {L1 L2}
  & @gr ~ (L1 (0 (cap (mnl (cs (T *))))))
  & @gout ~ (T (L2 (0 (n ((0 *) out)))))
""")
    return b.text()


@prog("t5_conflict_skipped")
def _():
    b = book(); greedy_core(b)
    b.add("""
@prog = ((n (cap (mnl cs))) out)
  & n ~ ?((@pz @pp) (cap (mnl (cs out))))
@pz = (* (* (* (0 *))))
@pp = (nm1 (cap (mnl (cs out))))
  & @lg ~ (nm1 L)
  & @gr ~ (L (0 (cap (mnl (cs (* out))))))
""")
    return b.text()


@prog("t5_reconcile_canon_mnl")
def _():
    b = book(); greedy_core(b); out_labels(b)
    b.add("""
@prog = ((n (tau (mnl cs))) out)
  & n ~ ?((@pz @pp) (tau (mnl (cs out))))
@pz = (* (* (* (0 *))))
@pp = (nm1 (tau (mnl (cs out))))
  & nm1 ~ {na nb}
  & na ~ $([+1] n)
  & @lg ~ (nb L)
  & L ~ {L1 L2}
  & @gr ~ (L1 (tau (16777215 (mnl (cs (T *))))))
  & @gout ~ (T (L2 (0 (n ((0 *) out)))))
""")
    return b.text()


@prog("t5_prop_merged")
def _():
    b = book(); list_to_trie(b); prop_merge(b)
    b.add("""
@prog = ((c at) out)
  & c ~ {c1 c2}
  & @gln_blk ~ (c1 (0 n))
  & n ~ ?((@pz @pp) (c2 (at out)))
@pz = (* (* (0 *)))
@pp = (nm1 (c2 (at out)))
  & @lg ~ (nm1 L)
  & L ~ {L1 {L2 L3}}
  & @gl_z0 ~ (L1 T0)
  & @gcb_blk ~ (c2 ((0 (L2 T0)) V))
  & @gprop ~ (L3 (V (at out)))
""")
    return b.text()


@prog("t5_reconcile_full")
def _():
    b = book(); greedy_core(b); numeric_copies(b, 2); to_list(b, "gtl"); edge_rewrite(b)
    b.add("""
@prog = ((n (tau (mnl (cs es)))) out)
  & n ~ ?((@pz @pp) (tau (mnl (cs (es out)))))
@pz = (* (* (* (* ((0 *) (0 *))))))
@pp = (nm1 (tau (mnl (cs (es (C E))))))
  & nm1 ~ {na nb}
  & na ~ $([+1] n)
  & @lg ~ (nb L)
  & L ~ {L1 {L2 {L3 L4}}}
  & @gr ~ (L1 (tau (16777215 (mnl (cs (T *))))))
  & @gv2 ~ (T (L2 (V1 V2)))
  & @gtl ~ (V1 (L3 (0 (n ((0 *) C)))))
  & @gedge ~ (L4 (V2 (es E)))
""")
    return b.text()


@prog("t5_reconcile_full_props")
def _():
    b = book(); greedy_core(b); numeric_copies(b, 3); to_list(b, "gtl"); edge_rewrite(b); prop_merge(b)
    b.add("""
@prog = ((n (tau (mnl (cs (es at))))) out)
  & n ~ ?((@pz @pp) (tau (mnl (cs (es (at out))))))
@pz = (* (* (* (* (* ((0 *) ((0 *) (0 *))))))))
@pp = (nm1 (tau (mnl (cs (es (at (C (E P))))))))
  & nm1 ~ {na nb}
  & na ~ $([+1] n)
  & @lg ~ (nb L)
  & L ~ {L1 {L2 {L3 {L4 L5}}}}
  & @gr ~ (L1 (tau (16777215 (mnl (cs (T *))))))
  & @gv3 ~ (T (L2 (V1 (V2 V3))))
  & @gtl ~ (V1 (L3 (0 (n ((0 *) C)))))
  & @gedge ~ (L4 (V2 (es E)))
  & @gprop ~ (L5 (V3 (at P)))
""")
    return b.text()


if __name__ == "__main__":
    names = list(NETS) if sys.argv[1] == "all" else sys.argv[1:]
    for nm in names:
        out = os.path.join(D, nm + ".hvm")
        open(out, "w").write(NETS[nm]())
        print("wrote", out)
