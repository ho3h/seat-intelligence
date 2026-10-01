# ---- ccp: pull-based label propagation with pointer jumping, over tuple tries.
# A: adjacency trie, leaf = Braun tree of neighbour ids. D: label trie, leaf = label (every leaf, padding too,
# starts with its own id). One round: every vertex reads its neighbours' labels and its label's label with
# keyed lookups into the previous round's trie (lookups are independent: no update thread), takes the min
# (or max), and the round's change flags are OR-reduced. Converges to the component min (max).
def walkp(es, A, l, m):
  match es:
    case List/Nil:
      return A
    case List/Cons:
      (u, v) = es.head
      return walkp(es.tail, pushb(pushb(A, u, l, m, v), v, l, m, u), l, m)

def ids(l, base):
  switch l:
    case 0:
      return base
    case _:
      h = 1 << (l-1)
      return (ids(l-1, base), ids(l-1, base + h))

def mn(a, b):
  return a - (a > b) * (a - b)

def mx(a, b):
  return a + (b > a) * (b - a)

def nbmin(t, D, l, m):
  match t:
    case Br/Leaf:
      return 16777215
    case Br/Node:
      return mn(get(D, t.e, l, m), mn(nbmin(t.l, D, l, m), nbmin(t.r, D, l, m)))

def nbmax(t, D, l, m):
  match t:
    case Br/Leaf:
      return 0
    case Br/Node:
      return mx(get(D, t.e, l, m), mx(nbmax(t.l, D, l, m), nbmax(t.r, D, l, m)))

def stepn(A, S, D, lv, l, m):
  switch lv:
    case 0:
      x = mn(S, mn(nbmin(A, D, l, m), get(D, S, l, m)))
      return (x, x < S)
    case _:
      (a1, a2) = A
      (s1, s2) = S
      (x1, c1) = stepn(a1, s1, D, lv-1, l, m)
      (x2, c2) = stepn(a2, s2, D, lv-1, l, m)
      return ((x1, x2), c1 | c2)

def stepx(A, S, D, lv, l, m):
  switch lv:
    case 0:
      x = mx(S, mx(nbmax(A, D, l, m), get(D, S, l, m)))
      return (x, x > S)
    case _:
      (a1, a2) = A
      (s1, s2) = S
      (x1, c1) = stepx(a1, s1, D, lv-1, l, m)
      (x2, c2) = stepx(a2, s2, D, lv-1, l, m)
      return ((x1, x2), c1 | c2)

def loopn(A, D, l, m):
  (D2, any) = stepn(A, D, D, l, l, m)
  if any:
    return loopn(A, D2, l, m)
  else:
    return D2

def loopx(A, D, l, m):
  (D2, any) = stepx(A, D, D, l, l, m)
  if any:
    return loopx(A, D2, l, m)
  else:
    return D2

def ccmin(A, n, l, m):
  return loopn(A, ids(l, 0), l, m)

def ccmax(A, n, l, m):
  return loopx(A, ids(l, 0), l, m)
