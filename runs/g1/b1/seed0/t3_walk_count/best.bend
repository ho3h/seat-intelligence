def prog(x):
  (n, s, t, k, edges) = x
  if s >= n:
    return 0
  else:
    if t >= n:
      return 0
    else:
      initial = init_vec(0, n, t)
      return walk_steps(k, n, s, edges, initial)

def init_vec(i, n, t):
  if i == n:
    return []
  else:
    if i == t:
      return List/Cons(1, init_vec(i + 1, n, t))
    else:
      return List/Cons(0, init_vec(i + 1, n, t))

def walk_steps(rem, n, s, edges, vec):
  if rem == 0:
    return vec_get(vec, s)
  else:
    new_vec = build_vec(0, n, edges, vec)
    return walk_steps(rem - 1, n, s, edges, new_vec)

def build_vec(i, n, edges, vec):
  if i == n:
    return []
  else:
    count = sum_from(edges, i, vec, 0)
    return List/Cons(count, build_vec(i + 1, n, edges, vec))

def sum_from(edges, src, vec, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      if u == src:
        count = vec_get(vec, v)
        return sum_from(edges.tail, src, vec, acc + count)
      else:
        return sum_from(edges.tail, src, vec, acc)

def vec_get(vec, idx):
  match vec:
    case List/Nil:
      return 0
    case List/Cons:
      if idx == 0:
        return vec.head
      else:
        return vec_get(vec.tail, idx - 1)
