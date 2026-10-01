type Trie: Empty | Branch { a, b, c, d, terminal }

def prog(x):
  (ledger, proposals) = x
  trie = build_ledger(ledger, Trie/Empty)
  kept_rev = process_proposals(proposals, trie, [])
  return reverse(kept_rev)

def build_ledger(ledger, trie):
  match ledger:
    case List/Nil:
      return trie
    case List/Cons:
      (verb, target, status) = ledger.head
      if status == 0:
        next_trie = trie_insert(trie, target, verb, 0)
        return build_ledger(ledger.tail, next_trie)
      else:
        if status == 1:
          next_trie = trie_insert(trie, target, verb, 0)
          return build_ledger(ledger.tail, next_trie)
        else:
          return build_ledger(ledger.tail, trie)

def process_proposals(proposals, trie, kept_rev):
  match proposals:
    case List/Nil:
      return kept_rev
    case List/Cons:
      (verb, target) = proposals.head
      if trie_has(trie, target, verb, 0) == 1:
        return process_proposals(proposals.tail, trie, kept_rev)
      else:
        next_trie = trie_insert(trie, target, verb, 0)
        next_kept = List/Cons(proposals.head, kept_rev)
        return process_proposals(proposals.tail, next_trie, next_kept)

def trie_has(tree, target, verb, level):
  match tree:
    case Trie/Empty:
      return 0
    case Trie/Branch:
      if level == 14:
        return tree.terminal
      else:
        digit = trie_digit(target, verb, level)
        if digit == 0:
          return trie_has(tree.a, target, verb, level + 1)
        else:
          if digit == 1:
            return trie_has(tree.b, target, verb, level + 1)
          else:
            if digit == 2:
              return trie_has(tree.c, target, verb, level + 1)
            else:
              return trie_has(tree.d, target, verb, level + 1)

def trie_insert(tree, target, verb, level):
  if level == 14:
    match tree:
      case Trie/Empty:
        return Trie/Branch(Trie/Empty, Trie/Empty, Trie/Empty, Trie/Empty, 1)
      case Trie/Branch:
        return Trie/Branch(tree.a, tree.b, tree.c, tree.d, 1)
  else:
    match tree:
      case Trie/Empty:
        return trie_insert_node(Trie/Empty, Trie/Empty, Trie/Empty, Trie/Empty, 0, target, verb, level)
      case Trie/Branch:
        return trie_insert_node(tree.a, tree.b, tree.c, tree.d, tree.terminal, target, verb, level)

def trie_insert_node(a, b, c, d, terminal, target, verb, level):
  digit = trie_digit(target, verb, level)
  if digit == 0:
    next_a = trie_insert(a, target, verb, level + 1)
    return Trie/Branch(next_a, b, c, d, terminal)
  else:
    if digit == 1:
      next_b = trie_insert(b, target, verb, level + 1)
      return Trie/Branch(a, next_b, c, d, terminal)
    else:
      if digit == 2:
        next_c = trie_insert(c, target, verb, level + 1)
        return Trie/Branch(a, b, next_c, d, terminal)
      else:
        next_d = trie_insert(d, target, verb, level + 1)
        return Trie/Branch(a, b, c, next_d, terminal)

def trie_digit(target, verb, level):
  if level < 12:
    shift = 22 - (2 * level)
    return (target >> shift) & 3
  else:
    shift = 2 * (13 - level)
    return (verb >> shift) & 3

def reverse(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))
