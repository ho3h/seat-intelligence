def prog(x):
  (n, edges) = x
  nodes = make_nodes(0, n)
  final_nodes = process_edges(edges, nodes)
  return count_good_roots(final_nodes, 0, n, 0)

def make_nodes(i, n):
  if i == n:
    return []
  else:
    return List/Cons((i, 0, 1, 0), make_nodes(i + 1, n))

def get_node(nodes, i):
  match nodes:
    case List/Nil:
      return (0, 0, 0, 0)
    case List/Cons:
      if i == 0:
        return nodes.head
      else:
        return get_node(nodes.tail, i - 1)

def set_node(nodes, i, value):
  match nodes:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, nodes.tail)
      else:
        tail = set_node(nodes.tail, i - 1, value)
        return List/Cons(nodes.head, tail)

def find_root(nodes, vertex, parity):
  (parent, link_parity, size, bad) = get_node(nodes, vertex)
  if parent == vertex:
    return (vertex, parity)
  else:
    return find_root(nodes, parent, parity ^ link_parity)

def process_edges(edges, nodes):
  match edges:
    case List/Nil:
      return nodes
    case List/Cons:
      (u, v) = edges.head
      (root_u, parity_u) = find_root(nodes, u, 0)
      (root_v, parity_v) = find_root(nodes, v, 0)
      if root_u == root_v:
        if parity_u == parity_v:
          (parent, link_parity, size, bad) = get_node(nodes, root_u)
          if bad == 0:
            updated = set_node(nodes, root_u, (parent, link_parity, size, 1))
            return process_edges(edges.tail, updated)
          else:
            return process_edges(edges.tail, nodes)
        else:
          return process_edges(edges.tail, nodes)
      else:
        (parent_u, link_u, size_u, bad_u) = get_node(nodes, root_u)
        (parent_v, link_v, size_v, bad_v) = get_node(nodes, root_v)
        merged_bad = bad_u | bad_v
        relation = parity_u ^ parity_v ^ 1
        if size_u >= size_v:
          updated_u = set_node(nodes, root_u, (root_u, 0, size_u + size_v, merged_bad))
          updated = set_node(updated_u, root_v, (root_u, relation, size_v, 0))
          return process_edges(edges.tail, updated)
        else:
          updated_v = set_node(nodes, root_v, (root_v, 0, size_u + size_v, merged_bad))
          updated = set_node(updated_v, root_u, (root_v, relation, size_u, 0))
          return process_edges(edges.tail, updated)

def count_good_roots(nodes, i, n, count):
  if i == n:
    return count
  else:
    (parent, link_parity, size, bad) = get_node(nodes, i)
    if parent == i and bad == 0:
      return count_good_roots(nodes, i + 1, n, count + 1)
    else:
      return count_good_roots(nodes, i + 1, n, count)
