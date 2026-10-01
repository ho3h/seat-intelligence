def prog(xs):
  return scan(xs, 0, 0, 0)

def step(i, best_i, best_v, v):
  if v > best_v:
    return (i, v)
  else:
    return (best_i, best_v)

def scan(xs, i, best_i, best_v):
  match xs:
    case List/Nil:
      return best_i
    case List/Cons:
      a = xs.head
      t1 = xs.tail
      match t1:
        case List/Nil:
          (bi1, bv1) = step(i, best_i, best_v, a)
          return bi1
        case List/Cons:
          b = t1.head
          t2 = t1.tail
          match t2:
            case List/Nil:
              (bi1, bv1) = step(i, best_i, best_v, a)
              (bi2, bv2) = step(i + 1, bi1, bv1, b)
              return bi2
            case List/Cons:
              c = t2.head
              t3 = t2.tail
              match t3:
                case List/Nil:
                  (bi1, bv1) = step(i, best_i, best_v, a)
                  (bi2, bv2) = step(i + 1, bi1, bv1, b)
                  (bi3, bv3) = step(i + 2, bi2, bv2, c)
                  return bi3
                case List/Cons:
                  d = t3.head
                  (bi1, bv1) = step(i, best_i, best_v, a)
                  (bi2, bv2) = step(i + 1, bi1, bv1, b)
                  (bi3, bv3) = step(i + 2, bi2, bv2, c)
                  (bi4, bv4) = step(i + 3, bi3, bv3, d)
                  return scan(t3.tail, i + 4, bi4, bv4)
