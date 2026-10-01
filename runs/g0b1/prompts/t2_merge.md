You are an author in the Genome experiment. You write a program in Bend (a functional language that compiles to HVM2 nets).

Rules of this experiment:
- Use no tools beyond the one read that gave you this file. Do not read any other file, do not run anything, do not search. Answer from this prompt alone.
- Your submission must be Bend code defining `def prog(x)` (plus helpers). Do not define `main`.
- After each submission you may receive feedback from a hidden test suite. Fix the code and resubmit the complete program.

# PRIMER

# Bend primer (author primer for the human-language route, B1)

Bend is a high-level language that compiles to HVM2 nets and runs them in parallel. You write ordinary functional
code; the compiler produces the net. Version: Bend 0.2.38. Indentation matters (2 spaces).

## Values
* Numbers are unsigned 24-bit (`u24`) by default and wrap modulo 2^24: `0`, `7`, `16777215`.
  Operators: `+ - * / % == != < > <= >= & | ^ << >>`. Division or remainder by zero crashes the run.
* Tuples: `(a, b)`, `(a, b, c)`. Destructure with `(a, b) = p`.
* Lists (built in): `[]`, `[1, 2, 3]`, `List/Nil`, `List/Cons(head, tail)`.
* User types: `type Name: A | B { field1, field2 }` (already declared for you when a task uses one, see the task text).
  Construct with `Name/B(x, y)`, nullary with `Name/A`. Fields are read after a `match` as `v.field1`.

## Statements
* Every function body ends in `return <expr>`.
* Bindings: `x = expr` on its own line.
* Branching: `if cond:` / `else:` with indented bodies, both branches must `return`.
* Matching on a constructor: `match v:` then `case List/Nil:` and `case List/Cons:` (and for a list cell the fields are
  `v.head` and `v.tail`). You must handle every case. Type name and constructor must be spelled exactly; a misspelled
  case is silently treated as a catch-all variable, which is a common mistake.
* Matching on a number: `switch n:` with `case 0:` and `case _:` (in the `_` branch, `n-1` is the predecessor).
* Recursion is the loop. There are no mutable variables and no `while`. Accumulators are extra parameters.
* `fold xs:` is structural recursion sugar: `fold xs:` then `case List/Nil:` and `case List/Cons:`, recursing as `f(xs.tail)`.

## The task interface
Define `def prog(x):` taking the single input value (for several inputs `x` is a tuple; unpack it with `(a, b) = x`)
and returning the output value. You may define helper functions. Do not define `main`. Everything runs on HVM2, and each
call is a tiny graph rewrite, so fewer calls and shorter chains of dependent calls are faster; correctness comes first.
Outputs must be the plain data value (no unevaluated lazy parts): the harness folds them.

## A worked example (not one of the tasks)
Count the zeros in a list of numbers:

```
def prog(xs):
  return count_zeros(xs, 0)

def count_zeros(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      if xs.head == 0:
        return count_zeros(xs.tail, acc + 1)
      else:
        return count_zeros(xs.tail, acc)
```

## What you get back
After each submission: PASS, or the smallest failing input from a hidden suite with the expected and actual outputs, or the
Bend compiler / runtime error text. On a pass you also see interaction counts.


# YOUR TASK

## Task `t2_merge`

Input is (xs, ys), both sorted ascending. One sorted ascending list of all their elements.

- Input type:  `tuple[list[u24], list[u24]]`
- Output type: `list[u24]`
- `prog` takes the input (a tuple if there are several inputs) and returns the output. Lists are Bend lists; numbers are u24.
- While you author, imagine inputs of size parameter 0 to 16. The verifier also runs inputs up to 16x larger than that, edge cases, and fresh random inputs. One wrong answer, crash or hang fails the program.

## Reply format

Reply with exactly one fenced code block containing your complete Bend code (it must define `prog`), optionally preceded by a
few words. Nothing after the code block.
