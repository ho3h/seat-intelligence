def prog(x):
  (n, mnl, cands) = x
  words = (n + 23) / 24
  labels = make_range(0, n)
  maxes = make_range(0, n)
  zero_row = make_zeros(words)
  adj = make_matrix(n, zero_row)
  members = make_member_rows(0, n, words)
  adj = add_constraints(mnl, adj)
  ordered = sort_cands(cands)
  return process(ordered, labels, maxes, adj, members)

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

def make_singleton(j, words, word_idx, mask):
  if j == words:
    return []
  else:
    if j == word_idx:
      return List/Cons(mask, make_singleton(j + 1, words, word_idx, mask))
    else:
      return List/Cons(0, make_singleton(j + 1, words, word_idx, mask))

def make_member_rows(i, n, words):
  if i == n:
    return []
  else:
    word_idx = i / 24
    mask = 1 << (i % 24)
    row = make_singleton(0, words, word_idx, mask)
    return List/Cons(row, make_member_rows(i + 1, n, words))

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

def add_bit(matrix, node, target):
  row = get_at(matrix, node)
  word_idx = target / 24
  mask = 1 << (target % 24)
  old_word = get_at(row, word_idx)
  new_row = set_at(row, word_idx, old_word | mask)
  return set_at(matrix, node, new_row)

def add_constraints(edges, matrix):
  match edges:
    case List/Nil:
      return matrix
    case List/Cons:
      (a, b) = edges.head
      matrix1 = add_bit(matrix, a, b)
      matrix2 = add_bit(matrix1, b, a)
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
          (left, right) = split_alt(xs.tail.tail)
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

def intersects(a, b):
  match a:
    case List/Nil:
      return 0
    case List/Cons:
      match b:
        case List/Nil:
          return 0
        case List/Cons:
          if (a.head & b.head) != 0:
            return 1
          else:
            return intersects(a.tail, b.tail)

def process(cands, labels, maxes, adj, members):
  match cands:
    case List/Nil:
      return make_output(labels, maxes)
    case List/Cons:
      (u, v, score) = cands.head
      rep_u = get_at(labels, u)
      rep_v = get_at(labels, v)
      if rep_u == rep_v:
        return process(cands.tail, labels, maxes, adj, members)
      else:
        conflict = intersects(get_at(adj, rep_u), get_at(members, rep_v))
        if conflict == 1:
          return process(cands.tail, labels, maxes, adj, members)
        else:
          new_labels = replace_value(labels, rep_v, rep_u)
          row_adj_u = get_at(adj, rep_u)
          row_adj_v = get_at(adj, rep_v)
          new_adj_row = or_rows(row_adj_u, row_adj_v)
          new_adj = set_at(adj, rep_u, new_adj_row)
          row_mem_u = get_at(members, rep_u)
          row_mem_v = get_at(members, rep_v)
          new_mem_row = or_rows(row_mem_u, row_mem_v)
          new_members = set_at(members, rep_u, new_mem_row)
          max_u = get_at(maxes, rep_u)
          max_v = get_at(maxes, rep_v)
          if max_u > max_v:
            new_max = max_u
          else:
            new_max = max_v
          new_maxes = set_at(maxes, rep_u, new_max)
          return process(cands.tail, new_labels, new_maxes, new_adj, new_members)

def make_output(labels, maxes):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      value = get_at(maxes, labels.head)
      return List/Cons(value, make_output(labels.tail, maxes))
