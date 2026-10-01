def prog(x):
  (k, t) = x
  a = annotate(t)
  return select(k, a)

def annotate(t):
  match t:
    case Gtree/C0:
      return (0, 0, 0, 0)
    case Gtree/C1:
      left = annotate(t.f0)
      right = annotate(t.f2)
      (left_size, left_left, left_value, left_right) = left
      (right_size, right_left, right_value, right_right) = right
      return (left_size + right_size + 1, left, t.f1, right)

def select(k, a):
  (size, left, value, right) = a
  if size == 0:
    return 16777215
  else:
    (left_size, left_left, left_value, left_right) = left
    if k < left_size:
      return select(k, left)
    else:
      if k == left_size:
        return value
      else:
        return select(k - left_size - 1, right)
