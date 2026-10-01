def prog(x):
  (ledger, proposals) = x
  return filter_proposals(ledger, proposals, [])

def filter_proposals(ledger, proposals, prefix):
  match proposals:
    case List/Nil:
      return []
    case List/Cons:
      next_prefix = List/Cons(proposals.head, prefix)
      rest = filter_proposals(ledger, proposals.tail, next_prefix)
      (verb, target) = proposals.head
      blocked = has_ledger_block(ledger, verb, target)
      if blocked == 1:
        return rest
      else:
        duplicate = has_pair(prefix, verb, target)
        if duplicate == 1:
          return rest
        else:
          return List/Cons(proposals.head, rest)

def has_ledger_block(ledger, verb, target):
  match ledger:
    case List/Nil:
      return 0
    case List/Cons:
      (entry_verb, entry_target, status) = ledger.head
      if entry_verb == verb:
        if entry_target == target:
          if status == 0:
            return 1
          else:
            if status == 1:
              return 1
            else:
              return has_ledger_block(ledger.tail, verb, target)
        else:
          return has_ledger_block(ledger.tail, verb, target)
      else:
        return has_ledger_block(ledger.tail, verb, target)

def has_pair(pairs, verb, target):
  match pairs:
    case List/Nil:
      return 0
    case List/Cons:
      (pair_verb, pair_target) = pairs.head
      if pair_verb == verb:
        if pair_target == target:
          return 1
        else:
          return has_pair(pairs.tail, verb, target)
      else:
        return has_pair(pairs.tail, verb, target)
