def prog(x):
  (tau, probs) = x
  return decide(probs, 0, 0, 0, tau)

def decide(probs, index, best_index, best_value, tau):
  match probs:
    case List/Nil:
      if best_value >= tau:
        return best_index
      else:
        return 6
    case List/Cons:
      if probs.head > best_value:
        return decide(probs.tail, index + 1, index, probs.head, tau)
      else:
        return decide(probs.tail, index + 1, best_index, best_value, tau)
