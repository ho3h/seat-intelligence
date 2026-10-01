def prog(x):
  (n, pairs) = x
  return count_isolated(n, 0, pairs, 0)

def count_isolated(n, i, pairs, acc):
  if i == n:
    return acc
  else:
    found = has_node(i, pairs)
    if found == 0:
      return count_isolated(n, i + 1, pairs, acc + 1)
    else:
      return count_isolated(n, i + 1, pairs, acc)

def has_node(id, pairs):
  match pairs:
    case List/Nil:
      return 0
    case List/Cons:
      (u, v) = pairs.head
      if u == id:
        return 1
      else:
        if v == id:
          return 1
        else:
          return has_node(id, pairs.tail)
