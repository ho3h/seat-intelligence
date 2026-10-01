def prog(x):
  (k, t) = x
  return map_tree(t, k)

def map_tree(t, k):
  # Leaf is (0,), Node is (1, left, value, right)
  if t == (0,):
    return (0,)
  else:
    (_, left, value, right) = t
    new_left = map_tree(left, k)
    new_right = map_tree(right, k)
    return (1, new_left, value + k, new_right)
