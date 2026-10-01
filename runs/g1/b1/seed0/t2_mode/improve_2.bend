type Trie: Empty | Node { count, zero, one }

def prog(xs):
  trie = insert_all(xs, Trie/Empty)
  (value, count) = find_best(trie, 24, 0)
  return value

def insert_all(xs, trie):
  match xs:
    case List/Nil:
      return trie
    case List/Cons:
      updated = trie_add(trie, xs.head, 24)
      return insert_all(xs.tail, updated)

def trie_add(trie, value, bit):
  match trie:
    case Trie/Empty:
      if bit == 0:
        return Trie/Node(1, Trie/Empty, Trie/Empty)
      else:
        if ((value >> (bit - 1)) & 1) == 0:
          child = trie_add(Trie/Empty, value, bit - 1)
          return Trie/Node(1, child, Trie/Empty)
        else:
          child = trie_add(Trie/Empty, value, bit - 1)
          return Trie/Node(1, Trie/Empty, child)
    case Trie/Node:
      if bit == 0:
        return Trie/Node(trie.count + 1, trie.zero, trie.one)
      else:
        if ((value >> (bit - 1)) & 1) == 0:
          child = trie_add(trie.zero, value, bit - 1)
          return Trie/Node(trie.count + 1, child, trie.one)
        else:
          child = trie_add(trie.one, value, bit - 1)
          return Trie/Node(trie.count + 1, trie.zero, child)

def find_best(trie, bit, prefix):
  match trie:
    case Trie/Empty:
      return (0, 0)
    case Trie/Node:
      if bit == 0:
        return (prefix, trie.count)
      else:
        left = find_best(trie.zero, bit - 1, prefix * 2)
        right = find_best(trie.one, bit - 1, prefix * 2 + 1)
        (left_value, left_count) = left
        (right_value, right_count) = right
        if left_count > right_count:
          return left
        else:
          if right_count > left_count:
            return right
          else:
            if left_value < right_value:
              return left
            else:
              return right
