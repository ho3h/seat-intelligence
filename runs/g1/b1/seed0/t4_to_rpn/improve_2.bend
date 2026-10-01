def prog(x):
  rev = scan(x, [], [])
  return reverse_list(rev, [])

def reverse_list(xs, acc):
  match xs:
    case List/Nil:
      return acc
    case List/Cons:
      return reverse_list(xs.tail, List/Cons(xs.head, acc))

def read_number(xs, acc):
  match xs:
    case List/Nil:
      return (acc, xs)
    case List/Cons:
      if xs.head < 48:
        return (acc, xs)
      else:
        if xs.head > 57:
          return (acc, xs)
        else:
          return read_number(xs.tail, acc * 10 + xs.head - 48)

def pop_for(ops, incoming, out):
  match ops:
    case List/Nil:
      return (out, ops)
    case List/Cons:
      if ops.head == 40:
        return (out, ops)
      else:
        if ops.head == 42:
          return pop_for(ops.tail, incoming, List/Cons((1, ops.head), out))
        else:
          if incoming == 43:
            return pop_for(ops.tail, incoming, List/Cons((1, ops.head), out))
          else:
            return (out, ops)

def pop_paren(ops, out):
  match ops:
    case List/Nil:
      return (out, ops)
    case List/Cons:
      if ops.head == 40:
        return (out, ops.tail)
      else:
        return pop_paren(ops.tail, List/Cons((1, ops.head), out))

def flush_ops(ops, out):
  match ops:
    case List/Nil:
      return out
    case List/Cons:
      if ops.head == 40:
        return flush_ops(ops.tail, out)
      else:
        return flush_ops(ops.tail, List/Cons((1, ops.head), out))

def scan(xs, out, ops):
  match xs:
    case List/Nil:
      return flush_ops(ops, out)
    case List/Cons:
      if xs.head == 32:
        return scan(xs.tail, out, ops)
      else:
        if xs.head >= 48:
          if xs.head <= 57:
            (n, rest) = read_number(xs, 0)
            return scan(rest, List/Cons((0, n), out), ops)
          else:
            if xs.head == 40:
              return scan(xs.tail, out, List/Cons(40, ops))
            else:
              if xs.head == 41:
                (new_out, new_ops) = pop_paren(ops, out)
                return scan(xs.tail, new_out, new_ops)
              else:
                (new_out, new_ops) = pop_for(ops, xs.head, out)
                return scan(xs.tail, new_out, List/Cons(xs.head, new_ops))
        else:
          if xs.head == 40:
            return scan(xs.tail, out, List/Cons(40, ops))
          else:
            if xs.head == 41:
              (new_out, new_ops) = pop_paren(ops, out)
              return scan(xs.tail, new_out, new_ops)
            else:
              (new_out, new_ops) = pop_for(ops, xs.head, out)
              return scan(xs.tail, new_out, List/Cons(xs.head, new_ops))
