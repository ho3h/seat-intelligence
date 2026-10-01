def prog(x):
  (k, t) = x
  return map_tree(t, k)

def map_tree(t, k):
  match t:
    case (0,):
      return (0,)
    case (1, left, value, right):
      new_left = map_tree(left, k)
      new_right = map_tree(right, k)
      return (1, new_left, value + k, new_right)
