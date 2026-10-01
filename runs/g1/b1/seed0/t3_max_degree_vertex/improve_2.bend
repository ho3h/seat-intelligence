def prog(x):
  (n, edges) = x
  if n == 0:
    return 16777215
  else:
    endpoints = collect_endpoints(edges, n)
    match endpoints:
      case List/Nil:
        return 0
      case List/Cons:
        (vertex, degree) = best_degree(endpoints, 0, 0)
        return vertex

def collect_endpoints(edges, n):
  match edges:
    case List/Nil:
      return []
    case List/Cons:
      (u, v) = edges.head
      rest = collect_endpoints(edges.tail, n)
      if v < n:
        with_v = List/Cons(v, rest)
      else:
        with_v = rest
      if u < n:
        return List/Cons(u, with_v)
      else:
        return with_v

def split_bit(xs, mask):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (zeros, ones) = split_bit(xs.tail, mask)
      if (xs.head & mask) == 0:
        return (List/Cons(xs.head, zeros), ones)
      else:
        return (zeros, List/Cons(xs.head, ones))

def count_list(xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      return count_list(xs.tail) + 1

def best_degree(xs, bit, prefix):
  if bit == 24:
    return (prefix, count_list(xs))
  else:
    mask = 1 << (23 - bit)
    (zeros, ones) = split_bit(xs, mask)
    match zeros:
      case List/Nil:
        return best_degree(ones, bit + 1, prefix * 2 + 1)
      case List/Cons:
        match ones:
          case List/Nil:
            return best_degree(zeros, bit + 1, prefix * 2)
          case List/Cons:
            (zero_vertex, zero_degree) = best_degree(zeros, bit + 1, prefix * 2)
            (one_vertex, one_degree) = best_degree(ones, bit + 1, prefix * 2 + 1)
            if zero_degree >= one_degree:
              return (zero_vertex, zero_degree)
            else:
              return (one_vertex, one_degree)
