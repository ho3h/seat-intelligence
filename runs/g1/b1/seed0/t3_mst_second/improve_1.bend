def prog(x):
  (n, edges) = x
  if n <= 1:
    return 16777215
  else:
    indexed = index_edges(edges, 0)
    sorted = sort_edges(indexed)
    parents = make_ids(n, 0)
    ranks = make_ids(n, 0)
    result = kruskal(sorted, parents, ranks, n - 1, List/Nil, 0)
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

def make_ids(n, i):
  if i == n:
    return List/Nil
  else:
    return List/Cons(i, make_ids(n, i + 1))

def list_get(xs, index):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if index == 0:
        return xs.head
      else:
        return list_get(xs.tail, index - 1)

def list_set(xs, index, value):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      if index == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, list_set(xs.tail, index - 1, value))

def find_root(parents, vertex):
  parent = list_get(parents, vertex)
  if parent == vertex:
    return vertex
  else:
    return find_root(parents, parent)

def split_alt(xs):
  match xs:
    case List/Nil:
      return (List/Nil, List/Nil)
    case List/Cons:
      (a, b) = split_alt(xs.tail)
      return (List/Cons(xs.head, b), a)

def sort_edges(xs):
  match xs:
    case List/Nil:
      return List/Nil
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (a, b) = split_alt(xs)
          return merge_edges(sort_edges(a), sort_edges(b))

def merge_edges(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          ((au, av, aw), aid) = a.head
          ((bu, bv, bw), bid) = b.head
          if aw <= bw:
            return List/Cons(a.head, merge_edges(a.tail, b))
          else:
            return List/Cons(b.head, merge_edges(a, b.tail))

def kruskal(edges, parents, ranks, remaining, tree, total):
  if remaining == 0:
    return (tree, total)
  else:
    match edges:
      case List/Nil:
        return (tree, total)
      case List/Cons:
        ((u, v, w), eid) = edges.head
        root_u = find_root(parents, u)
        root_v = find_root(parents, v)
        if root_u == root_v:
          return kruskal(edges.tail, parents, ranks, remaining, tree, total)
        else:
          rank_u = list_get(ranks, root_u)
          rank_v = list_get(ranks, root_v)
          if rank_u < rank_v:
            parents1 = list_set(parents, root_u, root_v)
            return kruskal(edges.tail, parents1, ranks, remaining - 1, List/Cons(edges.head, tree), total + w)
          else:
            if rank_u > rank_v:
              parents1 = list_set(parents, root_v, root_u)
              return kruskal(edges.tail, parents1, ranks, remaining - 1, List/Cons(edges.head, tree), total + w)
            else:
              parents1 = list_set(parents, root_v, root_u)
              ranks1 = list_set(ranks, root_u, rank_u + 1)
              return kruskal(edges.tail, parents1, ranks1, remaining - 1, List/Cons(edges.head, tree), total + w)

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
