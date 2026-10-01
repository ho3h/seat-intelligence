def prog(x):
  (n, s, t, k, edges) = x
  if s >= n:
    return 16777215
  else:
    if t >= n:
      return 16777215
    else:
      if k == 0:
        if s == t:
          return 0
        else:
          return 16777215
      else:
        initial = init_dist(n, s, 0)
        return solve(k, n, t, edges, initial)

def init_dist(n, s, i):
  if n == 0:
    return []
  else:
    if i == s:
      value = 0
    else:
      value = 16777215
    tail = init_dist(n - 1, s, i + 1)
    return List/Cons(value, tail)

def init_inf(n):
  if n == 0:
    return []
  else:
    tail = init_inf(n - 1)
    return List/Cons(16777215, tail)

def list_get(xs, i):
  match xs:
    case List/Nil:
      return 16777215
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return list_get(xs.tail, i - 1)

def put_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        tail = put_at(xs.tail, i - 1, value)
        return List/Cons(xs.head, tail)

def relax_one(old, fresh, n, u, v, w):
  if u >= n:
    return fresh
  else:
    if v >= n:
      return fresh
    else:
      du = list_get(old, u)
      if du == 16777215:
        return fresh
      else:
        room = 16777215 - du
        if w >= room:
          return fresh
        else:
          candidate = du + w
          current = list_get(fresh, v)
          if candidate < current:
            return put_at(fresh, v, candidate)
          else:
            return fresh

def relax_edges(edges, old, fresh, n):
  match edges:
    case List/Nil:
      return fresh
    case List/Cons:
      (u, v, w) = edges.head
      fresh2 = relax_one(old, fresh, n, u, v, w)
      return relax_edges(edges.tail, old, fresh2, n)

def solve(k, n, t, edges, old):
  if k == 0:
    return list_get(old, t)
  else:
    fresh = init_inf(n)
    updated = relax_edges(edges, old, fresh, n)
    return solve(k - 1, n, t, edges, updated)
