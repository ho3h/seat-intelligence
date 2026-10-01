"""exp6: program synthesis from I/O examples by SUPERPOSITION in HVM4 (no language model).

A list DSL whose stages mirror genome/taskgen.py's pipeline stages exactly (same parameter sets). Candidate programs
(stage lists of length 1..L) are one superposed HVM4 term; the interpreter runs it on the example inputs, mismatches are
erased (&{}), and collapse (-C) prints the survivors. The same interpreter evaluates one concrete candidate at a time for
the independent baseline.
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import itertools, os, re, subprocess, time

HVM = _REPO + "/physics/hvm4/src/hvm"
HERE = os.path.dirname(os.path.abspath(__file__))
M = 1 << 24

# ------------------------------------------------------------------ stage catalog: (hvm constructor, python fn, taskgen name)
KS = [3, 5, 10, 20, 50, 100, 500]
MS = [2, 3, 4, 5, 7]
AS = [2, 3, 5, 7, 10]; BS = [0, 1, 2, 7, 100]; MKS = [1, 3, 7, 15, 63, 255]; CS = [1, 2, 5, 9]
TK = [1, 2, 3, 5, 8]


def _filt(h, f):
    return (f"#Filt{{{h}}}", lambda xs, f=f: [x for x in xs if f(x)])


def _map(h, f):
    return (f"#Map{{{h}}}", lambda xs, f=f: [f(x) for x in xs])


def catalog():
    st = {}
    st["rev"] = ("#Rev{}", lambda xs: xs[::-1])
    st["sort"] = ("#Sort{}", lambda xs: sorted(xs))
    st["dedup"] = ("#Ddup{}", lambda xs: [x for i, x in enumerate(xs) if i == 0 or xs[i - 1] != x])
    st["scan"] = ("#Scan{}", lambda xs: [sum(xs[:i + 1]) % M for i in range(len(xs))])
    for k in TK:
        st[f"take{k}"] = (f"#Take{{{k}}}", lambda xs, k=k: xs[:k])
        st[f"drop{k}"] = (f"#Drop{{{k}}}", lambda xs, k=k: xs[k:])
    for k in KS:
        st[f"gt{k}"] = _filt(f"#Gt{{{k}}}", lambda x, k=k: x > k)
        st[f"lt{k}"] = _filt(f"#Lt{{{k}}}", lambda x, k=k: x < k)
        st[f"ge{k}"] = _filt(f"#Ge{{{k}}}", lambda x, k=k: x >= k)
    for m in MS:
        for r in range(m):
            st[f"mod{m}eq{r}"] = _filt(f"#Meq{{{m},{r}}}", lambda x, m=m, r=r: x % m == r)
    for a in AS:
        for b in BS:
            st[f"aff{a}_{b}"] = _map(f"#Aff{{{a},{b}}}", lambda x, a=a, b=b: (x * a + b) % M)
    for c in CS:
        st[f"add{c}"] = _map(f"#Aff{{1,{c}}}", lambda x, c=c: (x + c) % M)
    for mk in MKS:
        st[f"xor{mk}"] = _map(f"#Xor{{{mk}}}", lambda x, mk=mk: x ^ mk)
        st[f"and{mk}"] = _map(f"#And{{{mk}}}", lambda x, mk=mk: x & mk)
    st["sq"] = _map("#Sq{}", lambda x: x * x % M)
    for a in AS:
        st[f"mod{a + 1}"] = _map(f"#Mod{{{a + 1}}}", lambda x, m=a + 1: x % m)
        st[f"div{a}"] = _map(f"#Div{{{a}}}", lambda x, a=a: x // a)
    return st


CAT = catalog()
H2N = {v[0]: k for k, v in CAT.items()}


def py_run(names, xs):
    for n in names: xs = CAT[n][1](xs)
    return xs


# ------------------------------------------------------------------ HVM4 source
INTERP = r"""
@guard = λ{ 0: λp. &{}; _: λc. λp. p }

@eqL = λ{
  []: λ{ []: 1; <>: λh. λt. 0 };
  <>: λa. λas. λ{ []: 0; <>: λb. λbs. @eqK((a == b), as, bs) }
}
@eqK = λ{ 0: λas. λbs. 0; _: λc. λas. λbs. @eqL(as, bs) }

@exec = λ{ []: λxs. xs; <>: λs. λss. λxs. @exec(ss, @run(s, xs)) }

@run = λ{
  #Rev: λxs. @rev(xs, [])
  #Sort: λxs. @isort(xs)
  #Ddup: λxs. @ddup(xs)
  #Scan: λxs. @scan(xs, 0)
  #Take: λk. λxs. @take(xs, k)
  #Drop: λk. λxs. @drop(xs, k)
  #Map: λf. λxs. @map(f, xs)
  #Filt: λp. λxs. @filt(p, xs)
}

@rev = λ{ []: λacc. acc; <>: λh. λt. λacc. @rev(t, (h <> acc)) }

@isort = λ{ []: []; <>: λh. λt. @ins(@isort(t), h) }
@ins = λ{ []: λx. [x]; <>: λ&h. λt. λ&x. @insK((x <= h), x, h, t) }
@insK = λ{ 0: λx. λh. λt. (h <> @ins(t, x)); _: λc. λx. λh. λt. (x <> (h <> t)) }

@ddup = λ{ []: []; <>: λ&h. λt. (h <> @ddupG(h, t)) }
@ddupG = λp. λ{ []: []; <>: λ&h. λt. @ddupK((p == h), h, t) }
@ddupK = λ{ 0: λ&h. λt. (h <> @ddupG(h, t)); _: λc. λ&h. λt. @ddupG(h, t) }

@scan = λ{ []: λacc. []; <>: λh. λt. λacc. !&s = ((acc + h) % 16777216); (s <> @scan(t, s)) }

@take = λ{ []: λk. []; <>: λh. λt. λk. @takeG(k, h, t) }
@takeG = λ{ 0: λh. λt. []; _: λk. λh. λt. (h <> @take(t, (k - 1))) }
@drop = λ{ []: λk. []; <>: λh. λt. λk. @dropG(k, h, t) }
@dropG = λ{ 0: λh. λt. (h <> t); _: λk. λh. λt. @drop(t, (k - 1)) }

@ap = λ{
  #Aff: λa. λb. λx. (((x * a) + b) % 16777216)
  #Xor: λm. λx. (x ^ m)
  #And: λm. λx. (x && m)
  #Sq: λ&x. ((x * x) % 16777216)
  #Mod: λm. λx. (x % m)
  #Div: λa. λx. (x / a)
}
@map = λ&f. λ{ []: []; <>: λh. λt. (@ap(f, h) <> @map(f, t)) }

@test = λ{
  #Gt: λk. λx. (x > k)
  #Lt: λk. λx. (x < k)
  #Ge: λk. λx. (x >= k)
  #Meq: λm. λr. λx. ((x % m) == r)
}
@filt = λ&p. λ{ []: []; <>: λ&h. λt. @keep(@test(p, h), h, @filt(p, t)) }
@keep = λ{ 0: λh. λr. r; _: λc. λh. λr. (h <> r) }
"""


def hlist(xs):
    return "[" + ",".join(str(x) for x in xs) + "]"


def choice_term(label, stages):
    """&L{s0, &L{s1, ... s_{n-1}}} (same label nested: one independent choice)."""
    t = stages[-1]
    for s in reversed(stages[:-1]):
        t = f"&{label}{{{s}, {t}}}"
    return t


def sup_program(stage_hs, max_len, min_len=1):
    """Program = list of min_len..max_len stages. Position i picks a stage (label Si); from position min_len on, an
    independent choice (label Ei) decides whether the list stops there."""
    tail = "[]"
    for i in reversed(range(max_len)):
        cons = f"(@C{i} <> {tail})"
        tail = cons if i < min_len else f"&E{i}{{[], {cons}}}"
    defs = "\n".join(f"@C{i} = {choice_term(f'S{i}', stage_hs)}" for i in range(max_len))
    return defs, tail


def main_src(prog_term, examples, defs=""):
    """@main: guard each example in turn (later examples only run on survivors), then print the program."""
    body = "p"
    for xs, ys in reversed(examples):
        body = f"@guard(@eqL(@exec(p, {hlist(xs)}), {hlist(ys)}), {body})"
    return INTERP + "\n" + defs + f"\n@P = {prog_term}\n@main = !&p = @P; {body}\n"


ANSI = re.compile(r"\x1b\[[0-9;]*m")


def run_hvm(src, path, collapse=None, timeout=600):
    with open(path, "w") as f: f.write(src)
    args = [HVM, path, "-s"] + ([f"-C{collapse}"] if collapse else ["-C"])
    t0 = time.time()
    p = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
    wall = time.time() - t0
    out = ANSI.sub("", p.stdout + p.stderr)
    itrs = re.search(r"Itrs: (\d+)", out); heap = re.search(r"Heap: (\d+)", out)
    sols = [re.sub(r"\s+#\d+\s*$", "", l).strip() for l in out.splitlines() if l.startswith("[")]
    return {"itrs": int(itrs.group(1)) if itrs else None, "heap": int(heap.group(1)) if heap else None,
            "wall": wall, "sols": sols, "rc": p.returncode, "raw": out if not itrs else ""}


def parse_sol(s):
    """'[#Rev{},#Filt{#Gt{5}}]' -> ['rev', 'gt5'] using the catalog's constructor strings."""
    s = s.strip()[1:-1]
    parts, depth, cur = [], 0, ""
    for ch in s:
        if ch == "," and depth == 0: parts.append(cur); cur = ""; continue
        depth += ch == "{"; depth -= ch == "}"; cur += ch
    if cur: parts.append(cur)
    out = []
    for p in parts:
        p = p.replace(" ", "")
        if p not in H2N: return None
        out.append(H2N[p])
    return out


def all_programs(names, max_len):
    for L in range(1, max_len + 1):
        yield from itertools.product(names, repeat=L)
