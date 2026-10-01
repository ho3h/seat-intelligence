# The physics (author primer)

This is the fixed medium. It is HVM2 v2.0.22 (pinned), a runtime for interaction combinators with a few
small fixed extensions. You write a **net**: a graph of nodes joined by wires. The runtime rewrites it
until nothing more can fire; what is left at the root is the answer. Nothing about the runtime is learned
or negotiable. Everything you can express, you express as nodes and wires.

## Nodes

Every node has one **principal port** (facing "up", toward whatever it is attached to) and, for most,
two **auxiliary ports** (facing "down"). A tree written in text is a node with its principal port at the
top and its sub-trees hanging from its auxiliary ports.

| Text | Node | Ports |
| --- | --- | --- |
| `*` | eraser (ERA) | principal only |
| `(a b)` | constructor (CON) | principal, aux `a`, aux `b` |
| `{a b}` | duplicator (DUP) | principal, aux `a`, aux `b` |
| `7`, `0`, `16777215` | number (NUM), an unsigned 24-bit value | principal only |
| `$(f r)` | operator (OPR) | principal, aux `f`, aux `r` |
| `?(c r)` | switch (SWI) | principal, aux `c`, aux `r` |
| `@name` | reference (REF) to a definition | principal only |
| `x`, `foo`, `acc` | a wire end. Each wire name appears **exactly twice** in a definition | |

Wires are linear: a name is used exactly twice (once at each end of the wire). To use a value in two
places you must duplicate it with a DUP; to drop a value you must erase it with `*` (write `x ~ *`
as a redex, or put `*` where the value would go).

## Text format

A **book** is a list of definitions:

```
@name = <tree>
  & <tree> ~ <tree>
  & <tree> ~ <tree>
```

The tree after `=` is the definition's root: its interface to the rest of the net. Each `& A ~ B` line is
an **active pair**: two trees whose principal ports are connected. Active pairs are where computation
happens. A wire name may connect the two sides of a pair to anything else in the same definition.
`//` starts a comment that runs to the end of the line. Definition names use letters, digits and `_`. Names beginning `__` are reserved.

## The rewrites (all six, plus the extensions)

Two principal ports facing each other rewrite by their kinds:

* **CON ~ CON** and **DUP ~ DUP** annihilate: `(a1 a2) ~ (b1 b2)` becomes `a1 ~ b1` and `a2 ~ b2`.
  (Same for DUP.)
* **CON ~ DUP** commute: each is copied through the other. `(a1 a2) ~ {b1 b2}` becomes a crossed square of
  four nodes, so both `b` sides receive a copy of the constructor.
* **ERA ~ CON/DUP/OPR/SWI**: the eraser spreads: both aux ports of the node get an eraser. **ERA ~ ERA/NUM/REF**: both vanish.
* **NUM ~ CON** or **NUM ~ DUP**: the number copies itself into both aux ports (numbers are freely copyable).
  **NUM ~ NUM** and **NUM ~ REF**: both vanish.
* **REF ~ CON/DUP/OPR/SWI**: the reference is replaced by a fresh copy of the definition it names, whose
  root then meets the other side. This is how you recurse. A REF can only be copied by a DUP if its
  definition contains no DUP nodes (otherwise the run aborts with "attempt to clone a non-affine global
  reference").
* **NUM ~ OPR** (arithmetic) and **NUM ~ SWI** (branching), described below.
* Every other combination (a node against OPR/SWI etc.) commutes like CON ~ DUP.
* **A wire name joined to a tree** simply substitutes it.

There are **no labels**: every DUP is the same kind of DUP, and two DUPs that meet annihilate rather than
commute. So do not duplicate a structure that still contains an unresolved duplicator in a way that makes two
different duplications meet. Copy data that is already computed, or copy before you build.

Evaluation order is not yours to control and it is parallel: any active pair can fire at any time.

## Arithmetic: `$(f r)`

`n ~ $([op] $(m r))` reduces to `r` = `n op m`. The number `n` meets the outer OPR; `[op]` is an
operator symbol; the inner `$(m r)` supplies the second operand and receives the result. The operand order
is `n op m` (first operand is the one that arrives first), so subtraction is `n - m`.

Operators: `+ - * / % = ! < > & | ^ << >>` written `[+]` etc. `=` and `!` (not-equal) and `< >` return 1 or 0.
Arithmetic wraps modulo 2^24. Division or remainder by zero crashes the run (a failed test); guard against it.
A preset operand form also exists: `$([+1] r)` is "add 1 to whatever arrives and send it to r";
`$([*2] $([+1] r))` chains two of these.
Operands can be wires that carry numbers later; the operator waits.

## Branching: `?(c r)`

`n ~ ?((zero succ) r)` where `c = (zero succ)` is a constructor holding two branches:

* if `n == 0`: `zero ~ r`.
* if `n > 0`: `succ ~ (n-1 r)`.

So `r` is the **context** handed to whichever branch runs, and the succ branch additionally receives
`n-1` as its first argument. The branch you do not take is erased automatically. Branches are usually
references to definitions, and `r` is a constructor tuple carrying the variables the branches need. To
branch on a boolean from `=`/`<`/`>` use `z ~ ?((no yes) ctx)` with `no = (context pattern)` and
`yes = (* (context pattern))` (the `*` swallows the `0`).

## Data encodings (the same ones the task interface uses)

* number: a NUM. Booleans are 0 and 1.
* tuple `(a, b, c)`: `(a (b c))`. Right-nested constructors; the last element is not wrapped.
* list: `Nil = (0 *)`, `Cons = (1 (head tail))`. To take a list apart, connect it to `(?(cases ctx) payload)`:
  the tag (0 or 1) drives the switch, the payload goes to the branch through a wire.

* any other variant type (trees, expressions, ...): variant number `i` (counting from 0 in the order the task lists its
  variants) with fields `f1 ... fk` is `(i payload)`, where `payload` is `*` for no fields, `f1` alone for one field, and
  `(f1 (f2 ... fk))` right-nested for more. The list is the same rule: Nil is variant 0, Cons is variant 1 with `(head tail)`.
  A node's fields are themselves encoded values (a sub-tree is another `(i payload)`).

Functions are just constructors: a function of two arguments is `(arg1 (arg2 result))`; calling it is
`@f ~ (x (y out))`.

## The task interface

Each task is a program `@prog` whose root is `(input output)`. The harness runs:

```
@main = r
  & @prog ~ (<the input, encoded as above> r)
```

so `@prog = (input_pattern out)` with `input_pattern` taking the input apart and `out` receiving the
answer. Large inputs arrive as chains of references that expand lazily; you never see them written out.
Your answer must reach `out` as the **canonical encoding** of the output type: no leftover active
pairs, no unresolved wires, no partial data. You may define any number of helper definitions.
Do not define `@main`. Do not use names beginning `__`.

Numbers are 24-bit and wrap. Anything larger must be represented as data (lists of digits, for example).

## A worked example (not one of the tasks)

Count the zeros in a list of numbers. The input is a list; the output is a number.

```
@prog = (l out)
  & @zc ~ (l (0 out))

@zc = ((?((@zc_nil @zc_cons) (pl (acc out))) pl) (acc out))

@zc_nil = (* (a a))

@zc_cons = (* ((h t) (acc out)))
  & h ~ $([=] $(0 z))
  & z ~ ?((@zc_no @zc_yes) (acc (t out)))

@zc_no = (acc (t out))
  & @zc ~ (t (acc out))

@zc_yes = (* (acc (t out)))
  & acc ~ $([+] $(1 acc2))
  & @zc ~ (t (acc2 out))
```

Read `@zc`: its first argument is a list cell `(tag payload)`; the tag goes to a switch whose context is
`(payload (acc out))`. Tag 0 runs `@zc_nil`, which erases the payload and returns `acc`. Tag 1 runs
`@zc_cons` (the `*` swallows the `0` from `n-1`), splits the payload into head `h` and tail `t`,
tests `h == 0`, and recurses with the updated accumulator.

## Where nets usually go wrong (read before writing)

* **Keep definitions small.** Write one statement per line and split anything longer than about six lines into helper
  definitions. Long single-line trees are where brackets go missing. Count your brackets before you answer.
* **Every wire has exactly two ends.** A value needed in two places must pass through a `{ }` duplicator; a value you do not
  need must be erased with `*`. The static check reports wires that appear once or more than twice.
* **A reference only expands when it meets a node.** Never hand `@name` straight to an output wire or leave it as an
  unconsumed leaf: it stays unexpanded and the result is not a value. Put constant data inline, for example `(0 *)`.
* **Every branch must deliver its output.** In each case of a switch, the output wire must end up connected to a finished
  value; a branch that forgets it leaves an unresolved wire in the result.
* **Recurse with a fresh context.** Each recursive call receives its own arguments and its own output wire.

## What you get back

Before your net runs, a static check reports parse errors, wires that do not appear exactly twice in a definition, and undefined references.
After that, you receive PASS, or the smallest failing input from a hidden suite with the
expected and actual outputs, or the runtime's error text. On a pass you also see interaction counts.
Fewer interactions and shorter chains of dependent rewrites are better, but correctness comes first.
