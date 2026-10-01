type Vec: Leaf { value } | Branch { left, right }

def prog(x):
  (n, pairs) = x
  width = capacity(n, 1)
  (parents, sizes) = make_vectors(0, width, n)
  if n == 0:
    return process_edges(pairs, parents, sizes, width, 0)
  else:
    return process_edges(pairs, parents, sizes, width, 1)

def capacity(n, width):
  if width < n:
    return capacity(n, width * 2)
  else:
    return width

def make_vectors(start, width, n):
  if width == 1:
    if start < n:
      return (Vec/Leaf(start), Vec/Leaf(1))
    else:
      return (Vec/Leaf(0), Vec/Leaf(0))
  else:
    half = width / 2
    (left_parents, left_sizes) = make_vectors(start, half, n)
    (right_parents, right_sizes) = make_vectors(start + half, half, n)
    return (Vec/Branch(left_parents, right_parents), Vec/Branch(left_sizes, right_sizes))

def vec_get(tree, index, width):
  match tree:
    case Vec/Leaf:
      return tree.value
    case Vec/Branch:
      half = width / 2
      if index < half:
        return vec_get(tree.left, index, half)
      else:
        return vec_get(tree.right, index - half, half)

def vec_set(tree, index, width, value):
  match tree:
    case Vec/Leaf:
      return Vec/Leaf(value)
    case Vec/Branch:
      half = width / 2
      if index < half:
        return Vec/Branch(vec_set(tree.left, index, half, value), tree.right)
      else:
        return Vec/Branch(tree.left, vec_set(tree.right, index - half, half, value))

def find_root(parents, node, width):
  parent = vec_get(parents, node, width)
  if parent == node:
    return node
  else:
    return find_root(parents, parent, width)

def process_edges(pairs, parents, sizes, width, best):
  match pairs:
    case List/Nil:
      return best
    case List/Cons:
      (u, v) = pairs.head
      root_u = find_root(parents, u, width)
      root_v = find_root(parents, v, width)
      if root_u == root_v:
        return process_edges(pairs.tail, parents, sizes, width, best)
      else:
        size_u = vec_get(sizes, root_u, width)
        size_v = vec_get(sizes, root_v, width)
        new_size = size_u + size_v
        if size_u >= size_v:
          new_parents = vec_set(parents, root_v, width, root_u)
          new_sizes = vec_set(sizes, root_u, width, new_size)
        else:
          new_parents = vec_set(parents, root_u, width, root_v)
          new_sizes = vec_set(sizes, root_v, width, new_size)
        if new_size > best:
          return process_edges(pairs.tail, new_parents, new_sizes, width, new_size)
        else:
          return process_edges(pairs.tail, new_parents, new_sizes, width, best)
