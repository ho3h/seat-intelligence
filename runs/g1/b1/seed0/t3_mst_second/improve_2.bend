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
    root = build_node(tree, 0, n)
    answer = alt_scan(indexed, tree, root, total, 0, 0)
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

def build_node(tree, vertex, parent):
  children = build_children(tree, vertex, parent)
  return (vertex, children)

def build_children(tree, vertex, parent):
  match tree:
    case List/Nil:
      return List/Nil
    case List/Cons:
      ((u, v, w), eid) = tree.head
      if u == vertex:
        if v == parent:
          return build_children(tree.tail, vertex, parent)
        else:
          child = build_node(tree, v, vertex)
          return List/Cons((w, child), build_children(tree.tail, vertex, parent))
      else:
        if v == vertex:
          if u == parent:
            return build_children(tree.tail, vertex, parent)
          else:
            child = build_node(tree, u, vertex)
            return List/Cons((w, child), build_children(tree.tail, vertex, parent))
        else:
          return build_children(tree.tail, vertex, parent)

def max2(a, b):
  if a > b:
    return a
  else:
    return b

def tree_path_query(node, u, v):
  (vertex, children) = node
  if vertex == u:
    hu = 1
  else:
    hu = 0
  if vertex == v:
    hv = 1
  else:
    hv = 0
  state = (hu, hv, (0, 0), (0, 0))
  return tree_query_children(children, u, v, state)

def tree_query_children(children, u, v, state):
  match children:
    case List/Nil:
      return state
    case List/Cons:
      (weight, child) = children.head
      result = tree_path_query(child, u, v)
      (chu, chv, (cmu, cmv), (cfound, cans)) = result
      (hu, hv, (mu, mv), (found, answer)) = state
      if found == 1:
        return state
      else:
        if cfound == 1:
          return (hu, hv, (mu, mv), (1, cans))
        else:
          lift_u = max2(weight, cmu)
          lift_v = max2(weight, cmv)
          if hu == 1:
            if chv == 1:
              return (1, 1, (mu, mv), (1, max2(mu, lift_v)))
            else:
              if chu == 1:
                return tree_query_children(children.tail, u, v, (hu, hv, (mu, mv), (0, 0)))
              else:
                if chv == 1:
                  return tree_query_children(children.tail, u, v, (hu, 1, (mu, lift_v), (0, 0)))
                else:
                  return tree_query_children(children.tail, u, v, (hu, hv, (mu, mv), (0, 0)))
          else:
            if hv == 1:
              if chu == 1:
                return (1, 1, (mu, mv), (1, max2(mv, lift_u)))
              else:
                if chu == 1:
                  return tree_query_children(children.tail, u, v, (1, hv, (lift_u, mv), (0, 0)))
                else:
                  return tree_query_children(children.tail, u, v, (hu, hv, (mu, mv), (0, 0)))
            else:
              if chu == 1:
                if chv == 1:
                  return (1, 1, (mu, mv), (1, max2(lift_u, lift_v)))
                else:
                  return tree_query_children(children.tail, u, v, (1, hv, (lift_u, mv), (0, 0)))
              else:
                if chv == 1:
                  return tree_query_children(children.tail, u, v, (hu, 1, (mu, lift_v), (0, 0)))
                else:
                  return tree_query_children(children.tail, u, v, (hu, hv, (mu, mv), (0, 0)))

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

def alt_scan(edges, tree, root, total, found, best):
  match edges:
    case List/Nil:
      return (found, best)
    case List/Cons:
      ((u, v, w), eid) = edges.head
      if u == v:
        return alt_scan(edges.tail, tree, root, total, found, best)
      else:
        is_selected = selected_id(tree, eid)
        if is_selected == 1:
          return alt_scan(edges.tail, tree, root, total, found, best)
        else:
          result = tree_path_query(root, u, v)
          (hu, hv, (mu, mv), (path_found, max_weight)) = result
          if path_found == 0:
            return alt_scan(edges.tail, tree, root, total, found, best)
          else:
            candidate = total - max_weight + w
            if found == 0:
              return alt_scan(edges.tail, tree, root, total, 1, candidate)
            else:
              if candidate < best:
                return alt_scan(edges.tail, tree, root, total, 1, candidate)
              else:
                return alt_scan(edges.tail, tree, root, total, found, best)
