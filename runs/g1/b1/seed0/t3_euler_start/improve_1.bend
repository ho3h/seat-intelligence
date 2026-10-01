def prog(x):
  (n, edges) = x
  adj0 = make_adj(n)
  (adj, vertices, odds) = build(edges, adj0, [], [])
  match vertices:
    case List/Nil:
      return 16777215
    case List/Cons:
      seen0 = make_flags(n)
      seen1 = set_num(seen0, vertices.head, 1)
      seen = visit_stack(List/Cons(vertices.head, List/Nil), adj, seen1)
      if count_seen(seen) != length(vertices):
        return 16777215
      else:
        odd_count = length(odds)
        if odd_count == 0:
          return smallest(vertices)
        else:
          if odd_count == 2:
            return smallest(odds)
          else:
            return 16777215

def make_adj(n):
  if n == 0:
    return List/Nil
  else:
    return List/Cons(List/Nil, make_adj(n - 1))

def make_flags(n):
  if n == 0:
    return List/Nil
  else:
    return List/Cons(0, make_flags(n - 1))

def get_adj(xs, i):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_adj(xs.tail, i - 1)

def set_adj(xs, i, value):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_adj(xs.tail, i - 1, value))

def get_num(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_num(xs.tail, i - 1)

def set_num(xs, i, value):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_num(xs.tail, i - 1, value))

def build(edges, adj, vertices, odds):
  match edges:
    case List/Nil:
      return (adj, vertices, odds)
    case List/Cons:
      (u, v) = edges.head
      neighbors_u = get_adj(adj, u)
      adj1 = set_adj(adj, u, List/Cons(v, neighbors_u))
      neighbors_v = get_adj(adj1, v)
      adj2 = set_adj(adj1, v, List/Cons(u, neighbors_v))
      vertices1 = insert(vertices, u)
      vertices2 = insert(vertices1, v)
      odds1 = toggle(odds, u)
      odds2 = toggle(odds1, v)
      return build(edges.tail, adj2, vertices2, odds2)

def visit_stack(stack, adj, seen):
  match stack:
    case List/Nil:
      return seen
    case List/Cons:
      neighbors = get_adj(adj, stack.head)
      return visit_neighbors(neighbors, stack.tail, adj, seen)

def visit_neighbors(neighbors, stack, adj, seen):
  match neighbors:
    case List/Nil:
      return visit_stack(stack, adj, seen)
    case List/Cons:
      v = neighbors.head
      if get_num(seen, v) == 0:
        seen1 = set_num(seen, v, 1)
        stack1 = List/Cons(v, stack)
        return visit_neighbors(neighbors.tail, stack1, adj, seen1)
      else:
        return visit_neighbors(neighbors.tail, stack, adj, seen)

def count_seen(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == 1:
        return 1 + count_seen(xs.tail)
      else:
        return count_seen(xs.tail)

def contains(xs, x):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == x:
        return 1
      else:
        return contains(xs.tail, x)

def insert(xs, x):
  if contains(xs, x) == 1:
    return xs
  else:
    return List/Cons(x, xs)

def remove_one(xs, x):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if xs.head == x:
        return xs.tail
      else:
        return List/Cons(xs.head, remove_one(xs.tail, x))

def toggle(xs, x):
  if contains(xs, x) == 1:
    return remove_one(xs, x)
  else:
    return List/Cons(x, xs)

def length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + length(xs.tail)

def smallest(xs):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      return smallest_from(xs.tail, xs.head)

def smallest_from(xs, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      if xs.head < best:
        return smallest_from(xs.tail, xs.head)
      else:
        return smallest_from(xs.tail, best)
