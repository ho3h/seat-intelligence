def prog(x):
  (n, mnl, cands) = x
  labels = make_range(0, n)
  zero_row = make_zeros(n)
  matrix = make_matrix(n, zero_row)
  matrix = add_constraints(mnl, matrix)
  ordered = sort_cands(cands)
  labels = process(ordered, labels, matrix)
  return make_output(labels, labels)

def make_range(i, n):
  if i == n:
    return []
  else:
    return List/Cons(i, make_range(i + 1, n))

def make_zeros(n):
  if n == 0:
    return []
  else:
    return List/Cons(0, make_zeros(n - 1))

def make_matrix(n, row):
  if n == 0:
    return []
  else:
    return List/Cons(row, make_matrix(n - 1, row))

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

def set_cell(matrix, i, j, value):
  row = get_at(matrix, i)
  new_row = set_at(row, j, value)
  return set_at(matrix, i, new_row)

def add_constraints(edges, matrix):
  match edges:
    case List/Nil:
      return matrix
    case List/Cons:
      (a, b) = edges.head
      matrix1 = set_cell(matrix, a, b, 1)
      matrix2 = set_cell(matrix1, b, a, 1)
      return add_constraints(edges.tail, matrix2)

def split_alt(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return (List/Cons(xs.head, []), [])
        case List/Cons:
          rest = xs.tail.tail
          (left, right) = split_alt(rest)
          return (List/Cons(xs.head, left), List/Cons(xs.tail.head, right))

def before(a, b):
  (u1, v1, s1) = a
  (u2, v2, s2) = b
  if s1 > s2:
    return 1
  else:
    if s1 < s2:
      return 0
    else:
      if u1 < u2:
        return 1
      else:
        if u1 > u2:
          return 0
        else:
          if v1 < v2:
            return 1
          else:
            return 0

def merge_cands(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if before(a.head, b.head) == 1:
            return List/Cons(a.head, merge_cands(a.tail, b))
          else:
            return List/Cons(b.head, merge_cands(a, b.tail))

def sort_cands(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alt(xs)
          sorted_left = sort_cands(left)
          sorted_right = sort_cands(right)
          return merge_cands(sorted_left, sorted_right)

def replace_value(xs, old, new):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if xs.head == old:
        return List/Cons(new, replace_value(xs.tail, old, new))
      else:
        return List/Cons(xs.head, replace_value(xs.tail, old, new))

def or_rows(a, b):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      match b:
        case List/Nil:
          return []
        case List/Cons:
          return List/Cons(a.head | b.head, or_rows(a.tail, b.tail))

def merge_column(matrix, idx, a, b, merged_row):
  match matrix:
    case List/Nil:
      return []
    case List/Cons:
      if idx == a:
        return List/Cons(merged_row, matrix.tail)
      else:
        va = get_at(matrix.head, a)
        vb = get_at(matrix.head, b)
        new_row = set_at(matrix.head, a, va | vb)
        return List/Cons(new_row, merge_column(matrix.tail, idx + 1, a, b, merged_row))

def merge_matrix(matrix, a, b):
  row_a = get_at(matrix, a)
  row_b = get_at(matrix, b)
  merged_row = or_rows(row_a, row_b)
  return merge_column(matrix, 0, a, b, merged_row)

def process(cands, labels, matrix):
  match cands:
    case List/Nil:
      return labels
    case List/Cons:
      (u, v, score) = cands.head
      rep_u = get_at(labels, u)
      rep_v = get_at(labels, v)
      if rep_u == rep_v:
        return process(cands.tail, labels, matrix)
      else:
        row_u = get_at(matrix, rep_u)
        if get_at(row_u, rep_v) != 0:
          return process(cands.tail, labels, matrix)
        else:
          new_labels = replace_value(labels, rep_v, rep_u)
          new_matrix = merge_matrix(matrix, rep_u, rep_v)
          return process(cands.tail, new_labels, new_matrix)

def max_in_cluster(labels, rep, idx, best):
  match labels:
    case List/Nil:
      return best
    case List/Cons:
      if labels.head == rep:
        if idx > best:
          return max_in_cluster(labels.tail, rep, idx + 1, idx)
        else:
          return max_in_cluster(labels.tail, rep, idx + 1, best)
      else:
        return max_in_cluster(labels.tail, rep, idx + 1, best)

def make_output(labels, all_labels):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      largest = max_in_cluster(all_labels, labels.head, 0, 0)
      return List/Cons(largest, make_output(labels.tail, all_labels))
