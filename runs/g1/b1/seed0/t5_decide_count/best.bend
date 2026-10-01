def prog(x):
  (tau, cands) = x
  return count2(cands, tau, 0)

def count2(xs, tau, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u1, v1, s1) = xs.head
      tail1 = xs.tail
      match tail1:
        case List/Nil:
          if s1 >= tau:
            return acc + 1
          else:
            return acc
        case List/Cons:
          (u2, v2, s2) = tail1.head
          tail2 = tail1.tail
          if s1 >= tau:
            if s2 >= tau:
              return count2(tail2, tau, acc + 2)
            else:
              return count2(tail2, tau, acc + 1)
          else:
            if s2 >= tau:
              return count2(tail2, tau, acc + 1)
            else:
              return count2(tail2, tau, acc)
