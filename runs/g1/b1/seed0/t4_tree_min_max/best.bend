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

      if left_min < right_min:
        child_min = left_min
      else:
        child_min = right_min
      if t.f1 < child_min:
        smallest = t.f1
      else:
        smallest = child_min

      if left_max > right_max:
        child_max = left_max
      else:
        child_max = right_max
      if t.f1 > child_max:
        largest = t.f1
      else:
        largest = child_max

      return (smallest, largest)
