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
      smallest = min3(t.f1, left_min, right_min)
      largest = max3(t.f1, left_max, right_max)
      return (smallest, largest)

def min3(a, b, c):
  if a < b:
    if a < c:
      return a
    else:
      return c
  else:
    if b < c:
      return b
    else:
      return c

def max3(a, b, c):
  if a > b:
    if a > c:
      return a
    else:
      return c
  else:
    if b > c:
      return b
    else:
      return c
