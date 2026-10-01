def prog(x):
  (n, edges) = x
  adj = add_edges(edges, make_rows(n))
  reaches = all_reach(0, n, adj)
  return count_scc(0, n, reaches, [], 0)

def make_rows(n):
  switch n:
    case 0:
      return []
    case _:
      return List/Cons([], make_rows(n - 1))

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

def make_zeros(k):
  switch k:
    case 0:
      return []
    case _:
      return List/Cons(0, make_zeros(k - 1))

def has_bit(bits, v):
  word = get_at(bits, v / 24)
  bit = 1 << (v % 24)
  test = word & bit
  if test != 0:
    return 1
  else:
    return 0

def set_bit(bits, v):
  word_index = v / 24
  offset = v % 24
  word = get_at(bits, word_index)
  bit = 1 << offset
  return set_at(bits, word_index, word | bit)

def discover(neighbors, stack, seen):
  match neighbors:
    case List/Nil:
      return (stack, seen)
    case List/Cons:
      v = neighbors.head
      if has_bit(seen, v) == 1:
        return discover(neighbors.tail, stack, seen)
      else:
        seen2 = set_bit(seen, v)
        stack2 = List/Cons(v, stack)
        return discover(neighbors.tail, stack2, seen2)

def dfs(stack, seen, adj):
  match stack:
    case List/Nil:
      return seen
    case List/Cons:
      v = stack.head
      neighbors = get_at(adj, v)
      (stack2, seen2) = discover(neighbors, stack.tail, seen)
      return dfs(stack2, seen2, adj)

def all_reach(i, n, adj):
  if i < n:
    chunks = (n + 23) / 24
    empty = make_zeros(chunks)
    seen = set_bit(empty, i)
    reached = dfs(List/Cons(i, []), seen, adj)
    return List/Cons(reached, all_reach(i + 1, n, adj))
  else:
    return []

def has_prior_mutual(prior, i, curr):
  match prior:
    case List/Nil:
      return 0
    case List/Cons:
      j = i - 1
      if has_bit(curr, j) == 1:
        if has_bit(prior.head, i) == 1:
          return 1
        else:
          return has_prior_mutual(prior.tail, j, curr)
      else:
        return has_prior_mutual(prior.tail, j, curr)

def count_scc(i, n, remaining, prior, acc):
  if i == n:
    return acc
  else:
    match remaining:
      case List/Nil:
        return acc
      case List/Cons:
        curr = remaining.head
        if has_prior_mutual(prior, i, curr) == 1:
          return count_scc(i + 1, n, remaining.tail, List/Cons(curr, prior), acc)
        else:
          return count_scc(i + 1, n, remaining.tail, List/Cons(curr, prior), acc + 1)
