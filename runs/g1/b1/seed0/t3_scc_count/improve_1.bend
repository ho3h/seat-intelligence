def prog(x):
  (n, edges) = x
  adj = add_edges(edges, make_rows(n))
  zeros = make_zeros(n)
  active = make_zeros(n)
  state = ((zeros, zeros), ((active, []), (1, 0)))
  return run_vertices(0, n, adj, state)

def make_rows(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons([], make_rows(n - 1))

def make_zeros(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(0, make_zeros(n - 1))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      switch i:
        case 0:
          return xs.head
        case _:
          return get_at(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      switch i:
        case 0:
          return List/Cons(value, xs.tail)
        case _:
          return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def add_edges(edges, adj):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      row = get_at(adj, u)
      adj2 = set_at(adj, u, List/Cons(v, row))
      return add_edges(edges.tail, adj2)

def run_vertices(v, n, adj, state):
  if v < n:
    ((indices, lows), ((active, stack), (next_idx, count))) = state
    if get_at(indices, v) == 0:
      state2 = visit(v, adj, state)
      return run_vertices(v + 1, n, adj, state2)
    else:
      return run_vertices(v + 1, n, adj, state)
  else:
    ((indices, lows), ((active, stack), (next_idx, count))) = state
    return count

def visit(v, adj, state):
  ((indices, lows), ((active, stack), (next_idx, count))) = state
  indices2 = set_at(indices, v, next_idx)
  lows2 = set_at(lows, v, next_idx)
  active2 = set_at(active, v, 1)
  stack2 = List/Cons(v, stack)
  state2 = ((indices2, lows2), ((active2, stack2), (next_idx + 1, count)))
  row = get_at(adj, v)
  state3 = visit_neighbors(row, v, adj, state2)
  ((indices3, lows3), ((active3, stack3), (next_idx3, count3))) = state3
  if get_at(lows3, v) == get_at(indices3, v):
    (active4, stack4) = pop_component(stack3, v, active3)
    return ((indices3, lows3), ((active4, stack4), (next_idx3, count3 + 1)))
  else:
    return state3

def visit_neighbors(neighbors, v, adj, state):
  match neighbors:
    case List/Nil:
      return state
    case List/Cons:
      w = neighbors.head
      ((indices, lows), ((active, stack), (next_idx, count))) = state
      if get_at(indices, w) == 0:
        state2 = visit(w, adj, state)
        ((indices2, lows2), ((active2, stack2), (next_idx2, count2))) = state2
        low_v = get_at(lows2, v)
        low_w = get_at(lows2, w)
        if low_w < low_v:
          lows3 = set_at(lows2, v, low_w)
          state3 = ((indices2, lows3), ((active2, stack2), (next_idx2, count2)))
        else:
          state3 = state2
        return visit_neighbors(neighbors.tail, v, adj, state3)
      else:
        if get_at(active, w) == 1:
          low_v = get_at(lows, v)
          index_w = get_at(indices, w)
          if index_w < low_v:
            lows2 = set_at(lows, v, index_w)
            state2 = ((indices, lows2), ((active, stack), (next_idx, count)))
          else:
            state2 = state
          return visit_neighbors(neighbors.tail, v, adj, state2)
        else:
          return visit_neighbors(neighbors.tail, v, adj, state)

def pop_component(stack, v, active):
  match stack:
    case List/Nil:
      return (active, [])
    case List/Cons:
      active2 = set_at(active, stack.head, 0)
      if stack.head == v:
        return (active2, stack.tail)
      else:
        return pop_component(stack.tail, v, active2)
