def prog(x):
  (ledger, proposals) = x
  kept_rev = process(ledger, proposals, [])
  return reverse(kept_rev)

def process(ledger, proposals, kept_rev):
  match proposals:
    case List/Nil:
      return kept_rev
    case List/Cons:
      (verb, target) = proposals.head
      blocked = has_ledger_block(ledger, verb, target)
      duplicate = has_pair(kept_rev, verb, target)
      if blocked == 1:
        return process(ledger, proposals.tail, kept_rev)
      else:
        if duplicate == 1:
          return process(ledger, proposals.tail, kept_rev)
        else:
          return process(ledger, proposals.tail, List/Cons(proposals.head, kept_rev))

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

def reverse(xs):
  return reverse_acc(xs, [])

def reverse_acc(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_acc(xs.tail, List/Cons(xs.head, acc))
