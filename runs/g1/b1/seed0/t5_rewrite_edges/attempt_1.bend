def prog(x):
  (clusters, edges) = x
  return rewrite_edges(clusters, edges, [])

def rewrite_edges(clusters, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      cu = get_cluster(clusters, u)
      cv = get_cluster(clusters, v)
      if cu == cv:
        return rewrite_edges(clusters, edges.tail, acc)
      else:
        if cu < cv:
          acc2 = insert_edge(acc, (cu, cv))
          return rewrite_edges(clusters, edges.tail, acc2)
        else:
          acc2 = insert_edge(acc, (cv, cu))
          return rewrite_edges(clusters, edges.tail, acc2)

def get_cluster(clusters, i):
  match clusters:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return clusters.head
      else:
        return get_cluster(clusters.tail, i - 1)

def insert_edge(edges, edge):
  match edges:
    case List/Nil:
      return List/Cons(edge, List/Nil)
    case List/Cons:
      (a, b) = edge
      (x, y) = edges.head
      if a < x:
        return List/Cons(edge, edges)
      else:
        if a == x:
          if b < y:
            return List/Cons(edge, edges)
          else:
            if b == y:
              return edges
            else:
              rest = insert_edge(edges.tail, edge)
              return List/Cons(edges.head, rest)
        else:
          rest = insert_edge(edges.tail, edge)
          return List/Cons(edges.head, rest)
