def prog(x):
  (n, r, edges) = x
  size = capacity(n, 1)
  adj = make_vec(size, [])
  adj2 = build_adj(edges, adj, size)
  parents = make_vec(size, 16777215)
  rooted = walk_tree(r, 16777215, adj2, parents, size)
  return vector_to_list(rooted, 0, n, size)

def capacity(n, size):
  if size >= n:
    return size
  else:
    return capacity(n, size * 2)

def make_vec(size, value):
  if size == 1:
    return value
  else:
    half = size / 2
    return (make_vec(half, value), make_vec(half, value))

def vec_get(vec, index, size):
  if size == 1:
    return vec
  else:
    half = size / 2
    (left, right) = vec
    if index < half:
      return vec_get(left, index, half)
    else:
      return vec_get(right, index - half, half)

def vec_set(vec, index, value, size):
  if size == 1:
    return value
  else:
    half = size / 2
    (left, right) = vec
    if index < half:
      return (vec_set(left, index, value, half), right)
    else:
      return (left, vec_set(right, index - half, value, half))

def build_adj(edges, adj, size):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v) = edges.head
      u_neighbors = vec_get(adj, u, size)
      adj1 = vec_set(adj, u, List/Cons(v, u_neighbors), size)
      v_neighbors = vec_get(adj1, v, size)
      adj2 = vec_set(adj1, v, List/Cons(u, v_neighbors), size)
      return build_adj(edges.tail, adj2, size)

def walk_tree(u, p, adj, parents, size):
  neighbors = vec_get(adj, u, size)
  return walk_neighbors(neighbors, u, p, adj, parents, size)

def walk_neighbors(neighbors, u, p, adj, parents, size):
  match neighbors:
    case List/Nil:
      return parents
    case List/Cons:
      v = neighbors.head
      if v == p:
        return walk_neighbors(neighbors.tail, u, p, adj, parents, size)
      else:
        parents1 = vec_set(parents, v, u, size)
        parents2 = walk_tree(v, u, adj, parents1, size)
        return walk_neighbors(neighbors.tail, u, p, adj, parents2, size)

def vector_to_list(vec, index, n, size):
  if index == n:
    return []
  else:
    value = vec_get(vec, index, size)
    return List/Cons(value, vector_to_list(vec, index + 1, n, size))
