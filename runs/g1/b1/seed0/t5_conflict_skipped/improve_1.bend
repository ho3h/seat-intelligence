def prog(x):
  (n, cap, mnl, cands) = x
  words = (n + 23) / 24
  zero_bits = make_zero_bits(words)
  rows = make_rows(n, zero_bits)
  rows = add_constraints(mnl, rows)
  labels = make_labels(0, n)
  states = make_states(0, n, rows, zero_bits)
  ordered = merge_sort(cands)
  return process(ordered, labels, states, mnl, cap, [])

def make_zero_bits(count):
  if count == 0:
    return []
  else:
    return List/Cons(0, make_zero_bits(count - 1))

def make_rows(count, zero_bits):
  if count == 0:
    return []
  else:
    return List/Cons(zero_bits, make_rows(count - 1, zero_bits))

def make_labels(i, n):
  if i < n:
    return List/Cons(i, make_labels(i + 1, n))
  else:
    return []

def list_at(xs, i):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return list_at(xs.tail, i - 1)

def list_set(xs, i, value):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(value, xs.tail)
      else:
        return List/Cons(xs.head, list_set(xs.tail, i - 1, value))

def set_bit(bits, word_index, bit_index):
  word = list_at(bits, word_index)
  updated_word = word | (1 << bit_index)
  return list_set(bits, word_index, updated_word)

def add_constraints(mnl, rows):
  match mnl:
    case List/Nil:
      return rows
    case List/Cons:
      (a, b) = mnl.head
      row_a = list_at(rows, a)
      row_a = set_bit(row_a, b / 24, b % 24)
      rows = list_set(rows, a, row_a)
      row_b = list_at(rows, b)
      row_b = set_bit(row_b, a / 24, a % 24)
      rows = list_set(rows, b, row_b)
      return add_constraints(mnl.tail, rows)

def make_states(i, n, rows, zero_bits):
  if i < n:
    members = set_bit(zero_bits, i / 24, i % 24)
    forbidden = list_at(rows, i)
    state = (members, forbidden, 1)
    return List/Cons(state, make_states(i + 1, n, rows, zero_bits))
  else:
    return []

def bit_or(a, b):
  match a:
    case List/Nil:
      return []
    case List/Cons:
      return List/Cons(a.head | b.head, bit_or(a.tail, b.tail))

def has_intersection(a, b):
  match a:
    case List/Nil:
      return 0
    case List/Cons:
      if (a.head & b.head) != 0:
        return 1
      else:
        return has_intersection(a.tail, b.tail)

def candidate_precedes(a, b):
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

def split_alternating(xs):
  match xs:
    case List/Nil:
      return ([], [])
    case List/Cons:
      (left, right) = split_alternating(xs.tail)
      return (List/Cons(xs.head, right), left)

def merge_sorted(a, b):
  match a:
    case List/Nil:
      return b
    case List/Cons:
      match b:
        case List/Nil:
          return a
        case List/Cons:
          if candidate_precedes(a.head, b.head) == 1:
            return List/Cons(a.head, merge_sorted(a.tail, b))
          else:
            return List/Cons(b.head, merge_sorted(a, b.tail))

def merge_sort(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return xs
        case List/Cons:
          (left, right) = split_alternating(xs)
          sorted_left = merge_sort(left)
          sorted_right = merge_sort(right)
          return merge_sorted(sorted_left, sorted_right)

def replace_label(labels, old_label, new_label):
  match labels:
    case List/Nil:
      return []
    case List/Cons:
      tail = replace_label(labels.tail, old_label, new_label)
      if labels.head == old_label:
        return List/Cons(new_label, tail)
      else:
        return List/Cons(labels.head, tail)

def reverse_pairs(xs):
  return reverse_pairs_acc(xs, [])

def reverse_pairs_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_pairs_acc(xs.tail, List/Cons(xs.head, acc))

def process(cands, labels, states, mnl, cap, skipped_rev):
  match cands:
    case List/Nil:
      return reverse_pairs(skipped_rev)
    case List/Cons:
      (u, v, score) = cands.head
      la = list_at(labels, u)
      lb = list_at(labels, v)
      if la == lb:
        return process(cands.tail, labels, states, mnl, cap, skipped_rev)
      else:
        state_a = list_at(states, la)
        state_b = list_at(states, lb)
        (members_a, forbidden_a, size_a) = state_a
        (members_b, forbidden_b, size_b) = state_b
        if size_a + size_b > cap:
          skipped_rev = List/Cons((u, v), skipped_rev)
          return process(cands.tail, labels, states, mnl, cap, skipped_rev)
        else:
          if has_intersection(forbidden_a, members_b) == 1:
            skipped_rev = List/Cons((u, v), skipped_rev)
            return process(cands.tail, labels, states, mnl, cap, skipped_rev)
          else:
            members = bit_or(members_a, members_b)
            forbidden = bit_or(forbidden_a, forbidden_b)
            merged_state = (members, forbidden, size_a + size_b)
            states = list_set(states, la, merged_state)
            labels = replace_label(labels, lb, la)
            return process(cands.tail, labels, states, mnl, cap, skipped_rev)
