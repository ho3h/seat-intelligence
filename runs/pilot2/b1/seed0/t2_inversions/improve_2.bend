type Trie: Empty | Branch { count, zero, one }

def prog(xs):
  return count_inversions(xs, Trie/Empty)

def count_inversions(xs, trie):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      (next_trie, greater) = trie_insert(trie, xs.head, 23)
      return greater + count_inversions(xs.tail, next_trie)

def trie_count(trie):
  match trie:
    case Trie/Empty:
      return 0
    case Trie/Branch:
      return trie.count

def bump_leaf(trie):
  match trie:
    case Trie/Empty:
      return Trie/Branch(1, Trie/Empty, Trie/Empty)
    case Trie/Branch:
      return Trie/Branch(trie.count + 1, Trie/Empty, Trie/Empty)

def trie_insert(trie, x, bit):
  value_bit = (x >> bit) & 1
  if bit == 0:
    match trie:
      case Trie/Empty:
        if value_bit == 0:
          return (Trie/Branch(1, bump_leaf(Trie/Empty), Trie/Empty), 0)
        else:
          return (Trie/Branch(1, Trie/Empty, bump_leaf(Trie/Empty)), 0)
      case Trie/Branch:
        if value_bit == 0:
          return (Trie/Branch(trie.count + 1, bump_leaf(trie.zero), trie.one), trie_count(trie.one))
        else:
          return (Trie/Branch(trie.count + 1, trie.zero, bump_leaf(trie.one)), 0)
  else:
    match trie:
      case Trie/Empty:
        (child, _) = trie_insert(Trie/Empty, x, bit - 1)
        if value_bit == 0:
          return (Trie/Branch(1, child, Trie/Empty), 0)
        else:
          return (Trie/Branch(1, Trie/Empty, child), 0)
      case Trie/Branch:
        if value_bit == 0:
          (child, greater) = trie_insert(trie.zero, x, bit - 1)
          return (Trie/Branch(trie.count + 1, child, trie.one), trie_count(trie.one) + greater)
        else:
          (child, greater) = trie_insert(trie.one, x, bit - 1)
          return (Trie/Branch(trie.count + 1, trie.zero, child), greater)
