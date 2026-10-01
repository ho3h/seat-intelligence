def prog(x):
  (n, edges) = x
  adj = build_adj(edges, n, 0)
  rows = build_reachability(adj, n, 0)
  return build_labels(rows, n, 0)

def build_adj(edges, n, i):
  if i == n:
    return List/Nil
  else:
    row = collect_outgoing(edges, i)
    rest = build_adj(edges, n, i + 1)
    return List/Cons(row, rest)

def collect_outgoing(edges, source):
  match edges:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (u, v) = edges.head
      rest = collect_outgoing(edges.tail, source)
      if u == source:
        return List/Cons(v, rest)
      else:
        return rest

def nth_row(rows, i):
  match rows:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return rows.head
      else:
        return nth_row(rows.tail, i - 1)

def push_all(vertices, stack):
  match vertices:
    case List/Nil:
      return stack
    case List/Cons:
      rest = push_all(vertices.tail, stack)
      return List/Cons(vertices.head, rest)

def contains(xs, target):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == target:
        return 1
      else:
        return contains(xs.tail, target)

def dfs(adj, stack, seen):
  match stack:
    case List/Nil:
      return seen
    case List/Cons:
      vertex = stack.head
      rest = stack.tail
      if contains(seen, vertex) == 1:
        return dfs(adj, rest, seen)
      else:
        outgoing = nth_row(adj, vertex)
        next_stack = push_all(outgoing, rest)
        next_seen = List/Cons(vertex, seen)
        return dfs(adj, next_stack, next_seen)

def build_reachability(adj, n, source):
  if source == n:
    return List/Nil
  else:
    start = List/Cons(source, List/Nil)
    reachable = dfs(adj, start, List/Nil)
    rest = build_reachability(adj, n, source + 1)
    return List/Cons(reachable, rest)

def find_min_label(rows, row, source, candidate, n, best):
  if candidate == n:
    return best
  else:
    if contains(row, candidate) == 1:
      reverse_reachable = nth_row(rows, candidate)
      if contains(reverse_reachable, source) == 1:
        if candidate < best:
          return find_min_label(rows, row, source, candidate + 1, n, candidate)
        else:
          return find_min_label(rows, row, source, candidate + 1, n, best)
      else:
        return find_min_label(rows, row, source, candidate + 1, n, best)
    else:
      return find_min_label(rows, row, source, candidate + 1, n, best)

def build_labels(rows, n, source):
  if source == n:
    return List/Nil
  else:
    row = nth_row(rows, source)
    label = find_min_label(rows, row, source, 0, n, source)
    rest = build_labels(rows, n, source + 1)
    return List/Cons(label, rest)
