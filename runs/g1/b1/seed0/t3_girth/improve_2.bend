def prog(x):
  (n, edges) = x
  sentinel = n + 4
  adj = empty_adj(n)
  adj2 = build_adj(edges, adj)
  if has_triangle(n, adj2, 0):
    return 3
  else:
    degrees = graph_degrees(adj2)
    alive = ones(n)
    leaves = initial_leaves(degrees, 0, n, List/Nil)
    (degrees2, alive2) = peel(leaves, List/Nil, degrees, alive, adj2)
    core_adj = filter_graph(adj2, alive2)
    answer = all_sources(n, 0, sentinel, core_adj, alive2, sentinel)
    if answer == sentinel:
      return 0
    else:
      return answer

def empty_adj(n):
  if n == 0:
    return List/Nil
  else:
    return List/Cons(List/Nil, empty_adj(n - 1))

def ones(n):
  if n == 0:
    return List/Nil
  else:
    return List/Cons(1, ones(n - 1))

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def graph_degrees(adj):
  match adj:
    case List/Nil:
      return List/Nil
    case List/Cons:
      return List/Cons(list_length(adj.head), graph_degrees(adj.tail))

def adj_at(xs, i):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return adj_at(xs.tail, i - 1)

def info_at(xs, i):
  match xs:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return info_at(xs.tail, i - 1)

def num_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return num_at(xs.tail, i - 1)

def set_adj_at(xs, i, value):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_adj_at(xs.tail, i - 1, value))

def set_info_at(xs, i, value):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_info_at(xs.tail, i - 1, value))

def set_num_at(xs, i, value):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_num_at(xs.tail, i - 1, value))

def build_adj(edges, adj):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (a, b) = edges.head
      if a == b:
        return build_adj(edges.tail, adj)
      else:
        a_neighbors = adj_at(adj, a)
        adj1 = set_adj_at(adj, a, List/Cons(b, a_neighbors))
        b_neighbors = adj_at(adj1, b)
        adj2 = set_adj_at(adj1, b, List/Cons(a, b_neighbors))
        return build_adj(edges.tail, adj2)

def has_triangle(n, adj, u):
  if u == n:
    return 0
  else:
    neighbors = adj_at(adj, u)
    if triangle_neighbor(neighbors, neighbors, adj):
      return 1
    else:
      return has_triangle(n, adj, u + 1)

def triangle_neighbor(neighbors, original, adj):
  match neighbors:
    case List/Nil:
      return 0
    case List/Cons:
      other_neighbors = adj_at(adj, neighbors.head)
      if lists_intersect(original, other_neighbors):
        return 1
      else:
        return triangle_neighbor(neighbors.tail, original, adj)

def lists_intersect(xs, ys):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if list_contains(ys, xs.head):
        return 1
      else:
        return lists_intersect(xs.tail, ys)

def list_contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return list_contains(xs.tail, value)

def initial_leaves(degrees, i, n, acc):
  if i == n:
    return acc
  else:
    d = num_at(degrees, i)
    if d <= 1:
      return initial_leaves(degrees, i + 1, n, List/Cons(i, acc))
    else:
      return initial_leaves(degrees, i + 1, n, acc)

def peel(front, back, degrees, alive, adj):
  match front:
    case List/Nil:
      match back:
        case List/Nil:
          return (degrees, alive)
        case List/Cons:
          return peel(reverse_list(back, List/Nil), List/Nil, degrees, alive, adj)
    case List/Cons:
      u = front.head
      if num_at(alive, u) == 0:
        return peel(front.tail, back, degrees, alive, adj)
      else:
        alive2 = set_num_at(alive, u, 0)
        neighbors = adj_at(adj, u)
        (degrees2, back2) = peel_neighbors(neighbors, degrees, alive2, back)
        return peel(front.tail, back2, degrees2, alive2, adj)

def peel_neighbors(neighbors, degrees, alive, back):
  match neighbors:
    case List/Nil:
      return (degrees, back)
    case List/Cons:
      v = neighbors.head
      if num_at(alive, v) == 0:
        return peel_neighbors(neighbors.tail, degrees, alive, back)
      else:
        d = num_at(degrees, v) - 1
        degrees2 = set_num_at(degrees, v, d)
        if d <= 1:
          back2 = List/Cons(v, back)
        else:
          back2 = back
        return peel_neighbors(neighbors.tail, degrees2, alive, back2)

def filter_graph(adj, alive):
  match adj:
    case List/Nil:
      return List/Nil
    case List/Cons:
      return List/Cons(filter_neighbors(adj.head, alive), filter_graph(adj.tail, alive))

def filter_neighbors(neighbors, alive):
  match neighbors:
    case List/Nil:
      return List/Nil
    case List/Cons:
      v = neighbors.head
      rest = filter_neighbors(neighbors.tail, alive)
      if num_at(alive, v) == 1:
        return List/Cons(v, rest)
      else:
        return rest

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))

def empty_info(n, sentinel):
  if n == 0:
    return List/Nil
  else:
    return List/Cons((sentinel, sentinel), empty_info(n - 1, sentinel))

def all_sources(n, s, sentinel, adj, alive, best):
  if best == 4:
    return 4
  else:
    if s == n:
      return best
    else:
      if num_at(alive, s) == 0:
        return all_sources(n, s + 1, sentinel, adj, alive, best)
      else:
        info = empty_info(n, sentinel)
        info2 = set_info_at(info, s, (0, sentinel))
        front = List/Cons((s, 0, sentinel), List/Nil)
        found = bfs_loop(front, List/Nil, info2, adj, n, sentinel, best)
        if found == 4:
          return 4
        else:
          return all_sources(n, s + 1, sentinel, adj, alive, found)

def bfs_loop(front, back, info, adj, n, sentinel, best):
  if best == 4:
    return 4
  else:
    match front:
      case List/Nil:
        match back:
          case List/Nil:
            return best
          case List/Cons:
            return bfs_loop(reverse_list(back, List/Nil), List/Nil, info, adj, n, sentinel, best)
      case List/Cons:
        (u, du, pu) = front.head
        if best < sentinel:
          if du * 2 >= best:
            return best
          else:
            neighbors = adj_at(adj, u)
            (info2, back2, best2) = scan_neighbors(neighbors, u, du, pu, back, info, n, sentinel, best)
            return bfs_loop(front.tail, back2, info2, adj, n, sentinel, best2)
        else:
          neighbors = adj_at(adj, u)
          (info2, back2, best2) = scan_neighbors(neighbors, u, du, pu, back, info, n, sentinel, best)
          return bfs_loop(front.tail, back2, info2, adj, n, sentinel, best2)

def scan_neighbors(neighbors, u, du, pu, back, info, n, sentinel, best):
  if best == 4:
    return (info, back, 4)
  else:
    match neighbors:
      case List/Nil:
        return (info, back, best)
      case List/Cons:
        v = neighbors.head
        (info2, back2, best2) = visit_neighbor(v, u, du, pu, back, info, n, sentinel, best)
        return scan_neighbors(neighbors.tail, u, du, pu, back2, info2, n, sentinel, best2)

def visit_neighbor(v, u, du, pu, back, info, n, sentinel, best):
  if v == u:
    return (info, back, best)
  else:
    (dv, pv) = info_at(info, v)
    if dv == sentinel:
      info2 = set_info_at(info, v, (du + 1, u))
      back2 = List/Cons((v, du + 1, u), back)
      return (info2, back2, best)
    else:
      if pv == u:
        return (info, back, best)
      else:
        if pu == v:
          return (info, back, best)
        else:
          candidate = du + dv + 1
          if candidate <= n:
            if candidate < best:
              return (info, back, candidate)
            else:
              return (info, back, best)
          else:
            return (info, back, best)
