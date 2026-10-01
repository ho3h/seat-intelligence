def prog(x):
  (n, edges) = x
  disc = zeros(n)
  low = zeros(n)
  return count_roots(0, n, edges, disc, low, 0, 0)

def zeros(n):
  if n == 0:
    return []
  else:
    return List/Cons(0, zeros(n - 1))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def neighbors(edges, u):
  match edges:
    case List/Nil:
      return []
    case List/Cons:
      (a, b) = edges.head
      rest = neighbors(edges.tail, u)
      if a == u:
        return List/Cons(b, rest)
      else:
        if b == u:
          return List/Cons(a, rest)
        else:
          return rest

def dfs(u, parent, edges, disc, low, timer, bridges):
  time = timer + 1
  disc1 = set_at(disc, u, time)
  low1 = set_at(low, u, time)
  ns = neighbors(edges, u)
  return scan_neighbors(u, parent, ns, edges, disc1, low1, time, bridges)

def scan_neighbors(u, parent, ns, edges, disc, low, timer, bridges):
  match ns:
    case List/Nil:
      return (disc, low, (timer, bridges))
    case List/Cons:
      v = ns.head
      if get_at(disc, v) == 0:
        (disc2, low2, tb2) = dfs(v, u, edges, disc, low, timer, bridges)
        (timer2, bridges2) = tb2
        low_v = get_at(low2, v)
        disc_u = get_at(disc2, u)
        low_u = get_at(low2, u)
        if low_v > disc_u:
          bridges3 = bridges2 + 1
        else:
          bridges3 = bridges2
        if low_v < low_u:
          low3 = set_at(low2, u, low_v)
        else:
          low3 = low2
        return scan_neighbors(u, parent, ns.tail, edges, disc2, low3, timer2, bridges3)
      else:
        if v != parent:
          disc_v = get_at(disc, v)
          low_u = get_at(low, u)
          if disc_v < low_u:
            low2 = set_at(low, u, disc_v)
          else:
            low2 = low
          return scan_neighbors(u, parent, ns.tail, edges, disc, low2, timer, bridges)
        else:
          return scan_neighbors(u, parent, ns.tail, edges, disc, low, timer, bridges)

def count_roots(i, n, edges, disc, low, timer, bridges):
  if i == n:
    return bridges
  else:
    if get_at(disc, i) == 0:
      (disc2, low2, tb2) = dfs(i, n, edges, disc, low, timer, bridges)
      (timer2, bridges2) = tb2
      return count_roots(i + 1, n, edges, disc2, low2, timer2, bridges2)
    else:
      return count_roots(i + 1, n, edges, disc, low, timer, bridges)
