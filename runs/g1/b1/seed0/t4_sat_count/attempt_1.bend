def prog(formula):
  return count_assignments(formula, 7)

def count_assignments(formula, n):
  switch n:
    case 0:
      return eval_formula(formula, 0, 0, 0)
    case _:
      v0 = n % 2
      v1 = (n / 2) % 2
      v2 = n / 4
      current = eval_formula(formula, v0, v1, v2)
      return current + count_assignments(formula, n - 1)

def eval_formula(formula, v0, v1, v2):
  match formula:
    case Gbool/C0:
      return 0
    case Gbool/C1:
      return 1
    case Gbool/C2:
      if formula.f0 == 0:
        return v0
      else:
        if formula.f0 == 1:
          return v1
        else:
          return v2
    case Gbool/C3:
      return 1 - eval_formula(formula.f0, v0, v1, v2)
    case Gbool/C4:
      a = eval_formula(formula.f0, v0, v1, v2)
      b = eval_formula(formula.f1, v0, v1, v2)
      return a * b
    case Gbool/C5:
      a = eval_formula(formula.f0, v0, v1, v2)
      b = eval_formula(formula.f1, v0, v1, v2)
      if a + b > 0:
        return 1
      else:
        return 0
