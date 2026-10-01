def prog(x):
  (n, tau, cands) = x
  cap = capacity(n, 1)
  records = make_records(0, cap)
  records = process(cands, tau, cap, records)
  return build_output(0, n, cap, records)

def capacity(n, c):
  if c >= n:
    return c
  else:
    return capacity(n, c * 2)

def make_records(start, size):
  if size == 1:
    return (start, 1, start)
  else:
    half = size / 2
    left = make_records(start, half)
    right = make_records(start + half, half)
    return (left, right)

def tree_get(tree, size, index):
  if size == 1:
    return tree
  else:
    (left, right) = tree
    half = size / 2
    if index < half:
      return tree_get(left, half, index)
    else:
      return tree_get(right, half, index - half)

def tree_set(tree, size, index, value):
  if size == 1:
    return value
  else:
    (left, right) = tree
    half = size / 2
    if index < half:
      return (tree_set(left, half, index, value), right)
    else:
      return (left, tree_set(right, half, index - half, value))

def tree_set_two(tree, size, i, value_i, j, value_j):
  if size == 1:
    return value_i
  else:
    (left, right) = tree
    half = size / 2
    if i < half:
      if j < half:
        return (tree_set_two(left, half, i, value_i, j, value_j), right)
      else:
        return (tree_set(left, half, i, value_i), tree_set(right, half, j - half, value_j))
    else:
      if j < half:
        return (tree_set(left, half, j, value_j), tree_set(right, half, i - half, value_i))
      else:
        return (left, tree_set_two(right, half, i - half, value_i, j - half, value_j))

def find_root(records, cap, node):
  (parent, size, maximum) = tree_get(records, cap, node)
  if parent == node:
    return node
  else:
    return find_root(records, cap, parent)

def process(cands, tau, cap, records):
  match cands:
    case List/Nil:
      return records
    case List/Cons:
      (u, v, score) = cands.head
      if score >= tau:
        records2 = union(records, cap, u, v)
        return process(cands.tail, tau, cap, records2)
      else:
        return process(cands.tail, tau, cap, records)

def union(records, cap, u, v):
  ru = find_root(records, cap, u)
  rv = find_root(records, cap, v)
  if ru == rv:
    return records
  else:
    (pu, su, mu) = tree_get(records, cap, ru)
    (pv, sv, mv) = tree_get(records, cap, rv)
    if su < sv:
      if mu > mv:
        root_record = (rv, su + sv, mu)
      else:
        root_record = (rv, su + sv, mv)
      child_record = (rv, su, mu)
      return tree_set_two(records, cap, ru, child_record, rv, root_record)
    else:
      if mv > mu:
        root_record = (ru, su + sv, mv)
      else:
        root_record = (ru, su + sv, mu)
      child_record = (ru, sv, mv)
      return tree_set_two(records, cap, ru, root_record, rv, child_record)

def build_output(i, n, cap, records):
  if i == n:
    return List/Nil
  else:
    root = find_root(records, cap, i)
    (parent, size, maximum) = tree_get(records, cap, root)
    return List/Cons(maximum, build_output(i + 1, n, cap, records))
