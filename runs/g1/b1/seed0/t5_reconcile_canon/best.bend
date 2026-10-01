def prog(x):
  (n, tau, cands) = x
  labels = make_labels(0, n)
  return process(cands, tau, labels)

def make_labels(i, n):
  if i == n:
    return List/Nil
  else:
    return List/Cons(i, make_labels(i + 1, n))

def process(cands, tau, labels):
  match cands:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v, score) = cands.head
      if score >= tau:
        merged = merge(labels, u, v)
        return process(cands.tail, tau, merged)
      else:
        return process(cands.tail, tau, labels)

def merge(labels, u, v):
  a = at(labels, u)
  b = at(labels, v)
  if a == b:
    return labels
  else:
    if a > b:
      return relabel(labels, b, a)
    else:
      return relabel(labels, a, b)

def at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return at(xs.tail, i - 1)

def relabel(xs, old, new):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if xs.head == old:
        return List/Cons(new, relabel(xs.tail, old, new))
      else:
        return List/Cons(xs.head, relabel(xs.tail, old, new))
