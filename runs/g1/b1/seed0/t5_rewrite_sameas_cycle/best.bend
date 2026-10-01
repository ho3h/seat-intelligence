def prog(xs):
  n = list_size(xs)
  return check_nodes(xs, n, 0)

def list_size(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_size(xs.tail)

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def walk(xs, start, current, remaining):
  if remaining == 0:
    return 0
  else:
    next = get_at(xs, current)
    if next == current:
      return 0
    else:
      if next == start:
        return 1
      else:
        return walk(xs, start, next, remaining - 1)

def check_nodes(xs, n, i):
  if i == n:
    return 0
  else:
    found = walk(xs, i, i, n)
    if found == 1:
      return 1
    else:
      return check_nodes(xs, n, i + 1)
