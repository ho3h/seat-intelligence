type DsuVec: DsuLeaf { value } | DsuBranch { left, right }

def prog(x):
  (n, target, pairs) = x
  width = capacity(n, 1)
  (parents, sizes) = make_trees(0, width)
  (merged_parents, merged_sizes) = merge_all(pairs, parents, sizes, width)
  (target_root, compressed_parents) = find_root(merged_parents, target, width)
  return collect_members(n, compressed_parents, width, target_root, [])

def capacity(n, width):
  if width < n:
    return capacity(n, width * 2)
  else:
    return width

def make_trees(base, width):
  if width == 1:
    return (DsuVec/DsuLeaf(base), DsuVec/DsuLeaf(1))
  else:
    half = width / 2
    (left_parents, left_sizes) = make_trees(base, half)
    (right_parents, right_sizes) = make_trees(base + half, half)
    parents = DsuVec/DsuBranch(left_parents, right_parents)
    sizes = DsuVec/DsuBranch(left_sizes, right_sizes)
    return (parents, sizes)

def vec_get(tree, index, width):
  match tree:
    case DsuVec/DsuLeaf:
      return tree.value
    case DsuVec/DsuBranch:
      half = width / 2
      if index < half:
        return vec_get(tree.left, index, half)
      else:
        return vec_get(tree.right, index - half, half)

def vec_set(tree, index, width, value):
  match tree:
    case DsuVec/DsuLeaf:
      return DsuVec/DsuLeaf(value)
    case DsuVec/DsuBranch:
      half = width / 2
      if index < half:
        return DsuVec/DsuBranch(
          vec_set(tree.left, index, half, value),
          tree.right
        )
      else:
        return DsuVec/DsuBranch(
          tree.left,
          vec_set(tree.right, index - half, half, value)
        )

def find_root(parents, node, width):
  parent = vec_get(parents, node, width)
  if parent == node:
    return (node, parents)
  else:
    (root, compressed_parents) = find_root(parents, parent, width)
    return (root, vec_set(compressed_parents, node, width, root))

def merge_all(pairs, parents, sizes, width):
  match pairs:
    case List/Nil:
      return (parents, sizes)
    case List/Cons:
      (u, v) = pairs.head
      (root_u, parents_u) = find_root(parents, u, width)
      (root_v, parents_v) = find_root(parents_u, v, width)
      if root_u == root_v:
        return merge_all(pairs.tail, parents_v, sizes, width)
      else:
        size_u = vec_get(sizes, root_u, width)
        size_v = vec_get(sizes, root_v, width)
        if size_u < size_v:
          new_parents = vec_set(parents_v, root_u, width, root_v)
          new_sizes = vec_set(sizes, root_v, width, size_u + size_v)
          return merge_all(pairs.tail, new_parents, new_sizes, width)
        else:
          new_parents = vec_set(parents_v, root_v, width, root_u)
          new_sizes = vec_set(sizes, root_u, width, size_u + size_v)
          return merge_all(pairs.tail, new_parents, new_sizes, width)

def collect_members(i, parents, width, target_root, acc):
  if i == 0:
    return acc
  else:
    node = i - 1
    (root, compressed_parents) = find_root(parents, node, width)
    if root == target_root:
      return collect_members(node, compressed_parents, width, target_root, List/Cons(node, acc))
    else:
      return collect_members(node, compressed_parents, width, target_root, acc)
