def prog(x):
  (n, s, t, edges) = x
  if s >= n:
    return []
  else:
    if t >= n:
      return []
    else:
      if s == t:
        return List/Cons(s, [])
      else:
        states = make_dist_tree(n)
        from_t = tree_set(states, n, t, (0, 0, 0))
        empty_adj = make_adj_tree(n)
        adj = add_edges(edges, empty_adj, n)
        initial_heap = heap_node((0, 0, 0, t), [], [])
        optimal = dijkstra(initial_heap, from_t, adj, n, s)
        (hi, lo, hops) = tree_get(optimal, n, s)
        if hi == 16777215:
          return []
        else:
          return build_path(adj, optimal, n, s, t)

def make_dist_tree(n):
  if n == 1:
    return (0, (16777215, 0, 16777215))
  else:
    left_size = n / 2
    right_size = n - left_size
    return (1, make_dist_tree(left_size), make_dist_tree(right_size))

def make_adj_tree(n):
  if n == 1:
    return (0, [])
  else:
    left_size = n / 2
    right_size = n - left_size
    return (1, make_adj_tree(left_size), make_adj_tree(right_size))

def tree_get(tree, size, idx):
  if size == 1:
    (tag, value) = tree
    return value
  else:
    (tag, left, right) = tree
    left_size = size / 2
    if idx < left_size:
      return tree_get(left, left_size, idx)
    else:
      return tree_get(right, size - left_size, idx - left_size)

def tree_set(tree, size, idx, value):
  if size == 1:
    return (0, value)
  else:
    (tag, left, right) = tree
    left_size = size / 2
    if idx < left_size:
      return (1, tree_set(left, left_size, idx, value), right)
    else:
      return (1, left, tree_set(right, size - left_size, idx - left_size, value))

def add_neighbor(adj, n, vertex, neighbor, weight):
  old = tree_get(adj, n, vertex)
  updated = List/Cons((neighbor, weight), old)
  return tree_set(adj, n, vertex, updated)

def add_edges(edges, adj, n):
  match edges:
    case List/Nil:
      return adj
    case List/Cons:
      (u, v, w) = edges.head
      if u < n:
        if v < n:
          after_u = add_neighbor(adj, n, u, v, w)
          after_v = add_neighbor(after_u, n, v, u, w)
          return add_edges(edges.tail, after_v, n)
        else:
          return add_edges(edges.tail, adj, n)
      else:
        return add_edges(edges.tail, adj, n)

def better_metric(ah, al, ap, bh, bl, bp):
  if ah < bh:
    return 1
  else:
    if ah > bh:
      return 0
    else:
      if al < bl:
        return 1
      else:
        if al > bl:
          return 0
        else:
          if ap < bp:
            return 1
          else:
            return 0

def key_less(a, b):
  (ah, al, ap, av) = a
  (bh, bl, bp, bv) = b
  if ah < bh:
    return 1
  else:
    if ah > bh:
      return 0
    else:
      if al < bl:
        return 1
      else:
        if al > bl:
          return 0
        else:
          if ap < bp:
            return 1
          else:
            if ap > bp:
              return 0
            else:
              if av < bv:
                return 1
              else:
                return 0

def heap_rank(heap):
  match heap:
    case List/Nil:
      return 0
    case List/Cons:
      (rank, key, left, right) = heap.head
      return rank

def heap_node(key, left, right):
  left_rank = heap_rank(left)
  right_rank = heap_rank(right)
  if left_rank >= right_rank:
    return List/Cons((right_rank + 1, key, left, right), [])
  else:
    return List/Cons((left_rank + 1, key, right, left), [])

def heap_meld(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          (rank_a, key_a, left_a, right_a) = a.head
          (rank_b, key_b, left_b, right_b) = b.head
          if key_less(key_a, key_b) == 1:
            merged = heap_meld(right_a, b)
            return heap_node(key_a, left_a, merged)
          else:
            merged = heap_meld(right_b, a)
            return heap_node(key_b, left_b, merged)

def heap_pop(heap):
  match heap:
    case List/Nil:
      return ((0, 0, 0, 0), [])
    case List/Cons:
      (rank, key, left, right) = heap.head
      return (key, heap_meld(left, right))

def same_metric(tree, n, vertex, hi, lo, hops):
  (old_hi, old_lo, old_hops) = tree_get(tree, n, vertex)
  if old_hi == hi:
    if old_lo == lo:
      if old_hops == hops:
        return 1
      else:
        return 0
    else:
      return 0
  else:
    return 0

def add_weight(hi, lo, weight):
  new_lo = lo + weight
  if new_lo < lo:
    return (hi + 1, new_lo)
  else:
    return (hi, new_lo)

def relax_neighbors(neighbors, states, heap, n, hi, lo, hops):
  match neighbors:
    case List/Nil:
      return (states, heap)
    case List/Cons:
      (dest, weight) = neighbors.head
      (new_hi, new_lo) = add_weight(hi, lo, weight)
      new_hops = hops + 1
      (old_hi, old_lo, old_hops) = tree_get(states, n, dest)
      if better_metric(new_hi, new_lo, new_hops, old_hi, old_lo, old_hops) == 1:
        updated_states = tree_set(states, n, dest, (new_hi, new_lo, new_hops))
        new_heap = heap_meld(heap, heap_node((new_hi, new_lo, new_hops, dest), [], []))
        (final_states, final_heap) = relax_neighbors(neighbors.tail, updated_states, new_heap, n, hi, lo, hops)
        return (final_states, final_heap)
      else:
        return relax_neighbors(neighbors.tail, states, heap, n, hi, lo, hops)

def dijkstra(heap, states, adj, n, goal):
  match heap:
    case List/Nil:
      return states
    case List/Cons:
      (key, rest_heap) = heap_pop(heap)
      (hi, lo, hops, vertex) = key
      if same_metric(states, n, vertex, hi, lo, hops) == 0:
        return dijkstra(rest_heap, states, adj, n, goal)
      else:
        if vertex == goal:
          return states
        else:
          neighbors = tree_get(adj, n, vertex)
          (updated_states, updated_heap) = relax_neighbors(neighbors, states, rest_heap, n, hi, lo, hops)
          return dijkstra(updated_heap, updated_states, adj, n, goal)

def is_opt_step(states, n, current, nxt, weight):
  (ch, cl, cp) = tree_get(states, n, current)
  (nh, nl, np) = tree_get(states, n, nxt)
  (total_hi, total_lo) = add_weight(nh, nl, weight)
  if total_hi == ch:
    if total_lo == cl:
      if np + 1 == cp:
        return 1
      else:
        return 0
    else:
      return 0
  else:
    return 0

def consider_next(states, n, current, candidate, weight, best):
  if is_opt_step(states, n, current, candidate, weight) == 1:
    if candidate < best:
      return candidate
    else:
      return best
  else:
    return best

def choose_next(neighbors, states, n, current, best):
  match neighbors:
    case List/Nil:
      return best
    case List/Cons:
      (candidate, weight) = neighbors.head
      next_best = consider_next(states, n, current, candidate, weight, best)
      return choose_next(neighbors.tail, states, n, current, next_best)

def build_path(adj, states, n, current, target):
  if current == target:
    return List/Cons(current, [])
  else:
    neighbors = tree_get(adj, n, current)
    next_vertex = choose_next(neighbors, states, n, current, n)
    if next_vertex >= n:
      return []
    else:
      return List/Cons(current, build_path(adj, states, n, next_vertex, target))
