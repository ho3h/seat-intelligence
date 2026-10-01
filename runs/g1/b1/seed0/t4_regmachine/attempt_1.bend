def prog(xs):
  (r0, r1, r2, r3) = execute(xs, 0, 0, 0, 0)
  return [r0, r1, r2, r3]

def execute(xs, r0, r1, r2, r3):
  match xs:
    case List/Nil:
      return (r0, r1, r2, r3)
    case List/Cons:
      (op, a, b) = xs.head
      value = eval_inst(op, a, b, r0, r1, r2, r3)
      (s0, s1, s2, s3) = write_reg(a, value, r0, r1, r2, r3)
      return execute(xs.tail, s0, s1, s2, s3)

def eval_inst(op, a, b, r0, r1, r2, r3):
  if op == 0:
    return b
  else:
    if op == 1:
      return read_reg(a, r0, r1, r2, r3) + read_reg(b, r0, r1, r2, r3)
    else:
      if op == 2:
        return read_reg(a, r0, r1, r2, r3) - read_reg(b, r0, r1, r2, r3)
      else:
        if op == 3:
          return read_reg(a, r0, r1, r2, r3) * read_reg(b, r0, r1, r2, r3)
        else:
          return read_reg(b, r0, r1, r2, r3)

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

def write_reg(i, value, r0, r1, r2, r3):
  if i == 0:
    return (value, r1, r2, r3)
  else:
    if i == 1:
      return (r0, value, r2, r3)
    else:
      if i == 2:
        return (r0, r1, value, r3)
      else:
        return (r0, r1, r2, value)
