def prog(xs):
  return scan(xs, 0, 1, 0, 0, [])

def scan(xs, sum, term, pending_mul, atom, stack):
  match xs:
    case List/Nil:
      if pending_mul == 1:
        return sum + term * atom
      else:
        return sum + atom
    case List/Cons:
      if xs.head == 32:
        return scan(xs.tail, sum, term, pending_mul, atom, stack)
      else:
        if xs.head >= 48:
          if xs.head <= 57:
            return scan(xs.tail, sum, term, pending_mul, atom * 10 + xs.head - 48, stack)
          else:
            return scan_operator(xs, sum, term, pending_mul, atom, stack)
        else:
          return scan_operator(xs, sum, term, pending_mul, atom, stack)

def scan_operator(xs, sum, term, pending_mul, atom, stack):
  if xs.head == 42:
    if pending_mul == 1:
      next_term = term * atom
    else:
      next_term = atom
    return scan(xs.tail, sum, next_term, 1, 0, stack)
  else:
    if xs.head == 43:
      if pending_mul == 1:
        next_term = term * atom
      else:
        next_term = atom
      return scan(xs.tail, sum + next_term, 1, 0, 0, stack)
    else:
      if xs.head == 40:
        return scan(xs.tail, 0, 1, 0, 0, List/Cons((sum, term, pending_mul), stack))
      else:
        if pending_mul == 1:
          inner_term = term * atom
        else:
          inner_term = atom
        value = sum + inner_term
        match stack:
          case List/Nil:
            return value
          case List/Cons:
            (saved_sum, saved_term, saved_pending) = stack.head
            return scan(xs.tail, saved_sum, saved_term, saved_pending, value, stack.tail)
