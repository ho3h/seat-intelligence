def prog(x):
  (n, edges) = x
  adj0 = make_adj(0, n)
  adj = build_adj(edges, adj0)
  values = make_values(n, 0)
  (clock, disc, low, arts) = visit_all(0, n, adj, n, 0, values, values, values)
  return count_marks(arts)

def make_adj(i, n):
  if i == n:
    return []
  else:
    return List/Cons([], make_adj(i + 1, n))

def build_adj(edges, adj):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      adj1 = add_neighbor(adj, u, v)
      adj2 = add_neighbor(adj1, v, u)
      return build_adj(edges.tail, adj2)

def add_neighbor(adj, index, neighbor):
  match adj:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return List/Cons(List/Cons(neighbor, adj.head), adj.tail)
      else:
        rest = add_neighbor(adj.tail, index - 1, neighbor)
        return List/Cons(adj.head, rest)

def get_adj(adj, index):
  match adj:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return adj.head
      else:
        return get_adj(adj.tail, index - 1)

def make_values(i, n):
  if i == n:
    return []
  else:
    return List/Cons(0, make_values(i + 1, n))

def get_value(values, index):
  match values:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return values.head
      else:
        return get_value(values.tail, index - 1)

def set_value(values, index, value):
  match values:
    case List/Nil:
      return []
    case List/Cons:
      if index == 0:
        return List/Cons(value, values.tail)
      else:
        rest = set_value(values.tail, index - 1, value)
        return List/Cons(values.head, rest)

def visit_all(i, n, adj, sentinel, clock, disc, low, arts):
  if i == n:
    return (clock, disc, low, arts)
  else:
    if get_value(disc, i) != 0:
      return visit_all(i + 1, n, adj, sentinel, clock, disc, low, arts)
    else:
      (clock2, disc2, low2, arts2) = visit_vertex(i, sentinel, n, adj, clock, disc, low, arts)
      return visit_all(i + 1, n, adj, sentinel, clock2, disc2, low2, arts2)

def visit_vertex(u, parent, sentinel, adj, clock, disc, low, arts):
  clock2 = clock + 1
  disc2 = set_value(disc, u, clock2)
  low2 = set_value(low, u, clock2)
  neighbors = get_adj(adj, u)
  return visit_neighbors(neighbors, u, parent, sentinel, adj, clock2, disc2, low2, arts, 0)

def visit_neighbors(neighbors, u, parent, sentinel, adj, clock, disc, low, arts, children):
  match neighbors:
    case List/Nil:
      if parent == sentinel:
        if children > 1:
          arts2 = set_value(arts, u, 1)
          return (clock, disc, low, arts2)
        else:
          return (clock, disc, low, arts)
      else:
        return (clock, disc, low, arts)
    case List/Cons:
      v = neighbors.head
      if v == parent:
        return visit_neighbors(neighbors.tail, u, parent, sentinel, adj, clock, disc, low, arts, children)
      else:
        if get_value(disc, v) == 0:
          (clock2, disc2, low2, arts2) = visit_vertex(v, u, sentinel, adj, clock, disc, low, arts)
          child_low = get_value(low2, v)
          u_low = get_value(low2, u)
          if child_low < u_low:
            low3 = set_value(low2, u, child_low)
          else:
            low3 = low2
          if parent != sentinel:
            u_disc = get_value(disc2, u)
            if child_low >= u_disc:
              arts3 = set_value(arts2, u, 1)
            else:
              arts3 = arts2
          else:
            arts3 = arts2
          return visit_neighbors(neighbors.tail, u, parent, sentinel, adj, clock2, disc2, low3, arts3, children + 1)
        else:
          neighbor_disc = get_value(disc, v)
          u_low = get_value(low, u)
          if neighbor_disc < u_low:
            low2 = set_value(low, u, neighbor_disc)
          else:
            low2 = low
          return visit_neighbors(neighbors.tail, u, parent, sentinel, adj, clock, disc, low2, arts, children)

def count_marks(values):
  match values:
    case List/Nil:
      return 0
    case List/Cons:
      if values.head == 1:
        return 1 + count_marks(values.tail)
      else:
        return count_marks(values.tail)
