def prog(x):
  n = inv_len(x, 0)
  (s, c) = inv_sort(x, n)
  return c

def inv_len(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return inv_len(xs.tail, acc + 1)

def inv_split(xs, k):
  switch k:
    case 0:
      return (List/Nil, xs)
    case _:
      match xs:
        case List/Nil:
          return (List/Nil, List/Nil)
        case List/Cons:
          (l, r) = inv_split(xs.tail, k-1)
          return (List/Cons(xs.head, l), r)

def inv_sort(xs, n):
  if n < 2:
    return (xs, 0)
  else:
    h = n / 2
    (a, b) = inv_split(xs, h)
    (sa, ca) = inv_sort(a, h)
    (sb, cb) = inv_sort(b, n - h)
    (m, cm) = inv_merge(sa, h, sb)
    return (m, ca + cb + cm)

def inv_merge(a, la, b):
  match a:
    case List/Nil:
      return (b, 0)
    case List/Cons:
      match b:
        case List/Nil:
          return (List/Cons(a.head, a.tail), 0)
        case List/Cons:
          if b.head < a.head:
            (m, c) = inv_merge(List/Cons(a.head, a.tail), la, b.tail)
            return (List/Cons(b.head, m), c + la)
          else:
            (m, c) = inv_merge(a.tail, la - 1, List/Cons(b.head, b.tail))
            return (List/Cons(a.head, m), c)
