def prog(x):
  (n, edges) = x
  adj = build_adj(edges, n, 0, 0)
  reverse_adj = build_adj(edges, n, 0, 1)
  (seen, finish) = first_pass(adj, n, 0, List/Nil, List/Nil)
  (assigned, pairs) = second_pass(finish, reverse_adj, List/Nil, List/Nil)
  return make_output(pairs, n, 0)

def build_adj(edges, n, i, reverse):
  if i == n:
    return List/Nil
  else:
    row = collect_outgoing(edges, i, reverse)
    rest = build_adj(edges, n, i + 1, reverse)
    return List/Cons(row, rest)

def collect_outgoing(edges, source, reverse):
  match edges:
    case List/Nil:
      return List/Nil
    case List/Cons:
      (u, v) = edges.head
      rest = collect_outgoing(edges.tail, source, reverse)
      if reverse == 0:
        if u == source:
          return List/Cons(v, rest)
        else:
          return rest
      else:
        if v == source:
          return List/Cons(u, rest)
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

def contains(xs, target):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == target:
        return 1
      else:
        return contains(xs.tail, target)

def push_enter(vertices, stack):
  match vertices:
    case List/Nil:
      return stack
    case List/Cons:
      return push_enter(vertices.tail, List/Cons((vertices.head, 0), stack))

def first_dfs(adj, stack, seen, finish):
  match stack:
    case List/Nil:
      return (seen, finish)
    case List/Cons:
      (vertex, kind) = stack.head
      rest = stack.tail
      if kind == 1:
        return first_dfs(adj, rest, seen, List/Cons(vertex, finish))
      else:
        if contains(seen, vertex) == 1:
          return first_dfs(adj, rest, seen, finish)
        else:
          outgoing = nth_row(adj, vertex)
          next_seen = List/Cons(vertex, seen)
          exit_stack = List/Cons((vertex, 1), rest)
          next_stack = push_enter(outgoing, exit_stack)
          return first_dfs(adj, next_stack, next_seen, finish)

def first_pass(adj, n, source, seen, finish):
  if source == n:
    return (seen, finish)
  else:
    start = List/Cons((source, 0), List/Nil)
    (next_seen, next_finish) = first_dfs(adj, start, seen, finish)
    return first_pass(adj, n, source + 1, next_seen, next_finish)

def push_vertices(vertices, stack):
  match vertices:
    case List/Nil:
      return stack
    case List/Cons:
      return push_vertices(vertices.tail, List/Cons(vertices.head, stack))

def collect_component(adj, stack, assigned, component):
  match stack:
    case List/Nil:
      return (assigned, component)
    case List/Cons:
      vertex = stack.head
      rest = stack.tail
      if contains(assigned, vertex) == 1:
        return collect_component(adj, rest, assigned, component)
      else:
        outgoing = nth_row(adj, vertex)
        next_stack = push_vertices(outgoing, rest)
        next_assigned = List/Cons(vertex, assigned)
        next_component = List/Cons(vertex, component)
        return collect_component(adj, next_stack, next_assigned, next_component)

def minimum(xs, best):
  match xs:
    case List/Nil:
      return best
    case List/Cons:
      if xs.head < best:
        return minimum(xs.tail, xs.head)
      else:
        return minimum(xs.tail, best)

def add_labels(vertices, label, pairs):
  match vertices:
    case List/Nil:
      return pairs
    case List/Cons:
      return add_labels(vertices.tail, label, List/Cons((vertices.head, label), pairs))

def second_pass(order, reverse_adj, assigned, pairs):
  match order:
    case List/Nil:
      return (assigned, pairs)
    case List/Cons:
      vertex = order.head
      rest = order.tail
      if contains(assigned, vertex) == 1:
        return second_pass(rest, reverse_adj, assigned, pairs)
      else:
        start = List/Cons(vertex, List/Nil)
        (next_assigned, component) = collect_component(reverse_adj, start, assigned, List/Nil)
        label = minimum(component, vertex)
        next_pairs = add_labels(component, label, pairs)
        return second_pass(rest, reverse_adj, next_assigned, next_pairs)

def find_label(pairs, vertex):
  match pairs:
    case List/Nil:
      return vertex
    case List/Cons:
      (member, label) = pairs.head
      if member == vertex:
        return label
      else:
        return find_label(pairs.tail, vertex)

def make_output(pairs, n, vertex):
  if vertex == n:
    return List/Nil
  else:
    label = find_label(pairs, vertex)
    rest = make_output(pairs, n, vertex + 1)
    return List/Cons(label, rest)
