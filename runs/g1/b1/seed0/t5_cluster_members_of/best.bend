def prog(x):
  (n, target, pairs) = x
  reached = closure(pairs, List/Cons(target, List/Nil))
  return members(n, reached, [])

def has(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return has(xs.tail, value)

def scan_edges(pairs, reached, changed):
  match pairs:
    case List/Nil:
      return (reached, changed)
    case List/Cons:
      (u, v) = pairs.head
      if has(reached, u) == 1:
        if has(reached, v) == 1:
          return scan_edges(pairs.tail, reached, changed)
        else:
          return scan_edges(pairs.tail, List/Cons(v, reached), 1)
      else:
        if has(reached, v) == 1:
          return scan_edges(pairs.tail, List/Cons(u, reached), 1)
        else:
          return scan_edges(pairs.tail, reached, changed)

def closure(pairs, reached):
  (updated, changed) = scan_edges(pairs, reached, 0)
  if changed == 1:
    return closure(pairs, updated)
  else:
    return updated

def members(i, reached, acc):
  if i == 0:
    return acc
  else:
    node = i - 1
    if has(reached, node) == 1:
      return members(node, reached, List/Cons(node, acc))
    else:
      return members(node, reached, acc)
