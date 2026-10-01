def prog(x):
  (height, diameter) = measure(x)
  return diameter

def measure(tree):
  match tree:
    case Gtree/C0:
      return (0, 0)
    case Gtree/C1:
      (left_height, left_diameter) = measure(tree.f0)
      (right_height, right_diameter) = measure(tree.f2)
      height = 1 + max2(left_height, right_height)
      through_root = left_height + right_height
      diameter = max3(through_root, left_diameter, right_diameter)
      return (height, diameter)

def max2(a, b):
  if a > b:
    return a
  else:
    return b

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
