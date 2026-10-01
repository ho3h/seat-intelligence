def prog(x):
  (n, pairs) = x
  labels = make_labels(0, n)
  return converge(pairs, labels)

def make_labels(i, n):
  if i < n:
    rest = make_labels(i + 1, n)
    return List/Cons(i, rest)
  else:
    return List/Nil

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        rest = set_at(xs.tail, i - 1, value)
        return List/Cons(xs.head, rest)

def max2(a, b):
  if a > b:
    return a
  else:
    return b

def edge_sweep(pairs, labels, changed):
  match pairs:
    case List/Nil:
      return (labels, changed)
    case List/Cons:
      (u, v) = pairs.head
      lu = get_at(labels, u)
      lv = get_at(labels, v)
      if lu == lv:
        return edge_sweep(pairs.tail, labels, changed)
      else:
        m = max2(lu, lv)
        labels1 = set_at(labels, u, m)
        labels2 = set_at(labels1, v, m)
        return edge_sweep(pairs.tail, labels2, 1)

def converge(pairs, labels):
  (labels2, changed) = edge_sweep(pairs, labels, 0)
  if changed == 0:
    return labels2
  else:
    return converge(pairs, labels2)
