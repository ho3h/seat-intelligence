def prog(x):
  (n, tau, cands) = x
  cap = capacity(n, 1)
  parents = make_tree(0, cap)
  sizes = make_tree(1, cap)
  maxima = make_tree(0, cap)
  maxima = make_tree(0, cap)
  maxima = make_tree(0, cap)
  maxima = make_max_tree(0, cap)
  (parents, sizes, maxima) = process(cands, tau, cap, parents, sizes, maxima)
  return build_output(0, n, cap, parents, maxima)

def capacity(n, c):
  if c >= n:
    return c
  else:
    return capacity(n, c * 2)

def make_tree(start, size):
  if size == 1:
    return start
  else:
    half = size / 2
    left = make_tree(start, half)
    right = make_tree(start + half, half)
    return (left, right)

def make_max_tree(start, size):
  if size == 1:
    return start
  else:
    half = size / 2
    left = make_max_tree(start, half)
    right = make_max_tree(start + half, half)
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

def find_root(parents, cap, node):
  parent = tree_get(parents, cap, node)
  if parent == node:
    return node
  else:
    return find_root(parents, cap, parent)

def process(cands, tau, cap, parents, sizes, maxima):
  match cands:
    case List/Nil:
      return (parents, sizes, maxima)
    case List/Cons:
      (u, v, score) = cands.head
      if score >= tau:
        (parents2, sizes2, maxima2) = union(
          parents, sizes, maxima, cap, u, v
        )
        return process(cands.tail, tau, cap, parents2, sizes2, maxima2)
      else:
        return process(cands.tail, tau, cap, parents, sizes, maxima)

def union(parents, sizes, maxima, cap, u, v):
  ru = find_root(parents, cap, u)
  rv = find_root(parents, cap, v)
  if ru == rv:
    return (parents, sizes, maxima)
  else:
    su = tree_get(sizes, cap, ru)
    sv = tree_get(sizes, cap, rv)
    mu = tree_get(maxima, cap, ru)
    mv = tree_get(maxima, cap, rv)
    if su < sv:
      parents2 = tree_set(parents, cap, ru, rv)
      sizes2 = tree_set(sizes, cap, rv, su + sv)
      if mu > mv:
        maxima2 = tree_set(maxima, cap, rv, mu)
      else:
        maxima2 = maxima
      return (parents2, sizes2, maxima2)
    else:
      parents2 = tree_set(parents, cap, rv, ru)
      sizes2 = tree_set(sizes, cap, ru, su + sv)
      if mv > mu:
        maxima2 = tree_set(maxima, cap, ru, mv)
      else:
        maxima2 = maxima
      return (parents2, sizes2, maxima2)

def build_output(i, n, cap, parents, maxima):
  if i == n:
    return List/Nil
  else:
    root = find_root(parents, cap, i)
    value = tree_get(maxima, cap, root)
    return List/Cons(value, build_output(i + 1, n, cap, parents, maxima))
