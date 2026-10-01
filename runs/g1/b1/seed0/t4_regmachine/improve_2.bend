def prog(xs):
  (r0, r1, r2, r3) = execute(xs, 0, 0, 0, 0)
  return [r0, r1, r2, r3]

def execute(xs, r0, r1, r2, r3):
  match xs:
    case List/Nil:
      return (r0, r1, r2, r3)
    case List/Cons:
      (s0, s1, s2, s3) = step(xs.head, r0, r1, r2, r3)
      return execute(xs.tail, s0, s1, s2, s3)

def step(inst, r0, r1, r2, r3):
  (op, a, b) = inst
  if op == 0:
    return write_reg(a, b, r0, r1, r2, r3)
  else:
    src = read_reg(b, r0, r1, r2, r3)
    if a == 0:
      return (apply_op(op, r0, src), r1, r2, r3)
    else:
      if a == 1:
        return (r0, apply_op(op, r1, src), r2, r3)
      else:
        if a == 2:
          return (r0, r1, apply_op(op, r2, src), r3)
        else:
          return (r0, r1, r2, apply_op(op, r3, src))

def apply_op(op, old, src):
  if op == 1:
    return old + src
  else:
    if op == 2:
      return old - src
    else:
      if op == 3:
        return old * src
      else:
        return src

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
