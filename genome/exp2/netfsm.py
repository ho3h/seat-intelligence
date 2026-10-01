"""Incremental character-level automaton over a model's response that forbids static wiring/bracket errors in the net.

Tracks the response as it is generated: PRE (free prose, e.g. `<think></think>`) until an opening ``` fence line (or a line
starting with `@`, mirroring the lenient extractor's unfenced fallback), then CODE
(the net), then POST after the closing fence. Only CODE is constrained. Within CODE the lexer mirrors genome.verify.lint_net /
genome.netast.tokens (comments `//`, op literals `[..]` + digits, numbers `[-+]?\\d[\\w.]*`, refs `@[\\w/]+`, wires
`[A-Za-z_]\\w*`), per definition. A character is ILLEGAL if it would

  (a) close a bracket with no (or a mismatched) opener; end a statement (`&`, `~`, a new definition, the closing fence, EOS)
      while brackets are open; put `~` in a root tree or a second `~` in a redex; end a redex that has no `~`;
  (b) complete a third occurrence of a wire name in the current definition (a word is complete when a non-word char follows);
  (c) end a definition (a line starting with `@`, the `=` of a new header, the closing fence, EOS) while some wire of the current
      definition has appeared only once;
  or put text other than whitespace/comments/a definition header before the first definition, or `=` outside a header.

A token is legal iff every character of its decoded string is legal (checked on a clone). EOS is checked with `end()`.
After the closing fence only EOS is allowed (declared: prevents a second code block from replacing the first at extraction).
"""
from __future__ import annotations

PRE, PRELINE, CODE, POST = 0, 1, 2, 3
N, W, R, NUM, OP, OPD, C = range(7)
_WCH = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_")
_WSTART = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
_DIG = frozenset("0123456789")
_WS = frozenset(" \t\r\n\x0b\x0c")
_CLOSE = {")": "(", "}": "{"}


class NetFSM:
    __slots__ = ("mode", "lex", "word", "slash", "line_ws", "hdr_cand", "hdr", "counts", "n_open", "stack", "stmt", "tilde",
                 "ndefs", "bt", "why")

    def __init__(self):
        self.mode = PRE; self.lex = N; self.word = ""; self.slash = False; self.line_ws = True
        self.hdr_cand = False; self.hdr = False; self.counts = {}; self.n_open = 0; self.stack = []
        self.stmt = None; self.tilde = 0; self.ndefs = 0; self.bt = 0; self.why = None

    def clone(self):
        c = NetFSM.__new__(NetFSM)
        c.mode = self.mode; c.lex = self.lex; c.word = self.word; c.slash = self.slash; c.line_ws = self.line_ws
        c.hdr_cand = self.hdr_cand; c.hdr = self.hdr; c.counts = dict(self.counts); c.n_open = self.n_open
        c.stack = list(self.stack); c.stmt = self.stmt; c.tilde = self.tilde; c.ndefs = self.ndefs; c.bt = self.bt; c.why = None
        return c

    # ------------------------------------------------------------------ helpers
    def _fail(self, why):
        self.why = why; return False

    def _clean(self):
        """May the current definition end here?"""
        if self.stmt is None: return self._fail("no definition yet")
        if self.stack: return self._fail("open brackets at end of definition")
        if self.stmt == "redex" and self.tilde != 1: return self._fail("redex without ~ at end of definition")
        if self.n_open: return self._fail("wire seen once at end of definition")
        return True

    def _word_end(self):
        w = self.word; self.lex = N; self.word = ""
        c = self.counts.get(w, 0)
        if c >= 2: return self._fail(f"third use of wire {w}")
        self.counts[w] = c + 1; self.n_open += 1 if c == 0 else -1
        return True

    def _ref_end(self):
        self.lex = N; self.hdr = self.hdr_cand; self.hdr_cand = False

    # ------------------------------------------------------------------ one character
    def step(self, ch: str) -> bool:
        m = self.mode
        if m == POST: return True if ch in _WS else self._fail("text after closing fence")
        if m == PRE:
            if ch == "@" and self.line_ws:  # unfenced net (the lenient extractor's fallback: first line starting with @)
                self.mode = CODE; self.bt = 0
                return self._normal(ch)
            if ch == "`":
                self.bt += 1
                if self.bt == 3: self.mode = PRELINE; self.bt = 0
            else: self.bt = 0
            if ch == "\n": self.line_ws = True
            elif ch not in _WS: self.line_ws = False
            return True
        if m == PRELINE:
            if ch == "\n": self.mode = CODE; self.line_ws = True; self.lex = N
            return True
        # CODE: fence close = third consecutive backtick anywhere (the extractor's regex ignores comments)
        if ch == "`":
            self.bt += 1
            if self.bt == 3:
                if self.lex == W and not self._word_end(): return False
                if self.lex == R: self._ref_end()
                if not self._clean(): return False
                self.mode = POST; return True
        else: self.bt = 0
        lx = self.lex
        if lx == C:
            if ch == "\n": self.lex = N; self.line_ws = True
            return True
        if lx == OP:
            if ch == "]": self.lex = OPD
            return True
        if lx == W:
            if ch in _WCH: self.word += ch; return True
            if not self._word_end(): return False
        elif lx == NUM:
            if ch in _WCH or ch == ".": return True
            self.lex = N
        elif lx == OPD:
            if ch in _DIG: return True
            self.lex = N
        elif lx == R:
            if ch == "/":
                if self.slash: self.slash = False; self._ref_end(); self.lex = C; return True
                self.slash = True; return True
            if ch in _WCH: self.slash = False; return True
            self.slash = False; self._ref_end()
        return self._normal(ch)

    def _normal(self, ch):
        if ch in _WS:
            if ch == "\n": self.line_ws = True
            self.slash = False
            return True
        if self.slash:
            self.slash = False
            if ch == "/": self.lex = C; return True
        if ch == "/": self.slash = True; self.line_ws = False; return True
        hdr = self.hdr; self.hdr = False
        if ch == "=":
            if not hdr: return self._fail("= outside a definition header")
            # header complete: a new definition starts
            self.counts = {}; self.n_open = 0; self.stack = []; self.stmt = "root"; self.tilde = 0; self.ndefs += 1
            self.line_ws = False; return True
        lws = self.line_ws; self.line_ws = False
        if ch == "@":
            if lws:
                if self.stmt is not None and not self._clean(): return False
                self.hdr_cand = True
            elif self.stmt is None: return self._fail("text before first definition")
            self.lex = R; self.slash = False; return True
        if self.stmt is None: return self._fail("text before first definition")
        if ch in _WSTART: self.lex = W; self.word = ch; return True
        if ch in _DIG: self.lex = NUM; return True
        if ch == "(" or ch == "{": self.stack.append(ch); return True
        if ch == ")" or ch == "}":
            if not self.stack or self.stack[-1] != _CLOSE[ch]: return self._fail("unmatched closing bracket")
            self.stack.pop(); return True
        if ch == "&":
            if self.stack: return self._fail("& with open brackets")
            if self.stmt == "redex" and self.tilde != 1: return self._fail("redex without exactly one ~")
            self.stmt = "redex"; self.tilde = 0; return True
        if ch == "~":
            if self.stmt != "redex" or self.tilde or self.stack: return self._fail("misplaced ~")
            self.tilde = 1; return True
        if ch == "[": self.lex = OP; return True
        return True  # * $ ? ! + - and anything else the lexer skips

    # ------------------------------------------------------------------ strings / end
    def feed(self, s: str) -> bool:
        for ch in s:
            if not self.step(ch): return False
        return True

    def end(self) -> bool:
        """May the response end here (EOS)?"""
        if self.mode != CODE: return True
        if self.lex == W and not self._word_end(): return False
        return self._clean()

    def allows(self, s: str) -> bool:
        return self.clone().feed(s)

    def allows_end(self) -> bool:
        return self.clone().end()
