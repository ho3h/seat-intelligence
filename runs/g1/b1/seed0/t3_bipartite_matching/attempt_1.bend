def prog(x):
  (a, b, edges) = x
  adj = build_adj(0, a, edges)
  mtch = make_list(b, a)
  return process_left(0, a, adj, mtch, 0)

def make_list(n, value):
  if n == 0:
    return []
  else:
    return List/Cons(value, make_list(n - 1, value))

def build_adj(i, a, edges):
  if i == a:
    return []
  else:
    neighbors = collect_neighbors(i, edges, [])
    rest = build_adj(i + 1, a, edges)
    return List/Cons(neighbors, rest)

def collect_neighbors(target, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      if u == target:
        return collect_neighbors(target, edges.tail, List/Cons(v, acc))
      else:
        return collect_neighbors(target, edges.tail, acc)

def list_get(xs, i):
  if i == 0:
    match xs:
      case List/Nil:
        return 0
      case List/Cons:
        return xs.head
  else:
    match xs:
      case List/Nil:
        return 0
      case List/Cons:
        return list_get(xs.tail, i - 1)

def list_set(xs, i, value):
  if i == 0:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(value, xs.tail)
  else:
    match xs:
      case List/Nil:
        return []
      case List/Cons:
        return List/Cons(xs.head, list_set(xs.tail, i - 1, value))

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def augment(u, adj, mtch, seen, sentinel):
  neighbors = list_get(adj, u)
  return try_neighbors(u, neighbors, adj, mtch, seen, sentinel)

def try_neighbors(u, neighbors, adj, mtch, seen, sentinel):
  match neighbors:
    case List/Nil:
      return (0, mtch, seen)
    case List/Cons:
      v = neighbors.head
      if contains(seen, v) == 1:
        return try_neighbors(u, neighbors.tail, adj, mtch, seen, sentinel)
      else:
        seen2 = List/Cons(v, seen)
        owner = list_get(mtch, v)
        if owner == sentinel:
          mtch2 = list_set(mtch, v, u)
          return (1, mtch2, seen2)
        else:
          (ok, mtch2, seen3) = augment(owner, adj, mtch, seen2, sentinel)
          if ok == 1:
            mtch3 = list_set(mtch2, v, u)
            return (1, mtch3, seen3)
          else:
            return try_neighbors(u, neighbors.tail, adj, mtch2, seen3, sentinel)

def process_left(i, a, adj, mtch, count):
  if i == a:
    return count
  else:
    (ok, mtch2, seen) = augment(i, adj, mtch, [], a)
    if ok == 1:
      return process_left(i + 1, a, adj, mtch2, count + 1)
    else:
      return process_left(i + 1, a, adj, mtch2, count)
