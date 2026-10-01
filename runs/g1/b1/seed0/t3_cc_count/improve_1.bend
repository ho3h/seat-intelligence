def prog(x):
  (n, edges) = x
  adj = build_adj(0, n, edges)
  return count_components(0, n, adj, [], 0)

def build_adj(i, n, edges):
  if i == n:
    return []
  else:
    ns = get_neighbors(i, edges)
    rest = build_adj(i + 1, n, edges)
    return List/Cons(ns, rest)

def get_neighbors(v, edges):
  match edges:
    case List/Nil:
      return []
    case List/Cons:
      (a, b) = edges.head
      rest = get_neighbors(v, edges.tail)
      if a == v:
        return List/Cons(b, rest)
      else:
        if b == v:
          return List/Cons(a, rest)
        else:
          return rest

def count_components(i, n, adj, seen, components):
  if i == n:
    return components
  else:
    if contains(i, seen) == 1:
      return count_components(i + 1, n, adj, seen, components)
    else:
      seen2 = explore(List/Cons(i, []), adj, List/Cons(i, seen))
      return count_components(i + 1, n, adj, seen2, components + 1)

def explore(stack, adj, seen):
  match stack:
    case List/Nil:
      return seen
    case List/Cons:
      v = stack.head
      rest = stack.tail
      ns = get_at(v, adj)
      (seen2, stack2) = add_neighbors(ns, adj, seen, rest)
      return explore(stack2, adj, seen2)

def add_neighbors(ns, adj, seen, stack):
  match ns:
    case List/Nil:
      return (seen, stack)
    case List/Cons:
      v = ns.head
      rest = ns.tail
      if contains(v, seen) == 1:
        return add_neighbors(rest, adj, seen, stack)
      else:
        seen2 = List/Cons(v, seen)
        stack2 = List/Cons(v, stack)
        return add_neighbors(rest, adj, seen2, stack2)

def get_at(i, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(i - 1, xs.tail)

def contains(target, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == target:
        return 1
      else:
        return contains(target, xs.tail)
