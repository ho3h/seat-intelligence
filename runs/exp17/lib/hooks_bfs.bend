# ---- hooks for BFS + shortest-path counting from source s = mode: labels are hop distances (65535 = unreached);
# after the last round every vertex appends its path count c(v) to its stream: c(s) = 1, otherwise the sum of c(w)
# over input neighbours w with d(w) + 1 == d(v). The switch waits only on distances, so c(w) of a vertex that is
# not strictly closer is never awaited (no cycles).
def lab0(mode, base):
  if base == mode:
    return 0
  else:
    return 65535

def upd(mode, lab, x):
  y = x + (x < 65535)
  return lab - (lab > y) * (lab - y)

def fin(mode, base, lab, ins):
  c = (base == mode) + csum(ins, lab)
  return ([c], c)

def csum(t, d):
  match t:
    case Br/Leaf:
      return 0
    case Br/Node:
      return cone(t.e, d) + csum(t.l, d) + csum(t.r, d)

def cone(s, d):
  match s:
    case List/Nil:
      return 0
    case List/Cons:
      if s.head + 1 == d:
        match s.tail:
          case List/Nil:
            return 0
          case List/Cons:
            return s.tail.head
      else:
        return 0
