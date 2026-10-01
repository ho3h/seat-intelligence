def prog(x):
  (n, r, edges) = x
  parents = make_filled(n, 16777215)
  return walk(r, 16777215, edges, parents)

def make_filled(n, value):
  if n == 0:
    return []
  else:
    return List/Cons(value, make_filled(n - 1, value))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def replace_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, replace_at(xs.tail, i - 1, value))

def walk(u, p, edges, parents):
  return scan_edges(u, p, edges, edges, parents)

def scan_edges(u, p, all_edges, rest, parents):
  match rest:
    case List/Nil:
      return parents
    case List/Cons:
      (a, b) = rest.head
      if a == u:
        if b == p:
          return scan_edges(u, p, all_edges, rest.tail, parents)
        else:
          parents1 = replace_at(parents, b, u)
          parents2 = walk(b, u, all_edges, parents1)
          return scan_edges(u, p, all_edges, rest.tail, parents2)
      else:
        if b == u:
          if a == p:
            return scan_edges(u, p, all_edges, rest.tail, parents)
          else:
            parents1 = replace_at(parents, a, u)
            parents2 = walk(a, u, all_edges, parents1)
            return scan_edges(u, p, all_edges, rest.tail, parents2)
        else:
          return scan_edges(u, p, all_edges, rest.tail, parents)
