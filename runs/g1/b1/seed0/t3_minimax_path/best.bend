def prog(x):
  (n, s, t, edges) = x
  if s >= n:
    return 16777215
  else:
    if t >= n:
      return 16777215
    else:
      if s == t:
        return 0
      else:
        dist = make_dist(n, s, 0)
        dist = repeat_passes(n, edges, dist, n)
        return get_at(dist, t)

def make_dist(k, s, i):
  switch k:
    case 0:
      return []
    case _:
      tail = make_dist(k - 1, s, i + 1)
      if i == s:
        return List/Cons(0, tail)
      else:
        return List/Cons(16777215, tail)

def get_at(xs, i):
  switch i:
    case 0:
      match xs:
        case List/Nil:
          return 16777215
        case List/Cons:
          return xs.head
    case _:
      match xs:
        case List/Nil:
          return 16777215
        case List/Cons:
          return get_at(xs.tail, i - 1)

def set_at(xs, i, value):
  switch i:
    case 0:
      match xs:
        case List/Nil:
          return []
        case List/Cons:
          return List/Cons(value, xs.tail)
    case _:
      match xs:
        case List/Nil:
          return []
        case List/Cons:
          tail = set_at(xs.tail, i - 1, value)
          return List/Cons(xs.head, tail)

def max2(a, b):
  if a > b:
    return a
  else:
    return b

def relax_edges(edges, dist, n):
  match edges:
    case List/Nil:
      return dist
    case List/Cons:
      (u, v, w) = edges.head
      if u < n:
        if v < n:
          du = get_at(dist, u)
          dv = get_at(dist, v)
          cand_v = max2(du, w)
          if cand_v < dv:
            dist1 = set_at(dist, v, cand_v)
          else:
            dist1 = dist
          cand_u = max2(dv, w)
          if cand_u < du:
            dist2 = set_at(dist1, u, cand_u)
          else:
            dist2 = dist1
          return relax_edges(edges.tail, dist2, n)
        else:
          return relax_edges(edges.tail, dist, n)
      else:
        return relax_edges(edges.tail, dist, n)

def repeat_passes(k, edges, dist, n):
  switch k:
    case 0:
      return dist
    case _:
      dist1 = relax_edges(edges, dist, n)
      return repeat_passes(k - 1, edges, dist1, n)
