def prog(p):
  n = length(p)
  if n == 0:
    return []
  else:
    (tree, rest) = build4(p, n)
    return run(tree, n, rounds(n))

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def rounds(n):
  if n <= 1:
    return 0
  else:
    return 1 + rounds((n + 1) / 2)

def build4(xs, n):
  if n <= 4:
    leaf = (at(xs, 0), at(xs, 1), at(xs, 2), at(xs, 3))
    return (leaf, drop(xs, n))
  else:
    q = n / 4
    r = n % 4
    if r > 0:
      s0 = q + 1
    else:
      s0 = q
    if r > 1:
      s1 = q + 1
    else:
      s1 = q
    if r > 2:
      s2 = q + 1
    else:
      s2 = q
    s3 = q
    (t0, rest0) = build4(xs, s0)
    (t1, rest1) = build4(rest0, s1)
    (t2, rest2) = build4(rest1, s2)
    (t3, rest3) = build4(rest2, s3)
    return (((t0, t1), (t2, t3)), rest3)

def at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return at(xs.tail, i - 1)

def drop(xs, n):
  if n == 0:
    return xs
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return drop(xs.tail, n - 1)

def run(tree, n, count):
  if count == 0:
    return flatten4(tree, n, [])
  else:
    updated = jump4(tree, tree, n, n)
    return run(updated, n, count - 1)

def jump4(current, full, total, size):
  if size <= 4:
    return jump_leaf(full, total, current, size)
  else:
    ((t0, t1), (t2, t3)) = current
    q = size / 4
    r = size % 4
    if r > 0:
      s0 = q + 1
    else:
      s0 = q
    if r > 1:
      s1 = q + 1
    else:
      s1 = q
    if r > 2:
      s2 = q + 1
    else:
      s2 = q
    s3 = q
    u0 = jump4(t0, full, total, s0)
    u1 = jump4(t1, full, total, s1)
    u2 = jump4(t2, full, total, s2)
    u3 = jump4(t3, full, total, s3)
    return ((u0, u1), (u2, u3))

def jump_leaf(full, total, leaf, size):
  (a, b, c, d) = leaf
  na = get4(full, a, total)
  if size == 1:
    return (na, 0, 0, 0)
  else:
    nb = get4(full, b, total)
    if size == 2:
      return (na, nb, 0, 0)
    else:
      nc = get4(full, c, total)
      if size == 3:
        return (na, nb, nc, 0)
      else:
        nd = get4(full, d, total)
        return (na, nb, nc, nd)

def get4(tree, index, size):
  if size <= 4:
    (a, b, c, d) = tree
    if index == 0:
      return a
    else:
      if index == 1:
        return b
      else:
        if index == 2:
          return c
        else:
          return d
  else:
    ((t0, t1), (t2, t3)) = tree
    q = size / 4
    r = size % 4
    if r > 0:
      s0 = q + 1
    else:
      s0 = q
    if r > 1:
      s1 = q + 1
    else:
      s1 = q
    if r > 2:
      s2 = q + 1
    else:
      s2 = q
    s3 = q
    if index < s0:
      return get4(t0, index, s0)
    else:
      if index < s0 + s1:
        return get4(t1, index - s0, s1)
      else:
        if index < s0 + s1 + s2:
          return get4(t2, index - s0 - s1, s2)
        else:
          return get4(t3, index - s0 - s1 - s2, s3)

def flatten4(tree, size, tail):
  if size <= 4:
    (a, b, c, d) = tree
    if size == 1:
      return List/Cons(a, tail)
    else:
      if size == 2:
        return List/Cons(a, List/Cons(b, tail))
      else:
        if size == 3:
          return List/Cons(a, List/Cons(b, List/Cons(c, tail)))
        else:
          return List/Cons(a, List/Cons(b, List/Cons(c, List/Cons(d, tail))))
  else:
    ((t0, t1), (t2, t3)) = tree
    q = size / 4
    r = size % 4
    if r > 0:
      s0 = q + 1
    else:
      s0 = q
    if r > 1:
      s1 = q + 1
    else:
      s1 = q
    if r > 2:
      s2 = q + 1
    else:
      s2 = q
    s3 = q
    tail3 = flatten4(t3, s3, tail)
    tail2 = flatten4(t2, s2, tail3)
    tail1 = flatten4(t1, s1, tail2)
    return flatten4(t0, s0, tail1)
