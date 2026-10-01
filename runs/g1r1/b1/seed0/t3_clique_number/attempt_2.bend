def prog(x):
  (n, edges) = x
  adj0 = empty_adjacency(n)
  adj = build_adjacency(edges, adj0)
  vertices = make_vertices(0, n)
  if n == 0:
    return expand(vertices, adj, 0, 0)
  else:
    return expand(vertices, adj, 0, 1)

def empty_adjacency(n):
  if n == 0:
    return []
  else:
    return List/Cons([], empty_adjacency(n - 1))

def make_vertices(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_vertices(i + 1, n))

def build_adjacency(edges, adj):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      adj1 = add_at(adj, u, v)
      adj2 = add_at(adj1, v, u)
      return build_adjacency(edges.tail, adj2)

def add_at(xs, idx, val):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return List/Cons(List/Cons(val, xs.head), xs.tail)
      else:
        return List/Cons(xs.head, add_at(xs.tail, idx - 1, val))

def get_at(xs, idx):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if idx == 0:
        return xs.head
      else:
        return get_at(xs.tail, idx - 1)

def has_edge(u, v, adj):
  row = get_at(adj, u)
  return contains(row, v)

def contains(xs, val):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == val:
        return 1
      else:
        return contains(xs.tail, val)

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def touches_any(v, xs, adj):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if has_edge(v, xs.head, adj) == 1:
        return 1
      else:
        return touches_any(v, xs.tail, adj)

def build_color_class(remaining, picked, rejected, adj):
  match remaining:
    case List/Nil:
      return (picked, rejected)
    case List/Cons:
      if touches_any(remaining.head, picked, adj) == 1:
        return build_color_class(
          remaining.tail,
          picked,
          List/Cons(remaining.head, rejected),
          adj
        )
      else:
        return build_color_class(
          remaining.tail,
          List/Cons(remaining.head, picked),
          rejected,
          adj
        )

def add_color(picked, color, acc):
  match picked:
    case List/Nil:
      return acc
    case List/Cons:
      return List/Cons((picked.head, color), add_color(picked.tail, color, acc))

def color_loop(remaining, adj, color, acc):
  match remaining:
    case List/Nil:
      return acc
    case List/Cons:
      (picked, rejected) = build_color_class(remaining, [], [], adj)
      acc2 = add_color(picked, color, acc)
      return color_loop(rejected, adj, color + 1, acc2)

def colorize(candidates, adj):
  return color_loop(candidates, adj, 1, [])

def ordered_neighbors(order, v, adj):
  match order:
    case List/Nil:
      return []
    case List/Cons:
      (u, color) = order.head
      rest = ordered_neighbors(order.tail, v, adj)
      if has_edge(u, v, adj) == 1:
        return List/Cons(u, rest)
      else:
        return rest

def expand(candidates, adj, size, best):
  if size > best:
    return expand_with_best(candidates, adj, size, size)
  else:
    return expand_with_best(candidates, adj, size, best)

def expand_with_best(candidates, adj, size, best):
  if size + list_length(candidates) <= best:
    return best
  else:
    match candidates:
      case List/Nil:
        return best
      case List/Cons:
        order = colorize(candidates, adj)
        return expand_order(order, adj, size, best)

def expand_order(order, adj, size, best):
  match order:
    case List/Nil:
      return best
    case List/Cons:
      (v, bound) = order.head
      if size + bound <= best:
        return best
      else:
        next_candidates = ordered_neighbors(order.tail, v, adj)
        best1 = expand(next_candidates, adj, size + 1, best)
        return expand_order(order.tail, adj, size, best1)
