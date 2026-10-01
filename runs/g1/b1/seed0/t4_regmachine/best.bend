def prog(xs):
  (r0, r1, r2, r3) = execute(xs, 0, 0, 0, 0)
  return [r0, r1, r2, r3]

def execute(xs, r0, r1, r2, r3):
  match xs:
    case List/Nil:
      return (r0, r1, r2, r3)
    case List/Cons:
      (op, a, b) = xs.head
      if op == 0:
        if a == 0:
          return execute(xs.tail, b, r1, r2, r3)
        else:
          if a == 1:
            return execute(xs.tail, r0, b, r2, r3)
          else:
            if a == 2:
              return execute(xs.tail, r0, r1, b, r3)
            else:
              return execute(xs.tail, r0, r1, r2, b)
      else:
        bv = read_reg(b, r0, r1, r2, r3)
        if a == 0:
          if op == 1:
            return execute(xs.tail, r0 + bv, r1, r2, r3)
          else:
            if op == 2:
              return execute(xs.tail, r0 - bv, r1, r2, r3)
            else:
              if op == 3:
                return execute(xs.tail, r0 * bv, r1, r2, r3)
              else:
                return execute(xs.tail, bv, r1, r2, r3)
        else:
          if a == 1:
            if op == 1:
              return execute(xs.tail, r0, r1 + bv, r2, r3)
            else:
              if op == 2:
                return execute(xs.tail, r0, r1 - bv, r2, r3)
              else:
                if op == 3:
                  return execute(xs.tail, r0, r1 * bv, r2, r3)
                else:
                  return execute(xs.tail, r0, bv, r2, r3)
          else:
            if a == 2:
              if op == 1:
                return execute(xs.tail, r0, r1, r2 + bv, r3)
              else:
                if op == 2:
                  return execute(xs.tail, r0, r1, r2 - bv, r3)
                else:
                  if op == 3:
                    return execute(xs.tail, r0, r1, r2 * bv, r3)
                  else:
                    return execute(xs.tail, r0, r1, bv, r3)
            else:
              if op == 1:
                return execute(xs.tail, r0, r1, r2, r3 + bv)
              else:
                if op == 2:
                  return execute(xs.tail, r0, r1, r2, r3 - bv)
                else:
                  if op == 3:
                    return execute(xs.tail, r0, r1, r2, r3 * bv)
                  else:
                    return execute(xs.tail, r0, r1, r2, bv)

def read_reg(i, r0, r1, r2, r3):
  if i == 0:
    return r0
  else:
    if i == 1:
      return r1
    else:
      if i == 2:
        return r2
      else:
        return r3
