def prog(x):
  (n, edges) = x
  sentinel = n + 4
  adj = empty_adj(n)
  adj2 = build_adj(edges, adj)
  answer = all_sources(n, 0, sentinel, adj2, sentinel)
  if answer == sentinel:
    return 0
  else:
    return answer

def empty_adj(n):
  if n == 0:
    return List/Nil
  else:
    return List/Cons(List/Nil, empty_adj(n - 1))

def empty_info(n, sentinel):
  if n == 0:
    return List/Nil
  else:
    return List/Cons((sentinel, sentinel), empty_info(n - 1, sentinel))

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

def all_sources(n, s, sentinel, adj, best):
  if best == 3:
    return 3
  else:
    if s == n:
      return best
    else:
      info = empty_info(n, sentinel)
      info2 = set_info_at(info, s, (0, sentinel))
      front = List/Cons((s, 0, sentinel), List/Nil)
      found = bfs_loop(front, List/Nil, info2, adj, n, sentinel, best)
      if found == 3:
        return 3
      else:
        return all_sources(n, s + 1, sentinel, adj, found)

def rev_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return rev_list(xs.tail, List/Cons(xs.head, acc))

def bfs_loop(front, back, info, adj, n, sentinel, best):
  if best == 3:
    return 3
  else:
    match front:
      case List/Nil:
        match back:
          case List/Nil:
            return best
          case List/Cons:
            return bfs_loop(rev_list(back, List/Nil), List/Nil, info, adj, n, sentinel, best)
      case List/Cons:
        (u, du, pu) = front.head
        neighbors = adj_at(adj, u)
        (info2, back2, best2) = scan_neighbors(neighbors, u, du, pu, back, info, n, sentinel, best)
        return bfs_loop(front.tail, back2, info2, adj, n, sentinel, best2)

def scan_neighbors(neighbors, u, du, pu, back, info, n, sentinel, best):
  if best == 3:
    return (info, back, 3)
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
