def prog(x):
  return extrema(x)

def extrema(t):
  match t:
    case Gtree/C0:
      return (16777215, 0)
    case Gtree/C1:
      left = extrema(t.f0)
      right = extrema(t.f2)
      (left_min, left_max) = left
      (right_min, right_max) = right
      smallest = min2(t.f1, min2(left_min, right_min))
      largest = max2(t.f1, max2(left_max, right_max))
      return (smallest, largest)

def min2(a, b):
  if a < b:
    return a
  else:
    return b

def max2(a, b):
  if a > b:
    return a
  else:
    return b
