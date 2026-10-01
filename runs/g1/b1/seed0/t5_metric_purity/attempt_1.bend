def prog(x):
  (pred, truth) = x
  freqs = build_freqs(pred, truth, List/Nil)
  return sum_group_maxima(freqs, List/Nil, 0)

def build_freqs(pred, truth, acc):
  match pred:
    case List/Nil:
      return acc
    case List/Cons:
      match truth:
        case List/Nil:
          return acc
        case List/Cons:
          next_acc = add_freq(acc, pred.head, truth.head)
          return build_freqs(pred.tail, truth.tail, next_acc)

def add_freq(freqs, p, t):
  match freqs:
    case List/Nil:
      return List/Cons((p, t, 1), List/Nil)
    case List/Cons:
      (q, u, count) = freqs.head
      if p == q:
        if t == u:
          return List/Cons((q, u, count + 1), freqs.tail)
        else:
          rest = add_freq(freqs.tail, p, t)
          return List/Cons(freqs.head, rest)
      else:
        rest = add_freq(freqs.tail, p, t)
        return List/Cons(freqs.head, rest)

def contains_label(labels, p):
  match labels:
    case List/Nil:
      return 0
    case List/Cons:
      if labels.head == p:
        return 1
      else:
        return contains_label(labels.tail, p)

def group_max(freqs, p, best):
  match freqs:
    case List/Nil:
      return best
    case List/Cons:
      (q, t, count) = freqs.head
      if q == p:
        if count > best:
          return group_max(freqs.tail, p, count)
        else:
          return group_max(freqs.tail, p, best)
      else:
        return group_max(freqs.tail, p, best)

def sum_group_maxima(freqs, seen, total):
  match freqs:
    case List/Nil:
      return total
    case List/Cons:
      (p, t, count) = freqs.head
      if contains_label(seen, p) == 1:
        return sum_group_maxima(freqs.tail, seen, total)
      else:
        best = group_max(freqs, p, 0)
        next_seen = List/Cons(p, seen)
        return sum_group_maxima(freqs.tail, next_seen, total + best)
