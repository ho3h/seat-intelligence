def prog(x):
  (tau, cands) = x
  return count4(cands, tau, 0)

def count_tail(xs, tau, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u, v, score) = xs.head
      if score >= tau:
        return count_tail(xs.tail, tau, acc + 1)
      else:
        return count_tail(xs.tail, tau, acc)

def count4(xs, tau, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      (u1, v1, s1) = xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          return count_tail(xs, tau, acc)
        case List/Cons:
          (u2, v2, s2) = t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              return count_tail(xs, tau, acc)
            case List/Cons:
              (u3, v3, s3) = t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  return count_tail(xs, tau, acc)
                case List/Cons:
                  (u4, v4, s4) = t3.head
                  return count_block(s1, s2, s3, s4, tau, t3.tail, acc)

def count_block(a, b, c, d, tau, rest, acc):
  if a >= tau:
    if b >= tau:
      if c >= tau:
        if d >= tau:
          return count4(rest, tau, acc + 4)
        else:
          return count4(rest, tau, acc + 3)
      else:
        if d >= tau:
          return count4(rest, tau, acc + 3)
        else:
          return count4(rest, tau, acc + 2)
    else:
      if c >= tau:
        if d >= tau:
          return count4(rest, tau, acc + 3)
        else:
          return count4(rest, tau, acc + 2)
      else:
        if d >= tau:
          return count4(rest, tau, acc + 2)
        else:
          return count4(rest, tau, acc + 1)
  else:
    if b >= tau:
      if c >= tau:
        if d >= tau:
          return count4(rest, tau, acc + 3)
        else:
          return count4(rest, tau, acc + 2)
      else:
        if d >= tau:
          return count4(rest, tau, acc + 2)
        else:
          return count4(rest, tau, acc + 1)
    else:
      if c >= tau:
        if d >= tau:
          return count4(rest, tau, acc + 2)
        else:
          return count4(rest, tau, acc + 1)
      else:
        if d >= tau:
          return count4(rest, tau, acc + 1)
        else:
          return count4(rest, tau, acc)
