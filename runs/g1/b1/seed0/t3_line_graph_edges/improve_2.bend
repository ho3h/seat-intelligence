def prog(x):
  (n, edges) = x
  count = list_length(edges)
  if count <= 16:
    return count_pairs(edges, 0)
  else:
    endpoints = make_endpoints(edges)
    shared_at_vertices = radix_degree_sum(endpoints, 0)
    duplicate_edge_pairs = radix_duplicate_sum(edges, 0)
    return shared_at_vertices - duplicate_edge_pairs

def list_length(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return 1 + list_length(xs.tail)

def choose_two(count):
  if count < 2:
    return 0
  else:
    if count % 2 == 0:
      return (count / 2) * (count - 1)
    else:
      return count * ((count - 1) / 2)

def make_endpoints(edges):
  match edges:
    case List/Nil:
      return []
    case List/Cons:
      (u, v) = edges.head
      rest = make_endpoints(edges.tail)
      if u == v:
        return List/Cons(u, rest)
      else:
        return List/Cons(u, List/Cons(v, rest))

def radix_degree_sum(values, bit):
  match values:
    case List/Nil:
      return 0
    case List/Cons:
      match values.tail:
        case List/Nil:
          return 0
        case List/Cons:
          if bit == 24:
            return choose_two(list_length(values))
          else:
            (zero, one) = split_values(values, bit)
            left = radix_degree_sum(zero, bit + 1)
            right = radix_degree_sum(one, bit + 1)
            return left + right

def split_values(values, bit):
  match values:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (zero, one) = split_values(values.tail, bit)
      if ((values.head >> bit) & 1) == 0:
        return (List/Cons(values.head, zero), one)
      else:
        return (zero, List/Cons(values.head, one))

def radix_duplicate_sum(edges, bit):
  match edges:
    case List/Nil:
      return 0
    case List/Cons:
      match edges.tail:
        case List/Nil:
          return 0
        case List/Cons:
          if bit == 48:
            return choose_two(list_length(edges))
          else:
            (zero, one) = split_edges(edges, bit)
            left = radix_duplicate_sum(zero, bit + 1)
            right = radix_duplicate_sum(one, bit + 1)
            return left + right

def split_edges(edges, bit):
  match edges:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (zero, one) = split_edges(edges.tail, bit)
      if edge_bit(edges.head, bit) == 0:
        return (List/Cons(edges.head, zero), one)
      else:
        return (zero, List/Cons(edges.head, one))

def edge_bit(edge, bit):
  (u, v) = edge
  if u <= v:
    low = u
    high = v
  else:
    low = v
    high = u
  if bit < 24:
    return (low >> bit) & 1
  else:
    return (high >> (bit - 24)) & 1

def count_pairs(edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      count = count_with(edges.head, edges.tail, 0)
      return count_pairs(edges.tail, acc + count)

def count_with(edge, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edge
      (a, b) = edges.head
      if (u == a) | (u == b) | (v == a) | (v == b):
        return count_with(edge, edges.tail, acc + 1)
      else:
        return count_with(edge, edges.tail, acc)
