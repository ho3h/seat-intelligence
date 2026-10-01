"""exp11 (swing 11b): expression-level synthesis by superposition in HVM4, in the regime where candidates share
sub-computations (expression trees; loop bodies inside a shared fold skeleton).

DSL (u32 semantics, identical to HVM4's OP2):
  leaves  : x, 0..5            (fold bodies also: acc)
  unary   : e % m, m in 2..5
  binary  : + - * xor and min max lt(0/1) eq(0/1)
  E_1 = leaves ; E_h = leaves | unary(E_{h-1}) | binary(E_{h-1}, E_{h-1})     ("depth h" = height <= h)
AST: ('X',) ('A',) ('K',k) ('Mod',m,a) (op,a,b).
"""
from __future__ import annotations
import os as _os
_REPO = _os.path.abspath(_os.path.join(_os.path.dirname(__file__), "../.."))  # repo root (release copy; was an absolute path)
import os, random, re, subprocess, time

HVM = _REPO + "/physics/hvm4/src/hvm"
U = 0xFFFFFFFF
CONSTS = list(range(6))
MODS = [2, 3, 4, 5]
BINOPS = ["Add", "Sub", "Mul", "Xor", "And", "Min", "Max", "Lt", "Eq"]
PYOP = {
    "Add": lambda a, b: (a + b) & U, "Sub": lambda a, b: (a - b) & U, "Mul": lambda a, b: (a * b) & U,
    "Xor": lambda a, b: a ^ b, "And": lambda a, b: a & b, "Min": min, "Max": max,
    "Lt": lambda a, b: int(a < b), "Eq": lambda a, b: int(a == b),
}
FULL = (list(CONSTS), list(MODS), list(BINOPS))


def set_dsl(consts, mods, binops):
    """Switch the DSL in place (used for the small-DSL depth-scaling series)."""
    CONSTS[:] = consts; MODS[:] = mods; BINOPS[:] = binops


HOP = {"Add": "+", "Sub": "-", "Mul": "*", "Xor": "^", "And": "&&", "Lt": "<", "Eq": "=="}


def leaves(fold):
    return ([("A",)] if fold else []) + [("X",)] + [("K", k) for k in CONSTS]


def count(h, fold=False):
    n = len(leaves(fold))
    if h == 1: return n
    c = count(h - 1, fold)
    return n + len(MODS) * c + len(BINOPS) * c * c


# ------------------------------------------------------------------ python semantics
def ev(t, x, a=0):
    k = t[0]
    if k == "X": return x
    if k == "A": return a
    if k == "K": return t[1]
    if k == "Mod": return ev(t[2], x, a) % t[1]
    return PYOP[k](ev(t[1], x, a), ev(t[2], x, a))


def fold(t, z, xs):
    acc = z
    for x in xs: acc = ev(t, x, acc)
    return acc


def show(t):
    k = t[0]
    if k == "X": return "x"
    if k == "A": return "acc"
    if k == "K": return str(t[1])
    if k == "Mod": return f"({show(t[2])} % {t[1]})"
    sym = {"Add": "+", "Sub": "-", "Mul": "*", "Xor": "^", "And": "&", "Lt": "<", "Eq": "=="}
    if k in sym: return f"({show(t[1])} {sym[k]} {show(t[2])})"
    return f"{k.lower()}({show(t[1])}, {show(t[2])})"


# ------------------------------------------------------------------ sampling (uniform over the exact candidate set)
def sample(h, rng, fold=False):
    if h == 1: return rng.choice(leaves(fold))
    nl = len(leaves(fold)); c = count(h - 1, fold)
    w = [nl, len(MODS) * c, len(BINOPS) * c * c]
    r = rng.choices([0, 1, 2], w)[0]
    if r == 0: return rng.choice(leaves(fold))
    if r == 1: return ("Mod", rng.choice(MODS), sample(h - 1, rng, fold))
    return (rng.choice(BINOPS), sample(h - 1, rng, fold), sample(h - 1, rng, fold))


def size(t):
    return 1 if t[0] in ("X", "A", "K") else (1 + size(t[2]) if t[0] == "Mod" else 1 + size(t[1]) + size(t[2]))


# ------------------------------------------------------------------ HVM4 encoding
def hterm(t):
    k = t[0]
    if k in ("X", "A"): return f"#{k}{{}}"
    if k == "K": return f"#K{{{t[1]}}}"
    if k == "Mod": return f"#Mod{{{t[1]},{hterm(t[2])}}}"
    return f"#{k}{{{hterm(t[1])},{hterm(t[2])}}}"


class Labels:
    def __init__(self): self.n = 0
    def __call__(self):
        self.n += 1
        s, n = "", self.n
        while n: n, r = divmod(n - 1, 26); s = chr(65 + r) + s
        return "L" + s


def choice(opts, lab):
    """Balanced binary tree of SUPs, one fresh label per SUP node: a k-way independent choice."""
    if len(opts) == 1: return opts[0]
    m = len(opts) // 2
    return f"&{lab()}{{{choice(opts[:m], lab)},{choice(opts[m:], lab)}}}"


def sup_term(h, fold=False, lab=None):
    """Every position of the expression tree is its own choice (distinct labels per position)."""
    lab = lab or Labels()
    opts = [hterm(l) for l in leaves(fold)]
    if h > 1:
        opts += [f"#Mod{{{m},{sup_term(h - 1, fold, lab)}}}" for m in MODS]
        opts += [f"#{op}{{{sup_term(h - 1, fold, lab)},{sup_term(h - 1, fold, lab)}}}" for op in BINOPS]
    return choice(opts, lab)


def _evcases(fold):
    args = "λ&a. λ&x." if fold else "λ&x."
    call = (lambda s: f"@ev({s}, a, x)") if fold else (lambda s: f"@ev({s}, x)")
    cs = []
    if fold: cs.append("  #A: λa. λx. a")
    cs.append("  #X: λa. λx. x" if fold else "  #X: λx. x")
    cs.append("  #K: λk. λa. λx. k" if fold else "  #K: λk. λx. k")
    cs.append(f"  #Mod: λm. λe. {'λa. λx.' if fold else 'λx.'} ({call('e')} % m)")
    for op in BINOPS:
        if op in HOP: body = f"({call('l')} {HOP[op]} {call('r')})"
        else: body = f"@{op.lower()}({call('l')}, {call('r')})"
        cs.append(f"  #{op}: λl. λr. {args} {body}")
    return "@ev = λ{\n" + "\n".join(cs) + "\n}\n"


PRELUDE = """
@g = λ{ 0: λk. &{}; _: λc. λk. k }
@sel = λ{ 0: λa. λb. b; _: λc. λa. λb. a }
@min = λ&a. λ&b. @sel((a < b), a, b)
@max = λ&a. λ&b. @sel((a < b), b, a)
"""
MAPCHK = """
@chk = λ{ []: λys. λp. p; <>: λx. λxs. λ{ <>: λy. λys. λ&p. @g((@ev(p, x) == y), @chk(xs, ys, p)); []: λp. &{} } }
"""
FOLDCHK = """
@fold = λ{ []: λacc. λp. acc; <>: λx. λxs. λacc. λ&p. @fold(xs, @ev(p, acc, x), p) }
@chk = λ{ []: λys. λp. p; <>: λxs. λxss. λ{ <>: λy. λys. λ&p. @g((@fold(xs, Z, p) == y), @chk(xss, ys, p)); []: λp. &{} } }
"""


def cterm(t, fold=False):
    """Candidate compiled to a direct HVM expression over cloned x (and acc): no interpreter."""
    k = t[0]
    if k == "X": return "x"
    if k == "A": return "a"
    if k == "K": return str(t[1])
    if k == "Mod": return f"({cterm(t[2], fold)} % {t[1]})"
    if k in HOP: return f"({cterm(t[1], fold)} {HOP[k]} {cterm(t[2], fold)})"
    return f"@{k.lower()}({cterm(t[1], fold)}, {cterm(t[2], fold)})"


def compiled_program(t, task):
    fold = task["kind"] == "fold"
    body = cterm(t, fold)
    nx = len(re.findall(r"\bx\b", body))
    na = len(re.findall(r"\ba\b", body)) if fold else 0
    bx = "λ&x." if nx > 1 else "λx."; ba = "λ&a." if na > 1 else "λa."
    if not fold:
        f = f"@f = {bx} {body}\n"
        chk = "@chk = λ{ []: λys. 1; <>: λx. λxs. λ{ <>: λy. λys. @g((@f(x) == y), @chk(xs, ys)); []: &{} } }\n"
        return PRELUDE + f + chk + f"@main = @chk({hl(task['xs'])}, {hl(task['ys'])})\n"
    f = f"@f = {ba} {bx} {body}\n"
    fl = "@fold = λ{ []: λacc. acc; <>: λx. λxs. λacc. @fold(xs, @f(acc, x)) }\n"
    chk = f"@chk = λ{{ []: λys. 1; <>: λxs. λxss. λ{{ <>: λy. λys. @g((@fold(xs, {task['z']}) == y), @chk(xss, ys)); []: &{{}} }} }}\n"
    xss = "[" + ",".join(hl(xs) for xs in task["xss"]) + "]"
    return PRELUDE + f + fl + chk + f"@main = @chk({xss}, {hl(task['ys'])})\n"


def hl(xs): return "[" + ",".join(str(v) for v in xs) + "]"


def program(pterm, task):
    """task: {'kind':'map','xs':[..],'ys':[..]} (all example elements concatenated, one shared traversal)
             {'kind':'fold','z':int,'xss':[[..],..],'ys':[..]}"""
    if task["kind"] == "map":
        return PRELUDE + _evcases(False) + MAPCHK + f"@P = {pterm}\n@main = @chk({hl(task['xs'])}, {hl(task['ys'])}, @P)\n"
    xss = "[" + ",".join(hl(xs) for xs in task["xss"]) + "]"
    return (PRELUDE + _evcases(True) + FOLDCHK.replace("Z", str(task["z"])) +
            f"@P = {pterm}\n@main = @chk({xss}, {hl(task['ys'])}, @P)\n")


ANSI = re.compile(r"\x1b\[[0-9;]*m")


def run_hvm(src, path, timeout=3600):
    with open(path, "w") as f: f.write(src)
    t0 = time.time()
    p = subprocess.run([HVM, path, "-s", "-C"], capture_output=True, text=True, timeout=timeout)
    wall = time.time() - t0
    out = ANSI.sub("", p.stdout + p.stderr)
    m = re.search(r"Itrs: (\d+)", out); hp = re.search(r"Heap: (\d+)", out)
    sols = [re.sub(r"\s+#\d+\s*$", "", l).strip() for l in out.splitlines() if l.startswith("#")]
    return {"itrs": int(m.group(1)) if m else None, "heap": int(hp.group(1)) if hp else None, "wall": wall,
            "sols": sols, "rc": p.returncode, "err": "" if m else out[-2000:]}


def parse(s):
    """'#Add{#X{},#K{2}}' -> ('Add',('X',),('K',2))"""
    s = s.replace(" ", ""); i = 0
    def term():
        nonlocal i
        if s[i].isdigit():
            j = i
            while s[j].isdigit(): j += 1
            v = int(s[i:j]); i = j; return v
        assert s[i] == "#"; j = i + 1
        while s[j] != "{": j += 1
        name = s[i + 1:j]; i = j + 1; args = []
        while s[i] != "}":
            args.append(term())
            if s[i] == ",": i += 1
        i += 1
        return (name, *args)
    return term()
