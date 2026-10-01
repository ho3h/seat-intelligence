def prog(x):
  (n, edges) = x
  adj = build_adj(0, n, edges)
  bits = make_words((n + 23) / 24)
  return count_components(0, n, adj, bits, 0)

def make_words(k):
  if k == 0:
    return []
  else:
    return List/Cons(0, make_words(k - 1))

def build_adj(i, n, edges):
  if i == n:
    return []
  else:
    ns = get_neighbors(i, edges)
    rest = build_adj(i + 1, n, edges)
    return List/Cons(ns, rest)

def get_neighbors(v, edges):
  match edges:
    case List/Nil:
      return []
    case List/Cons:
      (a, b) = edges.head
      rest = get_neighbors(v, edges.tail)
      if a == v:
        return List/Cons(b, rest)
      else:
        if b == v:
          return List/Cons(a, rest)
        else:
          return rest

def count_components(i, n, adj, bits, components):
  if i == n:
    return components
  else:
    if is_seen(i, bits) == 1:
      return count_components(i + 1, n, adj, bits, components)
    else:
      bits2 = mark_seen(i, bits)
      seen2 = explore(List/Cons(i, []), adj, bits2)
      return count_components(i + 1, n, adj, seen2, components + 1)

def explore(stack, adj, bits):
  match stack:
    case List/Nil:
      return bits
    case List/Cons:
      v = stack.head
      rest = stack.tail
      ns = get_at(v, adj)
      (bits2, stack2) = add_neighbors(ns, bits, rest)
      return explore(stack2, adj, bits2)

def add_neighbors(ns, bits, stack):
  match ns:
    case List/Nil:
      return (bits, stack)
    case List/Cons:
      v = ns.head
      rest = ns.tail
      if is_seen(v, bits) == 1:
        return add_neighbors(rest, bits, stack)
      else:
        bits2 = mark_seen(v, bits)
        stack2 = List/Cons(v, stack)
        return add_neighbors(rest, bits2, stack2)

def is_seen(v, bits):
  word = get_at(v / 24, bits)
  bit = 1 << (v % 24)
  if (word & bit) == 0:
    return 0
  else:
    return 1

def mark_seen(v, bits):
  word_index = v / 24
  bit = 1 << (v % 24)
  return update_word(word_index, bit, bits)

def update_word(i, bit, words):
  match words:
    case List/Nil:
      return []
    case List/Cons:
      if i == 0:
        return List/Cons(words.head | bit, words.tail)
      else:
        rest = update_word(i - 1, bit, words.tail)
        return List/Cons(words.head, rest)

def get_at(i, xs):
  match xs:
    case List/Nil:
      return 0
    case List/Cons:
      if i == 0:
        return xs.head
      else:
        return get_at(i - 1, xs.tail)
