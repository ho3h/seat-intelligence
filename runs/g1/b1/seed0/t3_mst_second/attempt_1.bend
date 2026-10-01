def prog(x):
  (n, edges) = x
  if n <= 1:
    return 16777215
  else:
    indexed = index_edges(edges, 0)
    result = prim_build(indexed, List/Cons(0, List/Nil), n - 1, List/Nil, 0)
    (tree, total) = result
    adj = make_adj(n)
    adj = build_adj(tree, adj)
    answer = alt_scan(indexed, tree, adj, total, 0, 0)
    (found, best) = answer
    if found == 0:
      return 16777215
    else:
      return best

def index_edges(edges, i):
  match edges:
    case List/Nil:
      return List/Nil
    case List/Cons:
      return List/Cons((edges.head, i), index_edges(edges.tail, i + 1))

def contains(xs, value):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if xs.head == value:
        return 1
      else:
        return contains(xs.tail, value)

def prim_scan(edges, visited, found, best_edge, best_vertex, best_weight):
  match edges:
    case List/Nil:
      return ((found, best_edge), (best_vertex, best_weight))
    case List/Cons:
      ((u, v, w), eid) = edges.head
      in_u = contains(visited, u)
      in_v = contains(visited, v)
      if in_u != in_v:
        if found == 0:
          if in_u == 1:
            return prim_scan(edges.tail, visited, 1, edges.head, v, w)
          else:
            return prim_scan(edges.tail, visited, 1, edges.head, u, w)
        else:
          if w < best_weight:
            if in_u == 1:
              return prim_scan(edges.tail, visited, 1, edges.head, v, w)
            else:
              return prim_scan(edges.tail, visited, 1, edges.head, u, w)
          else:
            return prim_scan(edges.tail, visited, found, best_edge, best_vertex, best_weight)
      else:
        return prim_scan(edges.tail, visited, found, best_edge, best_vertex, best_weight)

def prim_build(edges, visited, remaining, tree, total):
  if remaining == 0:
    return (tree, total)
  else:
    result = prim_scan(edges, visited, 0, List/Nil, 0, 0)
    ((found, best_edge), (new_vertex, best_weight)) = result
    if found == 0:
      return (tree, total)
    else:
      ((u, v, w), eid) = best_edge
      return prim_build(edges, List/Cons(new_vertex, visited), remaining - 1, List/Cons(best_edge, tree), total + best_weight)

def make_adj(n):
  if n == 0:
    return List/Nil
  else:
    return List/Cons(List/Nil, make_adj(n - 1))

def adj_add(adj, index, value):
  match adj:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if index == 0:
        return List/Cons(List/Cons(value, adj.head), adj.tail)
      else:
        return List/Cons(adj.head, adj_add(adj.tail, index - 1, value))

def adj_get(adj, index):
  match adj:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if index == 0:
        return adj.head
      else:
        return adj_get(adj.tail, index - 1)

def build_adj(tree, adj):
  match tree:
    case List/Nil:
      return adj
    case List/Cons:
      ((u, v, w), eid) = tree.head
      adj1 = adj_add(adj, u, (v, w))
      adj2 = adj_add(adj1, v, (u, w))
      return build_adj(tree.tail, adj2)

def selected_id(tree, wanted):
  match tree:
    case List/Nil:
      return 0
    case List/Cons:
      ((u, v, w), eid) = tree.head
      if eid == wanted:
        return 1
      else:
        return selected_id(tree.tail, wanted)

def path_search(current, parent, target, max_weight, adj):
  if current == target:
    return (1, max_weight)
  else:
    neighbors = adj_get(adj, current)
    return path_scan(neighbors, current, parent, target, max_weight, adj)

def path_scan(neighbors, current, parent, target, max_weight, adj):
  match neighbors:
    case List/Nil:
      return (0, 0)
    case List/Cons:
      (next_vertex, weight) = neighbors.head
      if next_vertex == parent:
        return path_scan(neighbors.tail, current, parent, target, max_weight, adj)
      else:
        if weight > max_weight:
          next_max = weight
        else:
          next_max = max_weight
        result = path_search(next_vertex, current, target, next_max, adj)
        (found, path_max) = result
        if found == 1:
          return result
        else:
          return path_scan(neighbors.tail, current, parent, target, max_weight, adj)

def alt_scan(edges, tree, adj, total, found, best):
  match edges:
    case List/Nil:
      return (found, best)
    case List/Cons:
      ((u, v, w), eid) = edges.head
      if u == v:
        return alt_scan(edges.tail, tree, adj, total, found, best)
      else:
        is_selected = selected_id(tree, eid)
        if is_selected == 1:
          return alt_scan(edges.tail, tree, adj, total, found, best)
        else:
          result = path_search(u, 16777215, v, 0, adj)
          (path_found, max_weight) = result
          if path_found == 0:
            return alt_scan(edges.tail, tree, adj, total, found, best)
          else:
            candidate = total - max_weight + w
            if found == 0:
              return alt_scan(edges.tail, tree, adj, total, 1, candidate)
            else:
              if candidate < best:
                return alt_scan(edges.tail, tree, adj, total, 1, candidate)
              else:
                return alt_scan(edges.tail, tree, adj, total, found, best)
