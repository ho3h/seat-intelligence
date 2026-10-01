"""T4 Languages (20 programs): bracket languages, arithmetic tokenizing / parsing / evaluation, expression-tree
rewrites, boolean formulas and tiny machines. All arithmetic is mod 2^24 unless stated.

Text is a list of u24 character codes. Fixed codes used throughout:
  '0'..'9' = 48..57   ' ' = 32   '(' = 40   ')' = 41   '*' = 42   '+' = 43   '-' = 45
  '[' = 91   ']' = 93   '{' = 123   '}' = 125
"""
from . import program
from ..types import u24, list_of, tup, adt, REC, MASK

M = MASK
BIG = MASK
S = list(range(0, 12))
TS = [88, 176]

TEXT = list_of(u24)
TOK = list_of(tup(u24, u24))

SP, LP, RP, STAR, PLUS, MINUS = 32, 40, 41, 42, 43, 45
LB, RB, LC, RC = 91, 93, 123, 125
DIGITS = range(48, 58)

# Lit(n) | Add(a, b) | Mul(a, b)
EXPR = adt("expr", (u24,), (REC, REC), (REC, REC))
# Lit(n) | Add(a, b) | Mul(a, b) | Var(i)
VEXPR = adt("vexpr", (u24,), (REC, REC), (REC, REC), (u24,))
# False | True | Var(i) | Not(a) | And(a, b) | Or(a, b)
BOOL = adt("bool", (), (), (u24,), (REC,), (REC, REC), (REC, REC))

CODES = ("Character codes: '0'..'9' = 48..57, ' ' = 32, '(' = 40, ')' = 41, '*' = 42, '+' = 43, '-' = 45. ")
EXPR_T = ("The expression Adt `expr` has ctor 0 Lit(n: u24), ctor 1 Add(left, right), ctor 2 Mul(left, right); "
          "as values: (0, n), (1, left, right), (2, left, right). ")
VEXPR_T = ("The expression Adt `vexpr` has ctor 0 Lit(n: u24), ctor 1 Add(left, right), ctor 2 Mul(left, right), "
           "ctor 3 Var(i: u24); as values: (0, n), (1, left, right), (2, left, right), (3, i). ")
BOOL_T = ("The formula Adt `bool` has ctor 0 False, ctor 1 True, ctor 2 Var(i: u24), ctor 3 Not(a), ctor 4 And(a, b), "
          "ctor 5 Or(a, b); as values: (0,), (1,), (2, i), (3, a), (4, a, b), (5, a, b). ")
GRAMMAR = ("The text is an arithmetic expression over this grammar: expr := term ('+' term)* ; "
           "term := factor ('*' factor)* ; factor := number | '(' expr ')' ; number := one or more digit characters, "
           "read in decimal (leading zeros allowed, value < 2^24). Spaces (32) may appear before, between or after "
           "tokens and are ignored; they never occur inside a number, and no other characters occur. So '*' binds "
           "tighter than '+', both operators are left-associative (1+2+3 means (1+2)+3), and parentheses only group. "
           "The input is guaranteed to be a valid expression (precondition). ")


# ============================================================ helpers: brackets
def _bal(rng, n, kinds=((LP, RP),)):
    """A random balanced string of length n (n rounded down to even), mixing bracket kinds."""
    n -= n % 2
    out, stack = [], []
    for i in range(n):
        rem = n - i
        if stack and (len(stack) == rem or rng.random() < 0.5):
            out.append(stack.pop())
        else:
            o, c = rng.choice(kinds)
            out.append(o); stack.append(c)
    return out


def _paren_unmatched(s):
    open_, bad = 0, 0
    for c in s:
        if c == LP: open_ += 1
        elif open_: open_ -= 1
        else: bad += 1
    return (bad, open_)


def _paren_prefix(s):
    d, best = 0, 0
    for i, c in enumerate(s):
        d += 1 if c == LP else -1
        if d < 0: break
        if d == 0: best = i + 1
    return best


def _paren_depth(s):
    d = best = 0
    for c in s:
        d += 1 if c == LP else -1
        best = max(best, d)
    return best


def _paren_match(s):
    out, st = [0] * len(s), []
    for i, c in enumerate(s):
        if c == LP: st.append(i)
        else:
            j = st.pop(); out[i] = j; out[j] = i
    return out


def _is_parens(s): return all(c in (LP, RP) for c in s)
def _balanced(s): return _is_parens(s) and _paren_unmatched(s) == (0, 0)


def _gen_parens(rng, n):
    r = rng.random()
    if r < 0.4: return _bal(rng, n)
    if r < 0.7:  # balanced with a few flips
        s = _bal(rng, n)
        for _ in range(rng.randrange(1, 3)):
            if s: i = rng.randrange(len(s)); s[i] = LP + RP - s[i]
        return s
    return [rng.choice((LP, RP)) for _ in range(n)]


def _gen_prefix(rng, n):
    s = []
    while len(s) < n:
        if rng.random() < 0.75: s += _bal(rng, rng.randrange(2, 9))
        else: s.append(rng.choice((LP, RP)))
    return s[:n]


PAIRS3 = {RP: LP, RB: LB, RC: LC}
KINDS3 = ((LP, RP), (LB, RB), (LC, RC))
ALL3 = (LP, RP, LB, RB, LC, RC)


def _brackets3(s):
    st = []
    for i, c in enumerate(s):
        if c in (LP, LB, LC): st.append(c)
        elif not st or st[-1] != PAIRS3[c]: return i + 1
        else: st.pop()
    return len(s) + 1 if st else 0


def _gen_brackets3(rng, n):
    s = _bal(rng, n, KINDS3)
    r = rng.random()
    if r < 0.3 or not s: return s
    if r < 0.6: i = rng.randrange(len(s)); s[i] = rng.choice(ALL3)
    elif r < 0.8: del s[rng.randrange(len(s))]
    else: s.insert(rng.randrange(len(s) + 1), rng.choice(ALL3))
    return s


# ============================================================ helpers: arithmetic text
def _txt(s): return [ord(c) for c in s]


def _tokenize(s):
    out, i = [], 0
    while i < len(s):
        c = s[i]
        if c in DIGITS:
            v = 0
            while i < len(s) and s[i] in DIGITS:
                v = v * 10 + s[i] - 48; i += 1
            out.append((0, v)); continue
        if c in (PLUS, MINUS, STAR): out.append((1, c))
        elif c in (LP, RP): out.append((2, c))
        i += 1
    return out


def _tok_ok(s):
    if not all(c in DIGITS or c in (SP, LP, RP, STAR, PLUS, MINUS) for c in s): return False
    return all(v <= M for k, v in _tokenize(s) if k == 0)


class _Bad(Exception):
    pass


def _parse(s):
    """Recursive descent over the + * ( ) grammar; raises _Bad on invalid text."""
    if not all(c in DIGITS or c in (SP, LP, RP, STAR, PLUS) for c in s): raise _Bad
    # spaces inside a number would split it into two adjacent numbers, which the grammar rejects anyway
    toks = _tokenize(s)
    if any(k == 0 and v > M for k, v in toks): raise _Bad
    pos = 0

    def peek(): return toks[pos] if pos < len(toks) else None

    def expr():
        nonlocal pos
        a = term()
        while peek() == (1, PLUS):
            pos += 1; a = (1, a, term())
        return a

    def term():
        nonlocal pos
        a = factor()
        while peek() == (1, STAR):
            pos += 1; a = (2, a, factor())
        return a

    def factor():
        nonlocal pos
        t = peek()
        if t is None: raise _Bad
        if t[0] == 0: pos += 1; return (0, t[1])
        if t == (2, LP):
            pos += 1; a = expr()
            if peek() != (2, RP): raise _Bad
            pos += 1; return a
        raise _Bad

    e = expr()
    if pos != len(toks): raise _Bad
    return e


def _valid_expr(s):
    try: _parse(s); return True
    except _Bad: return False


def _eval(e):
    if e[0] == 0: return e[1]
    a, b = _eval(e[1]), _eval(e[2])
    return (a + b) & M if e[0] == 1 else (a * b) & M


def _rpn(e):
    if e[0] == 0: return [(0, e[1])]
    return _rpn(e[1]) + _rpn(e[2]) + [(1, PLUS if e[0] == 1 else STAR)]


def _shape(rng, k, leaf, ctors, skew):
    """Random binary tree with k internal nodes; ctors are the binary constructor indices."""
    if k == 0: return leaf(rng)
    l = rng.choice((0, k - 1)) if rng.random() < skew else rng.randrange(k)
    return (rng.choice(ctors), _shape(rng, l, leaf, ctors, skew), _shape(rng, k - 1 - l, leaf, ctors, skew))


def _rand_expr(rng, k, hi=100):
    return _shape(rng, k, lambda r: (0, r.randrange(hi)), (1, 2), rng.choice((0.0, 0.2, 0.5)))


def _render(rng, e, ctx="top"):
    """Render an expr as text with the parentheses the grammar needs, plus some redundant ones."""
    if e[0] == 0:
        s = str(e[1])
        if rng.random() < 0.05: s = "0" * rng.randrange(1, 3) + s
        need = False
    else:
        op = "+" if e[0] == 1 else "*"
        cl, cr = ("addL", "addR") if e[0] == 1 else ("mulL", "mulR")
        s = _render(rng, e[1], cl) + op + _render(rng, e[2], cr)
        need = ctx in ("addR", "mulL", "mulR") if e[0] == 1 else ctx == "mulR"
    if need or rng.random() < 0.08: s = "(" + s + ")"
    return s


def _spaced(rng, s):
    out = []
    for i, ch in enumerate(s):
        if ch.isdigit() and i > 0 and s[i - 1].isdigit():
            out.append(ch); continue
        while rng.random() < 0.15: out.append(" ")
        out.append(ch)
    while rng.random() < 0.15: out.append(" ")
    return _txt("".join(out))


def _gen_expr_text(rng, n):
    return _spaced(rng, _render(rng, _rand_expr(rng, n // 3)))


def _gen_tok_text(rng, n):
    out = []
    while len(out) < n:
        r = rng.random()
        if r < 0.35:
            if rng.random() < 0.05: v = rng.randrange(M + 1)
            else: v = rng.randrange(10 ** rng.randrange(1, 6))
            if out and out[-1] in DIGITS: out.append(SP)  # keep every digit run < 2^24
            out += _txt(("0" if rng.random() < 0.05 else "") + str(v))
        elif r < 0.6: out.append(rng.choice((PLUS, MINUS, STAR)))
        elif r < 0.8: out.append(rng.choice((LP, RP)))
        else: out.append(SP)
    return out


EXPR_EDGES = [_txt("0"), _txt("7"), _txt("1+2*3"), _txt("(1+2)*3"), _txt(" 2 * ( 3 + 4 ) * 5 "),
              _txt("1+2+3+4"), _txt("16777215+1"), _txt("4096*4096"), _txt("((((9))))"), _txt("007*010"),
              _txt("2*3+4*5"), _txt("1+(2+3)")]


# ============================================================ helpers: vexpr rewrites
def _fold(e):
    if e[0] in (0, 3): return e
    a, b = _fold(e[1]), _fold(e[2])
    lit = lambda x, v=None: x[0] == 0 and (v is None or x[1] == v)
    if e[0] == 1:
        if lit(a) and lit(b): return (0, (a[1] + b[1]) & M)
        if lit(a, 0): return b
        if lit(b, 0): return a
        return (1, a, b)
    if lit(a) and lit(b): return (0, (a[1] * b[1]) & M)
    if lit(a, 0) or lit(b, 0): return (0, 0)
    if lit(a, 1): return b
    if lit(b, 1): return a
    return (2, a, b)


def _deriv(e):
    k = e[0]
    if k == 0: return (0, 0)
    if k == 3: return (0, 1) if e[1] == 0 else (0, 0)
    if k == 1: return (1, _deriv(e[1]), _deriv(e[2]))
    return (1, (2, _deriv(e[1]), e[2]), (2, e[1], _deriv(e[2])))


def _rand_vexpr(rng, k, lits, nvars, pvar=0.5):
    def leaf(r):
        return (3, r.randrange(nvars)) if r.random() < pvar else (0, r.choice(lits))
    return _shape(rng, k, leaf, (1, 2), rng.choice((0.0, 0.2, 0.5)))


def _depth(e):
    return 1 if e[0] in (0, 3) else 1 + max(_depth(e[1]), _depth(e[2]))


def _print(e):
    if e[0] == 0: return _txt(str(e[1]))
    return [LP] + _print(e[1]) + [PLUS if e[0] == 1 else STAR] + _print(e[2]) + [RP]


# ============================================================ helpers: boolean formulas
def _beval(f, env):
    k = f[0]
    if k <= 1: return k
    if k == 2: return env[f[1]]
    if k == 3: return 1 - _beval(f[1], env)
    a, b = _beval(f[1], env), _beval(f[2], env)
    return a & b if k == 4 else a | b


def _satcount(f):
    return sum(_beval(f, (m & 1, m >> 1 & 1, m >> 2 & 1)) for m in range(8))


def _nnf(f, neg=False):
    k = f[0]
    if k <= 1: return (1 - k,) if neg else f
    if k == 2: return (3, f) if neg else f
    if k == 3: return _nnf(f[1], not neg)
    c = (5 if k == 4 else 4) if neg else k
    return (c, _nnf(f[1], neg), _nnf(f[2], neg))


def _bvars(f):
    k = f[0]
    if k <= 1: return set()
    if k == 2: return {f[1]}
    return set().union(*(_bvars(x) for x in f[1:]))


def _rand_bool(rng, k, nvars, pnot=0.25, pconst=0.1):
    """Random formula with k binary/unary operator nodes."""
    if k == 0:
        if rng.random() < pconst: return (rng.randrange(2),)
        return (2, rng.randrange(nvars))
    if rng.random() < pnot: return (3, _rand_bool(rng, k - 1, nvars, pnot, pconst))
    l = rng.randrange(k)
    return (rng.choice((4, 5)), _rand_bool(rng, l, nvars, pnot, pconst), _rand_bool(rng, k - 1 - l, nvars, pnot, pconst))


# ============================================================ helpers: machines
def _vm(prog, check=False):
    """Run the stack machine. With check=True return None when the run underflows or a JZ is invalid."""
    st, pc, n = [], 0, len(prog)
    need = {0: 0, 1: 2, 2: 2, 3: 1, 4: 2, 5: 1, 6: 1, 7: 2}
    while pc < n:
        op, arg = prog[pc]
        if op not in need or len(st) < need[op]:
            if check: return None
            raise ValueError("stack underflow")
        nxt = pc + 1
        if op == 0: st.append(arg)
        elif op == 1: b = st.pop(); a = st.pop(); st.append((a + b) & M)
        elif op == 2: b = st.pop(); a = st.pop(); st.append((a * b) & M)
        elif op == 3: st.append(st[-1])
        elif op == 4: st[-1], st[-2] = st[-2], st[-1]
        elif op == 5: st.pop()
        elif op == 6:
            if st.pop() == 0: nxt = arg
        elif op == 7: b = st.pop(); a = st.pop(); st.append((a - b) & M)
        pc = nxt
    return st[-1] if st else 0


def _vm_ok(prog):
    for i, (op, arg) in enumerate(prog):
        if op > 7: return False
        if op == 6 and not (i < arg <= len(prog)): return False
    return _vm(prog, check=True) is not None


def _gen_vm(rng, n):
    prog = []
    for i in range(n):
        op = rng.choice((0, 0, 0, 1, 2, 3, 4, 5, 6, 6, 7))
        arg = rng.randrange(4) if op == 0 else (rng.randrange(i + 1, n + 1) if op == 6 else 0)
        prog.append((op, arg))
    # repair: turn the first instruction that underflows in the actual run into a PUSH, and rerun
    for _ in range(n + 1):
        st, pc, bad = 0, 0, None
        need = {0: 0, 1: 2, 2: 2, 3: 1, 4: 2, 5: 1, 6: 1, 7: 2}
        # simulate with real values to follow jumps
        stack = []
        while pc < n:
            op, arg = prog[pc]
            if len(stack) < need[op]: bad = pc; break
            nxt = pc + 1
            if op == 0: stack.append(arg)
            elif op in (1, 2, 7):
                b = stack.pop(); a = stack.pop()
                stack.append((a + b) & M if op == 1 else (a * b) & M if op == 2 else (a - b) & M)
            elif op == 3: stack.append(stack[-1])
            elif op == 4: stack[-1], stack[-2] = stack[-2], stack[-1]
            elif op == 5: stack.pop()
            elif op == 6 and stack.pop() == 0: nxt = arg
            pc = nxt
        if bad is None: return prog
        prog[bad] = (0, rng.randrange(4))
    return prog


def _regs(prog):
    r = [0, 0, 0, 0]
    for op, a, b in prog:
        if op == 0: r[a] = b
        elif op == 1: r[a] = (r[a] + r[b]) & M
        elif op == 2: r[a] = (r[a] - r[b]) & M
        elif op == 3: r[a] = (r[a] * r[b]) & M
        else: r[a] = r[b]
    return r


def _regs_ok(prog):
    return all(op < 5 and a < 4 and (op == 0 or b < 4) for op, a, b in prog)


def _gen_regs(rng, n):
    out = []
    for _ in range(n):
        op = rng.choice((0, 0, 1, 1, 2, 3, 3, 4))
        out.append((op, rng.randrange(4), rng.randrange(20) if op == 0 else rng.randrange(4)))
    return out


def _rle(xs):
    out = []
    for x in xs:
        if out and out[-1][0] == x: out[-1] = (x, out[-1][1] + 1)
        else: out.append((x, 1))
    return out


# ============================================================ programs: bracket languages
program("t4_paren_unmatched", "T4",
        "Input is a text made only of '(' = 40 and ')' = 41. Scan left to right keeping a count of currently open "
        "'(': a '(' increments it; a ')' decrements it if it is positive, otherwise that ')' is unmatched. Output the "
        "pair (number of unmatched ')', number of '(' still open at the end). The text is balanced iff the output is "
        "(0, 0). Empty text gives (0, 0).",
        TEXT, tup(u24, u24), _paren_unmatched, _gen_parens, S, TS,
        edges=[[], [LP], [RP], [LP, RP], [RP, LP], [LP, LP, RP], [RP, RP, LP, LP, LP], [LP, RP, RP, LP]],
        pre=_is_parens)

program("t4_paren_prefix", "T4",
        "Input is a text made only of '(' = 40 and ')' = 41. Output the length k of the longest prefix text[0:k] that "
        "is balanced (every ')' closes an earlier '(' and nothing is left open). The empty prefix is balanced, so the "
        "answer is at least 0; e.g. '()(()' gives 2 and '(())()' gives 6, ')()' gives 0.",
        TEXT, u24, _paren_prefix, _gen_prefix, S, TS,
        edges=[[], [LP], [RP], [LP, RP], _txt("()(()"), _txt("(())()"), _txt(")()"), _txt("()()))()")],
        pre=_is_parens)

program("t4_paren_depth", "T4",
        "Input is a balanced text of '(' = 40 and ')' = 41 (precondition). Output the maximum nesting depth: the "
        "largest number of '(' open at the same time. Empty text gives 0; '()' gives 1; '(()())' gives 2.",
        TEXT, u24, _paren_depth, _bal, S, TS,
        edges=[[], _txt("()"), _txt("(()())"), _txt("()()()"), _txt("((()))"), _txt("(()((())))")],
        pre=_balanced)

program("t4_paren_match", "T4",
        "Input is a balanced text of '(' = 40 and ')' = 41 (precondition). Output a list of the same length whose "
        "entry i is the index (from 0) of the parenthesis that matches text[i]: for a '(' the index of its closing "
        "')', for a ')' the index of its opening '('. E.g. '(())()' gives [3, 2, 1, 0, 5, 4].",
        TEXT, TEXT, _paren_match, _bal, S, TS,
        edges=[[], _txt("()"), _txt("(())()"), _txt("((()))"), _txt("()()()")],
        pre=_balanced)

program("t4_brackets3", "T4",
        "Input is a text made only of the six bracket codes '(' = 40, ')' = 41, '[' = 91, ']' = 93, '{' = 123, "
        "'}' = 125. Check it with a stack, scanning positions i = 0, 1, ... left to right: an opening bracket is "
        "pushed; a closing bracket at position i is an error if the stack is empty or its top is not the opening "
        "bracket of the same kind, and then the output is i + 1 (scanning stops at the first error); otherwise the "
        "top is popped. If no error occurs but the stack is non-empty at the end, output len(text) + 1. If the text "
        "is well nested (including empty), output 0. E.g. '([)]' gives 3, '(()' gives 4, '{[]}' gives 0.",
        TEXT, u24, _brackets3, _gen_brackets3, S, TS,
        edges=[[], [LP], [RB], _txt("([)]"), _txt("(()"), _txt("{[]}"), _txt("()[]{}"), _txt("{[()]}}"), [LC, RP]],
        pre=lambda s: all(c in ALL3 for c in s))

# ============================================================ programs: arithmetic text
program("t4_tokenize", "T4",
        CODES + "Input is a text using only those codes (not necessarily a valid expression). Split it into tokens "
        "left to right: a maximal run of consecutive digit characters is one number token (kind 0, value = the run "
        "read in decimal; leading zeros allowed; every value is < 2^24, precondition); each '+', '-' or '*' is an "
        "operator token (kind 1, value = its character code 43, 45 or 42); each '(' or ')' is a paren token (kind 2, "
        "value = 40 or 41); spaces produce no token but do separate numbers ('1 2' is two numbers). Output the list "
        "of (kind, value) pairs in text order. E.g. '12+(3 4)' gives [(0,12),(1,43),(2,40),(0,3),(0,4),(2,41)].",
        TEXT, TOK, _tokenize, _gen_tok_text, S, TS,
        edges=[[], _txt(" "), _txt("0"), _txt("12+(3 4)"), _txt("007-16777215"), _txt("))*(("), _txt("1 2  3")],
        pre=_tok_ok)

program("t4_parse", "T4",
        CODES + GRAMMAR + EXPR_T + "Output the syntax tree as an `expr`: a number becomes Lit(value); 'a+b' becomes "
        "Add(a, b) and 'a*b' becomes Mul(a, b); a chain a+b+c becomes Add(Add(a, b), c) (left-associative, same for "
        "*); parentheses produce no node of their own. E.g. '1+2*3' gives (1, (0, 1), (2, (0, 2), (0, 3))).",
        TEXT, EXPR, _parse, _gen_expr_text, S, TS, edges=EXPR_EDGES, pre=_valid_expr)

program("t4_eval_str", "T4",
        CODES + GRAMMAR + "Output the value of the expression with + and * computed mod 2^24 (standard precedence: "
        "'*' before '+', parentheses first). E.g. '1+2*3' gives 7, '(1+2)*3' gives 9, '16777215+1' gives 0.",
        TEXT, u24, lambda s: _eval(_parse(s)), _gen_expr_text, S, TS, edges=EXPR_EDGES, pre=_valid_expr)

program("t4_to_rpn", "T4",
        CODES + GRAMMAR + "Output the expression in reverse Polish (postfix) order as a list of (kind, value) "
        "tokens: a number is (0, value), '+' is (1, 43), '*' is (1, 42); no paren tokens. The order is exactly the "
        "post-order of the parse tree (as a shunting-yard conversion with left-associative operators produces): "
        "for a number output its token; for 'A + B' output RPN(A), then RPN(B), then (1, 43); likewise for '*' with "
        "(1, 42); a+b+c is (a+b)+c. E.g. '1+2*3' gives [(0,1),(0,2),(0,3),(1,42),(1,43)] and '1+2+3' gives "
        "[(0,1),(0,2),(1,43),(0,3),(1,43)].",
        TEXT, TOK, lambda s: _rpn(_parse(s)), _gen_expr_text, S, TS, edges=EXPR_EDGES, pre=_valid_expr)


def _eval_rpn(toks):
    st = []
    for k, v in toks:
        if k == 0: st.append(v); continue
        b = st.pop(); a = st.pop()
        st.append((a + b) & M if v == PLUS else (a - b) & M if v == MINUS else (a * b) & M)
    return st[0]


def _rpn_ok(toks):
    d = 0
    for k, v in toks:
        if k == 0 and v <= M: d += 1
        elif k == 1 and v in (PLUS, MINUS, STAR) and d >= 2: d -= 1
        else: return False
    return d == 1


def _gen_rpn(rng, n):
    def post(e):
        if e[0] == 0: return [(0, e[1])]
        return post(e[1]) + post(e[2]) + [(1, (PLUS, MINUS, STAR)[e[0] - 1])]
    k = n // 2
    return post(_shape(rng, k, lambda r: (0, r.randrange(100)), (1, 2, 3), rng.choice((0.0, 0.2, 0.5))))


program("t4_eval_rpn", "T4",
        "Input is a list of (kind, value) tokens in reverse Polish (postfix) notation: (0, n) pushes the number n; "
        "(1, 43) is '+', (1, 45) is '-', (1, 42) is '*'. An operator pops b (the top) then a (the one below it) and "
        "pushes a+b, a-b or a*b, each mod 2^24 (so 3 - 5 = 16777214). The list is guaranteed valid (precondition): "
        "operators never find fewer than 2 values on the stack and exactly one value remains at the end. Output "
        "that value. E.g. [(0,7),(0,2),(1,45)] gives 5.",
        TOK, u24, _eval_rpn, _gen_rpn, S, TS,
        edges=[[(0, 0)], [(0, 7), (0, 2), (1, MINUS)], [(0, 2), (0, 7), (1, MINUS)], [(0, BIG), (0, 1), (1, PLUS)],
               [(0, 4096), (0, 4096), (1, STAR)], [(0, 1), (0, 2), (0, 3), (1, STAR), (1, PLUS)]],
        pre=_rpn_ok)

# ============================================================ programs: expression trees
program("t4_eval_ast", "T4",
        EXPR_T + "Input is an `expr` tree. Output its value: Lit(n) is n, Add(a, b) is (value(a) + value(b)) mod "
        "2^24, Mul(a, b) is (value(a) * value(b)) mod 2^24.",
        EXPR, u24, _eval, lambda r, n: _rand_expr(r, n // 2), S, TS,
        edges=[(0, 0), (0, BIG), (1, (0, BIG), (0, 1)), (2, (0, 4096), (0, 4096)), (1, (0, 2), (2, (0, 3), (0, 4))),
               (2, (1, (0, 1), (0, 2)), (0, 3))])

program("t4_expr_depth", "T4",
        EXPR_T + "Input is an `expr` tree. Output its depth: Lit(n) has depth 1; Add(a, b) and Mul(a, b) have depth "
        "1 + max(depth(a), depth(b)).",
        EXPR, u24, _depth, lambda r, n: _rand_expr(r, n // 2), S, TS,
        edges=[(0, 5), (1, (0, 1), (0, 2)), (2, (1, (0, 1), (0, 2)), (0, 3)), (1, (0, 1), (2, (0, 2), (1, (0, 3), (0, 4))))])

program("t4_print", "T4",
        EXPR_T + CODES + "Input is an `expr` tree. Output it as a fully parenthesised text: Lit(n) prints as the "
        "decimal digits of n with no leading zeros ('0' for zero, no sign, no spaces); Add(a, b) prints as '(' "
        "print(a) '+' print(b) ')' and Mul(a, b) as '(' print(a) '*' print(b) ')'. So every Add/Mul, including the "
        "root, gets exactly one pair of parentheses and literals get none; no spaces anywhere. E.g. "
        "Add(Lit 1, Mul(Lit 20, Lit 3)) prints as '(1+(20*3))'.",
        EXPR, TEXT, _print, lambda r, n: _rand_expr(r, n // 3, 1000), S, TS,
        edges=[(0, 0), (0, 7), (0, BIG), (1, (0, 1), (2, (0, 20), (0, 3))), (2, (2, (0, 10), (0, 0)), (0, 105))])

program("t4_fold", "T4",
        VEXPR_T + "Input is a `vexpr` tree. Output its constant-folded form, computed bottom-up by this function F: "
        "F(Lit n) = Lit n and F(Var i) = Var i. For Add(a, b) and Mul(a, b), first compute A = F(a) and B = F(b) "
        "(left then right), then apply the FIRST matching rule: "
        "Add: (1) A = Lit x and B = Lit y -> Lit((x + y) mod 2^24); (2) A = Lit 0 -> B; (3) B = Lit 0 -> A; "
        "(4) otherwise Add(A, B). "
        "Mul: (1) A = Lit x and B = Lit y -> Lit((x * y) mod 2^24); (2) A = Lit 0 or B = Lit 0 -> Lit 0; "
        "(3) A = Lit 1 -> B; (4) B = Lit 1 -> A; (5) otherwise Mul(A, B). "
        "The rule result is not rewritten again (its parts are already folded). E.g. Mul(Var 0, Add(Lit 1, Lit 0)) "
        "gives Var 0; Mul(Add(Var 1, Lit 0), Lit 0) gives Lit 0; Add(Lit 2, Add(Lit 3, Var 0)) is unchanged.",
        VEXPR, VEXPR, _fold, lambda r, n: _rand_vexpr(r, n // 2, (0, 0, 1, 1, 2, 3, 5, 4096), 3), S, TS,
        edges=[(0, 3), (3, 2), (2, (3, 0), (1, (0, 1), (0, 0))), (2, (1, (3, 1), (0, 0)), (0, 0)),
               (1, (0, 2), (1, (0, 3), (3, 0))), (2, (0, 4096), (0, 4096)), (1, (3, 0), (3, 0)), (2, (0, 1), (3, 5))])

program("t4_deriv", "T4",
        VEXPR_T + "Input is a `vexpr` tree read as a polynomial in the variable x = Var 0 (every Var i with i != 0 "
        "is a constant). Output its symbolic derivative with respect to x, built by exactly these rules with NO "
        "simplification: D(Lit n) = Lit 0; D(Var 0) = Lit 1; D(Var i) = Lit 0 for i != 0; D(Add(a, b)) = "
        "Add(D(a), D(b)); D(Mul(a, b)) = Add(Mul(D(a), b), Mul(a, D(b))), where a and b are the original subtrees "
        "copied unchanged. E.g. D(Mul(Var 0, Lit 3)) = Add(Mul(Lit 1, Lit 3), Mul(Var 0, Lit 0)).",
        VEXPR, VEXPR, _deriv, lambda r, n: _rand_vexpr(r, n // 2, range(10), 2), S, TS,
        edges=[(0, 5), (3, 0), (3, 1), (1, (3, 0), (0, 2)), (2, (3, 0), (0, 3)), (2, (3, 0), (3, 0)),
               (2, (2, (3, 0), (3, 1)), (3, 0))])

# ============================================================ programs: boolean formulas
program("t4_sat_count", "T4",
        BOOL_T + "Input is a `bool` formula whose Var indices are all in 0..2 (precondition). Output the number of "
        "assignments (v0, v1, v2) in {0,1}^3 (8 in total) that make the formula true, with the usual meanings: False "
        "is 0, True is 1, Var i is vi, Not(a) = 1 - a, And(a, b) = a AND b, Or(a, b) = a OR b. Variables that do not "
        "occur still count (Var 0 alone gives 4; True gives 8; False gives 0).",
        BOOL, u24, _satcount, lambda r, n: _rand_bool(r, n // 2, 3), S, TS,
        edges=[(0,), (1,), (2, 0), (3, (2, 2)), (4, (2, 0), (2, 1)), (5, (2, 0), (5, (2, 1), (2, 2))),
               (4, (2, 0), (3, (2, 0))), (4, (4, (2, 0), (2, 1)), (2, 2))],
        pre=lambda f: all(i < 3 for i in _bvars(f)))

program("t4_nnf", "T4",
        BOOL_T + "Input is a `bool` formula. Output its negation normal form, defined by the function N(f) = P(f) "
        "with two mutually recursive rewrites P (positive) and Q (negated, meaning the result is equivalent to "
        "Not f): P(False) = False; P(True) = True; P(Var i) = Var i; P(Not a) = Q(a); P(And(a, b)) = "
        "And(P(a), P(b)); P(Or(a, b)) = Or(P(a), P(b)); Q(False) = True; Q(True) = False; Q(Var i) = Not(Var i); "
        "Q(Not a) = P(a); Q(And(a, b)) = Or(Q(a), Q(b)); Q(Or(a, b)) = And(Q(a), Q(b)). Children keep their left/"
        "right order. In the output Not appears only directly around a Var. No other simplification is done.",
        BOOL, BOOL, _nnf, lambda r, n: _rand_bool(r, n // 2, 4, 0.4), S, TS,
        edges=[(0,), (3, (1,)), (3, (2, 7)), (3, (3, (2, 1))), (3, (4, (2, 0), (3, (2, 1)))),
               (3, (5, (0,), (4, (2, 2), (2, 3)))), (4, (3, (3, (3, (2, 0)))), (1,))])

# ============================================================ programs: machines and encodings
program("t4_stack_vm", "T4",
        "Input is a program for a stack machine: a list of instructions (opcode, arg), indexed from 0. Values are "
        "u24 and arithmetic is mod 2^24. The machine starts with an empty stack and pc = 0 and repeats: if pc = "
        "len(program), halt; otherwise execute instruction pc and go to pc + 1 unless stated. Opcodes: 0 PUSH (push "
        "arg); 1 ADD (pop b, pop a, push a+b); 2 MUL (pop b, pop a, push a*b); 3 DUP (push a copy of the top); "
        "4 SWAP (exchange the top two values); 5 POP (discard the top); 6 JZ (pop x; if x = 0 set pc = arg, else go "
        "to pc + 1); 7 SUB (pop b, pop a, push a-b). arg is ignored by every opcode except PUSH and JZ. "
        "Preconditions: opcodes are 0..7; every JZ at index i has i < arg <= len(program) (forward jumps only, so the "
        "run takes at most len(program) steps); no instruction actually executed finds too few values on the stack. "
        "Output the top of the stack at halt, or 0 if the stack is empty.",
        TOK, u24, _vm, _gen_vm, S, TS,
        edges=[[], [(0, 5)], [(0, 5), (5, 0)], [(0, 2), (0, 3), (7, 0)], [(0, 3), (3, 0), (2, 0)],
               [(0, 1), (0, 2), (4, 0), (7, 0)], [(0, 0), (6, 3), (0, 9), (0, 4)], [(0, 1), (6, 3), (0, 9), (0, 4)],
               [(0, 0), (6, 2), (0, 7)]],
        pre=_vm_ok)

program("t4_regmachine", "T4",
        "Input is a straight-line program for a machine with 4 registers r0..r3, all starting at 0: a list of "
        "instructions (op, a, b) executed once each in order. Arithmetic is mod 2^24 and the right-hand side is "
        "computed from the register values before the write. Ops: 0 LOADI (r[a] = b, b is a literal); 1 ADD "
        "(r[a] = r[a] + r[b]); 2 SUB (r[a] = r[a] - r[b]); 3 MUL (r[a] = r[a] * r[b]); 4 MOV (r[a] = r[b]). "
        "a and b may be the same register (ADD 1 1 doubles r1; SUB 2 2 zeroes r2). Preconditions: op is 0..4, "
        "a is 0..3, and b is 0..3 for ops 1..4. Output the list [r0, r1, r2, r3] of final register values.",
        list_of(tup(u24, u24, u24)), TEXT, _regs, _gen_regs, S, TS,
        edges=[[], [(0, 2, 7)], [(0, 0, 5), (1, 0, 0), (4, 3, 0)], [(0, 1, 1), (2, 1, 0), (2, 1, 1)],
               [(0, 0, 4096), (3, 0, 0)], [(0, 0, 3), (0, 1, 5), (2, 0, 1), (4, 2, 0)]],
        pre=_regs_ok)

program("t4_rle_encode", "T4",
        "Input is a list of u24. Output its run-length encoding: the list of pairs (value, count), one per maximal "
        "run of equal consecutive elements, in order, where count >= 1 is the run length. Empty list gives []. "
        "E.g. [5, 5, 2, 5] gives [(5, 2), (2, 1), (5, 1)].",
        TEXT, TOK, _rle, lambda r, n: [r.randrange(3) for _ in range(n)], S, TS,
        edges=[[], [0], [BIG, BIG], [5, 5, 2, 5], [1, 2, 3], [7] * 9])
