def prog(x):
  (n, cap, mnl, cands) = x
  parent = make_nodes(0, n)
  sizes = make_ones(0, n)
  maxima = make_nodes(0, n)
  matrix = make_matrix(0, n)
  matrix = mark_links(mnl, matrix)
  ordered = sort_candidates(cands)
  (parent, sizes, maxima, matrix) = process_candidates(ordered, cap, n, parent, sizes, maxima, matrix)
  return build_result(0, n, parent, maxima)

def make_nodes(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_nodes(i + 1, n))

def make_ones(i, n):
  if i == n:
    return []
  else:
    return List/Cons(1, make_ones(i + 1, n))

def zero_list(n):
  if n == 0:
    return []
  else:
    return List/Cons(0, zero_list(n - 1))

def make_matrix(i, n):
  if i == n:
    return []
  else:
    return List/Cons(zero_list(n), make_matrix(i + 1, n))

def get_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(xs.tail, i - 1)

def set_at(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, set_at(xs.tail, i - 1, value))

def get2(matrix, i, j):
  row = get_at(matrix, i)
  return get_at(row, j)

def set2(matrix, i, j, value):
  row = get_at(matrix, i)
  new_row = set_at(row, j, value)
  return set_at(matrix, i, new_row)

def find_root(parent, node):
  p = get_at(parent, node)
  if p == node:
    return node
  else:
    return find_root(parent, p)

def before(a, b):
  (au, av, ass) = a
  (bu, bv, bss) = b
  if ass > bss:
    return 1
  else:
    if ass < bss:
      return 0
    else:
      if au < bu:
        return 1
      else:
        if au > bu:
          return 0
        else:
          return av < bv

def split_alt(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return (List/Cons(xs.head, []), [])
        case List/Cons:
          (left, right) = split_alt(xs.tail.tail)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def merge_sorted(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if before(a.head, b.head) == 1:
            return List/Cons(a.head, merge_sorted(a.tail, b))
          else:
            return List/Cons(b.head, merge_sorted(a, b.tail))

def sort_candidates(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return List/Cons(xs.head, [])
        case List/Cons:
          (left, right) = split_alt(xs)
          sorted_left = sort_candidates(left)
          sorted_right = sort_candidates(right)
          return merge_sorted(sorted_left, sorted_right)

def mark_links(links, matrix):
  match links:
    case List/Nil:
      return matrix
    case List/Cons:
      (a, b) = links.head
      matrix1 = set2(matrix, a, b, 1)
      matrix2 = set2(matrix1, b, a, 1)
      return mark_links(links.tail, matrix2)

def merge_matrix_loop(base, current, ra, rb, k, n):
  if k == n:
    return current
  else:
    x = get2(current, ra, k)
    y = get2(base, rb, k)
    if x == 1:
      value = 1
    else:
      if y == 1:
        value = 1
      else:
        value = 0
    current1 = set2(current, ra, k, value)
    current2 = set2(current1, k, ra, value)
    return merge_matrix_loop(base, current2, ra, rb, k + 1, n)

def process_candidates(cands, cap, n, parent, sizes, maxima, matrix):
  match cands:
    case List/Nil:
      return (parent, sizes, maxima, matrix)
    case List/Cons:
      (u, v, score) = cands.head
      ru = find_root(parent, u)
      rv = find_root(parent, v)
      if ru == rv:
        return process_candidates(cands.tail, cap, n, parent, sizes, maxima, matrix)
      else:
        blocked = get2(matrix, ru, rv)
        if blocked == 1:
          return process_candidates(cands.tail, cap, n, parent, sizes, maxima, matrix)
        else:
          size_u = get_at(sizes, ru)
          size_v = get_at(sizes, rv)
          total = size_u + size_v
          if total > cap:
            return process_candidates(cands.tail, cap, n, parent, sizes, maxima, matrix)
          else:
            parent1 = set_at(parent, rv, ru)
            sizes1 = set_at(sizes, ru, total)
            max_u = get_at(maxima, ru)
            max_v = get_at(maxima, rv)
            if max_u > max_v:
              max_value = max_u
            else:
              max_value = max_v
            maxima1 = set_at(maxima, ru, max_value)
            matrix1 = merge_matrix_loop(matrix, matrix, ru, rv, 0, n)
            return process_candidates(cands.tail, cap, n, parent1, sizes1, maxima1, matrix1)

def build_result(i, n, parent, maxima):
  if i == n:
    return []
  else:
    root = find_root(parent, i)
    value = get_at(maxima, root)
    return List/Cons(value, build_result(i + 1, n, parent, maxima))
