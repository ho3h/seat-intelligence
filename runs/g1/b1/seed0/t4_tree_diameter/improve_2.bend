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
      through_root = left_height + right_height
      diameter = max3(through_root, left_diameter, right_diameter)
      if left_height > right_height:
        return (left_height + 1, diameter)
      else:
        return (right_height + 1, diameter)

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
