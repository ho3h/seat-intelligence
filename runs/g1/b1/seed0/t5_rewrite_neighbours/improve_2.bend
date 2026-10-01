type Trie: Empty | Branch { left, right } | Leaf { value }

def prog(x):
  (k, clusters, edges) = x
  map = build_map(clusters, 0, Trie/Empty)
  neighbours = gather(k, map, edges, Trie/Empty)
  return collect_ascending(neighbours, [])

def build_map(xs, i, tree):
  match xs:
    case List/Nil:
      return tree
    case List/Cons:
      next = trie_put(tree, i, xs.head, 0)
      return build_map(xs.tail, i + 1, next)

def trie_put(tree, key, value, depth):
  if depth == 24:
    return Trie/Leaf(value)
  else:
    bit = (key >> (23 - depth)) & 1
    match tree:
      case Trie/Empty:
        if bit == 0:
          left = trie_put(Trie/Empty, key, value, depth + 1)
          return Trie/Branch(left, Trie/Empty)
        else:
          right = trie_put(Trie/Empty, key, value, depth + 1)
          return Trie/Branch(Trie/Empty, right)
      case Trie/Branch:
        if bit == 0:
          left = trie_put(tree.left, key, value, depth + 1)
          return Trie/Branch(left, tree.right)
        else:
          right = trie_put(tree.right, key, value, depth + 1)
          return Trie/Branch(tree.left, right)
      case Trie/Leaf:
        return tree

def trie_get(tree, key, depth):
  if depth == 24:
    match tree:
      case Trie/Leaf:
        return tree.value
      case Trie/Empty:
        return 0
      case Trie/Branch:
        return 0
  else:
    match tree:
      case Trie/Empty:
        return 0
      case Trie/Leaf:
        return tree.value
      case Trie/Branch:
        bit = (key >> (23 - depth)) & 1
        if bit == 0:
          return trie_get(tree.left, key, depth + 1)
        else:
          return trie_get(tree.right, key, depth + 1)

def gather(k, map, edges, seen):
  match edges:
    case List/Nil:
      return seen
    case List/Cons:
      (u, v) = edges.head
      a = trie_get(map, u, 0)
      b = trie_get(map, v, 0)
      if a == k:
        if b == k:
          return gather(k, map, edges.tail, seen)
        else:
          return gather(k, map, edges.tail, trie_put(seen, b, b, 0))
      else:
        if b == k:
          return gather(k, map, edges.tail, trie_put(seen, a, a, 0))
        else:
          return gather(k, map, edges.tail, seen)

def collect_ascending(tree, acc):
  match tree:
    case Trie/Empty:
      return acc
    case Trie/Leaf:
      return List/Cons(tree.value, acc)
    case Trie/Branch:
      right = collect_ascending(tree.right, acc)
      return collect_ascending(tree.left, right)
