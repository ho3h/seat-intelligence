type Trie: Empty | Branch { left, right } | Leaf { value }

def prog(x):
  (k, clusters, edges) = x
  tree = build_trie(clusters, 0, Trie/Empty)
  candidates = collect_neighbours(k, tree, edges, [])
  return dedup(radix_sort(candidates, 23))

def build_trie(xs, i, tree):
  match xs:
    case List/Nil:
      return tree
    case List/Cons:
      next_tree = trie_put(tree, i, xs.head, 0)
      return build_trie(xs.tail, i + 1, next_tree)

def trie_put(tree, key, value, depth):
  if depth == 24:
    return Trie/Leaf(value)
  else:
    bit = key & 1
    rest = key >> 1
    match tree:
      case Trie/Empty:
        if bit == 0:
          left = trie_put(Trie/Empty, rest, value, depth + 1)
          return Trie/Branch(left, Trie/Empty)
        else:
          right = trie_put(Trie/Empty, rest, value, depth + 1)
          return Trie/Branch(Trie/Empty, right)
      case Trie/Branch:
        if bit == 0:
          left = trie_put(tree.left, rest, value, depth + 1)
          return Trie/Branch(left, tree.right)
        else:
          right = trie_put(tree.right, rest, value, depth + 1)
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
        if (key & 1) == 0:
          return trie_get(tree.left, key >> 1, depth + 1)
        else:
          return trie_get(tree.right, key >> 1, depth + 1)

def collect_neighbours(k, tree, edges, acc):
  match edges:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v) = edges.head
      a = trie_get(tree, u, 0)
      b = trie_get(tree, v, 0)
      if a == k:
        if b == k:
          return collect_neighbours(k, tree, edges.tail, acc)
        else:
          return collect_neighbours(k, tree, edges.tail, List/Cons(b, acc))
      else:
        if b == k:
          return collect_neighbours(k, tree, edges.tail, List/Cons(a, acc))
        else:
          return collect_neighbours(k, tree, edges.tail, acc)

def split_bit(xs, bit, zeros, ones):
  match xs:
    case List/Nil:
      return (zeros, ones)
    case List/Cons:
      if ((xs.head >> bit) & 1) == 0:
        return split_bit(xs.tail, bit, List/Cons(xs.head, zeros), ones)
      else:
        return split_bit(xs.tail, bit, zeros, List/Cons(xs.head, ones))

def append(xs, ys):
  match xs:
    case List/Nil:
      return ys
    case List/Cons:
      return List/Cons(xs.head, append(xs.tail, ys))

def radix_sort(xs, bit):
  (zeros, ones) = split_bit(xs, bit, [], [])
  if bit == 0:
    return append(zeros, ones)
  else:
    sorted_zeros = radix_sort(zeros, bit - 1)
    sorted_ones = radix_sort(ones, bit - 1)
    return append(sorted_zeros, sorted_ones)

def dedup(xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      match xs.tail:
        case List/Nil:
          return [xs.head]
        case List/Cons:
          if xs.head == xs.tail.head:
            return dedup(xs.tail)
          else:
            return List/Cons(xs.head, dedup(xs.tail))
