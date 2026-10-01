def prog(x):
  (tau, cands) = x
  return filter2(tau, cands)

def filter2(tau, xs):
  match xs:
    case List/Nil:
      return []
    case List/Cons:
      a = xs.head
      (a_u, a_v, score_a) = a
      match xs.tail:
        case List/Nil:
          if score_a >= tau:
            return [a]
          else:
            return []
        case List/Cons:
          b = xs.tail.head
          (b_u, b_v, score_b) = b
          rest = filter2(tau, xs.tail.tail)
          if score_a >= tau:
            if score_b >= tau:
              return List/Cons(a, List/Cons(b, rest))
            else:
              return List/Cons(a, rest)
          else:
            if score_b >= tau:
              return List/Cons(b, rest)
            else:
              return rest
