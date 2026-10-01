def prog(x):
  (n, s, edges) = x
  if s >= n:
    return make_inf(n)
  else:
    dist = make_dist(n, s, 0)
    return do_rounds(n - 1, dist, edges)

def make_inf(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons(16777215, make_inf(n - 1))

def make_dist(n, s, i):
  switch n:
    case 0:
      return []
    case _:
      if i == s:
        value = 0
      else:
        value = 16777215
      return List/Cons(value, make_dist(n - 1, s, i + 1))

def get_dist(xs, i):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      switch i:
        case 0:
          return xs.head
        case _:
          return get_dist(xs.tail, i - 1)

def set_dist(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      switch i:
        case 0:
          return List/Cons(value, xs.tail)
        case _:
          return List/Cons(xs.head, set_dist(xs.tail, i - 1, value))

def relax_one(dist, u, v, w):
  du = get_dist(dist, u)
  dv = get_dist(dist, v)
  if du == 16777215:
    return dist
  else:
    if w > 16777215 - du:
      return dist
    else:
      candidate = du + w
      if candidate < dv:
        return set_dist(dist, v, candidate)
      else:
        return dist

def relax_edges(edges, dist):
  match edges:
    case List/Nil:
      return dist
    case List/Cons:
      (u, v, w) = edges.head
      updated = relax_one(dist, u, v, w)
      return relax_edges(edges.tail, updated)

def do_rounds(k, dist, edges):
  switch k:
    case 0:
      return dist
    case _:
      updated = relax_edges(edges, dist)
      return do_rounds(k - 1, updated, edges)
